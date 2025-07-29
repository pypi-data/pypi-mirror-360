# Copyright 2023-2023 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of AccidentallyTheCables Automation Tools,
# and is released under "AGPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
AUTOMATION_VERSION := tags/release/1.4
AUTOMATION_GIT_PATH := accidentallythecable-code/utils/automation-tools
AUTOMATION_GIT_HOST := gitlab.com

THIS_DIR := $(shell pwd)
AUTOMATION_DIR := ${THIS_DIR}/automation/

NO_PULL ?= 0
RETRY ?= 0

HAVE_AUTOMATION := $(shell test -f "${AUTOMATION_DIR}/core.mk" && echo "1" || echo "0")

TAG_TYPE := $(shell echo ${AUTOMATION_VERSION} | sed -r 's%^tags/(.*)/[0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?$$%\1%g')
TAG_VERSION := $(shell echo ${AUTOMATION_VERSION} | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g')

CHECKSUM_IGNORE ?=  ^$$
CHECKSUM_ALWAYS_IGNORE := \.[Mm][Dd]|\.json|\.pylintrc|\.mypy\.ini|\.?gitignore|\.git|\.vscode|\.mypy_cache|__pycache__|\.egg-info|docs/|automation/|Doxyfile

ifneq ($(PULL_PASSWORD), )
PULL_AUTH := "token:${PULL_PASSWORD}@"
endif

ifeq ($(HAVE_AUTOMATION), 1)  ## Automation Has been pulled already
# Get current automation branch
CURR_BRANCH := $(shell cd "${AUTOMATION_DIR}" && git branch | sed -r 's/\(HEAD detached at (.*)\)/\1/g' | egrep '^\*' | awk '{print $$2;}')
ifneq ($(CURR_BRANCH), $(AUTOMATION_VERSION))  ## Re-pull if AUTOMATION_VERSION isnt the active automation branch
ifeq ($(NO_PULL), 0)
%:  # Pull Automation and Force Exit for all targets
	@echo "CURR_BRANCH:${CURR_BRANCH}; AUTOMATION_VERSION:${AUTOMATION_VERSION}; Incorrect Automation Version, Attempting to Pull it"
	$(MAKE) $(MAKEFLAGS) automation_pull
	@echo "Please Re-run this again"
	exit 99
endif
include ${AUTOMATION_DIR}/core.mk
else  ## Automation Up to date, Allow including core functionality
include ${AUTOMATION_DIR}/core.mk
endif

else ## Automation Does not exist, needs a pull
ifeq ($(NO_PULL), 0)
%:  # Pull Automation and Force Exit for all targets
	@echo "HAVE_AUTOMATION:${HAVE_AUTOMATION}; Unable to locate Automation, Attempting to Pull it"
	$(MAKE) $(MAKEFLAGS) automation_pull
	@echo "Please Re-run this again"
	exit 99
endif
endif

automation_version_update:  # Update Project to use Latest Automation Version
	cd "${AUTOMATION_DIR}" && git fetch -q -af --tags --prune
# Pull tags based on whether `tags/release/*` is in use
ifeq ($(TAG_TYPE), release)
	@echo "Using Release Tagging"
	if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/')" != "" ]; then\
		if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${TAG_VERSION}" ]; then\
			sed -ri 's%^AUTOMATION_VERSION.*%AUTOMATION_VERSION := tags/release/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)%g' "${THIS_DIR}/Makefile";\
			if [ -f "${THIS_DIR}/.gitlab-ci.yml" ]; then\
				sed -ri 's%^    ref:.*%    ref: tags/release/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)%g' "${THIS_DIR}/.gitlab-ci.yml";\
			fi;\
			echo "Automation Version Updated!";\
		else\
			echo "Automation Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/release/ tags for Automation! :(";\
		exit 1;\
	fi
else
# Pull tags based on whether `tags/versions/*` is in use
ifeq ($(TAG_TYPE), versions)
	@echo "Using Version Tagging"
	if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/')" != "" ]; then\
		if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${TAG_VERSION}" ]; then\
			sed -ri 's%^AUTOMATION_VERSION.*%AUTOMATION_VERSION := tags/versions/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)%g' "${THIS_DIR}/Makefile";\
			if [ -f "${THIS_DIR}/.gitlab-ci.yml" ]; then\
				sed -ri 's%^    ref:.*%    ref: tags/versions/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)%g' "${THIS_DIR}/.gitlab-ci.yml";\
			fi;\
			echo "Automation Version Updated!";\
		else\
			echo "Automation Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/versions/ tags for Automation! :(";\
		exit 1;\
	fi
else
# Cannot do anything about an updated version
	@echo "Unable to determine whether release or version tag."
	exit 1
endif
endif

automation_pull:  # Clone/Checkout Automation Repository
	if [ ! -d "${AUTOMATION_DIR}" ]; then\
		if [ "$$(git config --worktree -l | grep 'remote.origin.url' | egrep "https://")" != "" ]; then\
			git clone -q "https://${PULL_AUTH}${AUTOMATION_GIT_HOST}/${AUTOMATION_GIT_PATH}.git" "${AUTOMATION_DIR}";\
		else\
			git clone -q "git@${AUTOMATION_GIT_HOST}:${AUTOMATION_GIT_PATH}.git" "${AUTOMATION_DIR}";\
		fi;\
	fi
	cd "${AUTOMATION_DIR}" && git reset -q --hard
	cd "${AUTOMATION_DIR}" && git fetch -q -af --tags --prune
	cd "${AUTOMATION_DIR}" && git checkout -q "${AUTOMATION_VERSION}"

automation_check:  # Check Automation Version Status
	cd "${AUTOMATION_DIR}" && git fetch -q -af --tags --prune
ifeq ($(TAG_TYPE), release)
	@echo "Using Release Tagging"
	if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/')" != "" ]; then\
		if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${TAG_VERSION}" ]; then\
			echo "Automation Version is out of date, Consider updating to the tag below:";\
			echo "tags/versions/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/release/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)";\
			exit 1;\
		else\
			echo "Automation Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/release/ tags for Automation! :(";\
		exit 1;\
	fi
else
ifeq ($(TAG_TYPE), versions)
	@echo "Using Version Tagging"
	if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/')" != "" ]; then\
		if [ "$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)" != "${TAG_VERSION}" ]; then\
			echo "Automation Version is out of date, Consider updating to the tag below:";\
			echo "tags/versions/$(shell cd "${AUTOMATION_DIR}" && git tag -l | grep 'tags/versions/' | sed -r 's%^tags/(.*)/([0-9]{1,}\.[0-9]{1,}(\.[0-9]{1,})?)$$%\2%g' | sort -rV | head -n 1)";\
			exit 1;\
		else\
			echo "Automation Version is up to date!";\
		fi;\
	else\
		echo "Unable to locate any tags/versions/ tags for Automation! :(";\
		exit 1;\
	fi
else
	@echo "Unable to determine whether release or version tag."
	@echo "Unable to check for updates. You should just git pull in '${AUTOMATION_DIR}'"
endif
endif

.SILENT:
verify_checksums:  ## Verify File Checksums
	export _CHECKSUM_LIST=$$(find "${THIS_DIR}/" -type f | grep -vE "${CHECKSUM_IGNORE}" | grep -vE "${CHECKSUM_ALWAYS_IGNORE}");\
	res=0;\
	for f in $${_CHECKSUM_LIST}; do\
		c="$$(wc -l "$${f}" | awk '{print $$1;}')";\
		lines="$$((c - 1))";\
		if [ -z "$$(grep -E "^#### CHECKSUM" "$${f}")" ]; then echo "Warning: $${f} did not have a checksum line!"; res=1; continue; fi;\
		SRC=$$(head -n $${lines} $${f} | sha256sum | awk '{print $$1;}');\
		CHECK=$$(grep -E "^#### CHECKSUM" $${f} | awk '{print $$3;}');\
		if [ "$${SRC}" != "$${CHECK}" ]; then echo "$${f} Does not match Checksum; Check: $${CHECK}, Got: $${SRC}"; res=1; fi;\
	done;\
	if [ $${res} -eq 1 ]; then exit 1; fi

#### CHECKSUM 0a60199398951d924272a964b179ffd72445a53ba8d1f8d2d6ca772dc425c7a9
