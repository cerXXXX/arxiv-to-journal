PYTHON ?= python3
export PYTHONHASHSEED := 0
export TZ := UTC
export LC_ALL := C.UTF-8
export SOURCE_DATE_EPOCH := 946684800

.PHONY: reproduce test refresh verify-cache verify clean-check

reproduce:
	$(PYTHON) src/integrity.py verify
	$(PYTHON) src/bootstrap.py
	$(PYTHON) src/build.py
	$(PYTHON) -m unittest discover -s tests -q
	$(PYTHON) src/integrity.py results

test:
	$(PYTHON) src/bootstrap.py
	$(PYTHON) -m unittest discover -s tests -v

verify-cache:
	$(PYTHON) src/integrity.py verify

verify: reproduce

refresh:
	$(PYTHON) src/refresh.py

clean-check:
	$(PYTHON) src/clean_check.py
