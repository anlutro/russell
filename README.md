# Russell ![Build Status](https://travis-ci.org/anlutro/russell.png?branch=master)

A static HTML site generator written in Python 3.

## Installation

	pip install russell

I recommend either running the command with `--user`, or to create a virtualenv
and run the command with the virtualenv activated.

## Usage

`russell setup` will set up an example configuration file and directory
structure in the current working directory to get you started.

### Creating pages/posts

`russell new-page "My Test Page"` will create the file 'pages/my-test-page.md',
which you can then open in your favourite text editor. The process is the same
for `russell new-post`. You can change the filename yourself to modify what the
resulting .html file will be named.

### Generating the blog

In a directory with a `russell.yml` config file, running `russell generate` will
read all pages and posts, convert it into HTML and place it in the `dist`
directory by default.

After doing this, you probably want to add your own files like a CSS stylesheet.
Russell will not manage this bit for you.

You can override the root URL (used in generated links) with the `root-url`
option: `russell generate --root-url=http://localhost:8080`

### Templating

Jinja2 is used as a templating engine, and all its features are present.

Read the Jinja2 documentation here: http://jinja.pocoo.org/

`root_url` has been added as a global variable, which you can use for generating
URLs in your template.

The "home" and "archive" templates have the `posts` variable available. The
"post" template has the `post` variable and "page" has the `page` variable.
`posts` is an array of `Post` objects, the others are a single instance of
either `Post` or `Page`.

## Contact

Open an issue on GitHub if you have any problems or suggestions.

## License

The contents of this repository is released under the [MIT
license](http://opensource.org/licenses/MIT). See the LICENSE file included for
details.
