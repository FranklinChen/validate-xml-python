# Validate XML against XML Schema using Python

[![Build Status](https://travis-ci.org/FranklinChen/validate-xml-python.png)](https://travis-ci.org/FranklinChen/validate-xml-python)

## Prerequisites

Python 3 is required.

Install required libraries:

```
$ pip3 install -r requirements.txt
```

## Usage

Basic usage:

```
$ python3 validate.py3 root_dir 2> log.txt
```

## Performance

This was written to be super fast:

- Concurrency, using `multiprocessing`.
- Use of `lxml` binding to C `libxml2` library.
- Downloading of remote XML Schema files only once, and caching to `~/.xmlschemas/` for future runs of the program.
- Caching of `libxml2` schema data structure for reuse in multiple concurrent parses.

On my machine, it takes a few seconds to validate a sample set of 20,000 XML files. This is hundreds of times faster than the first attempt, which was a shell script that sequentially runs `xmllint` (after first pre-downloading remote XML Schema files and passing the local files to `xmllint` with `--schema`). The concurrency is a big win, as is the reuse of the `libxml2` schema data structure across threads and avoiding having to spawn `xmllint` as a heavyweight process.

## Comparison

I wrote this based on my Rust version of this program, https://github.com/FranklinChen/validate-xml-rust

The Python version is shorter largely because of the existence of `lxml`.
