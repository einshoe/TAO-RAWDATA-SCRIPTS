#!/bin/bash
# Note that as.ui.txt will be the same as scrapedata/overwrite_first_draft_dont_delete.txt
./run_buildxml.sh /fred/oz004/msinha/tao/data_products/output/premade/shark/lightcone/deep-optical/shark-combined_ABmags.hdf5
cp as.ui.xml shark-combined_ABmags.ui.xml
cp as.xml shark-combined_ABmags.xml
./run_buildxml.sh /fred/oz004/msinha/tao/data_products/output/premade/shark/lightcone/deep-optical/shark-combined_APmags.hdf5
cp as.ui.xml shark-combined_APmags.ui.xml
cp as.xml shark-combined_APmags.xml
