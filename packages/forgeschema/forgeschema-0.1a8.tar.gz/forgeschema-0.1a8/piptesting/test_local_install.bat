REM Needs to be run from top-level directory
docker run -v .:/package/ -i python:3.11 /bin/bash < piptesting/test_local_install.sh