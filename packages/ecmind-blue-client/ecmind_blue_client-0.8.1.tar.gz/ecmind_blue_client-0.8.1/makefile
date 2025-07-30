environment:
	python3 -m venv env
	
package-test:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --repository testpypi dist/*

package:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --repository pypi dist/*
