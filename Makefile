test:
	pep8
	./run-tests.sh

release:
	python3 setup.py sdist upload
