import logging
import jinja2

LOG = logging.getLogger(__name__)


def make_env(template_path, root_url):
	LOG.debug('setting up jinja env with root dir "%s"', template_path)
	loader = jinja2.FileSystemLoader(template_path)
	jinja_env = jinja2.Environment(loader=loader)
	jinja_env.globals['root_url'] = root_url
	return jinja_env
