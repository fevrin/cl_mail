.DEFAULT_GOAL := help

.PHONY: help
help: ## Miscellaneous: Returns this Makefile's commands and their descriptions in a formatted table
	@ci/scripts/makefile_help.sh $(MAKEFILE_LIST) 1


.PHONY: pkg-refresh ## purges all packages, then reinstalls only those that are imported
pkg-refresh:
	@pipenv uninstall --all && pipenv install -c .

.PHONY: gh-act-install
gh-act-install: ## Linting: Install 'gh' and the 'nektos/act' extension
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-@if command -v -- gh >/dev/null 2>&1; then \
		echo "$(shell gh --version | head -n1) installed"; \
		if gh act -h >/dev/null 2>&1; then \
			echo "$(shell gh act --version) installed"; \
		else \
			echo "installing 'act'..." && \
				gh extension install nektos/gh-act; \
		fi; \
	else \
		echo "error: install 'gh', then re-run 'make $@'"; \
		echo "https://github.com/cli/cli/blob/trunk/docs/install_linux.md#debian-ubuntu-linux-raspberry-pi-os-apt"; \
	fi

.PHONY: lint
lint: gh-act-install ## Linting: Run MegaLinter with nektos/act
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-gh act --artifact-server-path /tmp/artifacts -W .github/workflows/pre-commit.yml

.PHONY: lint-cleanup
lint-cleanup: ## Linting: Clean up any leftover docker continers from linting
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-for container in $$(docker container ls -a --format='{{.Names}}' | grep -E '^act-'); do \
		docker container stop --signal 9 "$${container}"; \
		docker container rm "$${container}"; \
	done && \
	for volume in $$(docker volume ls --format='{{.Name}}' | grep -E '^act-'); do \
		docker volume rm "$${volume}"; \
	done

.PHONY: pre-commit-install
pre-commit-install: ## Linting: Install pre-commit
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-@command -v -- pipenv >/dev/null 2>&1 || pip3 install pipenv
	-@if command -v -- pipenv >/dev/null 2>&1; then \
		echo "$(shell pipenv --version) installed"; \
		if pipenv run pre-commit -V >/dev/null 2>&1; then \
			echo "$(shell pipenv run pre-commit -V) installed"; \
		else \
			echo "installing pre-commit..." && \
				pipenv install pre-commit; \
		fi; \
	else \
	  echo "error: install 'pipenv', then re-run 'make $@'"; \
	fi

.PHONY: pre-commit-install-hooks
pre-commit-install-hooks: pre-commit-install ## Linting: Install pre-commit hooks
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-pipenv run pre-commit install

.PHONY: pre-commit
pre-commit: pre-commit-install ## Linting: Lints all files changed between the default branch and the current branch
	-@echo
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo $(shell echo '$@' | tr '[:lower:]' '[:upper:]')
	-@echo '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
	-@echo
	-pipenv run pre-commit run -v --show-diff-on-failure --color=always --all-files

.PHONY: act # runs nektos/act
act:
	gh act --verbose
