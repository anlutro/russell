import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

from russell.blog import Blog


def make_blog(src_dir='/fake/src', trg_dir='/fake/trg', title='Fake Title',
              root_url='http://fake.url'):
    return Blog(src_dir, trg_dir, title, root_url)


# patch builtins.print to do nothing everywhere
@patch('builtins.print', MagicMock())
class BlogTest(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_new_page(self, m):
        blog = make_blog()
        blog.new_page('Fake title')
        m.assert_called_once_with('/fake/src/pages/fake-title.md', 'w+')
        write_str = '# Fake title\n\nWrite your page contents here!'
        m().write.assert_called_once_with(write_str)

    @patch('builtins.open', new_callable=mock_open)
    def test_new_post(self, m):
        blog = make_blog()
        blog.new_post('Fake title')
        m.assert_called_once_with('/fake/src/posts/fake-title.md', 'w+')
        write_str = '# Fake title\n\nWrite your post contents here!'
        m().write.assert_called_once_with(write_str)
