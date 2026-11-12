PYTHON ?= python3
.DEFAULT_GOAL := full
export PYTHONHASHSEED := 0
export TZ := UTC
export LC_ALL := C.UTF-8
export SOURCE_DATE_EPOCH := 946684800

.PHONY: full pipeline

full:
	$(PYTHON) src/refresh.py

pipeline:
	@test -n "$(SNAPSHOT)" || { echo 'Usage: make pipeline SNAPSHOT=data/live/<timestamp>' >&2; exit 2; }
	$(PYTHON) src/pipeline.py --data-root "$(SNAPSHOT)" --output "$(SNAPSHOT)/results"
