import argparse
import logging
import os
import os.path

import russell
import russell.config
import russell.scaffold

LOG = logging.getLogger(__name__)


def get_args(args=None):
	parser = argparse.ArgumentParser('russell')
	parser.add_argument('-c', '--config',
		help='path to config file. defaults to $PWD/rusell.yml')
	parser.add_argument('-l', '--log-level')
	parser.add_argument('--log-file')
	subparsers = parser.add_subparsers(dest='command')

	setup_parser = subparsers.add_parser('setup')
	setup_parser.add_argument('path')
	setup_parser.add_argument('-f', '--files',
		help='specify which files to scaffold')
	setup_parser.add_argument('-o', '--overwrite', action='store_true',
		help='overwrite existing files')

	new_page_parser = subparsers.add_parser('new-page')
	new_page_parser.add_argument('title',
		help='title of the new page. wrap in quotes!')

	new_post_parser = subparsers.add_parser('new-post')
	new_post_parser.add_argument('title',
		help='title of the new post. wrap in quotes!')
	new_post_parser.add_argument('--pubdate', help='date/time of the post')
	new_post_parser.add_argument('--tags', help='comma-separated tags')

	generate_parser = subparsers.add_parser('generate')
	generate_parser.add_argument('-d', '--dist-path')
	generate_parser.add_argument('-r', '--root-url')

	return parser.parse_args(args)


def get_config(args):
	if not args.config:
		args.config = os.path.join(os.getcwd(), 'russell.yml')

	if os.path.isfile(args.config):
		return russell.config.load_config_file(args.config)

	return {}


def setup_logging(args, config):
	log_level = None
	if args.log_level:
		log_level = getattr(logging, args.log_level.upper())
	elif config.get('log_level'):
		log_level = getattr(logging, config['log_level'].upper())

	log_file = None
	if args.log_file:
		log_file = args.log_file
	elif config.get('log_file'):
		log_file = config['log_file']

	russell.setup_logging(log_file=log_file, log_level=log_level)


def main(args=None):
	args = get_args(args)
	config = get_config(args)
	setup_logging(args, config)

	if args.command == 'setup':
		if args.files:
			args.files = [file.strip() for file in args.files.split(',')]
		russell.scaffold.scaffold(args.path, args.files, args.overwrite)
		print('Done!')
		return

	if not os.path.isfile(args.config):
		raise FileNotFoundError('Config file not found - looked in ' + args.config)

	app = russell.Application(config)

	if args.command == 'new-page':
		app.create_new_page(args.title)
	elif args.command == 'new-post':
		if args.tags:
			args.tags = [tag.strip() for tag in args.tags.split(',')]
		app.create_new_post(args.title, args.pubdate, args.tags)
	elif args.command == 'generate':
		app.generate_site(args.dist_path, args.root_url)
	else:
		raise RuntimeError('This code should not be reachable!')

	print('Done!')


if __name__ == '__main__':
	main()
