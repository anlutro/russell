#!/usr/bin/env python3

import os.path
import logging
import sass
from russell import BlogEngine

ROOT_DIR = os.path.dirname(__file__)

logging.basicConfig()

blog = BlogEngine(
	root_path=ROOT_DIR,
	root_url='//localhost',
	site_title='Russell example',
	site_desc=('An example Russell site.')
)

# add content
blog.add_pages()
blog.add_posts()

# copy and generate assets
blog.copy_assets()
blog.write_file('assets/style.css', sass.compile(
	filename=os.path.join(ROOT_DIR, 'style.sass')
))
blog.add_asset_hashes()

# generate HTML pages
blog.generate_index(num_posts=3)
blog.generate_archive()
blog.generate_pages()
blog.generate_posts()
blog.generate_tags()

# generate other stuff
blog.generate_sitemap(https=False)
blog.generate_rss()
blog.write_file('robots.txt', 'User-agent: *\nDisallow:\n')
