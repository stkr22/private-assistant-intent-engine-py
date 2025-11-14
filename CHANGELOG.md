# Changelog

## [1.0.3](https://github.com/stkr22/private-assistant-intent-engine-py/compare/v1.0.2...v1.0.3) (2025-11-14)


### Bug Fixes

* :bug: recognize temperature units with °C and °F symbols [AI] ([8b87569](https://github.com/stkr22/private-assistant-intent-engine-py/commit/8b87569caf3cd03d72ebc9002cc4d45ebadbd75c))
* :bug: recognize temperature units with °C and °F symbols [AI] ([dd3ec8c](https://github.com/stkr22/private-assistant-intent-engine-py/commit/dd3ec8cf0c056d2b3ecedf34182594ecf346174c))
* :bug: update license to GPL-3.0-only in pyproject.toml ([eaf8102](https://github.com/stkr22/private-assistant-intent-engine-py/commit/eaf8102483896bbb70c48e2df02a8f0881ccabe8))

## [1.0.2](https://github.com/stkr22/private-assistant-intent-engine-py/compare/v1.0.1...v1.0.2) (2025-10-24)


### Bug Fixes

* :bug: extract all matching devices instead of only first match [AI] ([e3a81cd](https://github.com/stkr22/private-assistant-intent-engine-py/commit/e3a81cda4845b2432e88df93abdf7db199c37c1d))
* :bug: extract all matching devices instead of only first match [AI] ([86cb71c](https://github.com/stkr22/private-assistant-intent-engine-py/commit/86cb71cae565a2e45b122da87d2c5b4e52943c4e))

## [1.0.1](https://github.com/stkr22/private-assistant-intent-engine-py/compare/v1.0.0...v1.0.1) (2025-10-23)


### Bug Fixes

* :bug: resolve linter and type checker issues [AI] ([8bb1c28](https://github.com/stkr22/private-assistant-intent-engine-py/commit/8bb1c28a9db8138be088bd6131154144a94b5fdc))

## [1.0.0](https://github.com/stkr22/private-assistant-intent-engine-py/compare/v0.5.0...v1.0.0) (2025-10-22)


### ⚠ BREAKING CHANGES

* Replaces analyze_text() with classify_intent() and changes output format from verbs/nouns to structured ClassifiedIntent with entities.

### Features

* :sparkles: implement hybrid intent classification system [AI] ([809f719](https://github.com/stkr22/private-assistant-intent-engine-py/commit/809f7193637a6f574db7f9a5a2664b78d1069575))


### Bug Fixes

* :bug: add explicit type annotations to fix mypy errors [AI] ([484846a](https://github.com/stkr22/private-assistant-intent-engine-py/commit/484846a26ecbddc9edf4298c083b1e540edc820c))
* :bug: add graceful error handling for JSON parsing and text analysis failures [AI] ([b616b24](https://github.com/stkr22/private-assistant-intent-engine-py/commit/b616b2406693884955857bef6539329a971aaaeb)), closes [#37](https://github.com/stkr22/private-assistant-intent-engine-py/issues/37)
* Add graceful error handling for JSON parsing and text analysis failures ([55407ee](https://github.com/stkr22/private-assistant-intent-engine-py/commit/55407ee60ffca7dfab63df41330da4a44a2f9bc8))
* update dependency specification for private-assistant-commons to include database extras ([33d688d](https://github.com/stkr22/private-assistant-intent-engine-py/commit/33d688de3415585a93db369a470ae4e3447b5522))


### Documentation

* :memo: update documentation for intent classification system [AI] ([ba8e633](https://github.com/stkr22/private-assistant-intent-engine-py/commit/ba8e633db627968e76cc44e11841bbbbb9ba6ec4))

## [0.5.0](https://github.com/stkr22/private-assistant-intent-engine-py/compare/v0.4.2...v0.5.0) (2025-08-14)


### Features

* :sparkles: enhance configuration validation and module exports ([53c316c](https://github.com/stkr22/private-assistant-intent-engine-py/commit/53c316c913a268cb1abab55fafd16e25e5084b07))
* enable automerge ([b3bda5b](https://github.com/stkr22/private-assistant-intent-engine-py/commit/b3bda5b5de20e364704574b21b8e5ee22ec7c72e))
* enable automerge ([59d75a2](https://github.com/stkr22/private-assistant-intent-engine-py/commit/59d75a2cfc63aad20562749028f07235b9354abe))


### Bug Fixes

* :white_check_mark: resolve linting issues in test files ([1829d1a](https://github.com/stkr22/private-assistant-intent-engine-py/commit/1829d1ab88683ecb489406d8a0cb5c0b5e80fea7))
* fixing missing dependency ([6eefe64](https://github.com/stkr22/private-assistant-intent-engine-py/commit/6eefe6471269b4347547d71ec830bfd86ed3d585))


### Documentation

* :memo: add comprehensive docstrings to core engine components ([71ae37a](https://github.com/stkr22/private-assistant-intent-engine-py/commit/71ae37aa46e3b9867908d3abfe085812e2188161))
* :memo: add comprehensive project documentation ([70c69e1](https://github.com/stkr22/private-assistant-intent-engine-py/commit/70c69e1f09b38fc6012349556e8ac550baa96633))
* :memo: document text analysis utilities with detailed examples ([7d5407e](https://github.com/stkr22/private-assistant-intent-engine-py/commit/7d5407e1e6e5fbdf7f87312cb07f5f7d6d223953))
