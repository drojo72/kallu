# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- M0: repository skeleton, `src/` layout, packaging, XDG paths, CI, layer-dependency tests.
- `kellu --version` and a basic `kellu doctor`.

### Changed
- Layer `stack` renamed to `projects` (discovery, stack detection, scopes).
- Architecture rule: packages are created when their milestone starts.
