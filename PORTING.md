# Porting contract

Upstream: https://github.com/huggingface/pybot
Upstream interface: `bot/runtime.py`
Target language: https://github.com/flooooooooooow/flow
Target backend: Flow's self-hosted C backend

## Invariants adopted from PyBot

1. Observe the input into shared conversation state before routing.
2. Let independent responders propose replies without mutating the committed state.
3. Select a winning candidate by priority, with non-repetition used only as a tie-breaker.
4. Commit only the winner's state, then append the turn to conversation history.
5. Return a non-empty fallback when no responder matches.
6. Keep state across piped lines; reset it on `/reset` in interactive mode.

**Current limits:** The Flow port stores a fixed set of conversation attributes
and the all structured turns in a dynamically growing native Flow memory buffer. The buffer is freed when the conversation resets or exits. This still is not PyBot's complete structured memory model. Unlike PyBot,
it has no general-purpose dictionary memory, persistent journal or full transcript.
PyBot's arbiter has many additional rules, especially safety precedence, topic
specificity, and refusal handling. Weightless does not implement those policies yet.

## Ported

| Upstream | Weightless | Status |
|---|---|---|
| `bot/runtime.py` | `src/main.flow` | Partial observable pipeline, four candidate slots, dynamically growing transcript |
| `bot/modules/arbiter.py` | `choose`, `prefer` | Four candidate slots, priority and non-repeat tie-break only |
| `bot/modules/greeting.py` | `greeting_reply` | Tiny deterministic subset |
| `bot/modules/memory_store.py` | `Memory`, `observe`, `name_reply`, `recall_reply` | Name and latest-turn recall only |
| `bot/compose/*`, `bot/knowledge/*` | `knowledge_reply` | Three example answer families |
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

CI checks Flow's native compiler, fourteen runtime regression scenarios and representative CLI contracts.
A pull-request-only differential job checks 22 fixture turns against upstream PyBot
at pinned commit `7d63c7fbebb44c7e466e5c8b5c1f341ab767929e`.
The original Python runtime is used only as the external reference test oracle.
The JSON report stores both answers, winning modules and exact-match flags;
mismatches are expected until the port is complete. Do not interpret a
green diagnostic job as behavioural equivalence. The reference dataset lives in
`fixtures/differential.json`, the runner in `ci/compare_reference.py`.
Only passing CI on the target commit establishes successful execution.

## Next increments

Replace the four-slot candidate array with dynamically sized candidate sets and
isolated snapshots; implement after-hooks, robust
fallbacks, and per-module failure isolation. Then port safety precedence,
topic-specialist arbitration and topic inheritance tests.
Expand the current differential fixture corpus and record reference memory
transitions as well as replies and modules. Reimplement source modules one
family at a time and guard each new rule with native Flow tests.
The original repository is orders of magnitude larger than this initial slice.
