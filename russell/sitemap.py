from xml.etree import ElementTree as etree
import re


def text_element(tag, text):
	elem = etree.Element(tag)
	elem.text = text
	return elem


class SitemapGenerator:
	def __init__(self, blog, https=True):
		self.blog = blog
		self.schema = 'https' if https else 'http'

	def normalize_url(self, url):
		return re.sub(r'^\/\/', self.schema + '://', url)

	def generate_sitemap(self):
		tree = etree.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
		tree.append(self.get_index_element(self.blog.root_url))
		for page in self.blog.pages:
			if page.public:
				tree.append(self.get_page_element(page))
		for tag in self.blog.tags:
			tree.append(self.get_tag_element(tag))
		for post in self.blog.get_posts():
			tree.append(self.get_post_element(post))
		return etree.tostring(tree, 'utf-8')

	def get_post_element(self, post):
		elem = etree.Element('url')
		elem.append(text_element('loc', self.normalize_url(post.url)))
		elem.append(text_element('lastmod', post.pubdate.strftime('%Y-%m-%d')))
		elem.append(text_element('changefreq', 'monthly'))
		return elem

	def get_page_element(self, page):
		elem = etree.Element('url')
		elem.append(text_element('loc', self.normalize_url(page.url)))
		elem.append(text_element('changefreq', 'monthly'))
		return elem

	def get_tag_element(self, tag):
		elem = etree.Element('url')
		elem.append(text_element('loc', self.normalize_url(tag.url)))
		elem.append(text_element('changefreq', 'weekly'))
		return elem

	def get_index_element(self, url):
		elem = etree.Element('url')
		elem.append(text_element('loc', self.normalize_url(url)))
		elem.append(text_element('changefreq', 'daily'))
		return elem


def generate_sitemap(blog, https=True):
	return SitemapGenerator(blog, https).generate_sitemap()
