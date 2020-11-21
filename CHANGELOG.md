# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2020-11-20
### Added
- Support for setting a concurrency policy. The default policy is to wait for
the current worker to complete and immediately spawn a new one if the next start
time has lapsed. The other available policies are ``ConcurrencyPolic.SKIP`` which
will skip the lapsed schedule and ``ConcurrencyPolicy.ALLOW`` which will launch
a new worker concurrently if one is still running.
- MIT license.

## [0.0.1] - 2020-11-19
### Added
- Cron entrypoint that supports timezone-aware cron schedules.

[Unreleased]: https://github.com/bradshjg/nameko-cron/compare/0.1.0...HEAD
[0.1.0]: https://github.com/bradshjg/nameko-cron/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/bradshjg/nameko-cron/releases/tag/0.0.1
