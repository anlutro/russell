#!/usr/bin/env python3

"""
Russell - A static blog HTML generator

Usage:
    russell generate [src] [target] [--url=<url>] [--title=<title>]
    russell setup [src]
    russell new page <title>
    russell new post <title> [--pubdate=<datetime>]

Arguments:
    src     The source directory where assets, pages, posts and templates
            reside. Defaults to CWD.
    target  The target directory where HTML and assets should be published.
            Defaults to CWD/public.
    title   Title of the new post/page. Remember to wrap in quotes.

Options:
    --title=<title> Title of the website.
    --url=<url>     Root URL of the website.
    -h|--help       Show this help screen.
"""

import os
from docopt import docopt

from .blog import Blog


def main():
    args = docopt(__doc__)

    src_dir = args.get('src') or os.getcwd()
    trg_dir = args.get('target') or os.path.join(src_dir, 'public')
    title = args.get('--title') or 'Blog'
    root_url = args.get('--url') or ''
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
