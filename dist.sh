#!/bin/bash

cd `dirname $0`
PROJECT_DIR=`pwd`
TARGET_DIR=`mktemp -d`

mkdir $TARGET_DIR/pyshock
cd $TARGET_DIR

cp -ax $PROJECT_DIR/src/* pyshock
cp -ax $PROJECT_DIR/doc pyshock
cp -ax $PROJECT_DIR/*.md pyshock
rm -rf __pycache__
rm -rf */__pycache__
rm -rf */*/__pycache__
rm -rf */*/*/__pycache__
rm -rf */*/*/*/__pycache__

. $PROJECT_DIR/src/pyshock/core/version.py
mkdir -p $PROJECT_DIR/dist
rm -rf $PROJECT_DIR/dist/*
zip -r $PROJECT_DIR/dist/pyshock-$VERSION.zip . 
rm -rf $TARGET_DIR