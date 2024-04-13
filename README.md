# parse-exr-header
[![license](https://img.shields.io/github/license/vvzen/parse-exr-header)](https://github.com/vvzen/parse-exr-header/blob/master/LICENSE)


Pure Python (no additional dependencies) helper functions to read metadata from the header of EXR files.

# Reasons
In the VFX world we've got tons of great open source initiatives, like ILM's OpenEXR and Sony's OpenImageIO.
Both are great C++ projects (and OIIO also provides bindings for Python), so I definitely recommend using them.

BUT maybe your package manager doesn't have a specific version and compiling them from scratch can be a long process that could get you stuck in many, many different & non well documented cmake issues.

If you only need to do something as trivial as reading the metadata of an EXR file and you don't need to do any image manipulation stuff, it's just not worth the hassle.
That's why I've written this very small python module (currently ~360 LOCs) that simply reads the header of an exr file, according to the official EXR documentation available here: https://www.openexr.com/documentation/openexrfilelayout.pdf (now moved to https://openexr.com/en/latest/OpenEXRFileLayout.html)

# Dependencies
Optional, for tests:
`pytest==4.2.0`

Optional, for formatting:
`yapf==0.30.0`

# Support

## Python version
This repo now supports both Python2.7 and also Python3.8.
Thanks to [jonaskluger](https://github.com/jonaskluger) for providing python3 support.

## Multipart files
Support for multipart files is on its way but it will need a bit of work since the original design of this hobby project was a bit naive. A PR is currently pending.

# Install
This script is not packaged in any fancy way. Just grab the `parse_metadata.py` and put it wherever you want.

_Update (2021/12/27)_: Now there is also a tiny cli (`bin/vv-exr-metadata`) that you can use, if you want, to list the metadata of a file from a shell session. It supports the wildcard notation (*) if you want to look at multiple files at once.

# Tests
I'm not a TDD guy (yet) - so there are very few tests. I'm planning to write more of them as soon as I can breathe a little.
You can run tests by typing: `pytest tests` from the root dir of this repo.

You will need also the git submodule that contains all the exr images, so you need to clone the repo like this:

`git clone --recurse-submodules git@github.com:vvzen/parse-exr-header.git`

# PR & Bugs
Fill free to submit Pull Requests if you notice anything wrong. I'm more than happy to merge them and adapt them to my coding style (which is just PEP8 stuff with some additional things like lowercase functions args in order to distinguish arguments from variables inside the scope of a function - very useful in my opinion and blog post coming soon).

Note: Whenever you submit a PR, the CI should automatically run the tests for you using Github Actions.

### Formatting
I use [yapf](https://github.com/google/yapf) to end all style wars and let it do all of the formatting for me. After you made a PR, you can run it like this:
```
yapf --in-place src/*.py
```

This of course requires you to have `yapf` installed locally or somewhere in your `$PATH`.
Yapf will simply read the `.style.yapf` file that is hosted in this repo and format the file according to these rules.
