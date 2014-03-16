# Russell

A static blog HTML generator for Python 3.

## Installation

`pip install russell`

## Usage

`russell setup` will set up a directory structure for blogging with Russel in the current working directory. This will create the 'assets', 'backups', 'pages', 'posts', 'templates' directories, and create the required templates.

### Templating

Jinja2 is used as a templating engine, and all its features are present.

`root_url` has been added as a global variable, which you can use for generating urls in your template.

You may create your own layout.html template and then extend that via `{% extends 'layout.html' %}`.

### Creating pages/posts

`russell new page "My Test Page"` will create the file 'pages/my-test-page.md', which you can then open in your favourite text editor. The process is the same for `russell new post`. You can change the filename yourself to modify what the resulting .html file will be named.

### Generating the blog

Simply running `russell generate` will take all content from the current working directory, convert it to HTML (and copy any assets) and put it into the public/ directory, which can either be served directly or uploaded to your web host.

To specify a custom source/target path, simply use `russell /path/to/content /path/to/public`

You can specify the root url (you should) with `--url="http://www.website.com".

## Contact
Open an issue on GitHub if you have any problems or suggestions.

## License
The contents of this repository is released under the [MIT license](http://opensource.org/licenses/MIT). See the LICENSE file included for details.