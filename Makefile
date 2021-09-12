.PHONY: help ## prints help info
help:
	@sed -rne 's;^(\.PHONY:\s+)?([a-z-]+ ##)\s+(.+)$$;\2\3;p' $(MAKEFILE_LIST) | sort | column -t -s '##'


.PHONY: pkg-refresh ## purges all packages, then reinstalls only those that are imported
pkg-refresh:
	@pipenv uninstall --all && pipenv install -c .
