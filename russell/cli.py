import argparse
import datetime
import os
import os.path
import shutil
import subprocess

import dateutil.tz
import slugify

import russell


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
			os.path.join(dest, '.venv', 'bin', 'python'), '-m', 'pip',
			'install', '-r', os.path.join(dest, 'requirements.txt'),
		])


def new_page(title):
	path = os.path.join('pages', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	with open(path, 'w+') as page_file:
		page_file.write('# %s\n\nPage body here' % title)
	print('Created new page in', path)


def new_post(title, draft=False, tags=None, subtitle=None):
	path = os.path.join('drafts' if draft else 'posts', slugify.slugify(title) + '.md')
	if os.path.exists(path):
		print(path, 'already exists!')
		return
	now = datetime.datetime.now(dateutil.tz.tzlocal())
	data = {'pubdate': now.strftime('%Y-%m-%d %H:%M %Z')}
	if tags:
		data['tags'] = ', '.join(tags)
	if subtitle:
		data['subtitle'] = subtitle
	data_lines = '\n'.join('%s: %s' % (tag, value) for tag, value in data.items())
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	with open(path, 'w+') as post_file:
		post_file.write('# %s\n%s\n\nPost body here\n' % (title, data_lines))
	print('Created new post in', path)


def publish(draft_file, update_pubdate=True):
	old_path = os.path.abspath(draft_file)
	drafts_path = os.path.abspath('drafts')
	posts_path = os.path.abspath('posts')
	assert old_path.startswith(drafts_path)

	now = datetime.datetime.now(dateutil.tz.tzlocal())
	new_pubdate = now.strftime('%Y-%m-%d %H:%M %Z')

	new_path = old_path.replace(drafts_path, posts_path)
	print('Moving', old_path, 'to', new_path)
	with open(old_path, 'rt') as old_fh, open(new_path, 'wt') as new_fh:
		for line in old_fh:
			if line.startswith('pubdate') and update_pubdate:
				print('Changing pubdate to', new_pubdate)
				line = 'pubdate: ' + new_pubdate + '\n'
			new_fh.write(line)
	os.remove(old_path)


def generate():
	subprocess.check_call(['python', 'run.py'])


def serve():
	try:
		subprocess.check_call(['sh', '-c', 'cd dist && python -m http.server'])
	except KeyboardInterrupt:
		pass


def get_parser():
	parser = argparse.ArgumentParser('russell')
	parser.add_argument('-v', '--version', action='version',
		version='russell version ' + str(russell.__version__))

	cmd_subparsers = parser.add_subparsers(dest='command')

	setup_parser = cmd_subparsers.add_parser('setup')
	setup_parser.add_argument('dir')

	new_parser = cmd_subparsers.add_parser('new')
	new_subparsers = new_parser.add_subparsers(dest='new_type')

	new_page_parser = new_subparsers.add_parser('page')
	new_page_parser.add_argument('title')

	new_post_parser = new_subparsers.add_parser('post')
	new_post_parser.add_argument('title')
	new_post_parser.add_argument('-s', '--subtitle', type=str)
	new_post_parser.add_argument('-d', '--draft', action='store_true', default=False)
	new_post_parser.add_argument('-t', '--tags', type=str, nargs='*')

	publish_parser = cmd_subparsers.add_parser('publish')
	publish_parser.add_argument('draft_file')
	publish_parser.add_argument('--no-update-pubdate', action='store_false', dest='update_pubdate', default=True)

	generate_parser = cmd_subparsers.add_parser('generate')

	serve_parser = cmd_subparsers.add_parser('serve')

	return parser


def parse_args(parser=None, args=None):
	parser = parser or get_parser()
	return parser.parse_args(args)


def main(args=None):
	parser = get_parser()
	args = parse_args(parser)

	if not args.command:
		return parser.print_help()

	if args.command == 'setup':
		return setup(args.dir)
	if args.command == 'new':
		if args.new_type == 'page':
			return new_page(args.title)
		if args.new_type == 'post':
			return new_post(
				args.title,
				draft=args.draft,
				tags=args.tags,
				subtitle=args.subtitle,
			)
	if args.command == 'publish':
		return publish(args.draft_file, update_pubdate=args.update_pubdate)
	if args.command == 'generate':
		return generate()
	if args.command == 'serve':
		return serve()


if __name__ == '__main__':
	main()
