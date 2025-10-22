# Changelog

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
