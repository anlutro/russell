import datetime
import logging
import PyRSS2Gen

LOG = logging.getLogger(__name__)


def _get_rss_item(post):
	return PyRSS2Gen.RSSItem(
		title=post.title,
		description=post.excerpt,
		link=post.url,
		pubDate=post.pubdate,
	)


def write_feed(path, posts, title, root_url):
	LOG.info('generating RSS feed')

	rss = PyRSS2Gen.RSS2(
		title=title,
		description='',
		link=root_url,
		lastBuildDate=datetime.datetime.now(),
		items=[_get_rss_item(post) for post in posts],
	)

	with open(path, 'w') as file:
		LOG.info('writing RSS feed to "%s"', path)
		rss.write_xml(file)
