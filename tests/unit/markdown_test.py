import russell.content
import russell.markdown


def _make_page(contents):
	return russell.markdown.from_file_contents(contents, russell.content.Page)


def _make_post(contents):
	return russell.markdown.from_file_contents(contents, russell.content.Post)


def test_basic_parsing():
	md = '# Hello world!\n\nThis is a test post.'
	post = _make_post(md)
	assert 'Hello world!' == post.title
	assert '<p>This is a test post.</p>' == post.body


def test_pubdate_parsing():
	md = '# Hello world!\npubdate:2015-01-01 01:23:45\n\nThis is a test post.'
	post = _make_post(md)
	assert 'Hello world!' == post.title
	assert '2015-01-01T01:23:45' == post.pubdate.isoformat()
	assert '<p>This is a test post.</p>' == post.body


def test_tag_parsing():
	md = '# Hello world!\ntags:Foo Bar,Bar Baz\n\nThis is a test post.'
	post = _make_post(md)
	assert 'Hello world!' == post.title
	assert 'Foo Bar' == post.tags[0].title
	assert 'Bar Baz' == post.tags[1].title
	assert '<p>This is a test post.</p>' == post.body
