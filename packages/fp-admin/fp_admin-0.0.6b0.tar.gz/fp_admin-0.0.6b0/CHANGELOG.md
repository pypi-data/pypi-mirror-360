# Changelog

All notable changes to fp-admin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CI/CD pipeline with separate jobs for lint, unit, integration, and e2e tests
- Parallel test execution with proper job dependencies
- Coverage reporting with XML, HTML, and Codecov integration
- Database setup with migrations for consistent test environment
- Test categorization with unit, integration, and e2e markers
- Pre-commit hooks configuration with mypy and flake8 exclusions for examples
- E2E test markers for proper test categorization
- Contributing guidelines with detailed development workflow
- Comprehensive README with installation, usage, and API reference
- Beta version warnings and development status indicators

### Changed
- Updated mypy configuration to use mypy.ini for better module name conflict handling
- Improved flake8 configuration to properly exclude examples directory
- Enhanced pre-commit configuration with latest mypy hook version
- Updated project documentation with beta status and UI framework references

### Fixed
- Module name conflicts in examples directory for mypy type checking
- Pre-commit hook exclusions for examples folder
- Test function return type annotations for mypy compliance
- Factory method naming consistency (multi_choice_select_field, multi_choice_tags_field)

## [0.0.3beta] - 2025-07-XX

### Added
- FieldView system with comprehensive field type support
- MultiChoicesField with tags, chips, and multi-select widgets
- Admin model configuration system
- CLI tools for project and database management
- Authentication system with user management
- File upload support with validation and thumbnails
- Rich text and markdown editor widgets
- Comprehensive validation system
- SQLModel integration for automatic admin generation
- FastAPI integration with automatic CRUD endpoints

### Changed
- Initial beta release with core functionality
- Basic admin interface generation
- Field type system implementation

### Fixed
- Core framework stability
- Basic field validation
- Database model integration

## [0.0.2beta] - 2025-06-01

### Added
- Basic field type system
- Simple admin interface
- Database model support
- CLI basic commands

### Changed
- Initial framework structure
- Basic FastAPI integration

## [0.0.1beta] - 2025-06-30

### Added
- Initial project setup
- Basic FastAPI admin framework structure
- Core field system foundation
- Basic CLI interface

---

## Version History

### Beta Versions
- **0.0.3beta**: Current version with comprehensive field system and admin interface
- **0.0.2beta**: Basic field types and admin interface
- **0.0.1beta**: Initial project setup and core structure

### Release Schedule
- **Beta Phase**: Active development with API changes possible
- **RC Phase**: Release candidates with stable APIs
- **Stable Release**: Production-ready version with stable APIs

---

## Migration Guide

### From 0.0.2beta to 0.0.3beta

#### Breaking Changes
- Field factory method names updated for consistency:
  - `MultiChoicesField.multi_select_field` → `MultiChoicesField.multi_choice_select_field`
  - `MultiChoicesField.tags_field` → `MultiChoicesField.multi_choice_tags_field`
  - `MultiChoicesField.chips_field` → `MultiChoicesField.multi_choice_chips_field`

#### New Features
- Enhanced field validation system
- File upload support with thumbnails
- Rich text and markdown editors
- Comprehensive CLI tools
- Authentication system

#### Deprecations
- Old factory method names are deprecated and will be removed in 1.0.0

---

## Contributing to Changelog

When adding entries to the changelog, please follow these guidelines:

### Entry Types
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Format
```markdown
### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

### Version Format
- **Unreleased**: For upcoming changes
- **[Version]**: For released versions
- **Date**: YYYY-MM-DD format

---

## Links

- [GitHub Repository](https://github.com/esmairi/fp-admin)
- [Documentation](https://github.com/esmairi/fp-admin)
- [Issues](https://github.com/esmairi/fp-admin/issues)
- [Discussions](https://github.com/esmairi/fp-admin/discussions)
