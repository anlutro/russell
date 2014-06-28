from datetime import datetime

import PyRSS2Gen


class FeedGenerator():
    def __init__(self, blog):
        self.blog = blog

    def write_to(self, path):
        rss = PyRSS2Gen.RSS2(
            title=self.blog.title,
            description='',
            link=self.blog.root_url,
            lastBuildDate=datetime.now(),
            items=self.get_items()
        )

        rss.write_xml(open(path, 'w+'))

    def get_items(self):
        items = []

        for post in self.blog.posts:
            items.append(self.get_post_rss(post))

        return items

    def get_post_rss(self, post):
        return PyRSS2Gen.RSSItem(
            title=post.title,
            link=post.url,
            pubDate=post.pubdate
        )
