# CHANGELOG

<!-- version list -->

## v0.2.0-alpha.8 (2025-07-07)

### Features

- Various updates to enable hosted/shared use cases
  ([#112](https://github.com/aptible/daydream/pull/112),
  [`784b95f`](https://github.com/aptible/daydream/commit/784b95f24389e189d1d884bbe72b8edc5c7f3ce0))


## v0.2.0-alpha.7 (2025-06-27)

### Features

- Basic Kubernetes integration ([#101](https://github.com/aptible/daydream/pull/101),
  [`c4cb1a1`](https://github.com/aptible/daydream/commit/c4cb1a1ea29597322a001c8e7b2e96f1e59f3864))


## v0.2.0-alpha.6 (2025-06-26)

### Features

- Improve Aptible logs reliability ([#44](https://github.com/aptible/daydream/pull/44),
  [`4b61269`](https://github.com/aptible/daydream/commit/4b61269670d697871ef0743699aedab2e1e5a906))


## v0.2.0-alpha.5 (2025-06-24)

### Bug Fixes

- Plugin context was not being assigned to cached plugins
  ([#100](https://github.com/aptible/daydream/pull/100),
  [`23d69ba`](https://github.com/aptible/daydream/commit/23d69ba0213e38deb175f459a83be05fd3199a5c))


## v0.2.0-alpha.4 (2025-06-24)

### Bug Fixes

- Several minor issues with `daydream configure`
  ([#99](https://github.com/aptible/daydream/pull/99),
  [`5d895b0`](https://github.com/aptible/daydream/commit/5d895b0c2e602212d066f5dfff0bbc2d64ff2c10))


## v0.2.0-alpha.3 (2025-06-17)

### Bug Fixes

- Stage the uv.lock changes for released versions
  ([#95](https://github.com/aptible/daydream/pull/95),
  [`5e80e60`](https://github.com/aptible/daydream/commit/5e80e60c0c4b701af57bbcbd7a93abdb9cf883a3))


## v0.2.0-alpha.2 (2025-06-16)

### Features

- **aws**: Add support for importing S3 buckets into the knowledge graph [SC-33583] [SC-33589]
  ([#80](https://github.com/aptible/daydream/pull/80),
  [`1aa9fed`](https://github.com/aptible/daydream/commit/1aa9fed03cc0f21a08f8ac757885fe5721dd0aff))


## v0.2.0-alpha.1 (2025-06-16)

### Bug Fixes

- Infinite loop, plus bump version ([#77](https://github.com/aptible/daydream/pull/77),
  [`318e43a`](https://github.com/aptible/daydream/commit/318e43aee5ba8c396a042e8ef327e9822eb281da))

- Uv lock oops ([#76](https://github.com/aptible/daydream/pull/76),
  [`1593fae`](https://github.com/aptible/daydream/commit/1593fae034ef96f0db8cd6c44aaa0a2a9924c009))

### Documentation

- Update readme [SC-33559] ([#58](https://github.com/aptible/daydream/pull/58),
  [`80b6962`](https://github.com/aptible/daydream/commit/80b696213892fad7538ba4870ac7dc92ed2497c0))

### Features

- `daydream configure` command [SC-33566] ([#72](https://github.com/aptible/daydream/pull/72),
  [`195b0b3`](https://github.com/aptible/daydream/commit/195b0b3913bffc8faf1baf1d5e97941ffe355cdd))

- `daydream version` ([#78](https://github.com/aptible/daydream/pull/78),
  [`62f77a2`](https://github.com/aptible/daydream/commit/62f77a2369d5259e647bec4a4ef7b5e248732ca9))

- **integrations**: Implement a basic Datadog plugin
  ([#46](https://github.com/aptible/daydream/pull/46),
  [`309ebc9`](https://github.com/aptible/daydream/commit/309ebc90a9ebf5c28865aeaa40c0d771bd76d840))

- **meta**: Automate releases and changelog generation with `python-semantic-release`
  ([#71](https://github.com/aptible/daydream/pull/71),
  [`da63c2c`](https://github.com/aptible/daydream/commit/da63c2c31b6663277c58688e353a1357536376af))


## v0.1.0 (2025-06-02)

- Initial Release
