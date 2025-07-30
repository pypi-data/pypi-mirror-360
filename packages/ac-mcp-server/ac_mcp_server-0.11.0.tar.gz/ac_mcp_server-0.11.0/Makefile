.PHONY: build publish-release publish-snapshot clean install test test-cov

build:
	rm -rf dist
	uv sync
	uv build

publish-release: build
	uv publish

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/

install:
	uv sync

test:
	uv run pytest

test-cov:
	uv run pytest --cov=. tests --cov-report xml:coverage.xml --cov-report term:skip-covered --junitxml=junit.xml