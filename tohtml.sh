#!/bin/bash
# find . -name "*.ipynb" | xargs jupyter nbconvert {} --to script

for file in $(find . -name *.ipynb)
do
   jupyter nbconvert "$file" --to html
   htmlFile="${file/.ipynb/.html}"
   dest="./papers/html-nbconv/${htmlFile:2}"
   mkdir -p `dirname "$dest"`
   mv -v "$htmlFile" "$dest"
   # cp -Rv "$htmlFile" "$dest"
   # rm "$htmlFile"
done
