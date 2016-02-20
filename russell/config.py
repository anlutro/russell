import os
import os.path
import yaml


class ConfigFileNotFoundError(FileNotFoundError):
	pass


def normalize_config_dict(data):
	if 'root_path' not in data:
		data['root_path'] = os.getcwd()

	def set_dir_config(name):
		if name + '_dir' not in data:
			data[name + '_dir'] = name
		data[name + '_path'] = os.path.join(data['root_path'], data[name + '_dir'])

	set_dir_config('posts')
	set_dir_config('pages')
	set_dir_config('templates')
	set_dir_config('dist')

	return data


def load_config_file(path):
	with open(path) as file:
		return normalize_config_dict(yaml.load(file))
