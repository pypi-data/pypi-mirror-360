.PHONY: clean build release bump-major bump-minor bump-patch

clean:
	rm -rf dist build *.egg-info

build:
	python -m build

release:
	python -m build
	twine upload dist/*
