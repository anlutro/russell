from russell.feed import get_rss_feed
from russell.content import Post


def get_rss(engine, **kwargs):
    feed = get_rss_feed(engine, **kwargs)
    return feed.rss_str().decode("utf-8")


def test_can_generate_feed(engine):
    rss = get_rss(engine)
    assert "<?xml version='1.0' encoding='UTF-8'?>" in rss
    assert "<title>Test Blog</title>" in rss
    assert "<link>http://localhost</link>" in rss


def test_posts_are_in_feed(engine):
    engine.cm.add_posts([Post("Test Post", "This is a test")])
    rss = get_rss(engine)
    assert "<title>Test Post</title>" in rss
    assert "<link>http://localhost/posts/test-post</link>" in rss
    assert '<guid isPermaLink="false">http://localhost/posts/test-post</guid>' in rss


def test_read_more_link_is_present_if_only_excerpt_is_true(engine):
    engine.cm.add_posts([Post("Test Post", "This is a test\n\nVery long post")])
    rss = get_rss(engine, only_excerpt=True)
    assert "&lt;p&gt;This is a test&lt;/p&gt;" in rss
    assert (
        '&lt;p&gt;Read the full article at &lt;a href="//localhost/posts/test-post" '
        'target="_blank"&gt;//localhost/posts/test-post&lt;/a&gt;&lt;/p&gt;'
    ) in rss
    assert "Very long post" not in rss


def test_full_body_is_present_if_only_excerpt_is_true(engine):
    engine.cm.add_posts([Post("Test Post", "This is a test\n\nVery long post")])
    rss = get_rss(engine, only_excerpt=False)
    assert "Read the full article at" not in rss
    assert "Very long post" in rss
