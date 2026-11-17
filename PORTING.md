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

**Current limits:** The Flow port stores only a fixed set of conversation attributes
and a turn count, not PyBot's complete transcript or deep structured memories.
PyBot's arbiter has many additional rules, especially safety precedence, topic
specificity, and refusal handling. Weightless does not implement those policies yet.

## Ported

| Upstream | Weightless | Status |
|---|---|---|
| `bot/runtime.py` | `src/main.flow` | Partial observable pipeline |
| `bot/modules/arbiter.py` | `prefer` | Priority and non-repeat tie-break only |
| `bot/modules/greeting.py` | `greeting_reply` | Tiny deterministic subset |
| `bot/modules/memory_store.py` | `Memory`, `observe`, `name_reply` | Name recall only |
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

CI checks Flow's native compiler and the representative CLI contracts.
Only passing CI on the target commit establishes successful execution.

## Next increments

Implement a complete `Candidate` collection with independent memory copies,
then port the upstream safety precedence and topic inheritance tests.
Build differential fixtures by running the original PyBot on a fixed corpus
and recording its `reply`, `module`, and state transitions. Reimplement
modules one family at a time and guard each new rule with native Flow tests.
The original repository is orders of magnitude larger than this initial slice.
