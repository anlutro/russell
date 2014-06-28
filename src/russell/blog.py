from datetime import datetime
import os
import shutil
import tarfile

from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from slugify import slugify
import dateutil.parser


def make_tarfile(trg_path, src_dir):
    """
    Make a tarfile out of a directory's contents.

    Keyword arguments:
    trg_path - The path to the target tar file.
    src_dir - The directory that should be archived.
    """
    with tarfile.open(trg_path, 'w:gz') as tar:
        tar.add(src_dir, arcname=os.path.basename(src_dir))


def list_files(dir):
    """List all files recursively in a directory."""
    results = set()

    for root, dirs, files in os.walk(dir):
        for f in files:
            results.add(os.path.join(root, f))

    return results


class Entry():
    """Generic class for posts and pages."""
    def __init__(self, title, pubdate, body, tags=set(), slug=None):
        self.title = title
        self.pubdate = pubdate
        self.body = body
        self.excerpt = body.split('\n', 1)[0]
        self.tags = tags
        self.slug = slug or slugify(title)

    @classmethod
    def from_file(cls, path):
        """Create a new object from a markdown file."""
        with open(path, 'r') as f:
            lines = f.read().split('\n')

        # The first line will be the title of the post.
        title = lines[0].replace('#', '').strip()
        # The remaining contents will be the body.
        body = '\n'.join(lines[1:]).strip()

        # Analyze the first line to see if there is a custom pubdate
        if lines[1][:8].lower() == 'pubdate:':
            try:
                pubdate = datetime.strptime(lines[1][9:], '%Y-%m-%d %H:%M:%S')
                body = '\n'.join(body.split('\n')[1:]).strip()
            except ValueError:
                print('Could not parse datetime from article:', lines[1])
                print('Pubdate must be in format Y-m-d H:M:S')
                return
        else:
            # The oldest of the file's creation date and update time will be
            # used as a pubdate. This allows you to `touch` a file with a time
            # in the past to set its pubdate that way
            timestamp = min(os.path.getctime(path), os.path.getmtime(path))
            pubdate = datetime.fromtimestamp(timestamp)

        # convert body from markdown to HTML
        body = markdown(body)

        # The slug will be the name of the file.
        slug = os.path.splitext(os.path.basename(path))[0]

        return cls(title=title, body=body, pubdate=pubdate, slug=slug)


class Blog():
    """God class that controls the blog."""
    def __init__(self, src_dir, trg_dir, root_url=''):
        self.src_dir = src_dir
        self.trg_dir = trg_dir
        self.setup_jinja(root_url)
        self.posts = []

    def setup_jinja(self, root_url):
        loader = FileSystemLoader(os.path.join(self.src_dir, 'templates'))
        self.j2env = Environment(loader=loader)
        self.j2env.globals['root_url'] = root_url

    def setup(self):
        def write_file(path, content=''):
            """Write to a file if it does not already exist."""
            path = os.path.join(self.src_dir, path)
            if not os.path.exists(path):
                with open(path, 'w+') as f:
                    f.write(content)

        print('Setting up directories...')

        # create directories if they don't already exist
        dirs = ['assets', 'pages', 'posts', 'templates']
        for d in dirs:
            d = os.path.join(self.src_dir, d)
            if not os.path.isdir(d):
                os.makedirs(d)

        print('Creating files...')
        write_file(os.path.join('pages', 'sample-page.md'), '# Sample page\n\n\
            This is a sample page! Do with it whatever you like.')
        write_file(os.path.join('posts', 'sample-post.md'), '# Sample post\n\n\
            This is a sample post! Do with it whatever you like.')
        write_file(os.path.join('templates', 'archive.html'))
        write_file(os.path.join('templates', 'home.html'))
        write_file(os.path.join('templates', 'page.html'))
        write_file(os.path.join('templates', 'single.html'))
        write_file(os.path.join('assets', 'style.css'))
        print('Done!')

    def new_page(self, title):
        """Create a new page file."""
        slug = slugify(title)
        path = os.path.join(self.src_dir, 'pages', slug + '.md')
        if os.path.exists(path):
            print('File already exists in', path, '- aborting!')
            return
        print('Creating new page in', path)
        with open(path, 'w+') as f:
            f.write('# ' + title + '\n\nWrite your page contents here!')
        print('Done!')

    def new_post(self, title, timestr=None):
        """Create a new post file."""
        slug = slugify(title)
        path = os.path.join(self.src_dir, 'posts', slug + '.md')

        if os.path.exists(path):
            print('File already exists in', path, '- aborting!')
            return

        dt = None
        if timestr:
            try:
                dt = dateutil.parser.parse(timestr)
            except TypeError:
                print('Could not parse datetime', timestr)
                return

        print('Creating new post in', path)
        with open(path, 'w+') as f:
            f.write('# ' + title + '\n')
            if dt:
                f.write('pubdate: ' + dt.strftime('%Y-%m-%d %H:%M:%S') + '\n')
            f.write('\nWrite your post contents here!')
        print('Done!')

    def generate(self):
        """Generate the blog."""
        self.backup()
        print('Generating...')
        print('Copying assets...')
        for f in self.get_asset_files():
            self.copy_asset(f)
        print('Creating pages...')
        for f in self.get_page_files():
            self.convert_page(f)
        print('Creating posts...')
        for f in self.get_post_files():
            self.convert_post(f)

        # sort posts by pubdate (newest first) before generating home/archives
        self.posts.sort(key=lambda post: post.pubdate, reverse=True)
        self.generate_home()
        self.generate_archive()
        print('Done!')

    def backup(self):
        """Generate a backup of existing files."""
        if not os.path.exists(self.trg_dir):
            print('Nothing to back up, skipping...')
            return

        trg_dir = os.path.join(self.src_dir, 'backups')
        if not os.path.isdir(trg_dir):
            os.makedirs(trg_dir)

        filename = datetime.now().strftime('backup_%Y-%m-%d_%H%M%S.tar')
        trg_path = os.path.join(trg_dir, filename)

        print('Backing up data into', trg_path)
        make_tarfile(trg_path, self.trg_dir)
        shutil.rmtree(self.trg_dir)
        os.makedirs(self.trg_dir)

    def get_asset_files(self):
        return list_files(os.path.join(self.src_dir, 'assets'))

    def get_page_files(self):
        return list_files(os.path.join(self.src_dir, 'pages'))

    def get_post_files(self):
        return list_files(os.path.join(self.src_dir, 'posts'))

    def get_template(self, tpl):
        return self.j2env.get_template(tpl)

    def convert_page(self, path):
        """Generate a page html file."""
        trg_dir = self.trg_dir
        if not os.path.isdir(trg_dir):
            os.makedirs(trg_dir)

        page = Entry.from_file(path)
        tpl = self.get_template('page.html')
        html = tpl.render(page=page)
        trg_path = os.path.join(trg_dir, page.slug + '.html')

        print('Writing', trg_path)
        with open(trg_path, 'w+') as f:
            f.write(html)

    def convert_post(self, path):
        """Generate a post html file."""
        trg_dir = os.path.join(self.trg_dir, 'posts')
        if not os.path.isdir(trg_dir):
            os.makedirs(trg_dir)

        post = Entry.from_file(path)
        self.posts.append(post)
        tpl = self.get_template('post.html')
        html = tpl.render(post=post)
        trg_path = os.path.join(trg_dir, post.slug + '.html')

        print('Writing', trg_path)
        with open(trg_path, 'w+') as f:
            f.write(html)

    def generate_home(self, limit=5):
        """Generate the home page."""
        print('Generating home page (index.html)...')
        posts = self.posts[:limit]
        tpl = self.get_template('home.html')
        html = tpl.render(posts=posts)
        with open(os.path.join(self.trg_dir, 'index.html'), 'w+') as f:
            f.write(html)

    def generate_archive(self):
        """Generate the archive page."""
        print('Generating archives (archive.html)...')
        tpl = self.get_template('archive.html')
        html = tpl.render(posts=self.posts)
        with open(os.path.join(self.trg_dir, 'archive.html'), 'w+') as f:
            f.write(html)

    def copy_asset(self, path):
        """Copy asset files."""
        trg_dir = os.path.join(self.trg_dir, 'assets')
        if not os.path.isdir(trg_dir):
            os.makedirs(trg_dir)
        shutil.copy2(path, trg_dir)
