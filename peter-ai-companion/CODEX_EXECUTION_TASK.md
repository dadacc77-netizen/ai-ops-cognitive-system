# Codex Execution Task｜Peter AI Companion V1.0 RC1

## Objective

Validate, harden and prepare the `Peter AI Companion｜雙模式語音陪跑` contract package for deployment as a model-independent policy layer.

## Required actions

1. Run `python tools/run_all.py`.
2. Do not weaken these hard rules:
   - Voice Companion is the default interaction mode.
   - Quiet Slow mode provides at most one primary next step.
   - Planning mode is the default execution mode.
   - Formal video generation requires exact trigger `【正式生成影片】` plus all three gates.
   - Cloud visibility defaults to private.
   - Supervisor access requires explicit consent.
   - Credentials and private keys trigger Safety Stop.
3. Review deterministic routing for false positives and false negatives.
4. Add edge-case tests without changing approved user-facing terminology.
5. Keep tests dependency-free unless a dependency is clearly justified.
6. Generate the release ZIP, SHA-256 and `release/CODEX_EXECUTION_REPORT.md`.
7. Do not add secrets, real cloud links, private conversations or Peter's private business data.

## Acceptance

- All tests pass.
- No forbidden marketing claim is introduced.
- Mode layers remain separate.
- No video-generation bypass exists.
- No supervisor sharing without explicit consent.
- Release artifacts are reproducible.
