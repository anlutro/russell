import logging
import os
import os.path
import sys
import yaml

import russell.parser
import russell.jinja
import russell.generator
import russell.rss
import russell.scaffold

LOG = logging.getLogger(__name__)


def setup_logging(log_file=None, log_level=None):
	if log_level is None:
		log_level = logging.WARNING
	root = logging.getLogger()
	root.setLevel(log_level)

	if not log_file or log_file == 'stdout':
		handler = logging.StreamHandler(sys.stdout)
		log_file = 'STDOUT'
	elif log_file == 'stderr':
		handler = logging.StreamHandler(sys.stderr)
		log_file = 'STDERR'
	elif log_file:
		handler = logging.StreamHandler(log_file)

	# define the logging format
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
	handler.setFormatter(formatter)

	# add the logging handler for all loggers
	root.addHandler(handler)

	LOG.info('set up logging to %s with level %s', log_file, log_level)


class Application:
	def __init__(self, config):
		self.config = config

	def generate_site(self, dist_path=None, root_url=None):
		if dist_path is None:
			dist_path = self.config['dist_path']
		if root_url is None:
			root_url = self.config.get('root_url', '')

		pages = russell.parser.read_pages(self.config['pages_path'], root_url)
		posts = russell.parser.read_posts(self.config['posts_path'], root_url)
		tags = russell.parser.get_tags(posts)

		jinja_env = russell.jinja.make_env(self.config['templates_path'], root_url)
		generator = russell.generator.Generator(dist_path, jinja_env)
		home_num_posts = self.config.get('home_num_posts', 5)
		generator.generate(pages, posts, tags, home_num_posts=home_num_posts)

		rss_path = os.path.join(dist_path, 'rss.xml')
		rss_title = self.config.get('title', root_url)
		russell.rss.write_feed(rss_path, posts, rss_title, root_url)

	def create_new_page(self, title):
		russell.scaffold.create_new_page(self.config['posts_path'], title)

	def create_new_post(self, title, pubdate=None, tags=None):
		russell.scaffold.create_new_post(self.config['posts_path'], title,
			pubdate=pubdate, tags=tags)
