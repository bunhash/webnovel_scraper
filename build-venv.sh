#!/bin/bash
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Initializes venv
#

if [ ! -d venv ]; then
    virtualenv venv
fi
source venv/bin/activate
pip install -r requirements.txt
