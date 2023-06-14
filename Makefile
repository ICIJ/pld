CURRENT_VERSION ?= `poetry version -s`
SEMVERS := major minor patch

clean:
		find . -name "*.pyc" -exec rm -rf {} \;
		rm -rf dist *.egg-info __pycache__

install: poetry_install

poetry_install:
		poetry install

tag_version: 
		git commit -m "build: bump to ${CURRENT_VERSION}" pyproject.toml
		git tag ${CURRENT_VERSION}

set_version:
		poetry version ${CURRENT_VERSION}
		$(MAKE) tag_version

$(SEMVERS):
		poetry version $@
		$(MAKE) tag_version

distribute:
		poetry publish --build 