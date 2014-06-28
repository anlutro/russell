test:
	pep8
	run-tests.sh

release:
	python setup.py sdist upload
