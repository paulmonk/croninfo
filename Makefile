# Warn when if an undefined variable is used mainly to catch misspelled
MAKEFLAGS+= --warn-undefined-variables

# This disables the bewildering array of built in rules to automatically build
# Yacc grammars out of your data if you accidentally add the wrong file suffix.
# Rules: https://www.gnu.org/software/make/manual/html_node/Catalogue-of-Rules.html
MAKEFLAGS += --no-builtin-rules

# Force Makefile to use Bash over Sh.
SHELL := /bin/bash

# The -c flag is in the default value of .SHELLFLAGS and we must preserve it,
# because it is how make passes the script to be executed to bash.
.SHELLFLAGS := -o errexit -o errtrace -o pipefail -o nounset -c

# Cancel out as not needed here.
.SUFFIXES:

# If no target is provided default to help.
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "==========================================================="
	@echo "croninfo"
	@echo ""
	@echo "List of available recipes:"
	@echo "--------------------------"
	@$(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2> /dev/null \
		| awk -v RS= -F: '/^# File/,/^# Finished Make data base/ \
		{if ($$1 !~ "^[#.]") {print $$1}}' \
			| sort \
				| egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
	@echo "==========================================================="


#------------------------------
# Consts
#------------------------------
ROOT_DIR = $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

#------------------------------
# Deps
# Management the local virtualenv for dev.
#------------------------------
VENV ?= ./.virtualenv
VENV_STAMP := $(VENV)/requirements-installed.txt
PY_VERSION ?= "3.9"
PY_MAJOR_VERSION := $(shell echo $(shell cut -d '.' -f 1 <<< "$(PY_VERSION)")"."$(shell cut -d '.' -f 2 <<< "$(PY_VERSION)"))
PY_MAJOR_VERSION_REQ := $(shell echo $(PY_MAJOR_VERSION) | tr -d '.')

$(VENV_STAMP): requirements/py$(PY_MAJOR_VERSION_REQ).txt
	@echo "Installing dependencies..."
	python$(PY_MAJOR_VERSION) -m venv $(@D)
	$(@D)/bin/pip install --upgrade wheel pip setuptools
	$(@D)/bin/pip install --upgrade -r $<
	@cp $< ${@D}/requirements-declared.txt
	@$(@D)/bin/pip freeze --disable-pip-version-check > $@
	@$(@D)/bin/pip install --no-dependencies .

.PHONY: deps
deps: $(VENV_STAMP)

.PHONY: clean
deps-clean:
	rm -rf $(VENV)

# Assumes you have all required Python versions available locally with pip-tools
# available too. Can not be run if a virtualenv is active.
.PHONY: deps-compile
deps-compile:
	@$(CURDIR)/requirements/compile

#------------------------------
# Docker
# Requires docker to be installed and on $PATH
#------------------------------
DOCKER_IMAGE_TAG ?= "croninfo:latest"
ARGS ?= --help

.PHONY: docker-build
docker-build:
	@docker build . --tag $(DOCKER_IMAGE_TAG) --file $(CURDIR)/Dockerfile

.PHONY: docker-run
docker-run:
	@docker run $(DOCKER_IMAGE_TAG) $(ARGS)

#------------------------------
# Helpers
# Local development assistance.
#------------------------------
.PHONY: lint-fix
lint-fix:
	@pre-commit run --all-files

.PHONY: test
test: deps
	@$(VENV)/bin/coverage erase
	@tox --recreate
	@$(VENV)/bin/coverage combine
	@$(VENV)/bin/coverage report --fail-under=90
