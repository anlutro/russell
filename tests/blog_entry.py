import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

from russell.blog import Entry


def make_entry(title='Some Title', pubdate=None,
               body=None, tags=None, slug=None):
    if pubdate is None:
        pubdate = datetime.now()
    if body is None:
        body = 'Some body\n\nMore body'
    if tags is None:
        tags = set(['tag1', 'tag2'])
    return Entry(title, pubdate, body, tags, slug)


class BlogEntryTest(unittest.TestCase):

    def test_title_is_sluggified(self):
        entry = make_entry(title='Test Title')
        self.assertEqual('test-title', entry.slug)

    def test_excerpt_is_first_paragraph(self):
        entry = make_entry(body='p1\np2')
        self.assertEqual('<p>p1</p>', entry.excerpt)


class EntryFromFileTest(unittest.TestCase):
    body = '# Title\n\nBody'
    pubdate_body = '# Title\npubdate: 2014-01-01 12:00:00\n\nBody'
    getctime = datetime(2014, 1, 2, 12, 0, 0)
    getmtime = datetime(2014, 1, 1, 12, 0, 0)

    @patch('os.path', getctime=MagicMock(return_value=getctime.timestamp()),
           getmtime=MagicMock(return_value=getmtime.timestamp()))
    @patch('builtins.open', mock_open(read_data=body), create=True)
    def test_entry_can_be_created_from_file(self, path_mock):
        entry = Entry.from_file('/fake/path')
        self.assertEqual('Title', entry.title)
        self.assertEqual('<p>Body</p>', entry.body)
        self.assertEqual(datetime(2014, 1, 1, 12, 0, 0), entry.pubdate)

    @patch('builtins.open', mock_open(read_data=pubdate_body), create=True)
    def test_pubdate_is_parsed_from_body(self):
        entry = Entry.from_file('/fake/path')
        self.assertEqual(datetime(2014, 1, 1, 12, 0, 0), entry.pubdate)
