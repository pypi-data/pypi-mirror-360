# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.10] - 2025-07-07

### Fixed

- Issue where windows wheels couldn't be installed.


## [0.4.9] - 2025-06-30

### Changed

- ADD: ECC checking and correction for UPAC96 data.


## [0.4.8] - 2025-06-20

### Changed

- Algorithm for calculating time axis offset now uses timing field instead of window labels to determine offset.


## [0.4.7] - 2025-06-16

### Fixed

- The HDSoCv1 parser only checked the first two samples of a window to determine whether to include the packages. This caused problems at higher input levels when the data rolls over to zero.


## [0.4.6] - 2025-05-30

### Fixed

- HDSoCv2 parsing bug where the package length was set to the wrong value, this caused the parser to return an MissingDataError
- Parse HDSOCv2 data using HDSOCv1 parser with correct parameters
- CSV exporter now skips writing channels that have bad data

### Added

- Added a new PackageEmpty Error type where an entire package is missing.


## [0.4.5] - 2024-08-19

### Fixed

- AARDVARCv3 now baes event num channels on maximum channels instead of num parsed channels. Fixing issue with channel numbering.


## [0.4.4] - 2024-04-09

### Added

- Pedestals CSV export

## [0.4.3] - 2024-04-09

### Fixed

- Typo in Be/Le code in utils.rs caused UPAC96 parsing to be wrong.


## [0.4.2] - 2024-03-27

### Added

- NaluAcq Error types for IO errors.
- Parser for ASoCv3S events.

## [0.4.1] - 2023-08-31

### Changed

- Utilities for combining u8s into u16s are now iterator extensions.
- Some I/O errors now have better descriptions
- Limited precision of pedestals-corrected CSV data to 1 decimal place to reduce file size.

### Fixed

- Python bindings for CSV export held the GIL unnecessarily long, blocking other Python threads.


## [0.4.0] - 2023-08-27

### Added

- UPAC96 data format.
- UDC16 data format.

## [0.3.1] - 2023-08-10

### Fixed

- Data was indexed improperly by the CSV exporter. Data with disabled channels caused panics.

## [0.3.0] - 2023-08-09

### Added

- Python bindings

## [0.2.0] - 2023-07-25

### Added

- Parser for TRBHMv1 events.

## [0.1.0] - 2023-07-25

Initial release.

### Added

-  Parsers for HDSoCv1 and AARDVARCv3 events.
-  CSV export.
