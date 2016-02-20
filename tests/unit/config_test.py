import russell.config


def test_joins_root_path_with_dir_config():
	d = {'root_path': '/root', 'posts_dir': 'asdf'}
	d = russell.config.normalize_config_dict(d)
	assert '/root/asdf' == d['posts_path']


def test_has_dir_config_defaults():
	d = {'root_path': '/root'}
	d = russell.config.normalize_config_dict(d)
	assert '/root/posts' == d['posts_path']
	assert '/root/pages' == d['pages_path']
	assert '/root/templates' == d['templates_path']
	assert '/root/dist' == d['dist_path']
