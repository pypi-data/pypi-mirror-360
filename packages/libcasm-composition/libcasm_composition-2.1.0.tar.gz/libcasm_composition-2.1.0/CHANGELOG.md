# Changelog

All notable changes to `libcasm-composition` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-07

### Changed

- Build Linux wheels using manylinux_2_28 (previously manylinux2014)


## [2.0.0] - 2025-05-02

### Changed

- Build for Python 3.13
- Restrict requires-python to ">=3.9,<3.14"
- Run CI tests using Python 3.13
- Build MacOS arm64 wheels using MacOS 15
- Build Linux wheels using Ubuntu 24.04


## [2.0a4] - 2024-08-18

### Added

- Added range checks for CompositionConverter methods taking a parametric composition axis index
- Added FormationEnergyCalculator
- Added make_standard_axes, make_normalized_origin_and_end_members
- Added pretty_json, print_axes_summary, and print_axes_table
- Added methods to CompositionCalculator: allowed_occs, vacancy_names, from_dict, to_dict, __repr__
- Added CompositionConverter.__repr__
- Added include_va option to CompositionConverter.param_chem_pot_formula to allow printing formulas with or without "chem_pot(Va)"

### Fixed

- Fixed CompositionConverter.origin_formula, which was calling the wrong method
- Removed extra space in CompositionConverter.param_chem_pot_formula with leading negative term


## [2.0a3] - 2024-07-12

### Changed

- Wheels compiled with numpy>=2.0.0


## [2.0a2] - 2024-03-13

### Added

- Build python3.12 wheels

### Changed

- Update libcasm-global dependency to >=2.0.4
- Use index_to_kcombination and nchoosek from libcasm-global 2.0.4

## [2.0a1] - 2023-08-17

This release separates out casm/composition from CASM v1. It creates a Python package, libcasm.composition, that enables using casm/composition and may be installed via pip install, using scikit-build, CMake, and pybind11. This release also includes API documentation for using libcasm.composition, built using Sphinx.

### Added

- Added JSON IO for composition::CompositionConverter
- Added Python package libcasm.composition to use CASM composition converter and calculation methods.
- Added scikit-build, CMake, and pybind11 build process
- Added GitHub Actions for unit testing
- Added GitHub Action build_wheels.yml for Python x86_64 wheel building using cibuildwheel
- Added Cirrus-CI .cirrus.yml for Python aarch64 and arm64 wheel building using cibuildwheel
- Added Python documentation


### Removed

- Removed autotools build process
- Removed boost dependencies
