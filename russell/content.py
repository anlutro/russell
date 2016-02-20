import slugify

import russell.util


class Page:
	def __init__(self, title, body, slug=None, root_url=None):
		self.title = title
		self.body = body
		self.slug = slug or slugify.slugify(title)
		self.root_url = root_url

	@property
	def url(self):
		return self.root_url + '/' + self.slug


class Post(Page):
	# pylint: disable=too-many-arguments
	def __init__(self, title, body, pubdate=None, slug=None, excerpt=None,
			tags=None, root_url=None):
		super().__init__(title, body, slug, root_url)
		self.excerpt = excerpt or russell.util.generate_excerpt(body)
		self.pubdate = pubdate
		self.tags = tags or []
	# pylint: enable=too-many-arguments

	@property
	def url(self):
		return self.root_url + '/posts/' + self.slug

	@property
	def tag_links(self):
		return ['<a href="' + tag.url + '">' + tag.title + '</a>' for tag in self.tags]


class Tag:
	def __init__(self, title, slug=None, root_url=None):
		self.title = title
		self.slug = slug or slugify.slugify(title)
		self.root_url = root_url

	@property
	def url(self):
		return self.root_url + '/tags/' + self.slug
