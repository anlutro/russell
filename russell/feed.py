from feedgen.feed import FeedGenerator
from russell.content import _schema_url


def get_rss_feed(blog, only_excerpt=True, https=False):
	fg = FeedGenerator()

	root_href = _schema_url(blog.root_url, https)
	fg.id(root_href)
	fg.link(href=root_href, rel='alternate')
	fg.title(blog.site_title)
	fg.subtitle(blog.site_desc or '')

	for post in blog.get_posts():
		if only_excerpt:
			read_more = 'Read the full article at <a href="%s" target="_blank">%s</a>' % (post.url, post.url)
			body = '<p>%s</p><p>%s</p>' % (post.excerpt, read_more)
		else:
			body = post.body

		post_href = _schema_url(post.url, https=https)

		fe = fg.add_entry()
		fe.id(post_href)
		fe.link(href=post_href, rel='alternate')
		fe.title(post.title)
		fe.description(body)
		fe.published(post.pubdate)

	return fg
