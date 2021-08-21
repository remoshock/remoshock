#!/bin/bash

# setup folders
cd `dirname $0`
PROJECT_DIR=`pwd`
TARGET_DIR=`mktemp -d`
mkdir $TARGET_DIR/remoshock
cd $TARGET_DIR

# update version
. $PROJECT_DIR/src/remoshock/core/version.py
cp $PROJECT_DIR/README.md $TARGET_DIR/remoshock
sed "s/\([v\-]\)[0-9][0-9]*\.[0-9][0-9]*\([/.\-]\)/\1$VERSION\2/g" < $TARGET_DIR/remoshock/README.md > $PROJECT_DIR/README.md
rm $TARGET_DIR/remoshock/README.md


# copy files to temporary folder with the desired directory structure
cp -ax $PROJECT_DIR/src/* remoshock
cp -ax $PROJECT_DIR/docs remoshock
cp -ax $PROJECT_DIR/*.md remoshock
rm -rf __pycache__
rm -rf */__pycache__
rm -rf */*/__pycache__
rm -rf */*/*/__pycache__
rm -rf */*/*/*/__pycache__

# create the .zip file
mkdir -p $PROJECT_DIR/build
rm -rf $PROJECT_DIR/build/*
zip -r $PROJECT_DIR/build/remoshock-$VERSION.zip . 

# clean up
rm -rf $TARGET_DIR
