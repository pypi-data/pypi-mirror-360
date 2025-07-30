.PHONY: test
test:
	pytest --snowflake-session local

.PHONY: test/coverage
test/coverage:
	pytest --snowflake-session local --cov=src.winningvariant tests/

.PHONY: test/coverage/html
test/coverage/html:
	pytest --snowflake-session local --cov=src.winningvariant tests/ --cov-report html

.PHONY: build
build:
	python3 -m build

.PHONY: publish
publish:
	python3 -m twine upload --repository winningvariant dist/*