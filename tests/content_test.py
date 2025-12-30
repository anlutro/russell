from datetime import datetime

from russell.content import (
    ContentManager,
    Post,
    Page,
    Tag,
    CaseInsensitiveDict,
    schema_url,
)


def test_basic_parsing():
    md = "# Hello world!\n\nThis is a test post."
    post = Post.from_string(md)
    assert "Hello world!" == post.title
    assert "<p>This is a test post.</p>" == post.body


def test_code_block_parsing():
    md = "# Hello world!\n\n```sh\nfoo\n```"
    post = Post.from_string(md)
    html_class = "language-sh"
    expected = '<pre><code class="%s">foo\n</code></pre>' % html_class
    assert expected in post.body


def test_pubdate_parsing():
    md = "# Hello world!\npubdate:2015-01-01 01:23:45\n\nThis is a test post."
    post = Post.from_string(md)
    assert post.title == "Hello world!"
    # we don't know what the timezone at the end will be
    assert post.pubdate.isoformat().startswith("2015-01-01T01:23:45+")
    assert post.body == "<p>This is a test post.</p>"


def test_tag_parsing():
    md = "# Hello world!\ntags:Foo Bar, Bar Baz\n\nThis is a test post."
    post = Post.from_string(md)
    assert post.title == "Hello world!"
    assert [tag.title for tag in post.tags] == ["Foo Bar", "Bar Baz"]
    assert post.body == "<p>This is a test post.</p>"


def test_empty_tags_parsing():
    md = "# Hello world!\ntags:\n\nThis is a test post."
    post = Post.from_string(md)
    assert post.tags == []


def test_public_parsing():
    md = "# Hello world!\npublic: false\n\nThis is a test post."
    post = Post.from_string(md)
    assert post.public is False


def test_private_parsing():
    md = "# Hello world!\nprivate: true\n\nThis is a test post."
    post = Post.from_string(md)
    assert post.public is False


def test_excerpt_cuts_off_at_double_newline():
    md = (
        "# Hello world!\n\n"
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec\n"
        "maximus diam ut ligula blandit semper. Proin id nulla libero.\n\n"
        "Quisque blandit ut enim in ultricies. Sed sollicitudin aliquam\n"
        "consectetur. In pharetra, justo a ultrices porttitor, quam risus\n"
        "semper dolor, interdum tempus est libero ac tellus."
    )
    post = Post.from_string(md)
    expected = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Donec maximus diam ut ligula blandit semper. Proin id nulla libero."
    )
    assert "<p>%s</p>" % expected == post.excerpt


def test_description_cuts_off_at_160_characters():
    md = (
        "# Hello world!\n\n"
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec\n"
        "maximus diam ut ligula blandit semper. Proin id nulla libero.\n"
        "Quisque blandit ut enim in ultricies. Sed sollicitudin aliquam\n"
        "consectetur. In pharetra, justo a ultrices porttitor, quam risus\n"
        "semper dolor, interdum tempus est libero ac tellus."
    )
    post = Post.from_string(md)
    expected = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Donec maximus diam ut ligula blandit semper. Proin id nulla libero."
    )
    assert expected == post.description
    assert len(post.description) < 160


def test_content_manager_root_url():
    cm = ContentManager(root_url="//example.com")
    md = "# Hello world!\n\nThis is a test post."
    post = cm.Post.from_string(md)
    assert post.url == "//example.com/posts/hello-world"


def test_content_manager_tags():
    cm = ContentManager(root_url="//example.com")
    md = "# Hello world!\ntags:Foo Bar, Bar Baz\n\nThis is a test post."
    post1 = cm.Post.from_string(md)
    post2 = cm.Post.from_string(md)
    assert post1.tags[0] is post2.tags[0]
    assert post1.tags[1] is post2.tags[1]


def test_page_sort():
    pages = sorted(
        [
            Page("b", ""),
            Page("c", ""),
            Page("a", ""),
        ]
    )
    assert pages[0].title == "a"
    assert pages[1].title == "b"
    assert pages[2].title == "c"


def test_post_sort():
    posts = sorted(
        [
            Post("b", ""),
            Post("c", ""),
            Post("a", ""),
        ]
    )
    assert posts[0].title == "a"
    assert posts[1].title == "b"
    assert posts[2].title == "c"


def test_post_sort_pubdate():
    posts = sorted(
        [
            Post("a", "", pubdate=datetime(2016, 2, 1, 1, 1, 1)),
            Post("b", "", pubdate=datetime(2016, 1, 1, 1, 1, 1)),
            Post("c", "", pubdate=datetime(2016, 3, 1, 1, 1, 1)),
        ]
    )
    assert posts[0].title == "c"
    assert posts[1].title == "a"
    assert posts[2].title == "b"


def test_tag_sorting():
    tags = sorted([Tag("b"), Tag("a")])
    assert tags[0].title == "a"
    assert tags[1].title == "b"


def test_tag_equality():
    assert Tag("Test Tag") == "test-tag"
    assert Tag("Test Tag") == "Test Tag"


def test_post_has_tag():
    tag = Tag("Test Tag")
    post = Post("test", "test", tags=[tag])
    assert post.has_tag(tag)
    assert post.has_tag("test-tag")
    assert post.has_tag("Test Tag")
    assert not post.has_tag("foo")


def test_post_has_tags():
    tag1 = Tag("tag 1")
    tag2 = Tag("tag 2")
    post = Post("test", "test", tags=[tag1, tag2])
    assert post.has_tags(["tag 1"], oper=any)
    assert post.has_tags(["tag 1"], oper=all)
    assert post.has_tags(["tag 1", "tag 2"], oper=any)
    assert post.has_tags(["tag 1", "tag 2"], oper=all)
    assert post.has_tags(["tag 1", "tag 3"], oper=any)
    assert not post.has_tags(["tag 1", "tag 3"], oper=all)


def test_case_insensitive_dict():
    d = CaseInsensitiveDict({"a": True})
    assert "a" in d
    assert "A" in d
    assert "b" not in d


def test_schema_url_changes_schema_agnostic_urls_to_http_or_https():
    assert "http://example.com" == schema_url("//example.com", https=False)
    assert "https://example.com" == schema_url("//example.com", https=True)


def test_schema_url_does_not_change_existing_schema_urls():
    assert "http://example.com" == schema_url("http://example.com", https=True)
