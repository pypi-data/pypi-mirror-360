#!/bin/bash

echo "Now we're cooking!"
python --version

pip install --install-option test --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple forgeschema
forgeschema