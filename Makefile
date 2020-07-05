init:
	pip install -r requirements.txt

test:
	nosetests -v  --with-coverage --cover-package vigil_reporter tests/*.py

build:
	rm -rf dist/ && python setup.py sdist bdist_wheel

check-build:
	twine check dist/*