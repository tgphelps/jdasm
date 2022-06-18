#!/bin/sh

find classes -name '*.class' | xargs ./jdasm -d
