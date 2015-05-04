flake:
	flake8 aiorest_ws tests

develop:
	python setup.py develop

test:
	py.test -q -s --cov aiorest_ws --tb=native -n4
