#!/bin/bash

rm -rf weldbench

virtualenv -p python2.7 weldbench
source weldbench/bin/activate

# Install requirements
pip install -r requirements.txt

# Weld should be installed here...
cd ~/weld
cargo build --release

cd python/pyweld
python setup.py install
cd ..

cd numpy
python setup.py install
cd ..

cd grizzly
python setup.py install
