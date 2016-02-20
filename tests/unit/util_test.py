import russell.util


def test_generate_excerpt():
	body = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec\n'
		'maximus diam ut ligula blandit semper. Proin id nulla libero.\n\n'
		'Quisque blandit ut enim in ultricies. Sed sollicitudin aliquam\n'
		'consectetur. In pharetra, justo a ultrices porttitor, quam risus\n'
		'semper dolor, interdum tempus est libero ac tellus.')
	excerpt = russell.util.generate_excerpt(body)
	expected = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec '
		'maximus diam ut ligula blandit semper. Proin id nulla libero.')
	assert expected == excerpt
