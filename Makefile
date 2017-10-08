install:
	pip install -U -r requirements/base.txt

devinstall:
	pip install -U -r requirements/test.txt

test:
	nosetests --with-coverage
