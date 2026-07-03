.PHONY: test test-fast

VENV_PY := ./venv/bin/python

# Full unit test suite.
test:
	$(VENV_PY) -m pytest

# Fast subset run at AGENT_OS pre-commit / completion checkpoints.
# Every test here is deterministic and offline, so this mirrors `test`.
test-fast:
	$(VENV_PY) -m pytest -q
