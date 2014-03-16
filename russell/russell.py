#!/usr/bin/env python3

"""
Russell - A static blog HTML generator

Usage:
  russell.py generate [src] [target] [--url=<url>]
  russell.py setup [src]
  russell.py new (page|post) <title>

Arguments:
  src     The source directory where assets, pages, posts and templates
          reside. Defaults to CWD.
  target  The target directory where HTML and assets should be published.
          Defaults to CWD/public.
  title   Title of the new post/page. Remember to wrap in quotes.

Options:
  --url=<url>  Root URL of the website.
  -h|--help    Show this help screen.
"""

import os, shutil, tarfile
from datetime import datetime

from docopt import docopt
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from slugify import slugify

def make_tarfile(trg_path, src_dir):
	with tarfile.open(trg_path, 'w:gz') as tar:
		tar.add(src_dir, arcname=os.path.basename(src_dir))

def list_files(dir):
	results = set()

	for root, dirs, files in os.walk(dir):
		for f in files:
			results.add(os.path.join(root, f))

	return results

class Entry():
	"""Generic class for posts and pages."""
	def __init__(self, title, pubdate, body, tags=set(), slug=None):
		self.title = title
		self.pubdate = pubdate
		self.body = body
		self.excerpt = body.split('\n', 1)[0]
		self.tags = tags
		self.slug = slug or slugify(title)

	@classmethod
	def from_file(cls, path):
		"""Create a new object from a markdown file."""
		with open(path, 'r') as f:
			# The first line will be the title of the post.
			title = f.readline().replace('#', '').strip()
			# The remaining contents will be the body.
			body = markdown(f.read().strip())

		# The time the file was created will be the pubdate.
		pubdate = datetime.fromtimestamp(os.path.getctime(path))
		# The slug will be the name of the file.
		slug = os.path.splitext(os.path.basename(path))[0]
		return cls(title=title, body=body, pubdate=pubdate, slug=slug)

class Russell():
	def __init__(self, src_dir, trg_dir, root_url=''):
		self.src_dir = src_dir
		self.trg_dir = trg_dir
		self.setup_jinja(root_url)
		self.posts = []

	def setup_jinja(self, root_url):
		loader = FileSystemLoader(os.path.join(self.src_dir, 'templates'))
		self.j2env = Environment(loader=loader)
		self.j2env.globals['root_url'] = root_url

	def setup(self):
		def write_file(path, content=''):
			path = os.path.join(self.src_dir, path)
			if not os.path.exists(path):
				with open(path, 'w+') as f:
					f.write(content)

		print('Setting up directories...')
		dirs = ['assets', 'pages', 'posts', 'templates']
		for d in dirs:
			d = os.path.join(self.src_dir, d)
			if not os.path.isdir(d):
				os.makedirs(d)

		print('Creating files...')
		write_file(os.path.join('pages', 'sample-page.md'), '# Sample page\n\n\
			This is a sample page! Do with it whatever you like.')
		write_file(os.path.join('posts', 'sample-post.md'), '# Sample post\n\n\
			This is a sample post! Do with it whatever you like.')
		write_file(os.path.join('templates', 'archive.html'))
		write_file(os.path.join('templates', 'home.html'))
		write_file(os.path.join('templates', 'page.html'))
		write_file(os.path.join('templates', 'single.html'))
		write_file(os.path.join('assets', 'style.css'))
		print('Done!')

	def new_page(self, title):
		slug = slugify(title)
		path = os.path.join(self.src_dir, 'pages', slug + '.md')
		if os.path.exists(path):
			print('File already exists in',path,'- aborting!')
			return
		print('Creating new page in',path)
		with open(path, 'w+') as f:
			f.write('# ' + title + '\n\nWrite your page contents here!')
		print('Done!')

	def new_post(self, title):
		slug = slugify(title)
		path = os.path.join(self.src_dir, 'posts', slug + '.md')
		if os.path.exists(path):
			print('File already exists in',path,'- aborting!')
			return
		print('Creating new post in',path)
		with open(path, 'w+') as f:
			f.write('# ' + title + '\n\nWrite your post contents here!')		
		print('Done!')

	def generate(self):
		self.backup()
		print('Generating...')
		for f in self.get_asset_files():
			self.copy_asset(f)
		for f in self.get_page_files():
			self.convert_page(f)
		for f in self.get_post_files():
			self.convert_post(f)

		# sort posts by pubdate (newest first) before generating home/archives
		self.posts.sort(key=lambda post: post.pubdate, reverse=True)
		self.generate_home()
		self.generate_archive()
		print('Done!')

	def backup(self):
		if not os.path.exists(self.trg_dir):
			print('Nothing to back up, skipping...')
		trg_dir = os.path.join(self.src_dir, 'backups')
		if not os.path.isdir(trg_dir):
			os.makedirs(trg_dir)
		filename = datetime.now().strftime('backup_%Y-%m-%d_%H%M%S.tar')
		trg_path = os.path.join(trg_dir, filename)
		print('Backing up data into', trg_path)
		make_tarfile(trg_path, self.trg_dir)
		shutil.rmtree(self.trg_dir)
		os.makedirs(self.trg_dir)

	def get_asset_files(self):
		return list_files(os.path.join(self.src_dir, 'assets'))

	def get_page_files(self):
		return list_files(os.path.join(self.src_dir, 'pages'))

	def get_post_files(self):
		return list_files(os.path.join(self.src_dir, 'posts'))

	def get_template(self, tpl):
		return self.j2env.get_template(tpl)

	def convert_page(self, path):
		trg_dir = self.trg_dir
		if not os.path.isdir(trg_dir):
			os.makedirs(trg_dir)

		page = Entry.from_file(path)
		tpl = self.get_template('page.html')
		html = tpl.render(page=page)
		trg_path = os.path.join(trg_dir, page.slug + '.html')
		print('Writing',trg_path)
		with open(trg_path, 'w+') as f:
			f.write(html)

	def convert_post(self, path):
		trg_dir = os.path.join(self.trg_dir, 'posts')
		if not os.path.isdir(trg_dir):
			os.makedirs(trg_dir)

		post = Entry.from_file(path)
		self.posts.append(post)
		tpl = self.get_template('post.html')
		html = tpl.render(post=post)
		trg_path = os.path.join(trg_dir, post.slug + '.html');
		print('Writing',trg_path)
		with open(trg_path, 'w+') as f:
			f.write(html)

	def generate_home(self, limit=5):
		print('Generating home page (index.html)...')
		posts = self.posts[:5]
		tpl = self.get_template('home.html')
		html = tpl.render(posts=posts)
		with open(os.path.join(self.trg_dir, 'index.html'), 'w+') as f:
			f.write(html)

	def generate_archive(self):
		print('Generating archives (archive.html)...')
		tpl = self.get_template('archive.html')
		html = tpl.render(posts=self.posts)
		with open(os.path.join(self.trg_dir, 'archive.html'), 'w+') as f:
			f.write(html)

	def copy_asset(self, path):
		trg_dir = os.path.join(self.trg_dir, 'assets')
		if not os.path.isdir(trg_dir):
			os.makedirs(trg_dir)
		print('Copying assets into', trg_dir)
		shutil.copy2(path, trg_dir)

def main():
	args = docopt(__doc__)
#	print(args)
#	return

	src_dir = args.get('src') or os.getcwd()
	trg_dir = args.get('target') or os.path.join(src_dir, 'public')
	root_url = args.get('--url') or ''
	blog = Russell(src_dir, trg_dir, root_url=root_url)

	if args.get('setup'):
		blog.setup()
	elif args.get('new'):
		if args.get('post'):
			blog.new_post(args.get('<title>'))
		elif args.get('page'):
			blog.new_page(args.get('<title>'))
	else:
		blog.generate()

if __name__ == '__main__':
	main()
