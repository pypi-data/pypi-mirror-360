install:
	pip install --verbose -e .

package:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	python setup.py sdist bdist_wheel
