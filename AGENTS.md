# Weightless autonomous implementation contract

## Mission

Rewrite [Hugging Face PyBot](https://github.com/huggingface/pybot) in native
[Flow](https://github.com/flooooooooooow/flow). The objective is genuine
behavioral coverage, not a file-count, source-byte or line-count milestone.
Use Flow's self-hosted portable-C backend as the first runtime qualification
target. Do not embed Python, invoke PyBot, load models or use weights during
Weightless's normal execution.

**Upstream baseline:** `7d63c7fbebb44c7e466e5c8b5c1f341ab767929e`
(PyBot `main` on 17 November 2026). Update the pin deliberately with
new differential evidence if upstream changes.

**Primary tracking:** [issue #2](https://github.com/godofecht/weightless/issues/2).
**Per-file inventory:** [docs/generated/port-status.tsv](docs/generated/port-status.tsv).
**System contract:** [PORTING.md](PORTING.md).
**Inventory analysis:** [docs/upstream-inventory.md](docs/upstream-inventory.md).

## Autonomous decision procedure

At the beginning of each session, inspect `main`, open PRs, failing GitHub
Actions, issue #2, the recent commits, and the port-status ledger. Never
recreate or overwrite changes from another worker. Resume the highest-value
incomplete work rather than restarting the project or writing another plan.

Correct red CI and failing regression fixtures before taking on unrelated
features. If CI is clean, choose the smallest unblocked *vertical slice*
that makes an actual PyBot behavior available in Flow. Prefer finishing
the runtime's contract and shared understanding/memory/arbiter infrastructure
before blindly transcribing large lookup tables.

Do not leave a PR in draft or unmerged simply because no other tasks are
obvious. Merge a coherent PR when its current exact SHA has green native and
differential CI, the diff is reviewable and the base is mergeable. Never
merge an unverified or red commit. Continue to the next slice.

## Critical semantic invariants

Read the original `bot/runtime.py` and `bot/modules/arbiter.py` rather
than copying descriptions alone. The reference runtime performs an observer
phase over shared state, then requests replies from all responding modules,
each against its own deep copy of mutable state (the shared history is
read-only). It arbitrates among proposals, commits *only* the winning
responder's state, executes `after` callbacks, and then appends a structured
turn to its unbounded transcript. A responder failure cannot crash a turn.
Tie-breaking and higher-priority claims are important, but the actual arbiter
also includes specialist topic fit, safety precedence and
context-specific vetoes. Do not generalize an observed special case into
an incorrect global priority rule.

The understanding engine is not a string-search utility. It normalizes
text, classifies the line, recovers topic and pronoun referents, and
supplies a structured reading for later responders. Its output must remain
stable across clients. The memory store retains facts and their subjects,
including user versus other people, corrections, chronology and provenance.
A bare follow-up must be interpreted against the real answer in hand,
not whatever word appears in a stale topic field.

The knowledge layer is large and mostly declarative. Preserve separate
groups of matching keys, explicit ask gates, negative conditions and
priority/bias when porting a source entry. The current Flow matcher lacks
most of PyBot's typo recovery, morphology and global arbitration semantics.
Do not mark a source file complete just because its reply strings are
present in `data/knowledge.tsv`.

Safety response logic requires its own regression suite and must retain
priority over lower-band small talk. Do not claim general-purpose safety
parity or make performance claims without measurement.

## Workstreams and recommended order

1. **Runtime and observable CLI:** dynamic candidate collections, isolated
   responder snapshots, after-hooks, failure isolation, transcript and
   state reset, full CLI flags, seeded selection and timing.
2. **Understanding:** normalization, question kind, intent, topics, entity
   references and follow-up classification, each validated by fixtures.
3. **Memory:** attribution of facts, user/other distinction, corrections,
   recall, name and pronoun resolution, active topic, plans and
   conversational history.
4. **Arbitration:** specialist preference, mandatory safety precedence,
   negative preference filtering, repetition control and explicit claims.
5. **Knowledge and composition:** native Flow-indexed and source-attributed
   tables, sentence shaping, follow-up continuations and reply variants.
6. **Completion:** fill the remaining module families, run differential
   coverage for every one, qualify Linux/macOS, and publish bench results
   with the source and settings identified.

These tracks have dependencies. Work within a track may be parallelized
only when it is demonstrably non-overlapping.

## Evidence protocol

Every source-derived change must identify the upstream path(s) and commit.
Add positive, negative, and stateful multi-turn tests that exercise the
behavior *through the Flow entry point*. For a matcher, include ambiguous
phrases and exclusion tests. For memory, include corrections, alternate
subjects, reset and at least one prior topic. For the arbiter, compare all
candidates, not only the final reply.

The pipeline is:

```sh
flow run src/main.flow -- --self-test
flow run src/main.flow -- -p "hello"
flow run src/main.flow -- --knowledge-stats
```

`flow run` uses the self-hosted compiler; it must actually compile and
execute. The GitHub Actions workflow also runs a pinned PyBot reference
through `ci/compare_reference.py` on
`fixtures/differential.json`. That external *test oracle* may use Python;
the native product may not. The comparison reports exact reply and module
matches separately. Green CI means the checks ran, not that unmatched
outputs are correct. Expand the fixture corpus and improve measured coverage
without deleting challenging tests.

When a Flow language feature seems attractive, inspect its real compiler,
fixtures and language specification on the current Flow repository.
Do not invent library methods or assume a designed feature exists.
For modules, favor documented package-relative imports and exported types.
For memory layout, prefer verified `sizeof<T>()` and tested runtime APIs.

## Updating coverage

The source ledger includes all 528 files under upstream `bot/`
and the separate `pybot.py` wrapper. Status values are
`not-started`, `partial` and `complete`.
Change `partial` to `complete` only after all observable public
functions and relevant interactions of that source file have a Flow
implementation and tests. Cite the checked behavior in the PR body,
and update the target-path column when a file moves. Never turn a module
into a misleading single high-level stub to claim completion.

After each increment, update `PORTING.md` where relevant, update
the exact ledger rows, and report the commit, test commands/results,
differential changes, PR and remaining limitations. Keep source
attribution and Apache-2.0 requirements in `NOTICE` and `LICENSE`.

## Completion criteria

Issue #2 remains open until the full agreed public behavior of PyBot is
ported to Flow, every upstream module is accounted for, critical safety
and state transitions pass differential tests, any intentional differences
are explicitly documented, and the finished runtime is qualified from
a clean native release build. Raw line count and demo answers are not
completion criteria. Do not silently redefine this bar to finish early.
