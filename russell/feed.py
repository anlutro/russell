from datetime import datetime

import PyRSS2Gen


def write_rss(blog, path):
    items = [get_post_rss(post) for post in blog.posts]

    rss = PyRSS2Gen.RSS2(
        title=blog.title,
        description='',
        link=blog.root_url,
        lastBuildDate=datetime.now(),
        items=items
    )

    with open(path, 'w+') as f:
        rss.write_xml(f)


def get_post_rss(post):
    return PyRSS2Gen.RSSItem(
        title=post.title,
        description=post.excerpt,
        link=post.url,
        pubDate=post.pubdate
    )
