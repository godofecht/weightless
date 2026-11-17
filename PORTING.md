# Porting contract

Upstream: https://github.com/huggingface/pybot
Upstream interface: `bot/runtime.py`
Target language: https://github.com/flooooooooooow/flow
Target backend: Flow's self-hosted C backend

## Invariants adopted from PyBot

1. Observe the input into shared conversation state before routing.
2. Let independent responders propose replies with separate copies of the value-state, retaining only a shared immutable transcript pointer.
3. Collect all non-empty proposals in a dynamically growing candidate array, then select a winner by priority, with non-repetition used only as a tie-breaker.
4. Commit only the winner's state, apply the current name-correction after-hook, then append the turn to conversation history.
5. Return a non-empty fallback when no responder matches.
6. Keep state across piped lines; reset it on `/reset` in interactive mode.

**Current limits:** The Flow port stores a fixed set of conversation attributes
and every recorded turn in a dynamically growing native Flow memory buffer. The buffer is freed when the conversation resets or exits. The full transcript is available within the process, but this is not PyBot's complete structured memory model. Unlike PyBot, Weightless has no general-purpose dictionary memory or persistent journal. It now maintains an immutable linked history for the first recognized facts: self/relative names, jobs and locations, with source utterance and turn. This fact schema is not yet a complete memory implementation; supported subjects and fields are deliberately narrow.
PyBot's arbiter has many additional rules, especially safety precedence, topic
specificity, and refusal handling. Weightless does not implement those policies yet.

## Ported

| Upstream | Weightless | Status |
|---|---|---|
| `bot/runtime.py` | `src/main.flow` | Partial observable pipeline, growable candidate collection, value-state copies, dynamically growing transcript and a correction hook |
| `bot/modules/arbiter.py` | `choose`, `prefer` | Arbitrary candidate count, priority and non-repeat tie-break only |
| `bot/modules/greeting.py` | `greeting_reply` | Tiny deterministic subset |
| `bot/modules/memory_store.py` | `Memory`, `observe`, `name_reply`, `recall_reply`, `fact_reply` | Name, latest-turn, job, city, and named-relative recall subsets |
| `bot/understanding/{normalize,kinds,topics,references}.py` | `src/understanding.flow` | Partial shared line reading: ASCII normalization, kind, intent, answer shape and short follow-up topic inheritance |
| `bot/memory/facts.py` | `src/facts.flow` | Immutable, attributed fact nodes with source utterance and turn; only a small observation/retrieval subset |
| `bot/compose/*`, `bot/knowledge/*` | `knowledge_reply` and `src/knowledge.flow` | Three example answer families plus 8 source-derived knowledge entries |
| `pybot.py` | `main`, `read_line` | Basic CLI; timing and terminal clearing omitted |

## Not ported

The majority of `bot/modules/`, `bot/understanding/`, `bot/memory/`,
`bot/knowledge/`, `bot/compose/` and PyBot's full safety routing.
The sample rule set is **not** a general-purpose advice or safety chatbot.
No claim of benchmark parity or production readiness is made.

## Running

From a Flow 2.x installation:

```sh
flow run src/main.flow -- --self-test
flow run src/main.flow -- -p "hi, i'm Sam"
printf "hi, i'm Sam\nwhat's my name?\n" | flow run src/main.flow
flow run src/main.flow
```

The `-s/--seed` argument is accepted for compatibility but has no effect
until candidate wording is randomized. The `-v` option prints a module tag,
not PyBot's millisecond timings.

CI checks Flow's native compiler, forty-three runtime regression scenarios plus eleven standalone understanding tests and representative CLI contracts.
A pull-request-only differential job checks 61 fixture turns against upstream PyBot
at pinned commit `7d63c7fbebb44c7e466e5c8b5c1f341ab767929e`.
The original Python runtime is used only as the external reference test oracle.
The knowledge corpus is loaded natively from `data/knowledge.tsv`, or the path set in `WEIGHTLESS_KNOWLEDGE`.
`flow run src/main.flow -- --knowledge-stats` prints its loaded entry count.
Source paths are recorded with each row and the current in-memory scorer is a deliberately
limited approximation of PyBot's full `lookup.py` (no spelling or morphological matching yet).
The JSON report stores both answers, winning modules, every proposed reply with module identity, candidate-set overlap totals, and exact-match flags;
mismatches are expected until the port is complete. Do not interpret a
green diagnostic job as behavioural equivalence. The reference dataset lives in
`fixtures/differential.json`, the runner in `ci/compare_reference.py`.
Only passing CI on the target commit establishes successful execution.

## Next increments

Complete observer/after-hook dispatch, correct independent nested-state snapshots, robust fallbacks and per-module failure isolation. The current snapshots are struct-value copies with an intentionally shared read-only transcript: full PyBot-style deep mutable dictionaries remain unimplemented. Machine-readable `--trace-candidates` output now exposes each nonempty proposal to the differential harness. The shared reading now prevents greeting-prefixed questions from preempting knowledge replies and clears stale kettle context when a fresh question names a different topic. Its normalization, categorization and reference coverage remain very limited. Then port safety precedence,
topic-specialist arbitration and topic inheritance tests.
Expand the current differential fixture corpus and record reference memory
transitions as well as replies and modules. Reimplement source modules one
family at a time and guard each new rule with native Flow tests.
The original repository is orders of magnitude larger than this initial slice.
