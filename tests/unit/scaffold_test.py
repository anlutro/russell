import russell.scaffold


def test_create_page():
	slug, contents = russell.scaffold.get_page_slug_and_contents('Test title', 'Test body')
	assert 'test-title' == slug
	assert '# Test title\n\nTest body' == contents


def test_create_post():
	slug, contents = russell.scaffold.get_post_slug_and_contents('Test title',
		'Test body', pubdate='2015-01-01 12:34:56', tags=['Foo bar', 'Bar baz'])
	assert 'test-title' == slug
	assert '# Test title\npubdate: 2015-01-01 12:34:56\ntags: Foo bar, Bar baz\n\nTest body' == contents
