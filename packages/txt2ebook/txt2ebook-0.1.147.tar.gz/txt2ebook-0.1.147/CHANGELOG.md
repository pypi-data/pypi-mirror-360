# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## [Unreleased]

## v0.1.147 (2025-07-06)

- Bump deps and `pre-commit` hook for `ruff`
- Enable `ruff format` and code format
- Resync `uv.lock` file during release `nox` job

## v0.1.146 (2025-06-29)

- Bump deps and `pre-commit` hook for `ruff`
- Fix `massage` subcommand did not retain the original content
- Fix missing regex for translator for en language
- Move fixture to the right file
- Update help message in readme
- Update installation step using `uv` tool
- Update project classifier keywords

## v0.1.145 (2025-06-22)

- Bump deps and `pre-commit` hooks
- Clear previous release builds before releasing
- Remove other lint tools from `pre-commit`
- Update translations

## v0.1.144 (2025-06-15)

- Bump deps
- Bump `pre-commit` hook for `ruff`
- Fix deps upgrade and relax deps requirements
- Fix incorrect type in args
- Fix missing langconf to parser class
- Resolve `uv` not using nox's `venv` warning

## v0.1.143 (2025-06-08)

- Add `ruff` to `pre-commit` hook
- Bump deps
- Bump `pre-commit` deps to the right version
- No need to run `pre-commit` under active session
- Skip `uv.lock` from `codespell`

## v0.1.142 (2025-06-01)

- Bump deps
- Bump `pre-commit` hook for `mypy`
- Handle empty content when parsing
- Update test to use `parse` subcommand
- Use pre-commit in `venv` in `deps` `nox` job

## v0.1.141 (2025-05-25)

- Bump and sort deps
- Switch `venv` backend to `uv` in `nox`

## v0.1.140 (2025-05-18)

- Bump deps
- Bump local editable installation
- Remove duplicate `pre-commit` config item
- Remove unused `cjkwrap` import
- Remove unused field import

## v0.1.139 (2025-05-11)

- Bump deps
- Bump typst to 0.13.2
- Ensure indentation for first paragraph for typ doc
- Refactor content tokenization to handle metadata blocks correctly.
- Remove field() from Parser attributes

## v0.1.138 (2025-05-04)

- Bump deps
- Migrate `poetry` to `uv`
- Rename subcommand test files to convention

## v0.1.137 (2025-04-27)

- Bump deps
- Ensure subcommand is required and assign to a variable
- Fix newline in -ff option not rendered
- Migrate `--epub-template` test case
- Refactor and validate subcommand

## v0.1.136 (2025-04-20)

- Bump deps
- Code format
- Rename authors to translators in parser
- Reword prompt for `release` nox job

## v0.1.135 (2025-04-13)

- Bump deps
- Group build and publish package commands together
- Prompt to publish package in release `nox` job
- Remove unused `_args` parameter from build_parser function

## v0.1.134 (2025-04-06)

- Build release after release nox job
- Bump deps and `pre-commit` hook
- Update help message in readme

## v0.1.133 (2025-03-30)

- Bump deps and `pre-commit` hook
- Commit changes after bump release
- Fix incorrect git options in `nox` job
- Remove unused variables in `PdfWriter` footer drawing

## v0.1.132 (2025-03-23)

- Bump deps and `pre-commit` hook
- Fix incorrect extension in `gmi` format
- Rename `_to_md` to `_to_gmi` for Gemtext format consistency
- Remove unnecessary if condition
- Correctly disable header numbering based on config and language
- Fix help message for `gmi` subcommand to reflect Gemtext format

## v0.1.131 (2025-03-16)

- Fix help message for `gmi` subcommand to reflect Gemtext format
- Ignore aider files
- Rename msg variable to message for clarity
- Set default output folder using DEFAULT_OUTPUT_FOLDER variable
- Update docstrings and fix incorrect args
- Update docstrings on detecting language

## v0.1.130 (2025-03-09)

- Bump deps
- Update comment for EmptyFileError
- Use better variable naming
- Use google style docstrings

## v0.1.129 (2025-03-02)

- Bump deps and pre-commit hooks
- Remove duplicated regex patterns
- Use dictionary to map fileformat output
- Use list instead of lambda function

## v0.1.128 (2025-02-23)

- Add examples to lower_underscore helper function
- Bump deps and `pre-commit` hooks
- Fix extra newline in changelog
- Fix incorrect script module name for `txt2ebook` cli

## v0.1.127 (2025-02-16)

- Bump deps
- Refactor lower_underscore helper function
- Remove deprecated load_class and to_classname helper function
- Set coverage mode to parallel
- Use --short flag to obtain current and bump release version

## v0.1.126 (2025-02-09)

- Bump deps and `pre-commit` hooks
- Remove deprecated `create_format` helper function

## v0.1.125 (2025-02-02)

- Add `--single-newline` flag to `massage` subcommand
- Add initial `epub` subcommand test
- Bump deps and `pre-commit` hooks
- Fix missing args to `massage` subcommand

## v0.1.124 (2025-01-26)

- Bump deps and `pre-commit` hooks
- Remove deprecated `--env` flag tests
- Rename test cases by subcommand
- Resolve `pybabel` deps issue

## v0.1.123 (2025-01-19)

- Bump deps
- Fix `epub` subcommand missing required arg
- Remove some deprecated tests
- Switch from `txt2ebook` to `tte`

## v0.1.122 (2025-01-13)

- Bump deps
- Move `--fullwidth`, `--header-number`, `--paragraph-separator` from `tte`
  command to respective subcommand

## v0.1.121 (2025-01-05)

- Bump copyright years
- Bump deps and `pre-commit` hooks
- Remove extra empty line

## v0.1.120 (2024-12-29)

- Bump deps and `pre-commit` hooks
- Resolve unused variable warning
- Remove title, author, and translator from new cli

## v0.1.119 (2024-12-22)

- Bump deps
- Migrate header number to `massage` subcommand
- Refactor setup logging and `env` subcommand

## v0.1.118 (2024-12-15)

- Bump deps
- Fix incorrect comments
- Move `-ff` or `--file-format` to each ebook subcommand
- Move `-c` or `--cover` to select ebook subcommand
- Refactor building subparser for each subcommand

## v0.1.117 (2024-12-08)

- Bump deps
- Move `--op` flag to each ebook subcommand
- Move `--sort-volume-and-chapter` flag to `massage` subcommand
- Refactor loading subcommands parser dynamically
- Remove some `re-*` options and migrate some to `massage` subcommand
- Use Python major version for pyenv

## v0.1.116 (2024-12-01)

- Add bottom margin to volume and chapter title for higher readability
- Add index support to `typ` format
- Bump deps
- Fix the incorrect last page size in pdf output of `typ` format
- Support Typst 0.12.0 version

## v0.1.115 (2024-11-24)

- Add `--toc` and `--no-toc` flag to `typ` subcommand
- Bump deps
- Fix incorrect comment
- Update pypi classifier

## v0.1.114 (2024-11-17)

- Bump deps and `pre-commit` hooks
- Migrate `typ` and `pdf` format to subcommand
- Migrate deprecated regex-\* options test cases
- Refactor `massage` subcommand
- Refactor language detection and validation
- Remove Tokenizer from handling `fullwidth` flag
- Set `deps` job in `nox` to Python 3.9

## v0.1.113 (2024-11-10)

- Extract top keywords from txt file
- Migrate `gmi` and `pdf` format to subcommand

## v0.1.112 (2024-11-03)

- Bump deps
- Migrate `epub` and `md` format to subcommand

## v0.1.111 (2024-10-27)

- Bump deps and `pre-commit` hooks
- Switch Python version to 3.13.0 to all `nox` tasks

## v0.1.110 (2024-10-20)

- Bump deps and `pre-commit` hooks
- Support Python 3.13 in `pyenv` and `nox`

## v0.1.109 (2024-10-13)

- Bump deps and `pre-commit` hooks
- Migrate `tex` format to subcommand

## v0.1.108 (2024-10-06)

- Bump deps and Python version for `pyenv`
- Initial migration to use subcommand for `env`, `massage`, and `parse`
- Show each metadata on separate line as info log

## v0.1.107 (2024-09-29)

- Add `-ct` or `--clean-tex` flag to remove all LaTeX artifacts
- Bump deps and `pre-commit` hooks

## v0.1.106 (2024-09-22)

- Bump Python versions for `pyenv`
- Bump deps
- Optimize index keyword replacement in TeX format
- Show PDF filename when generating TeX format
- Show index keyword in red in PDF format

## v0.1.105 (2024-09-15)

- Bump deps
- Refactor showing stacktrace based on raw args

## v0.1.104 (2024-09-08)

- Support `posargs` to most sessions in `nox`
- Update `nox` session in contributing doc

## v0.1.103 (2024-09-01)

- Bump deps and `pre-commit` hooks
- Show total time taken to generate an ebook

## v0.1.102 (2024-08-25)

- Bump deps and `pyenv` versions
- Group `nox` sessions
- Refactor `release` session

## v0.1.101 (2024-08-18)

- Bump deps and `pre-commit` hooks
- Run lint session with latest Python
- Truncate updated readme during write
- Update nox sessions in contributing doc

## v0.1.100 (2024-08-11)

- Add `release` session in `nox` to bump a release
- Bump deps and `pre-commit` hooks

## v0.1.99 (2024-08-04)

- Add extra args to `test` session in `nox`
- Bump deps and `pre-commit` hooks
- Ignore pyint rule
- Remove extra lines in `nox` config
- Update readme

## v0.1.98 (2024-07-28)

- Bump deps and `pre-commit` hooks
- Fix `lint` session run correctly in `nox`
- Refactor `readme` session to update README file correctly

## v0.1.97 (2024-07-21)

- Bump deps
- Generate doc using venv managed by `nox` in `doc` session
- Update contributing doc to use `nox` and `poetry`

## v0.1.96 (2024-07-14)

- Bump deps
- Drop support for Python 3.8
- Fix `doc` session in `nox`
- Refactor `readme` session in `nox`

## v0.1.95 (2024-07-07)

- Bump deps, `pre-commit` hook, and Python for `pyenv`
- Do not reuse `venv` for all `nox` sessions
- Update translations

## v0.1.94 (2024-06-30)

- Bump deps and `pre-commit` hook
- Resolve using variable before assignment issue
- Update `nox` session list to contributing doc

## v0.1.93 (2024-06-23)

- Add `readme` session to `nox` to update help message to readme
- Bump deps and `pre-commit` hook
- Set CLI program name explicitly

## v0.1.92 (2024-06-16)

- Bump deps
- Fix incorrect installer step in `nox`
- Migrate remaining translation steps to `pot` session in `nox`
- Remove all `tox` related config and deps

## v0.1.91 (2024-06-09)

- Add initial `pot` session to `nox`
- Bump deps
- Update `nox` output to contributing doc

## v0.1.90 (2024-06-02)

- Bump deps
- Remove `pre-commit` instruction from contributing doc
- Update `doc` session description
- Update `nox` output to contributing doc

## v0.1.89 (2024-05-26)

- Add `cov` (coverage) session to `nox`
- Bump deps and `pre-commit` hook
- Fix indexed keyword not showing in `pdf` file through `tex` format

## v0.1.88 (2024-05-19)

- Add `doc` and `test` session to `nox`
- Bump deps
- Migrate `dev` related deps to `dev` group
- Remove subheaders from changelog

## v0.1.87 (2024-05-12)

- Add `lint` session to `nox` task runner
- Bump deps and `pre-commit` hooks

## v0.1.86 (2024-05-05)

- Fix test errors without translator option
- Bump deps and `pre-commit` hooks
- Update readme and contributing doc

## v0.1.85 (2024-04-28)

- Add `index` as field to metadata of a book model
- Bump deps and `pre-commit` hooks
- Refactor adding paragraphs to `tex` format
- Revise ToC style with `tocloft` package

## v0.1.84 (2024-04-21)

- Add `-ik` or `--index-keyword` to add keyword to index
- Bump deps and `pre-commit` hooks
- Do not show date in title page
- Only colour and link page number in TOC page
- Update translations
- Use `\par` command to wrap paragraph
- Use correct way to remove page header/footer in multiple TOC pages

## v0.1.83 (2024-04-14)

- Bump deps, `pre-commit` hooks, and Python version for `pyenv`
- Ignore and resolve `flake8` and `pylint` linting rules
- Set the default paper size for `tex` format as `a6paper`

## v0.1.82 (2024-04-07)

- Add initial support for TeX format through `-f tex` option
- Bump deps

## v0.1.81 (2024-03-31)

- Bump deps
- Open `pdf` file when `--open` flag was toggled
- Remove indentation for all paragraphs in `typ` format instead of buggy hacks
- Update translations

## v0.1.80 (2024-03-24)

- Add test for `--env` flag
- Fix newline in the `sys.version` output in Python 3.8

## v0.1.79 (2024-03-17)

- Increase default font size for `typ` format
- Update deps and `pre-commit` hook
- Update translations

## v0.1.78 (2024-03-10)

- Add `--env` flag to print debugging information
- Update `pre-commit` hook

## v0.1.77 (2024-03-03)

- Update translations

## v0.1.76 (2024-02-25)

- Update translations

## v0.1.75 (2024-02-18)

- Add `-op` or `--open` flag to open the generated file using default program

## v0.1.74 (2024-02-11)

- Arrange function name by sequence of calling
- Remove leading from paragraph in `typ` format
- Update translations

## v0.1.73 (2024-02-04)

- Get page size from arg or language's config
- Fix missing quote when setting page size for `typ` doc

## v0.1.72 (2024-01-28)

- Add instruction on upgrade

## v0.1.71 (2024-01-21)

- Exclude `__repr__` from test coverage
- Set default page size to `a5`
- Use page size from config for `typ` format

## v0.1.70 (2024-01-14)

- Test `typ` format debug log
- Fix comment wordings
- Fix missing markdown markup in contributing doc

## v0.1.69 (2024-01-07)

- Bump copyright years and project and pre-commit hooks deps
- Remove `creosote` pre-commit hook
- Update translations

## v0.1.68 (2023-12-31)

- Bump Python versions for `pyenv` environment
- Ignore `poetry.lock` for `prettier` pre-commit hook

## v0.1.67 (2023-12-24)

- Generate PDF file for Typst document
- Add creosote pre-commit hook
- Set default Chinese font for Typst document
- Set python 3.12 as base version for all pre-commit hooks
- Resolve incorrect type of base method

## v0.1.66 (2023-12-17)

- Support `typ` (typst) output format

## v0.1.65 (2023-12-10)

- Test for epub file format

## v0.1.64 (2023-12-03)

- Split scripttest cli runner output to stdout and stderr

## v0.1.63 (2023-11-26)

- Allow scriptttest runner to accept keyword args
- Revise the pre-conditions before purging output directory
- Enable all purge flag related tests
- Do not purge output folder when output file is explicitly set

## v0.1.62 (2023-11-19)

- Add `-y` or `--yes` flag to confirm any prompts
- Fix output folder should be defaulted to current working directory
- Add Developer's Certificate of Origin (DCO) to contributing doc

## v0.1.61 (2023-11-12)

- Prompt before purging output folder
- Put `--page-size` option under the `pdf` section in help message
- Fix missing f-string in `--purge` flag

## v0.1.60 (2023-11-05)

- Add `-p` or `--purge` flag to remove converted ebooks specified by
  `--output-folder` option
- Fix typo

## v0.1.59 (2023-10-29)

- Generate split `md`, and `gmi` files to default output folder
- Update Python version for `pyenv`

## v0.1.58 (2023-10-22)

- Add missing classifier
- Generate split `txt` files to default output folder

## v0.1.57 (2023-10-15)

- Test using both short, and long option, or flag
- Fix incorrect coverage omit pattern

## v0.1.56 (2023-10-08)

- Support Python 3.12.0

## v0.1.55 (2023-10-01)

- Add `flake8-simplify` to `pre-commit` hook
- Use `pylint` code instead of name for disabling rules
- Update chapter regex for `zh-tw` language
- Refactor codes raised by `flake8-simplify`

## v0.1.54 (2023-09-24)

- Show missing in test coverage report
- Move program description in module doc

## v0.1.53 (2023-09-17)

- Rename test scripts to follow naming convention
- Update test scripts to use list as CLI argument
- Add more tests to increase test coverage

## v0.1.52 (2023-09-10)

- Switch CLI test from `pytest-console-scripts` to `scripttest`

## v0.1.51 (2023-09-03)

- Refactor logging code
- Show statistics when converting PO to MO files
- Update translations

## v0.1.50 (2023-08-27)

- Add `-q` or `--quiet` flag to suppress all logging
- Remove remaining mentioned of `py37` in contributing doc
- Bump python versions for `pyenv`

## v0.1.49 (2023-08-20)

- Switch to `Babel` for translations
- Fix missing language export variable for `zh-tw`

## v0.1.48 (2023-08-13)

- Fix missing config items for `zh-tw` language
- Remove duplicated configs in project config
- Rename test filenames using the correct term

## v0.1.47 (2023-08-06)

- Add additional default hook for `pre-commit`
- Add `-ss` or `--sort-volume-and-chapter` arg to sort the parsed volume and
  chapter
- Fix incorrect `coverage` config for `pytest-cov`

## v0.1.46 (2023-07-30)

- Add changelog URL to help message
- Get config explicitly instead of `__getattr__` function
- Remove included markdown files during installation
- Sort coverage report by cover rate and skip covered files
- Update missing translations

## v0.1.45 (2023-07-23)

- Add `-of` or `--output-folder` to set a default `output` folder to prevent clutter
- Fix missing dashes in metadata header when exporting `txt` format
- Fix missing translator field in metadata for `md` and `gmi` format
- Force all source text file to follow a YAML-inspired metadata header
- Parse and include translators into metadata of a book
- Refactor all toc markups for `md`, `gmi`, and `txt` format
- Refactor and optimize tokenizing metadata header of a source `txt` file
- Rename and standardize extra `tox` environment names

## v0.1.44 (2023-07-16)

- Add test fixture with metadata
- Update `pyenv` installation steps in contributing doc
- Use active virtualenvs in `poetry` in contributing doc
- Fix not using book title as output file name when input source from
  redirection or piping

## v0.1.43 (2023-07-09)

- Add additional config for coverage report
- Add source of the fish logo image used in documentation
- Initial support for GemText, or Gemini format using `-f gmi` option
- Link to license doc from contributing doc
- Use the same output folder for HTML documentation generation
- Fix inconsistent log message when generating output file
- Update the right `poetry` command to create, and activate virtual environment

## v0.1.42 (2023-07-02)

- Fix deps still locked to Python 3.7
- Move Tox configuration as separate ini file
- Update help message in readme

## v0.1.41 (2023-06-25)

- Remove support for Python 3.7
- Enable parallel support during coverage testing
- Remove unused deps

## v0.1.40 (2023-06-18)

- Add `-tr` or `--translator` arg to set translator
- Bump project and pre-commit dependencies
- Format date in changelog
- Update project description
- Fix missing translations for `zh-tw` language
- Fix incorrect URL in contributing doc

## v0.1.39 (2023-06-11)

- Switch to use fixtures for all test cases
- Revise contributing guide
- Refactor generating volume section in PDF document

## v0.1.38 (2023-06-04)

- Add `zh-tw` translations
- Update deprecating call of script_runner in tests

## v0.1.37 (2023-05-28)

- Add chapter regex rules for `zh-cn` language
- Add missing return type for PDFWriter
- Align page number against body content in PDF file
- Fix missing export variable for `zh-tw` language
- Refactor TOC generation in PDF file
- Update outdated translation

## v0.1.36 (2023-05-21)

- Add `-pz` or `--pagesize` flag to set page size to PDF format
- Add clickable link to table of content to PDF format
- Add page number in footer to PDF document
- Get language details from language config when generating PDF
- Refactor generating cover page for PDF format
- Revise indentation of table of content in PDF file
- Show boundary box in PDF document in debug mode

## v0.1.35 (2023-05-14)

- Add and get default font name and file from language settings
- Add table of content to PDF file
- Log when generating volume or chapter in PDF output
- Refactor all writer class to use common generated filename
- Use translated table of content text in PDF output

## v0.1.34 (2023-05-07)

- Add initial support for exporting to PDF format through `-f pdf` for
  `--language zh-cn`
- Group deps accordingly
- Ensure pre-commit works with Python 3.11
- Update missing translations

## v0.1.33 (2023-04-30)

- Add tests for `format` flag
- Bump Python's deps
- Regroup Python deps under same group in project config
- Refactor common functions for format writer as abstract class
- Fix missing dep error in environments for Tox

## v0.1.32 (2023-04-23)

- Add initial support for exporting to Markdown (`md`) format
- Bump Python's deps
- Update PyPi's classifiers

## v0.1.31 (2023-04-16)

- Add new filename format of `authors_title.ebook_extension`
- Add initial pypandoc dep for future support for pandoc
- Fix incorrect example in help message

## v0.1.30 (2023-04-09)

- Add `-of` or `--filename-format` to save filename in different naming
  convention
- Rename all test files with names from `options` to `flags`
- Add missing typing for Book model

## v0.1.29 (2023-04-02)

- Fix missing replacing space with underscore when exporting multiple text file
- Ensure all split and overwritten text filenames are in lower case and
  underscore

## v0.1.28 (2023-03-26)

- `zh_words_to_numbers(words, match_all=True)` will convert all found word, by
  default it convert the first found word only
- Convert `zh_words_to_numbers` to support keyword arguments,
  `zh_words_to_numbers(words, length)` to `zh_words_to_numbers(words, length=5)`

## v0.1.27 (2023-03-19)

- Add `-toc` or `--table-of-content` option which add a toc to the text file
- Change filename format when generating multiple txt through `-sp` option
- Fix cannot set export format to `txt`
- Group options in help message
- New `txt` file will be created when `-f txt` option is set
- Remove `-ob` or `--overwrite-backup` option

## v0.1.26 (2023-03-12)

- Fix missing translations
- Fix missing EPUB template names not showing in help message
- Raise warnings for invalid prepend length for `zh_words_to_numbers` function
- Rename epub template names, `clean_no_indent` to `noindent`, and
  `clean_no_paragraph_space` to `condense`

## v0.1.25 (2023-03-05)

- Add missing `zh-*` character for `zh_numeric`
- Add new EPUB templates, `clean_no_indent` and `clean_no_paragraph_space`
- Fix incorrect dep added to wrong environment
- Refactor ebook extensions variable into package
- Remove unused import

## v0.1.24 (2023-02-26)

- Bump Python's version for `pyenv`
- Extract and add `zh_utils.zh_words_to_numbers` function
- Remove escaped paragraph separator argument during argument parsing

## v0.1.23 (2023-02-19)

- Add more chapter regex for `zh-*` language
- Group options by ebook format in help message
- Refactor conversion of halfwidth to fullwidth into
  `zh_utils.zh_halfwidth_to_fullwidth` function
- Revise default environments for tox to run
- Support default value for `zh_utils.zh_numeric` function

## v0.1.22 (2023-02-12)

- Add `zh_utils` module for handling all `zh-*` language text
- Add missing chapter number for `zh-*`
- Support more conversion of chapter words to numbers for `zh-*` language

## v0.1.21 (2023-02-05)

- Add `-sp` or `--split-volume-and-chapter` to export a `txt` file into
  multiple text files by header
- Exclude gettext related files from pre-commit

## v0.1.20 (2023-01-29)

- Add more test cases to improve test coverage
- Fix UUID not added to the EPUB e-book
- Format help message indentation to improve readability
- Put coverage report config into `.coveragerc`
- Speed up tests through parallel testing using `pytest-xdist`

## v0.1.19 (2023-01-22)

- Fix cannot build doc in Tox
- Fix missing msgfmt step for updating mo translation files
- Remove unused `cchardet` dep which break Python 3.11
- Set base python in Tox env to Python 3.11
- Support Python 3.11 environment for Tox in testing
- Use correct way to get module attribute
- Use gettext for structure names for book model

## v0.1.18 (2023-01-15)

- Fix halfwidth to fullwidth conversion `-fw` only applies to `zh-cn` or
  `zh-tw` language
- Fix incorrect text file generated due to undecode paragraph separator
- Fix missing default tags regex for `en` language
- Fix words to numbers conversion `-hn` only applies to `zh-cn` or `zh-tw` language
- Remove chapter regex rule that affect header with punctuation
- Support long options for all command option flags
- Use Gettext for localization of book metadata by language
- Warn on mismatch between configured and detected language

## v0.1.17 (2023-01-08)

default instead of title of the ebook

- Add `-v`, `-vv`, or `-vvv` to set verbosity level for debugging log
- Add padding between volume in table of content in default EPUB CSS style
- Add test cases for `-hn` or `--header-number` option
- Add test cases for `-rw` or `--raise-warns` option
- Generated output ebook filename should follow the source input filename by
- Rename `raise-warns` option to `raise-on-warning`
- Replace categories with tags of a book metadata
- Show debug log for tokenized chapter at `-vv` and paragraph at `-vvv`
- Show line number in source file for token in debug log
- Show selected text when converting words to numbers in debug log
- Show token sequence number in padded zeroes in debug log
- Support repr for Tokenizer class
- Use `-V` flag instead of `-v` for show program version
- Use the sample paragraph separator `-ps` when exporting to text format

## v0.1.16 (2022-12-30)

- Add `-hn` or `--header-number` to convert section sequence from words to
  numbers, only for `zh-cn` language, and left padding added when section
  sequence is integer
- Add `-fw` or `--fullwidth` to convert ASCII characters from halfwidth to
  fullwidth numbers, only for `zh-cn` language
- Add `-rw` or `--raise-warns` to raise exception when there are warnings on
  parsing
- Add `-ob` or `--overwrite-backup` to overwrite massaged content and backup
  the original source content
- Add category field to metadata of the book
- Add `repr` for Volume model
- Show warning on extra newline before section header
- Get statistic data on Book model
- Output text file from parsed Book structure data instead of massaged text
- Rename `-nb` / `--no-backup` option as `-ow` / `--overwrite`
- Retain the original source content file by default unless explicitly set
  using `-ow`
- Do not backup source content file by default unless explicitly set using
  `-ob`
- Support setting multiple ebook formats at once using `-f` option
- Remove unused `raw_content` field for Volume and Chapter model
- Add custom `repr` for Volume and Chapter model
- Deprecate `DEFAULT_RE_VOLUME_CHAPTER` regex for each language
- Update and revise regex for different section header for `zh-cn` and `en`
  language
- Use `logger.warning` instead of deprecated `logger_warn`
- Refactor debugging and logging of Book model
- Raise warning when cannot split paragraphs by paragraph separator
- Raise warning when no table of content found when generating ebook
- Deprecate unused `raw_content` field in Volume and Chapter model
- Fix and update regex patterns for `zh-cn` language
- Fix escaped paragraph separator not unescaped when set from command line

## v0.1.15 (2022-11-10)

- Fix help menu which affected the sphinx doc generation
- Fix missing volume pattern when parsing header with both volume and chapter
- Refactor parsing by tokenizing instead
- Shorten the option description in the help menu
- Support and test against Python 3.11

## v0.1.14 (2022-10-14)

- Able to run program as `python -m txt2ebook` or `python -m src.txt2ebook`
- Add `--ps` option to parse text file by paragraph separator
- Add `--rvc` option to parse header with volume and chapter title
- Handle argument parsing using argparse standard library instead of Click
- Logging using standard library instead of loguru
- Refactor language config into separate own module
- Refactor to use single Parser module to handle all supported languages
- Replace DotMap with argparse.Namespace as config container
- Show repo details in help message
- Show stacktrace in debug mode or `-d` option enabled
- Switch linting to pre-commit instead of tox environment
- Test console script directly using pytest-console-scripts
- Use `importlib.resources` to load CSS template
- Use better approach to handle exception message

## v0.1.13 (2022-05-02)

- Add `-ra/--re-author` option to parse and extract author by regex
- Add `-rc/--re-chapter` option to parse multiple volume header by regex
- Add `-rt/--re-title` option to parse and extract title by regex
- Add `-rv/--re-volume` option to parse multiple volume header by regex
- Add `-vp/--volume-page` option to create separate page for volume title
- Add contribution guideline on how to contribute to this project
- Generate documentation through Sphinx
- Refactor detecting book title to base parsing class
- Rename `-dlr/--delete-line-regex` to `-rl/re-delete-line`
- Rename `-dr/--delete-regex` to `-rd/re-delete`
- Rename `-rr/--replace-regex` to `-rr/re-replace`
- Rename and standardize on regex option
- Show longer and exact raw string when repr(Chapter)

## v0.1.12 (2022-01-18)

- Add `tte` as the alternative shorter command name to `txt2ebook`
- Add more fields to repr for Chapter model
- Fix cannot generate ebook for English text file
- Fix cannot parse content with no empty line as paragraph separator
- Fix removing line by regex not working
- Fix section header not showing in toc in Foliate
- Refactor EPUB template loading
- Refactor base parser module to use dataclass
- Separate page for volume title in epub format
- Stricter rules on Chinese header parsing
- Support Python 3.7 onwards
- Use DotMap to manage config
- Use Tox for automation and testing

## v0.1.11 (2021-12-19)

- Add `--epub-template/-et` option to set CSS style for EPUB file
- Add `--test-parsing/-tp` option to show only parsed headers without
  generating ebook
- Add missing language when generating HTML for each chapter
- Add typing to the project
- Build cover page when cover image `--cover` was set
- Do not capture newline when parsing book title and author name
- Generate EPUB file in tmp dir when running test case
- Remove whitespace in chapter title in HTML
- Switch logging to loguru library and rephrase logging messages
- Update default table of content style sheet
- Update more project classifiers
- Wrap program's config with configuror library

## v0.1.10 (2021-11-22)

- Do not generate txt file twice when txt format was set
- Fix cannot parse txt file other than Unix line end
- Fix test default to unknown parser
- Move common functions to helper subpackage
- Refactor parser and writer factory into subpackage
- Set unique identified for epub based on book's title
- Support setting multiple authors

## v0.1.9 (2021-10-26)

- Add `--format` option to specify output format
- Fix missing deps in requirements.txt
- Fix issues raised by PyLint
- Refactor txt and epub file generation in separate module
- Refactor txt formatting and parsing in separate module
- Switch chapter header regex to constant

## v0.1.8 (2021-10-04)

- Add `--width` option to set line width for paragraph wrapping
- Allow setting of optional argument for output path and file name
- Disable backup txt fixtures during test
- Fix warnings raised by Pylint
- Refactor and move string helper functions
- Refactor extracting title and author from txt file
- Remove using Click's context object
- Rename `--remove-wrapping` option to `-no-wrapping` to follow the convention
- Replace magic number with constant

## v0.1.7 (2021-09-19)

- Add `--cover` option to add cover image to ebook
- Detect the original encoding of txt file, convert, and save to utf-8
- Do not raise exception when no chapter header found
- Fix group match not working with replacing regex
- Fix paragraph wrapping of imbalance opening and closing quote
- Generate HTML manually instead through Markdown
- Keep original txt file formatting except chapter header
- Match different chapter headers and line separator
- Refactor and use more ways to extract book title from txt file
- Relax chapter header regex rules
- Replace full-width space with half-width space in chapter headers
- Revise logging message format
- Show indentation for chapter title in debugging message

## v0.1.6 (2021-09-11)

- Add `--no-backup` option to skip backup the original txt file
- Backup original txt file and overwrite with parsed content
- Include and refactor more chapter header regex

## v0.1.5 (2021-09-02)

- Add `--delete-line-regex` option to remove whole line from the file content
- Add `--delete-regex` option to remove selected words or phrases from the file
  content
- Add `--replace-regex` option to replace selected words or phrases from the
  file content
- Detect author name from file content
- Dump parsed txt file during debug mode
- Fix incorrect chapter filename
- Fix issues raised by Flake8 and PyLint
- Fix missing title in Epub file
- Parse more different chapter headers
- Parse volumes and chapters correctly and generate nested toc
- Replace missing space between chapter header and chapter title
- Save HTML filename in Epub as chapter header and title
- Use only single quotation punctuation

## v0.1.4 (2021-08-04)

- Add `--remove_wrapping` option to remove text wrapping in the body content of
  a chapter
- Capture the book title from the file if found and not explicitly set through
  `--title` option
- Fix issues raised by PyLint
- Fix no paragraph separation for txt file without single-line spacing for
  markdown
- Parse more different chapter headers
- Refactor argument parsing

## v0.1.3 (2021-07-24)

- Fix issues raised by PyLint
- Fix no parsing and split by introduction chapter
- Switch license to AGPL-3

## v0.1.2 (2021-07-20)

- Add missing requirements.txt
- Add option to set metadata for ebook
- Code formatting
- Print message using click.ecto
- Show full help message when missing required argument
- Use better way to check for input file

## v0.1.1 (2021-07-13)

- Check for missing filename, empty file content, and missing chapters
- Enable logging for debugging and showing status
- Set log level through `LOG` environment variable

## v0.1.0 (2021-07-08)

- Initial public release
- Support converting txt file in Chinese language into epub format
