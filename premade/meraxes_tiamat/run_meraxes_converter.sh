#!/bin/bash
export TAODIR=/fred/oz114/kdtao
source $TAODIR/bin/setup-runtime.sh
python meraxes_converter.py meraxes_abs_mags_premade_testing.h5
