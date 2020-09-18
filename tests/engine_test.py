from russell.content import Post, Tag
from russell.engine import make_link


def test_make_link(engine):
    assert '<a href="/test">Test</a>' == make_link("Test", "/test")
    assert '<a href="http://test">Test</a>' == make_link("Test", "http://test")
    assert (
        '<a href="http://test" target="_blank" rel="noopener noreferrer">Test</a>'
        == make_link("Test", "http://test", blank=True)
    )


def test_get_asset_link(engine):
    assert "//localhost/assets/test.css" == engine.get_asset_url("test.css")


def test_get_asset_link_with_hash(engine):
    engine.asset_hash["test.css"] = "0f4c"
    assert "//localhost/assets/test.css?0f4c" == engine.get_asset_url_qs("test.css")
    assert "//localhost/assets/test.0f4c.css" == engine.get_asset_url_part("test.css")


def test_get_posts_does_not_mutate_posts(engine):
    engine.cm.add_posts(
        [
            Post("test post 1", "test post 1", public=True),
            Post("test post 2", "test post 2", public=False),
        ]
    )
    original_posts = engine.posts.copy()
    engine.get_posts(private=False)
    assert original_posts == engine.posts
    engine.get_posts(private=True)
    assert original_posts == engine.posts


def test_get_posts_exclude_tags(engine):
    engine.cm.add_posts(
        [
            Post("test post 1", "test post 1", tags=[Tag("a")]),
            Post("test post 2", "test post 2", tags=[Tag("b")]),
        ]
    )
    posts = engine.get_posts(exclude_tags=["a"])
    assert len(posts) == 1
    assert posts[0].title == "test post 2"
    posts = engine.get_posts(exclude_tags=["b"])
    assert len(posts) == 1
    assert posts[0].title == "test post 1"
