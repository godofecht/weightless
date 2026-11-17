# Weightless

A native [Flow](https://github.com/flooooooooooow/flow) reimplementation of [Hugging Face's PyBot](https://github.com/huggingface/pybot). No model, no weights, no training.

**Status: initial implementation, not a complete PyBot replacement.** PyBot consists of approximately 640k lines of Python. Weightless currently implements the runtime pipeline and a small set of deterministic rules. It does not reproduce PyBot's benchmark results or safety response coverage.

## Run

Install [Flow 2.x](https://github.com/flooooooooooow/flow), then run:

```sh
flow run src/main.flow -- --self-test
flow run src/main.flow -- -p "hi, i'm Sam"
printf "hi, i'm Sam\nwhat's my name?\n" | flow run src/main.flow
flow run src/main.flow
```

The Flow code uses the production portable-C backend and the Flow standard library. No Python interpreter or model runtime is used by Weightless.

## Implemented

The transcript now grows dynamically rather than truncating after 32 turns. Source-backed knowledge rows are loaded by a native Flow parser from `data/knowledge.tsv`. Set `WEIGHTLESS_KNOWLEDGE` to an explicit corpus path when running outside the checkout; use `--knowledge-stats` to inspect the loaded row count. The core sequence matches the structural contract in PyBot's `bot/runtime.py`: first observe the user message, then generate responder proposals against isolated memory values, pick the highest-priority candidate from a dynamically sized set, commit only the selected state, run the first post-selection name-correction hook, and record the turn. A shared Flow line reading now identifies basic question kinds, answer shapes, and topic follow-ups before responders propose answers, avoiding a greeting prefix stealing a real question or a stale kettle subject answering an unrelated train question. An immutable attributed fact log now remembers the limited set of recognized self and relative names, jobs, and cities, including revisions with source turn numbers. Current responders cover greetings, introductions and name recall, a kettle descaling example, a follow-up on its timing, a simple factual answer, and a fallback. The terminal supports `-p`, piped input, interactive mode, `/reset`, `/help`, `/exit`, and module tracing with `-v`. `--trace-candidates` emits each proposed response plus a machine-readable winner, allowing side-by-side checks against upstream PyBot's candidate list. The `-s` flag is accepted but does not alter deterministic replies.

## Port roadmap and verification

See [PORTING.md](PORTING.md) for exact source-to-target mapping, unported components, parity requirements, and next implementation steps.

The [native Flow CI workflow](.github/workflows/flow.yml) checks the compiler and basic CLI scenarios. The source also has a `--self-test` mode; successful CI, not merely committed tests, is evidence that the compiler executes this revision.

## Origin and licence

Upstream: [huggingface/pybot](https://github.com/huggingface/pybot), Apache-2.0. The runtime design is adapted from upstream, with attribution in [NOTICE](NOTICE) and the upstream [LICENSE](LICENSE) reproduced. This is an independent Flow rewrite, not an official Hugging Face release.
