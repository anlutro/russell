from feedgen.feed import FeedGenerator
from russell.content import schema_url


def get_rss_feed(blog, only_excerpt=True, https=False):
    generator = FeedGenerator()

    root_href = schema_url(blog.root_url, https)
    generator.id(root_href)
    generator.link(href=root_href, rel="alternate")
    generator.title(blog.site_title)
    generator.subtitle(blog.site_desc or blog.site_title)

    for post in blog.get_posts():
        if only_excerpt:
            read_more = (
                'Read the full article at <a href="%s" target="_blank">%s</a>'
                % (post.url, post.url)
            )
            body = "<p>%s</p><p>%s</p>" % (post.excerpt, read_more)
        else:
            body = post.body

        post_href = schema_url(post.url, https=https)

        entry = generator.add_entry()
        entry.id(post_href)
        entry.link(href=post_href, rel="alternate")
        entry.title(post.title)
        entry.description(body)
        entry.published(post.pubdate)

    return generator
