# PyBot source inventory and port prioritization

Pinned source tree: `huggingface/pybot@7d63c7fbebb44c7e466e5c8b5c1f341ab767929e`
Inventory method: recursive Git tree; `.py` blobs classified by top-level
`bot/` directory. Source size is Git blob byte size, **not translated code**.

| Upstream layer | Python files | Source bytes | Largest source modules |
| --- | ---: | ---: | --- |
| `bot/knowledge` | 159 | 22,612,439 | `family.py`, `home_craft.py`, `cooking_entries.py` |
| `bot/compose` | 126 | 6,186,226 | `fallback.py`, `fallback_data.py`, `fit.py` |
| `bot/memory` | 117 | 5,866,370 | `store_replies.py`, `facts.py`, `topics.py` |
| `bot/modules` | 110 | 4,801,675 | `chat.py`, `safety.py`, `answers.py` |
| `bot/understanding` | 13 | 1,448,366 | `kinds.py`, `normalize.py`, `topics.py` |
| `bot/runtime.py`, `bot/__main__.py`, `bot/__init__.py` | 3 | 5,359 | Runtime and entry points |
| **PyBot's `bot/` package** | **528** | **40,920,435** | |
| `pybot.py`, `tests/test_cli.py` | 2 | 13,131 | External CLI and test harness |

This snapshot describes source volume only, never measured behavioral coverage.
There is no rational basis for declaring progress by dividing Weightless's
Flow line count by PyBot's Python line count: rules may become compact tables,
and library abstractions may replace repeated source code.

## Port order

The original runtime uses three phases: observer hooks update shared memory,
every responder operates on an independently isolated memory snapshot, the
arbiter selects a candidate, only the winner's state is committed, and
`after` hooks plus a structured turn record follow.

Finish this invariant-preserving runtime before investing in bulk content.
Then port understanding and normalized topic IDs, memory/recall,
specialist/safety arbitration, composer and knowledge representations,
and individual responder modules. Port safety routing and its tests before
attempting broad public responses.

Knowledge accounts for over half the upstream source size. Investigate how
much is declarative rule/data material before choosing a representation:
a compact, indexed Flow-native data reader may be more faithful and efficient
than a literal line-for-line translation. Reproduction of source semantics
matters more than preserving source syntax.

## Verification protocol

Pull-request CI builds Weightless using Flow's self-hosted portable-C backend.
The differential runner executes original PyBot on the same multi-turn corpus
with isolated memory per session and a fixed random seed, then executes
Weightless once in tracing mode. Its report preserves input, original
response/module, Weightless response/module, and exact-match flags.

Exact string parity is a deliberately strict diagnostic, not a measure of
semantic correctness. A module name differs unless the naming conventions
are aligned; report it independently. Expand prompt coverage and test safety
invariants as actual functionality grows. New content must be checked against
the original implementation, rather than invented from the PyBot README.

Primary milestone tracker: [issue #2](https://github.com/godofecht/weightless/issues/2).
