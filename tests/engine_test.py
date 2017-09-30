from russell.engine import make_link


def test_make_link(engine):
	assert '<a href="/test">Test</a>' == make_link('Test', '/test')
	assert '<a href="http://test">Test</a>' == make_link('Test', 'http://test')
	assert '<a href="http://test" target="_blank" rel="noopener noreferrer">Test</a>' == make_link('Test', 'http://test', blank=True)


def test_get_asset_link(engine):
	assert '//localhost/assets/test.css' == engine.get_asset_url('test.css')


def test_get_asset_link_with_hash(engine):
	engine.asset_hash['test.css'] = 'asdf'
	assert '//localhost/assets/test.css?asdf' == engine.get_asset_url('test.css')
