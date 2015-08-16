#!/usr/bin/env python3

"""
Russell - A static blog HTML generator

Usage:
    russell generate [--config=<config>] [--src=<src>] [--target=<target>]
                     [--title=<title>] [--url=<url>]
    russell setup [path]
    russell new page <title>
    russell new post <title> [--pubdate=<date>]

Arguments:
    path    Path where the files should be set up. Defaults to $CWD.
    title   Title of the new post/page. Remember to wrap in quotes.

Options:
    --config=<config> Path to the YAML config file. Defaults to $CWD/russell.yml
    --src=<src>       Path to source files (templates and markdown files).
    --target=<target> Path to place output HTML files.
    --title=<title>   Title of the website.
    --url=<url>       Root URL of the website.
    --pubdate=<date>  Date the post should appear published as.
    -h|--help         Show this help screen.
"""

import os
import yaml
from docopt import docopt

from .blog import Blog


def main():
    args = docopt(__doc__)
    config_path = args.get('--config') or os.path.join(os.getcwd(), 'russell.yml')
    if os.path.exists(config_path):
        config = yaml.load(open(config_path))
    else:
        config = {}

    def get_config(key, default):
        arg_key = '--' + key.replace('_', '-')
        if arg_key in args and args[arg_key] is not None:
            return args[arg_key]
        return config.get(key, default)

    src_dir = get_config('src', os.getcwd())
    trg_dir = get_config('target', os.path.join(src_dir, 'public'))
    title = get_config('title', 'Russell Blog')
    root_url = get_config('url', '')

    blog = Blog(src_dir, trg_dir, title=title, root_url=root_url)

    if args.get('setup'):
        blog.setup()
    elif args.get('new'):
        if args.get('post'):
            blog.new_post(args.get('<title>'), args.get('--pubdate'))
        elif args.get('page'):
            blog.new_page(args.get('<title>'))
    else:
        blog.generate()

if __name__ == '__main__':
    main()
