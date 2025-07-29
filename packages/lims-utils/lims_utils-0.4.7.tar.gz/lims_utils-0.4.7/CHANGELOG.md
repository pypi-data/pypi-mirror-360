# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.7] - 2025-07-04

### Changed

- Updated table models

## [0.4.6] - 2025-05-13

### Changed

- Updated table models to schema version 4.7.0

## [0.4.5] - 2025-04-29

### Changed

- Updated table models to schema version 4.6.0

## [0.4.4] - 2025-02-24

### Changed

- Updated dependency versions

## [0.4.3] - 2025-02-20

### Changed

- Updated table models

## [0.4.2] - 2025-02-17

### Changed

- Allow emails to be null

## [0.4.1] - 2025-02-07

### Changed

- Updated table models to schema version 4.4.0

## [0.4.0] - 2025-01-31

### Added

- Include email in user model

## [0.3.0] - 2025-01-24

### Changed

- Make logging URL ignores configurable

## Added

- Provide string representation for proposal references

## [0.2.6] - 2024-12-18

### Changed

- Updated table models to schema version 4.3.0

## [0.2.5] - 2024-11-11

### Changed

- Update dependency versions

## [0.2.4] - 2024-11-08

### Changed

- Update dependency versions

## [0.2.3] - 2024-09-05

### Changed

- Updated table models to schema version 4.2.1

## [0.2.2] - 2024-06-27

### Changed

- Update dependency versions

## [0.2.1] - 2024-04-05

### Changed

- Updated table models to schema version 4.1.0

## [0.2.0] - 2024-02-14

### Added

- `ProposalReference` model and `parse_proposal`, for parsing proposal reference strings
- `Database()` now exposes `paginate`, for inserting pagination into queries, and `fast_count`, for counting total items rapidly
- `Settings()`, which provides a base settings model that reads from JSON files

### Changed

- Updated table models

## [0.1.2] - 2024-02-08

### Removed

- Unused dependencies (MySQL related dependencies)

### Changed

- Updated table models
