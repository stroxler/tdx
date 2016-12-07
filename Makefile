test:
	py.test
	flake8

dev-install:
	pip install -e .

install:
	pip install .

clean:
	rm -rf dist *.egg-info .cache
	find . -name __pycache__ | xargs rm -rf
	find . -name '*.pyc' | xargs rm

package: clean
	python setup.py sdist

pypi: package
	twine upload dist/tdx-*.tar.gz

tag:
	./dev-scripts/tag-release.sh
