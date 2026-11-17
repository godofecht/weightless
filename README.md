# Weightless

A native [Flow](https://github.com/flooooooooooow/flow) reimplementation of [Hugging Face's PyBot](https://github.com/huggingface/pybot).

This repository is being built incrementally. The source project contains roughly 640,000 lines of Python across its rule-based understanding, memory, knowledge, composition, and module arbitration layers. This repository is **not yet a feature-complete replacement**.

Development proceeds by porting the observable runtime contract, adding focused deterministic regression tests, and translating response modules and data in traceable batches. Flow's portable-C backend is the initial target.

Upstream PyBot is Apache-2.0 licensed; derived material must retain attribution and license notices. See the development branch for the first implementation.
