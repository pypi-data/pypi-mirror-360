# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.1.0] - 2025-07-04

### Added
- Allow default values in class definitions.
- `Union` and `Optional` types are now supported, allowing for more flexible type definitions.

### Changed
- `dict_to_object` function no longer requires target class to have a parameterless (or with default values) constructor.
- An error with a meaningful message is now raised if an attribute is missing from source dictionary and has no default value.

## [1.0.0] - 2025-02-09

### Added
- Initial release with the `dict_to_object` function, enabling conversion of dictionaries to objects with type hints.
- Type safety checks for nested collections and custom class attributes.
- Support for handling and validating `Literal` types.
- Error handling for mismatched types, unsupported types (e.g., `Union`, `Optional`), and invalid literal values.
