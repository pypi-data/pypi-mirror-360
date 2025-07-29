
PROJECT_OWNER := AccidentallyTheCable
PROJECT_EMAIL := cableninja@cableninja.net
PROJECT_FIRST_YEAR := 2023
PROJECT_LICENSE := GPLv3
PROJECT_NAME := argstruct
PROJECT_DESCRIPTION := Reusable Argument Structure
PROJECT_VERSION := 1.2.0

## Enable Feature 'Python'
BUILD_PYTHON := 1
## Enable Feature 'Shell'
BUILD_SHELL := 0
## Enable Feature 'Docker'
BUILD_DOCKER := 0
## Enable python `dist` Phase for Projects destined for PYPI
PYTHON_PYPI_PROJECT := 1
## Additional Flags for pylint. EX --ignore-paths=mypath
PYLINT_EXTRA_FLAGS := 

CHECKSUM_IGNORE := \.spec|spec_doc/

### Any Further Project-specific make targets can go here
ARGSTRUCT_DIR := $(shell pwd)/spec_doc/
ARGSTRUCT_SPEC_VERSION := tags/release/1.1
ARGSTRUCT_SPEC_HOST := gitlab.com
ARGSTRUCT_SPEC_REPO := accidentallythecable-public/argstruct-spec
ARGSTRUCT_TAG_VERSION := $(shell echo ${ARGSTRUCT_SPEC_VERSION} | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g')
ARGSTRUCT_TAG_TYPE := $(shell echo ${ARGSTRUCT_SPEC_VERSION} | sed -r 's%^tags/(.*)/[0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?$$%\1%g')

spec_project_version: spec_check spec_copy  ## Check ArgStruct Git Version, Copy Specker Specs from ArgStruct Spec repo

spec_copy:  ## Copy Specker Specs from ARGSTRUCT_DIR into this library
	rm ${THIS_DIR}/src/argstruct/specs/*.spec
	cp ${ARGSTRUCT_DIR}/specker/*.spec ${THIS_DIR}/src/argstruct/specs/

spec_pull:  # Pull Specker Specs from https://gitlab.com/accidentallythecable-public/argstruct-spec.git
	if [ ! -d "${ARGSTRUCT_DIR}" ]; then\
		if [ "$$(git config --worktree -l | grep 'remote.origin.url' | egrep "https://")" != "" ]; then\
			git clone -q "https://${PULL_AUTH}${ARGSTRUCT_SPEC_HOST}/${ARGSTRUCT_SPEC_REPO}.git" "${ARGSTRUCT_DIR}";\
		else\
			git clone -q "git@${ARGSTRUCT_SPEC_HOST}:${ARGSTRUCT_SPEC_REPO}.git" "${ARGSTRUCT_DIR}";\
		fi;\
	fi
	cd "${ARGSTRUCT_DIR}" && git reset -q --hard
	cd "${ARGSTRUCT_DIR}" && git fetch -q -af --tags --prune
	cd "${ARGSTRUCT_DIR}" && git checkout -q "${ARGSTRUCT_SPEC_VERSION}"

spec_check:  ## Check if Specification being used matches latest on repo
	cd "${ARGSTRUCT_DIR}" && git fetch -q -af --tags --prune
ifeq ($(ARGSTRUCT_TAG_TYPE), release)
	@echo "Using Release Tagging"
	if [ "$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/release/')" != "" ]; then\
		if [ "$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${ARGSTRUCT_TAG_VERSION}" ]; then\
			echo "ArgStruct Version is out of date, Consider updating to the tag below:";\
			echo "tags/versions/$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)";\
			exit 1;\
		else\
			echo "ArgStruct Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/release/ tags for ArgStruct! :(";\
		exit 1;\
	fi
else
ifeq ($(ARGSTRUCT_TAG_TYPE), versions)
	@echo "Using Version Tagging"
	if [ "$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/versions/')" != "" ]; then\
		if [ "$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${ARGSTRUCT_TAG_VERSION}" ]; then\
			echo "ArgStruct Version is out of date, Consider updating to the tag below:";\
			echo "tags/versions/$(shell cd "${ARGSTRUCT_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)";\
			exit 1;\
		else\
			echo "ArgStruct Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/versions/ tags for ArgStruct! :(";\
		exit 1;\
	fi
else
	@echo "Unable to determine whether release or version tag."
	@echo "Unable to check for updates. You should just git pull in '${ARGSTRUCT_DIR}'"
endif
endif

#### CHECKSUM cdc8c29ada8cbcd8f766314aa9eca9359cde526368a3d5bf514da7ebdce3ec17
