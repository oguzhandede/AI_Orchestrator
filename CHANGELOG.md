# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Progress bar support with tqdm (with graceful fallback)
- Semgrep rules for C#, Go, and Rust (18 new rules)
- GENERATOR_README.md documentation
- Open source project files (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT)
- GitHub issue and PR templates

### Changed
- Updated requirements.txt to include tqdm
- Improved exception handling (replaced bare except with specific exceptions)

### Fixed
- Line 191 and 303: Replaced bare `except:` with specific exception types

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Orchestrator pipeline for automated refactoring
- Project generator for creating new projects from scratch
- Gemini integration for analysis and planning
- Codex integration for code generation
- Semgrep integration for static analysis
- CLI arguments support
- JSON-based configuration
- Logging system
- Windows UTF-8 encoding support
- Dry run mode
- Skip steps functionality

### Included
- Python/Dart/JavaScript/TypeScript Semgrep rules
- Prompt templates for Gemini and Codex
- Example configurations
- Comprehensive README documentation

[Unreleased]: https://github.com/YOUR_USERNAME/ai-orchestrator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_USERNAME/ai-orchestrator/releases/tag/v1.0.0
