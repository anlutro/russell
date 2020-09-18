#!/usr/bin/env python3

import os.path
import logging
import sass
import russell

root_path = os.path.dirname(__file__)
args = russell.get_cli_args()
logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s %(levelname)8s [%(name)s] %(message)s",
)
blog = russell.BlogEngine(
    root_path=root_path,
    root_url=args.root_url or "//localhost",
    site_title="Russell example",
    site_desc=("An example Russell site."),
)

# add content
blog.add_pages()
blog.add_posts()


def generate():
    # copy and generate assets
    blog.copy_assets()
    blog.write_file(
        "assets/style.css",
        sass.compile(filename=os.path.join(blog.root_path, "style.sass")),
    )
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
    blog.write_file("robots.txt", "User-agent: *\nDisallow:\n")
