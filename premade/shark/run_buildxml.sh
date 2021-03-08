#!/bin/bash
export TAODIR=/fred/oz114/kdtao
source $TAODIR/bin/setup-runtime.sh
python buildxml.py $*
