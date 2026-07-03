# CHANGE: Add offline unit test suite

Date: 2026-07-03
Type: test
ADR: none — test scaffolding, no architectural change (AGENT_OS §7)

## What changed

- Makefile: added with `test` and `test-fast` targets (satisfies AGENT_OS §12 python-runtime command interface)
- pytest.ini: pytest config (testpaths=tests)
- conftest.py: puts project root on sys.path so top-level modules import under pytest
- requirements-dev.txt: pins pytest==9.1.1
- tests/test_config.py: `_bool` truthy/falsey/default parsing
- tests/test_content_builder.py: fit_tweet budget + model-extra stripping, hashtag derivation, price formatting, store-link UTM
- tests/test_printful_client.py: image-url selection, product normalization, empty-store handling
- tests/test_llm_provider.py: provider dispatch + failure returns empty string
- .gitignore: ignore .pytest_cache/

## Why

python-runtime projects require a test suite and a `make test-fast` command (AGENT_OS §8, §12); none existed. Closes the last AGENT_OS compliance gap flagged in CHANGE-2026-07-03-001.

## Risk

LOW

Test-only + build tooling. No product/runtime code changed. Tests are deterministic and offline (no network, no live API/LLM calls).

## Verified

- [x] Tests pass — `make test-fast`: 18 passed
- [x] No regressions observed — no application code modified
- [x] Behavior matches intent — tests exercise the pure functions of config, content_builder, printful_client, llm_provider
