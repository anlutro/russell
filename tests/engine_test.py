import os.path
import pytest
from russell.engine import BlogEngine


@pytest.fixture
def engine():
	root_path = os.path.dirname(__file__)
	return BlogEngine(root_path, 'test', '//localhost')


def test_get_link(engine):
	assert '<a href="/test">Test</a>' == engine.get_link('Test', '/test')
	assert '<a href="http://test">Test</a>' == engine.get_link('Test', 'http://test')
	assert '<a href="http://test" target="_blank" rel="noopener noreferrer">Test</a>' == engine.get_link('Test', 'http://test', blank=True)
