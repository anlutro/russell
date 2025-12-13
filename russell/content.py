from datetime import datetime
import logging
import os.path
import re

import dateutil.parser
import dateutil.tz
import markdown
import slugify

LOG = logging.getLogger(__name__)
SYSTEM_TZINFO = dateutil.tz.tzlocal()


md = markdown.Markdown(extensions=["markdown.extensions.fenced_code"])


def render_markdown(text):
    return md.convert(text)


def schema_url(url, https=False):
    """
    Convert schemaless URLs like //localhost to http:// or https:// URLs.
    """
    return re.sub(r"^\/\/", ("https" if https else "http") + "://", url)


def _get_excerpt(body):
    excerpt_parts = []
    # iterate through lines until we find an empty line, which would indicate
    # two newlines in a row
    for line in body.splitlines():
        if line == "":
            break
        excerpt_parts.append(line)
    return " ".join(excerpt_parts)


def _get_description(body, max_chars, search=". "):
    # the idea here is to grab the first few sentences of a body and use that
    # as the description.
    stop_idx = body.rfind(search, 0, max_chars)
    if stop_idx == -1 or stop_idx < (max_chars / 2):
        stop_idx = body.find(search, max_chars)
    if stop_idx == -1:
        return body
    return body[0 : stop_idx + 1]


# TODO: surely there's something in stdlib for this
def _str_to_bool(string):
    norm_string = str(string).strip().lower()
    if norm_string in ("yes", "true"):
        return True
    elif norm_string in ("no", "false", ""):
        return False
    raise ValueError("Invalid boolean string: %r" % string)


class Content:
    """
    Abstract class to act as a base for all types of content (defined as
    anything with a URL).
    """

    # this property allows us to use the root url as well as other nice
    # things. it's not clean design, it's a circular dependency type of
    # situation, but it makes things very convenient. the property is set
    # with metaprogramming magic which is also scary.
    cm = None  # pylint: disable=invalid-name

    @property
    def root_url(self):
        if self.cm:
            return self.cm.root_url
        return "//localhost"


class Entry(Content):
    """
    Abstract class for text content.
    """

    def __init__(
        self, title, body, slug=None, subtitle=None, description=None, public=True
    ):
        """
        Constructor.
        Args:
          title (str): Title.
          body (str): Markdown body of the entry.
          slug (str): Optional slug for the entry. If not provided, sulg will be
            guessed based on the title.
          subtitle (str): Optional subtitle.
          description (str): Optional description/excerpt. Mostly used for
            <meta> tags.
          public (bool): Whether the entry should be public or not. Usually this
            defines whether the entry shows up in the front page, archive pages
            etc., but even private entries are publicly accessable if you know
            the URL.
        """
        self.title = title
        self.body = body
        self.slug = slug or slugify.slugify(title)
        self.subtitle = subtitle
        self.description = description
        self.public = public

    @property
    def url(self):
        return self.root_url + "/" + self.slug

    @classmethod
    def from_string(cls, contents, **kwargs):
        """
        Given a markdown string, create an Entry object.

        Usually subclasses will want to customize the parts of the markdown
        where you provide values for attributes like public - this can be done
        by overriding the process_meta method.
        """
        lines = contents.splitlines()
        title = None
        description = None

        line = lines.pop(0)
        while line != "":
            if not title and line.startswith("#"):
                title = line[1:].strip()
            elif line.startswith("title:"):
                title = line[6:].strip()
            elif line.startswith("description:"):
                description = line[12:].strip()
            elif line.startswith("subtitle:"):
                kwargs["subtitle"] = line[9:].strip()
            elif line.startswith("comments:"):
                try:
                    kwargs["allow_comments"] = _str_to_bool(line[9:])
                except ValueError:
                    LOG.warning("invalid boolean value for comments", exc_info=True)

            cls.process_meta(line, kwargs)

            line = lines.pop(0)

        # the only lines left should be the actual contents
        body = "\n".join(lines).strip()
        excerpt = _get_excerpt(body)
        if description is None:
            description = _get_description(excerpt, 160)
        if issubclass(cls, Post):
            kwargs["excerpt"] = render_markdown(excerpt)
        body = render_markdown(body)

        return cls(title=title, body=body, description=description, **kwargs)

    @classmethod
    def process_meta(cls, line, kwargs):
        """
        Process a line of metadata found in the markdown.

        Lines are usually in the format of "key: value".

        Modify the kwargs dict in order to change or add new kwargs that should
        be passed to the class's constructor.
        """
        if line.startswith("slug:"):
            kwargs["slug"] = line[5:].strip()

        elif line.startswith("public:"):
            try:
                kwargs["public"] = _str_to_bool(line[7:])
            except ValueError:
                LOG.warning("invalid boolean value for public", exc_info=True)

        elif line.startswith("private:"):
            try:
                kwargs["public"] = not _str_to_bool(line[8:])
            except ValueError:
                LOG.warning("invalid boolean value for private", exc_info=True)

    @classmethod
    def from_file(cls, path, **kwargs):
        """
        Given a markdown file, get an Entry object.
        """
        LOG.debug('creating %s from "%s"', cls, path)

        # the filename will be the default slug - can be overridden later
        kwargs["slug"] = os.path.splitext(os.path.basename(path))[0]

        # TODO: ideally this should be part of the Post class.
        # if a pubdate isn't explicitly passed, get it from the file metadata
        # instead. note that it might still be overriden later on while reading
        # the file contents.
        if issubclass(cls, Post) and not kwargs.get("pubdate"):
            # you would think creation always comes before modification, but you
            # can manually modify a file's modification date to one earlier than
            # the creation date. this lets you set a post's pubdate by running
            # the command `touch`. we support this behaviour by simply finding
            # the chronologically earliest date of creation and modification.
            timestamp = min(os.path.getctime(path), os.path.getmtime(path))
            kwargs["pubdate"] = datetime.fromtimestamp(timestamp)

        with open(path, "r") as file:
            entry = cls.from_string(file.read(), **kwargs)

        return entry

    def __lt__(self, other):
        """
        Implement "less than" comparisons to allow alphabetic sorting.
        """
        return self.title < other.title


class Page(Entry):
    def __init__(self, *args, allow_comments=False, directory=None, **kwargs):
        """
        Constructor. Also see Entry.__init__.

        Args:
          allow_comments (bool): Whether to allow comments. Default False.
          directory (str): Optional. If the page should live in a subdirectory
            instead of at the web root, specify it here instead of making it
            part of the slug.
        """
        super().__init__(*args, **kwargs)
        self.allow_comments = allow_comments
        self.dir = directory


class Post(Entry):
    def __init__(
        self,
        *args,
        pubdate=None,
        excerpt=None,
        tags=None,
        allow_comments=True,
        **kwargs,
    ):
        """
        Constructor. Also see Entry.__init__.

        Args:
          pubdate (datetime): When the post was published.
          excerpt (str): An excerpt of the post body.
          tags (list): A list of Tag objects associated with the post.
          allow_comments (bool): Whether to allow comments. Default False.
        """
        super().__init__(*args, **kwargs)
        self.excerpt = excerpt or _get_excerpt(self.body)
        self.pubdate = pubdate
        self.tags = tags or []
        self.allow_comments = allow_comments

    @classmethod
    def make_tag(cls, tag_name):
        """
        Make a Tag object from a tag name. Registers it with the content manager
        if possible.
        """
        if cls.cm:
            return cls.cm.make_tag(tag_name)
        return Tag(tag_name.strip())

    def has_tag(self, tag):
        return self.has_tags((tag,))

    def has_tags(self, tags, oper=any):
        # inefficient, could be improved by having a custom TagCollection
        # class, but the number of tags is usually very low so it's fine
        return oper((tag in self.tags) for tag in tags)

    @classmethod
    def process_meta(cls, line, kwargs):
        super().process_meta(line, kwargs)

        if line.startswith("pubdate:"):
            pubdate_str = line[8:].strip()
            try:
                kwargs["pubdate"] = dateutil.parser.parse(pubdate_str)
            except ValueError:
                LOG.warning("invalid pubdate given", exc_info=True)
            if "pubdate" in kwargs and not kwargs["pubdate"].tzinfo:
                kwargs["pubdate"] = kwargs["pubdate"].replace(tzinfo=SYSTEM_TZINFO)
                LOG.warning(
                    "found pubdate without timezone: %r - using %r",
                    pubdate_str,
                    SYSTEM_TZINFO,
                )

        elif line.startswith("tags:"):
            line_tags = line[5:].strip().split(",")
            kwargs["tags"] = [cls.make_tag(tag) for tag in line_tags if tag]

    @property
    def url(self):
        return "%s/posts/%s" % (self.root_url, self.slug)

    @property
    def tag_links(self):
        """
        Get a list of HTML links for all the tags associated with the post.
        """
        return ['<a href="%s">%s</a>' % (tag.url, tag.title) for tag in self.tags]

    def __lt__(self, other):
        """
        Implement comparison/sorting that takes pubdate into consideration.
        """
        if self.pubdate == other.pubdate:
            return super().__lt__(other)
        return self.pubdate > other.pubdate


class Tag(Content):
    def __init__(self, title, slug=None):
        if not title:
            raise ValueError("cannot create Tag with empty title")
        self.title = title
        self.slug = slug or slugify.slugify(title)

    @property
    def url(self):
        return self.root_url + "/tags/" + self.slug

    def __lt__(self, other):
        return self.title < other.title

    def __eq__(self, other):
        if isinstance(other, Tag):
            return self.slug == other.slug
        if not isinstance(other, str):
            raise ValueError("can only compare with Tag or str, %s given" % type(other))
        other = other.lower()
        return self.slug == other or self.title.lower() == other


class CaseInsensitiveDict(dict):
    """
    A dictionary where the keys (assumed to be strings) are not case-sensitive.
    """

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())


class ContentManager:
    """
    Class that keeps track of various content.

    Objects of this class have "Page", "Post" and "Tag" attributes, which work
    as plain class constructors, but will also set the attribute "cm" on these,
    to make it easy for instances of these to know what their site's root_url
    is. Also keeps track of tags to avoid duplicate instances of Tag objectss
    """

    def __init__(self, root_url):
        # pylint: disable=invalid-name
        self.Page = type("CM_Page", (Page,), {"cm": self})
        self.Post = type("CM_Post", (Post,), {"cm": self})
        self.Tag = type("CM_Tag", (Tag,), {"cm": self})
        # pylint: enable=invalid-name
        self.root_url = root_url
        self.pages = []
        self.posts = []
        self.tags = []
        self.tags_dict = CaseInsensitiveDict()

    def make_tag(self, tag_name):
        tag_name = tag_name.strip()
        if tag_name not in self.tags_dict:
            self.tags_dict[tag_name] = self.Tag(tag_name)
        return self.tags_dict[tag_name]

    def add_pages(self, pages, resort=True):
        self.pages.extend(pages)
        if resort:
            self.pages.sort()

    def add_posts(self, posts, resort=True):
        self.posts.extend(posts)
        for post in posts:
            for tag in post.tags:
                if tag not in self.tags:
                    self.tags.append(tag)

        if resort:
            self.tags.sort()
            self.posts.sort()
