#!/bin/bash
this="${BASH_SOURCE[0]:-$0}"
top="$(dirname ${this})/.."
dest="${dest:-${TMPDIR:-${HOME}/tmp}/test_py_encase}"

export PYTHON=python3.13 PYTHON3=python3.13 
export PIP=pip-3.13      PIP3=pip-3.13 

src="${top%/}/src/py_encase/py_encase.py"

if [ -d "${dest}" ]; then
    echo rm -rf "${dest}"
    rm -rf "${dest}"
fi

if [ "x${1}" == 'xclean' ]; then
    exit
fi


"${src}" --manage init --prefix="${dest}" -g -r -v -m pytz -m tzlocal -S trial1.py

"${dest}"/bin/trial1 -d
"${dest}"/bin/mng_encase add    -v -r trial2
"${dest}"/bin/mng_encase addlib -v -r trial3

echo "Test output under: ${dest}"
