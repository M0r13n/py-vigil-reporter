init:
	pip install -r requirements.txt

test:
	nosetests -v  --with-coverage --cover-package reporter tests/test_vigil.py