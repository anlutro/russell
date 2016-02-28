import os
import os.path
import logging

import russell.content
import russell.markdown

LOG = logging.getLogger(__name__)


def _list_files(root_dir):
	results = set()

	for root, _, files in os.walk(root_dir):
		for file in files:
			results.add(os.path.join(root, file))

	return results


def read_pages(path, root_url):
	pages = []
	LOG.debug('looking for page files in %s', path)
	for file in _list_files(path):
		page = russell.markdown.from_file(file, russell.content.Page,
			kwargs={'root_url': root_url})
		pages.append(page)
	return pages


def read_posts(path, root_url):
	posts = []
	LOG.debug('looking for post files in %s', path)
	for file in _list_files(path):
		post = russell.markdown.from_file(file, russell.content.Post,
			kwargs={'root_url': root_url})
		posts.append(post)

	posts.sort(key=lambda post: post.title)
	posts.sort(key=lambda post: post.pubdate, reverse=True)

	return posts


def get_tags(posts):
	tags = set()
	for post in posts:
		for tag in post.tags:
			tags.add(tag)
	LOG.debug('found %d unique tags', len(tags))
	return tags
