## [1.10.1](https://github.com/mivek/python-metar-taf-parser/compare/v1.10.0...v1.10.1) (2025-07-06)


### Bug Fixes

* remove the license classifiers ([4cba100](https://github.com/mivek/python-metar-taf-parser/commit/4cba1002816cf969ce2f353f892f119dc0520ee3))
* update license in pyproject.toml ([7b12a13](https://github.com/mivek/python-metar-taf-parser/commit/7b12a13cc1d41ff7f6a72730c29f15548df48c9e))

# Change Log 

## [1.9.0] - 2024-05-19

### Added

- When information about a runway is incomplete in a METAR, a `ParseError` is raised instead of `ValueError`.

## [1.8.2] - 2024-01-14

### Fixed

- Fix the calm wind regex to prevent parsing error with visibility.
- Fix single quotes in French translations.

## [1.8.0] - 2024-01-04

### Added

- Support of Russian locale thanks to [@a184ot](https://github.com/a184ot)

### Fixed

- Reformat object representation. Removed breaking lines in formatting. 

## [1.7.1] - 2023-12-09

### Fixed

- Parsing of `WeatherCondition` tokens with recent (`RE`) intensity.

## [1.7.0] - 2023-08-20

### Added

- `Wind` and `WindShear` elements now supports 3 digits in gusts part

## [1.6.5] - 2023-08-06

### Added

- Implementation of method `__repr__` on class of module `model`.

### Fixed

- Use `getlocale()` instead of `getdefaultlocale()`

## [1.6.4] - 2023-06-23

### Fixed

- Parsing of `TAF` with stations starting by `FM`.

## [1.6.3] - 2023-03-12

### Fixed

- Parsing of token `0000KT` no longer causes an error.

## [1.6.2] - 2023-01-29

### Fixed

- Parsing of Runway does not fail if thickness and braking capacity are not in the enum.

### Changed

- RunwayInfo properties `thickness` and `braking_capacity` type is changed to string. Enums `DepositThickness` and `DepositBreakingCapacity` are removed.

## [1.6.1] - 2022-12-20

### Added

- Implement parsing of deposit on a Runway. Properties `indicator`, `deposit_type`, `coverage`, `thickness`, `braking_capacity`.

## [1.6.0] - 2022-12-04

### Added

- Support for unknown height and unknown types in cloud elements. Clouds elements with `///` are no longer ignored.
- `Turbulence` and `Icing` elements are available in `TAF` and `TAFTrend` objects. The new properties are `turbulence` and `icings`.

### Fixed

- WeatherConditions are now added to the list only if the entire token was parsed. This prevents false positive matches.
- Phenomenons in WeatherConditions are now listed in the same order they appear in the token.
- Cloud regex matches the cloud type part only of the height is present. Tokens made of 6 letters do not match the regex anymore.

## [1.5.0] - 2022-07-17

### Added

- Added `flags` property to `AbstractWeatherCode`. This property is a set holding flags: AUTO, AMD, CNL, NIL and COR. Properties `auto`, `amendment`, `nil`, `canceled` and `corrected` are also available.
- Added new translations.

## [1.4.1] - 2022-05-29

### Fixed

- Parsing of visibility in miles having indication: `P` for greater than and `M` for less than.

## [1.4.0] - 2022-04-20

### Added

- Added `WeatherChangeType.INTER` for TAFTrend.
- Added methods to retrieve Taf trends by `WeatherChangeType`: taf.becmgs, taf.fms, taf.inters, taf.probs and taf.tempos
- Turkish translation
- Added `PrecipitationBegCommand` and `PrecipitationEndCommand` in remark parsing.

### Fixed

- Parsing of remarks added Phenomenon.FC to the list of WeatherConditions when the remarks contained `FCST`

## [1.3.0] - 2021-10-05

### Added

- i18n support for simplified Chinese locale
- Completed remarks parsing

## [1.2.0] - 2021-05-04

### Added

- i18n support for Italian locale

## [1.1.1] - 2021-04-20

### Fixed

-   Added packages source directory in `setup.cfg` to fix deployment.   

## [1.1.0] - 2021-03-20

### Added

-   i18n module to support English, French, German and Polish locales.
-   Remarks are now parsed and converted in a readable sentence.
The value is stored in properties `remark` and `remarks`. The `remarks` property contains an element for each remark or
    token. The `remark` property contains the whole decoded remarks in a sentence.

-   Makefile and `pyproject.toml`.
    
-   Coverage measurement.

### Changed

-   The packaging now uses setuptools and build modules instead of `setup.py`.


## [1.0.1] - 2021-02-28

### Changed

-   Removed the regex search from the weatherCondition parsing.
Replaced by a single string search.
  
### Fixed

-   Added `^` (start of string) at the beginning of the wind regex.

## [1.0.0] - 2020-10-18

### Added

-   First version of the MetarParser and the TAFParser.
-   Github actions to handle commits, release and 

### Changed

### Fixed
