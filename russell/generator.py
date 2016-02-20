import os
import os.path
import logging

LOG = logging.getLogger(__name__)


def generate(path, pages, posts, tags, jinja_env):
	if not os.path.isdir(path):
		os.mkdir(path)

	generate_pages(path, pages, jinja_env)
	generate_posts(os.path.join(path, 'posts'), posts, jinja_env)
	generate_tags(os.path.join(path, 'tags'), tags, posts, jinja_env)
	generate_home(os.path.join(path, 'index.html'), posts, jinja_env)
	generate_archive(os.path.join(path, 'archive.html'), posts, jinja_env)


def generate_pages(path, pages, jinja_env):
	template = jinja_env.select_template(['page.html.jinja', 'post.html.jinja'])

	for page in pages:
		LOG.info('generating HTML for page "%s"', page.title)
		html = template.render(page=page)
		page_path = os.path.join(path, page.slug + '.html')
		with open(page_path, 'w') as file:
			LOG.info('writing page "%s" to "%s"', page.title, page_path)
			file.write(html)


def generate_posts(path, posts, jinja_env):
	if not os.path.isdir(path):
		os.mkdir(path)

	template = jinja_env.select_template(['post.html.jinja', 'page.html.jinja'])

	for post in posts:
		LOG.info('generating HTML for post "%s"', post.title)
		html = template.render(post=post)
		post_path = os.path.join(path, post.slug + '.html')
		with open(post_path, 'w') as file:
			LOG.info('writing post "%s" to "%s"', post.title, post_path)
			file.write(html)


def generate_tags(path, tags, posts, jinja_env):
	if not os.path.isdir(path):
		os.mkdir(path)

	for tag in tags:
		tag_posts = [post for post in posts if tag in post.tags]
		if tag_posts:
			tag_path = os.path.join(path, tag.slug + '.html')
			generate_archive(tag_path, tag_posts, jinja_env)


def generate_home(path, posts, jinja_env):
	LOG.info('generating HTML for home page "%s"', path)
	template = jinja_env.select_template(['home.html.jinja', 'archive.html.jinja'])
	html = template.render(posts=posts)
	with open(path, 'w') as file:
		LOG.info('writing home page "%s"', path)
		file.write(html)


def generate_archive(path, posts, jinja_env):
	LOG.info('generating HTML for archive "%s"', path)
	template = jinja_env.select_template(['archive.html.jinja', 'home.html.jinja'])
	html = template.render(posts=posts)
	with open(path, 'w') as file:
		LOG.info('writing archive "%s"', path)
		file.write(html)
