import logging
import os
import os.path
import slugify

import russell.util

LOG = logging.getLogger(__name__)


DEFAULT_CONFIG = '''
root_path: {pwd}
root_url: //localhost:8080
title: My blog

# these are relative to root_path. you can remove them
# or comment them out to leave them as their defaults.
#posts_dir: posts
#pages_dir: pages
#dist_dir: dist
#templates_dir: templates
'''

LAYOUT_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>{% block title %}{% endblock %} - Russell generated</title>
	<link rel="alternate" type="application/rss+xml" href="{{ root_url }}/rss.xml">
	<link rel="stylesheet" href="{{ root_url }}/static/style.css">
</head>
<body>
	<header class="site-header">
		<h1 class="site-title">
			<a href="{{ root_url }}">My website</a>
		</h1>
	</header>
	<main class="site-main">
		{% block content %}{% endblock %}
	</main>
</body>
</html>
'''

HOME_TEMPLATE = '''
{% extends 'layout.html.jinja' %}
{% block title %}Archives{% endblock %}
{% block content %}
{% for post in posts %}
	<article class="post">
		<header class="post-header">
			<span class="post-pubdate">{{ post.pubdate.strftime('%B %d, %Y') }}</span>
			<h2 class="post-title">
				<a href="{{ post.url }}">{{ post.title }}</a>
			</h2>
			<span class="post-tags">{{ ', '.join(post.tag_links) }}</span>
		</header>
		<div class="post-body">{{ post.excerpt }}</div>
	</article>
{% endfor %}
{% endblock %}
'''

PAGE_TEMPLATE = '''
{% extends 'layout.html.jinja' %}
{% block title %}{{ page.title }}{% endblock %}
{% block content %}
<article class="page">
	<header class="page-header">
		<h1 class="page-title">{{ page.title }}</h1>
	</header>
	<div class="page-body">{{ page.body }}</div>
</article>
{% endblock %}
'''

POST_TEMPLATE = '''
{% extends 'layout.html.jinja' %}
{% block title %}{{ post.title }}{% endblock %}
{% block content %}
<article class="post">
	<header class="post-header">
		<h2 class="post-title">{{ post.title }}</h2>
		<span class="post-pubdate">{{ post.pubdate.strftime('%B %d, %Y') }}</span>
	</header>
	<div class="post-body">{{ post.body }}</div>
	<span class="post-tags">{{ ', '.join(post.tag_links) }}</span>
</article>
{% endblock %}
'''

SAMPLE_PAGE = '''
# About me

Write something about you here!
'''

SAMPLE_POST = '''
# Hello world!
pubdate: {pubdate}
tags: tag1, tag2

This is my first Russell blogpost!
'''


class ScaffoldingException(Exception):
	pass


def _create_dir(path):
	if os.path.isdir(path):
		LOG.info('directory already exists, not doing anything: %s', path)
	else:
		LOG.info('creating directory: %s', path)
		os.mkdir(path)


def get_page_slug_and_contents(title, body):
	contents = '# {}\n\n{}'.format(title, body)

	return slugify.slugify(title), contents


def create_new_page(path, title):
	slug, contents = get_page_slug_and_contents(title, 'Write something here.')
	path = os.path.join(path, slug + '.md')
	if os.path.isfile(path):
		raise ScaffoldingException('File already exists: {}'.format(path))

	LOG.info('writing page to "%s"', path)
	with open(path, 'w') as file:
		file.write(contents + '\n')


def get_post_slug_and_contents(title, body, pubdate=None, tags=None):
	contents = '# {}\n'.format(title)

	if pubdate is None:
		pubdate = russell.util.now_datetime_str()
	contents += 'pubdate: {}\n'.format(pubdate)

	if tags:
		contents += 'tags: {}\n'.format(', '.join(tags))

	contents += '\n{}'.format(body)

	return slugify.slugify(title), contents


def create_new_post(path, title, **kwargs):
	slug, contents = get_post_slug_and_contents(title, 'Write something here.', **kwargs)
	path = os.path.join(path, slug + '.md')
	if os.path.isfile(path):
		raise ScaffoldingException('File already exists: {}'.format(path))

	LOG.info('writing post to "%s"', path)
	with open(path, 'w') as file:
		file.write(contents + '\n')


def scaffold(path, files=None, overwrite=False):
	_create_dir(path)
	scaffolder = Scaffolder(path, overwrite)
	if files is None or 'config' in files:
		scaffolder.create_config()
	if files is None or 'templates' in files:
		scaffolder.create_templates()
	if files is None or 'posts' in files:
		scaffolder.create_posts()
	if files is None or 'pages' in files:
		scaffolder.create_pages()


class Scaffolder:
	def __init__(self, root_path, overwrite=False):
		self.root_path = root_path
		self.overwrite = overwrite

	def _create_file(self, path, contents):
		if os.path.isfile(path) and not self.overwrite:
			LOG.info('file already exists, not doing anything: %s', path)
		else:
			LOG.info('writing file: %s', path)
			with open(path, 'w') as file:
				file.write(contents.lstrip())

	def create_config(self):
		path = os.path.join(self.root_path, 'russell.yml')
		self._create_file(path, DEFAULT_CONFIG.format(pwd=os.getcwd()))

	def create_templates(self):
		path = os.path.join(self.root_path, 'templates')
		_create_dir(path)

		home_path = os.path.join(path, 'home.html.jinja')
		self._create_file(home_path, HOME_TEMPLATE)

		layout_path = os.path.join(path, 'layout.html.jinja')
		self._create_file(layout_path, LAYOUT_TEMPLATE)

		page_path = os.path.join(path, 'page.html.jinja')
		self._create_file(page_path, PAGE_TEMPLATE)

		post_path = os.path.join(path, 'post.html.jinja')
		self._create_file(post_path, POST_TEMPLATE)

	def create_pages(self):
		path = os.path.join(self.root_path, 'pages')
		_create_dir(path)
		self._create_file(os.path.join(path, 'about.md'), SAMPLE_PAGE)

	def create_posts(self):
		path = os.path.join(self.root_path, 'posts')
		_create_dir(path)
		contents = SAMPLE_POST.format(pubdate=russell.util.now_datetime_str())
		self._create_file(os.path.join(path, 'hello-world.md'), contents)
