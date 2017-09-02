import argparse
import datetime
import os
import os.path
import shutil
import subprocess

import dateutil.tz
import slugify


def setup(dest):
	module_root = os.path.dirname(os.path.dirname(__file__))
	example_dir = os.path.join(module_root, 'example')

	if os.path.exists(dest):
		def iter_copy(src_dir, dest_dir):
			for item in os.listdir(src_dir):
				src_path = os.path.join(src_dir, item)
				dest_path = os.path.join(dest_dir, item)
				if os.path.exists(dest_path):
					continue
				if os.path.isdir(src_path):
					shutil.copytree(src_path, dest_path)
				else:
					shutil.copy(
						os.path.join(example_dir, item),
						os.path.join(dest, item)
					)
		iter_copy(example_dir, dest)
	else:
		shutil.copytree(example_dir, dest)
		subprocess.check_call(['python3', '-m', 'venv', os.path.join(dest, '.venv')])
		subprocess.check_call([
			os.path.join(dest, '.venv', 'bin', 'pip'),
			'install', '-r', os.path.join(dest, 'requirements.txt'),
		])


def new_page(title):
	path = os.path.join('pages', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	with open(path, 'w+') as page_file:
		page_file.write('# %s\n\nPage body here' % title)


def new_post(title):
	path = os.path.join('posts', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	now = datetime.datetime.now(dateutil.tz.tzlocal())
	pubdate = now.strftime('%Y-%m-%d %H:%M %Z')
	with open(path, 'w+') as post_file:
		post_file.write('# %s\npubdate: %s\n\nPost body here' % (title, pubdate))


def generate():
	subprocess.check_call(['python', 'run.py'])


def serve():
	try:
		subprocess.check_call(['sh', '-c', 'cd dist && python -m http.server'])
	except KeyboardInterrupt:
		pass


def main():
	parser = argparse.ArgumentParser('russell')
	cmd_subparsers = parser.add_subparsers(dest='command')

	setup_parser = cmd_subparsers.add_parser('setup')
	setup_parser.add_argument('dir')

	new_parser = cmd_subparsers.add_parser('new')
	new_subparsers = new_parser.add_subparsers(dest='new_type')

	new_page_parser = new_subparsers.add_parser('page')
	new_page_parser.add_argument('title')

	new_post_parser = new_subparsers.add_parser('post')
	new_post_parser.add_argument('title')

	generate_parser = cmd_subparsers.add_parser('generate')

	serve_parser = cmd_subparsers.add_parser('serve')

	args = parser.parse_args()
	if not args.command:
		return parser.print_help()

	if args.command == 'setup':
		return setup(args.dir)
	if args.command == 'new':
		if args.new_type == 'page':
			return new_page(args.title)
		if args.new_type == 'post':
			return new_post(args.title)
	if args.command == 'generate':
		return generate()
	if args.command == 'serve':
		return serve()


if __name__ == '__main__':
	main()
