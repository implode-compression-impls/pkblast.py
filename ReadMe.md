pkblast.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
==========
~~[wheel (GitLab)](https://gitlab.com/KOLANICH/pkblast.py/-/jobs/artifacts/master/raw/dist/pkblast-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/implode-compression-impls/pkblast.py/workflows/CI/master/pkblast-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH/pkblast.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/pkblast.py/badges/master/coverage.svg)~~
[![GitHub Actions](https://github.com/implode-compression-impls/pkblast.py/workflows/CI/badge.svg)](https://github.com/implode-compression-impls/pkblast.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/implode-compression-impls/pkblast.py.svg)](https://libraries.io/github/implode-compression-impls/pkblast.py)

This are free and Open-Source ctypes-based bindings to [`libblast`](https://github.com/madler/zlib/tree/master/contrib/blast) by [Mark @madler Adler](https://github.com/madler), which is a Free Open-Source implementation of a decompressor of PKWare Data Compression Library (DCL) compression format.

For compression you need [`pkimplode.py`](https://github.com/implode-compression-impls/pkimplode.py) a separate wrapper to a separate library by another author.

For decompression you can alternatively use [`pwexplode`](https://github.com/Schallaven/pwexplode) a pure-python impl, but it is licensed under GPL-3.0-or-later.

Benefits of CTypes-based impl:

* Supports python versions other than CPython
* No need to recompile python module after python version upgrade

Drawbacks:
* performance and overhead may be worse, than in the case of a cext.

Installation
------------

In order to make it work you need a package with `liblast` itself installed into your system using your distro package manager. If your distro doesn't provide one, you can build it yourself using CMake CPack from the sources [by the link](https://github.com/implode-compression-impls/libblast). You will get 3 packages, one with the headers, another one with the shared library, and yet another one with the CLI tool. Only the one with the lib is mandatory.

Usage
-----

The package contains multiple functions. They have names matching the regular expression `^decompress(Stream|Bytes(Whole|Chunked))To(Stream|Bytes)$`.

The first subgroup describes the type of input argument, the second subgroup describes the type of output.
* If input is `Bytes`, then you need
    * `Whole`, which means that the lib gots a pointer to whole array with compressed data. This is considered to be **the optimal input format**.
    * `Chunked` (which means the data are processed in reality by `decompressStreamTo$3`) was created mainly for convenience of testing.
* Otherwise it is an object acting like a stream. In this case you can also provide `chunkSize`, because streams are processed in chunks. Larger the chunk - less the count of chunks in the stream, so less overhead on calls of callbacks, but more memory is needed to store the chunk.

The second subgroup describes the type of the result.
* The internal type of the result is always a `Stream`. This is considered to be **the optimal output format**. It is because we don't know the size of output ahead of time, so have to use streams.
* `Bytes` are only for your convenience and just wrap the `decompress$1ToStream` with a context with `BytesIO`.
