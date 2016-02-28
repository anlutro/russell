import os
import os.path
import logging

LOG = logging.getLogger(__name__)


class Generator:
	def __init__(self, root_path, jinja_env):
		self.root_path = root_path
		self.jinja_env = jinja_env

	def _path_to(self, name):
		return os.path.join(self.root_path, name)

	def generate(self, pages, posts, tags, **options):
		if not os.path.isdir(self.root_path):
			os.mkdir(self.root_path)

		self.generate_pages(pages)
		self.generate_posts(posts)
		self.generate_tags(tags, posts)
		home_num_posts = options.get('home_num_posts', 5)
		self.generate_home(posts[:home_num_posts])
		self.generate_archive(posts)

	def generate_pages(self, pages):
		path = self.root_path
		template = self.jinja_env.get_template('page.html.jinja')

		for page in pages:
			LOG.info('generating HTML for page "%s"', page.title)
			html = template.render(page=page)
			page_path = os.path.join(path, page.slug + '.html')
			with open(page_path, 'w') as file:
				LOG.info('writing page "%s" to "%s"', page.title, page_path)
				file.write(html)

	def generate_posts(self, posts):
		path = self._path_to('posts')
		if not os.path.isdir(path):
			os.mkdir(path)

		template = self.jinja_env.get_template('post.html.jinja')

		for post in posts:
			LOG.info('generating HTML for post "%s"', post.title)
			html = template.render(post=post)
			post_path = os.path.join(path, post.slug + '.html')
			with open(post_path, 'w') as file:
				LOG.info('writing post "%s" to "%s"', post.title, post_path)
				file.write(html)

	def generate_tags(self, tags, posts):
		path = self._path_to('tags')
		if not os.path.isdir(path):
			os.mkdir(path)

		for tag in tags:
			tag_posts = [post for post in posts if tag in post.tags]
			if tag_posts:
				tag_path = os.path.join(path, tag.slug + '.html')
				self.generate_archive(tag_posts, path=tag_path)

	def generate_home(self, posts):
		path = self._path_to('index.html')
		LOG.info('generating HTML for home page "%s"', path)
		template = self.jinja_env.select_template(['home.html.jinja', 'archive.html.jinja'])
		html = template.render(posts=posts)
		with open(path, 'w') as file:
			LOG.info('writing home page "%s"', path)
			file.write(html)


	def generate_archive(self, posts, path=None):
		path = path or self._path_to('archive.html')
		LOG.info('generating HTML for archive "%s"', path)
		template = self.jinja_env.select_template(['archive.html.jinja', 'home.html.jinja'])
		html = template.render(posts=posts)
		with open(path, 'w') as file:
			LOG.info('writing archive "%s"', path)
			file.write(html)
