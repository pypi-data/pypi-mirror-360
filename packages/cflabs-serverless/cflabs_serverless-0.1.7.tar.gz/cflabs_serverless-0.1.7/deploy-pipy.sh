#!/bin/bash

pip install -e .

# upload to pypi
rm -rf dist
python -m build
python -m pip install --upgrade twine
python -m twine upload dist/*