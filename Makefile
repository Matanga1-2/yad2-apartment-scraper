.PHONY: test

test:
	pytest -v

test-address:
	pytest -v tests/address/

test-db:
	pytest -v tests/db/

test-app:
	pytest -v tests/test_app.py

test-yad2:
	pytest -v tests/yad2/

coverage:
	pytest --cov=src tests/

lint:
	ruff check .

lint-fix:
	ruff check --fix .

.PHONY: build-exe
build-exe:
	python build_exe.py