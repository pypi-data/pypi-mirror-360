#!/bin/bash

python --version
cd /package/
pip install pytest
pip install .
pytest
