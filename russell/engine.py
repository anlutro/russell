from datetime import datetime
import hashlib
import logging
import os
import os.path
import shutil

import jinja2

import russell.content
import russell.feed
import russell.sitemap

LOG = logging.getLogger(__name__)


def _listfiles(root_dir):
    results = set()

    for root, _, files in os.walk(root_dir):
        for file in files:
            results.add(os.path.join(root, file))

    return results


def make_link(title, url, blank=False):
    """
    Make a HTML link out of an URL.

    Args:
      title (str): Text to show for the link.
      url (str): URL the link will point to.
      blank (bool): If True, appends target=_blank, noopener and noreferrer to
        the <a> element. Defaults to False.
    """
    attrs = 'href="%s"' % url
    if blank:
        attrs += ' target="_blank" rel="noopener noreferrer"'
    return "<a %s>%s</a>" % (attrs, title)


class BlogEngine:
    """
    The main instance that contains blog configuration and content, as well as
    generating end results.
    """

    def __init__(
        self,
        root_path,
        root_url,
        site_title,
        site_desc=None,
        cache_busting_strategy="qs",
    ):
        """
        Constructor.

        Args:
          root_path (str): Full path to the directory which contains the posts,
            pages, templates etc. directories.
          root_url (str): The root URL of your website.
          site_title (str): The title of your website.
          site_desc (str): A subtitle or description of your website.
          cache_busting_strategy (str): None, "qs" or "part"
        """
        assert os.path.exists(root_path), "root_path must be an existing directory"
        self.root_path = root_path
        self.root_url = root_url or ""
        self.site_title = site_title
        self.site_desc = site_desc

        self.cm = russell.content.ContentManager(
            root_url
        )  # pylint: disable=invalid-name
        self.pages = self.cm.pages
        self.posts = self.cm.posts
        self.tags = self.cm.tags

        self.asset_hash = {}
        if cache_busting_strategy == "qs":
            self.get_asset_url = self.get_asset_url_qs
        elif cache_busting_strategy == "part":
            self.get_asset_url = self.get_asset_url_part
        else:
            LOG.warning("no cache busting will be used!")
            self.get_asset_url = str

        self.jinja = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(root_path, "templates")),
        )
        self.jinja.globals.update(
            {
                "a": make_link,
                "asset_hash": self.asset_hash,
                "asset_url": self.get_asset_url,
                "now": datetime.now(),
                "root_url": self.root_url,
                "site_description": self.site_desc,
                "site_title": self.site_title,
                "tags": self.tags,
            }
        )

    def get_asset_url_qs(self, path):
        """
        Get the URL of an asset. If asset hashes are added and one exists for
        the path, it will be appended as a query string.

        Args:
          path (str): Path to the file, relative to your "assets" directory.
        """
        if path.endswith(self.bust_extensions) and path in self.asset_hash:
            path += "?" + self.asset_hash[path]
        return self.root_url + "/assets/" + path

    bust_extensions = (".js", ".min.js", ".js.map", ".css", ".min.css", ".css.map")

    def get_asset_url_part(self, path):
        """
        Get the URL of an asset. If asset hashes are added and one exists for
        the path, it will be appended as a query string.

        Args:
          path (str): Path to the file, relative to your "assets" directory.
        """
        if path.endswith(self.bust_extensions) and path in self.asset_hash:
            *dirs, filename = path.split("/")
            file_parts = filename.split(".", maxsplit=1)
            file_parts.insert(1, self.asset_hash[path])
            path = "/".join(dirs + [".".join(file_parts)])
        return self.root_url + "/assets/" + path

    def add_pages(self, path="pages"):
        """
        Look through a directory for markdown files and add them as pages.
        """
        pages_path = os.path.join(self.root_path, path)
        pages = []
        for file in _listfiles(pages_path):
            page_dir = os.path.relpath(os.path.dirname(file), pages_path)
            if page_dir == ".":
                page_dir = None
            pages.append(self.cm.Page.from_file(file, directory=page_dir))
        self.cm.add_pages(pages)

    def add_posts(self, path="posts"):
        """
        Look through a directory for markdown files and add them as posts.
        """
        path = os.path.join(self.root_path, path)
        self.cm.add_posts([self.cm.Post.from_file(file) for file in _listfiles(path)])

    def copy_assets(self, path="assets"):
        """
        Copy assets into the destination directory.
        """
        path = os.path.join(self.root_path, path)
        for root, _, files in os.walk(path):
            for file in files:
                fullpath = os.path.join(root, file)
                relpath = os.path.relpath(fullpath, path)
                copy_to = os.path.join(self._get_dist_path(relpath, directory="assets"))
                LOG.debug("copying %r to %r", fullpath, copy_to)
                shutil.copyfile(fullpath, copy_to)

    def add_asset_hashes(self, path="dist/assets"):
        """
        Scan through a directory and add hashes for each file found.
        """
        for fullpath in _listfiles(os.path.join(self.root_path, path)):
            relpath = fullpath.replace(self.root_path + "/" + path + "/", "")
            md5sum = hashlib.md5(open(fullpath, "rb").read()).hexdigest()
            LOG.debug("MD5 of %s (%s): %s", fullpath, relpath, md5sum)
            self.asset_hash[relpath] = md5sum

    def get_posts(self, num=None, tag=None, exclude_tags=None, private=False):
        """
              Get all the posts added to the blog.

              Args:
                num (int): Optional. If provided, only return N posts (sorted by date,
                  most recent first).
                tag (Tag): Optional. If provided, only return posts that have a
                  specific tag.
        exclude_tags (set): Optional. If provided, don't return posts that
          have these tags.
                private (bool): By default (if False), private posts are not included.
                  If set to True, private posts will also be included.
        """
        posts = self.posts

        if not private:
            posts = [post for post in posts if post.public]

        if tag:
            posts = [post for post in posts if tag in post.tags]
        elif exclude_tags:
            posts = [post for post in posts if not post.has_tags(exclude_tags)]

        if num:
            return posts[:num]
        return posts

    def _get_dist_path(self, path, directory=None):
        if isinstance(path, str):
            path = [path]
        # TODO: the assumption that there will only ever be one directory
        # works for now, but probably won't hold up
        if directory:
            path.insert(0, directory)
        return os.path.join(self.root_path, "dist", *path)

    def _get_template(self, template):
        if isinstance(template, str):
            template = self.jinja.get_template(template)
        return template

    def generate_pages(self):
        """
        Generate HTML out of the pages added to the blog.
        """
        for page in self.pages:
            self.generate_page(page.slug, template="page.html.jinja", page=page)

    def generate_posts(self):
        """
        Generate single-post HTML files out of posts added to the blog. Will not
        generate front page, archives or tag files - those have to be generated
        separately.
        """
        for post in self.posts:
            self.generate_page(
                ["posts", post.slug],
                template="post.html.jinja",
                post=post,
            )

    def generate_tags(self):
        """
        Generate one HTML page for each tag, each containing all posts that
        match that tag.
        """
        for tag in self.tags:
            posts = self.get_posts(tag=tag, private=True)
            self.generate_page(
                ["tags", tag.slug], template="archive.html.jinja", posts=posts
            )

    def generate_page(self, path, template, **kwargs):
        """
        Generate the HTML for a single page. You usually don't need to call this
        method manually, it is used by a lot of other, more end-user friendly
        methods.

        Args:
          path (str): Where to place the page relative to the root URL. Usually
            something like "index", "about-me", "projects/example", etc.
          template (str): Which jinja template to use to render the page.
          **kwargs: Kwargs will be passed on to the jinja template. Also, if
            the `page` kwarg is passed, its directory attribute will be
            prepended to the path.
        """
        directory = None
        if kwargs.get("page"):
            directory = kwargs["page"].dir

        path = self._get_dist_path(path, directory=directory)
        if not path.endswith(".html"):
            path = path + ".html"

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        html = self._get_template(template).render(**kwargs)

        with open(path, "w+") as file:
            file.write(html)

    def generate_index(self, num_posts=5, exclude_tags=None):
        """
        Generate the front page, aka index.html.
        """
        posts = self.get_posts(num=num_posts, exclude_tags=None)
        self.generate_page("index", template="index.html.jinja", posts=posts)

    def generate_archive(self):
        """
        Generate the archive HTML page.
        """
        self.generate_page(
            "archive", template="archive.html.jinja", posts=self.get_posts()
        )

    def generate_rss(self, path="rss.xml", only_excerpt=True, https=False):
        """
        Generate the RSS feed.

        Args:
          path (str): Where to save the RSS file. Make sure that your jinja
            templates refer to the same path using <link>.
          only_excerpt (bool): If True (the default), don't include the full
            body of posts in the RSS. Instead, include the first paragraph and
            a "read more" link to your website.
          https (bool): If True, links inside the RSS with relative scheme (e.g.
            //example.com/something) will be set to HTTPS. If False (the
            default), they will be set to plain HTTP.
        """
        feed = russell.feed.get_rss_feed(self, only_excerpt=only_excerpt, https=https)
        feed.rss_file(self._get_dist_path(path))

    def generate_sitemap(self, path="sitemap.xml", https=False):
        """
        Generate an XML sitemap.

        Args:
          path (str): The name of the file to write to.
          https (bool): If True, links inside the sitemap with relative scheme
            (e.g. example.com/something) will be set to HTTPS. If False (the
            default), they will be set to plain HTTP.
        """
        sitemap = russell.sitemap.generate_sitemap(self, https=https)
        self.write_file(path, sitemap)

    def write_file(self, path, contents):
        """
        Write a file of any type to the destination path. Useful for files like
        robots.txt, manifest.json, and so on.

        Args:
          path (str): The name of the file to write to.
          contents (str or bytes): The contents to write.
        """
        path = self._get_dist_path(path)
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if isinstance(contents, bytes):
            mode = "wb+"
        else:
            mode = "w"
        with open(path, mode) as file:
            file.write(contents)
