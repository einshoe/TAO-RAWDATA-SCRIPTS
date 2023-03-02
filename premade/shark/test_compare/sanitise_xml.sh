#!/bin/bash
# the "&" is not legal for xml readers
sed -e "s| & |\&amp;|g" $1
