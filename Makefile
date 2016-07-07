test:
	nosetests

dev-install:
	pip install -e .

install:
	pip install .

clean:
	rm -rf dist *.egg_info

package: clean
	python setup.py sdist

pypi: package
	twine upload dist/clickutil-*.tar.gz
