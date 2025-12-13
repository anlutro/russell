# Russell

A static HTML site generator written in Python 3.

## Installation

The recommended way to install Russell is to use [`uv`](https://docs.astral.sh/uv/):

	$ mkdir /home/myuser/blog
	$ cd /home/myuser/blog
	$ uv init
	$ uv add russell

Once that's done, you can either manually create the required files, or let Russell set up an example project for you:

	$ uv run russell setup .

## Usage

`russell setup` will set up an example configuration file and directory
structure in the current working directory to get you started.

### Creating pages/posts

`russell new page "My Test Page"` will create the file 'pages/my-test-page.md',
which you can then open in your favourite text editor. The process is the same
for `russell new post`. You can change the filename yourself to modify what the
resulting .html file will be named.

### Generating the blog

`russell generate` will run the `generate` function in your `config.py`, which
should contain all the instructions for generating HTML and other assets.

To test your newly generated site, run `russell serve`.

### Templating

Jinja2 is used as a templating engine, and all its features are present.

Read the Jinja2 documentation here: http://jinja.pocoo.org/

`root_url` has been added as a global variable, which you can use for generating
URLs in your template.

The "index" and "archive" templates have the `posts` variable available. The
"post" template has the `post` variable and "page" has the `page` variable.
`posts` is an array of `Post` objects, the others are a single instance of
either `Post` or `Page`.

## License

The contents of this repository are released under the [GPL v3 license](https://opensource.org/licenses/GPL-3.0). See the [LICENSE](LICENSE) file included for more information.
