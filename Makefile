PYTHON ?= python3
.DEFAULT_GOAL := verify
export PYTHONHASHSEED := 0
export TZ := UTC
export LC_ALL := C.UTF-8
export SOURCE_DATE_EPOCH := 946684800

.PHONY: refresh verify

verify:
	$(PYTHON) src/integrity.py results

refresh:
	$(PYTHON) src/refresh.py
