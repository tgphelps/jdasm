#!/bin/sh

find . -name '*.class' | xargs ./jdasm -d
