test:
	find src dist dist tests  -type f -name '*.py' -print0 | xargs -0 pep8 -
	./run-tests.sh

release:
	python3 setup.py sdist upload
