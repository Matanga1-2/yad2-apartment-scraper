.PHONY: test

test:
	pytest -v

test-address:
	pytest -v tests/address/

coverage:
	pytest --cov=src tests/