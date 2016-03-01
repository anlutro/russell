import datetime
import os.path
import logging
import markdown

import russell.content
import russell.util

LOG = logging.getLogger(__name__)


def from_file_contents(contents, cls, kwargs=None, tags=None):
	if kwargs is None:
		kwargs = {}
	if tags is None:
		tags = {}

	def make_tag(tag_name):
		tag_name = tag_name.strip()
		if tag_name not in tags:
			tags[tag_name] = russell.content.Tag(tag_name,
				root_url=kwargs.get('root_url', ''))
		return tags[tag_name]

	lines = contents.splitlines()
	title = None

	line = lines.pop(0)
	while line != '':
		if not title and line.startswith('#'):
			title = line.replace('#', '').strip()
		elif line.startswith('title:'):
			title = line[6:].strip()

		elif line.startswith('slug:'):
			kwargs['slug'] = line[5:].strip()

		elif line.startswith('pubdate:') and cls is russell.content.Post:
			pubdate_str = line[8:].strip()
			pubdate = russell.util.parse_pubdate(pubdate_str)
			if pubdate:
				kwargs['pubdate'] = pubdate
			else:
				LOG.warning('while parsing post "%s", found invalid pubdate: "%s"',
					title, pubdate_str)
			if not pubdate.tzinfo:
				LOG.warning('while parsing post "%s", found pubdate without timezone: "%s"',
					title, pubdate_str)

		elif line.startswith('tags:') and cls is russell.content.Post:
			kwargs['tags'] = [make_tag(tag) for tag in line[5:].strip().split(',')]

		line = lines.pop(0)

	# the only lines left should be the actual contents
	body = '\n'.join(lines).strip()
	if cls is russell.content.Post:
		kwargs['excerpt'] = markdown.markdown(
			russell.util.generate_excerpt(body)
		)
	body = markdown.markdown(body)

	return cls(title=title, body=body, **kwargs)


def from_file(path, cls, kwargs=None, tags=None):
	if kwargs is None:
		kwargs = {}

	LOG.debug('creating %s from "%s"', cls, path)

	# the filename will be the default slug - can be overridden later
	kwargs['slug'] = os.path.splitext(os.path.basename(path))[0]

	with open(path, 'r') as file:
		post = from_file_contents(file.read(), cls, kwargs, tags)

	# if a pubdate wasn't found, use the file's last modified time
	if cls is russell.content.Post and not kwargs.get('pubdate'):
		timestamp = min(os.path.getctime(path), os.path.getmtime(path))
		kwargs['pubdate'] = datetime.datetime.fromtimestamp(timestamp)

	return post
