#!/bin/bash
export TAODIR=/fred/oz114/kdtao
source $TAODIR/bin/setup-runtime-python3.sh
mpirun -n 1 python parse_xml_and_validate.py $*
