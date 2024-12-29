.PHONY: check

check:
	ruff check . --fix
	pytest

check_browser:
	pytest -v -s tests/test_browser.py

check_yad2:
	pytest -v -s tests/test_yad2_client.py