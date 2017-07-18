import argparse
import datetime
import os
import os.path
import shutil
import slugify
import subprocess


def setup(dest):
	module_root = os.path.dirname(os.path.dirname(__file__))
	example_dir = os.path.join(module_root, 'example')
	shutil.copytree(example_dir, dest)


def new_page(title):
	path = os.path.join('pages', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	now = datetime.datetime.now()
	pubdate = now.strftime('%Y-%m-%d %H:%M %Z')
	with open(path, 'w+') as f:
		f.write('# %s\npubdate: %s\n\nPost body here' % (title, pubdate))


def new_post(title):
	path = os.path.join('posts', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	with open(path, 'w+') as f:
		f.write('# %s\n\nPage body here' % title)


def generate():
	subprocess.run(['python', 'run.py'])


def serve():
	try:
		subprocess.run(['sh', '-c', 'cd dist && python -m http.server'])
	except KeyboardInterrupt:
		pass


def main():
	parser = argparse.ArgumentParser('russell')
	cmd_subparsers = parser.add_subparsers(dest='command')

	setup_parser = cmd_subparsers.add_parser('setup')
	setup_parser.add_argument('dir')

	new_page_parser = cmd_subparsers.add_parser('new-page')
	new_page_parser.add_argument('title')

	new_post_parser = cmd_subparsers.add_parser('new-post')
	new_post_parser.add_argument('title')

	generate_parser = cmd_subparsers.add_parser('generate')

	serve_parser = cmd_subparsers.add_parser('serve')

	args = parser.parse_args()
	if not args.command:
		return parser.print_help()

	if args.command == 'setup':
		return setup(args.dir)
	if args.command == 'new-page':
		return new_page(args.title)
	if args.command == 'new-post':
		return new_post(args.title)
	if args.command == 'generate':
		return generate()
	if args.command == 'serve':
		return serve()


if __name__ == '__main__':
	main()
