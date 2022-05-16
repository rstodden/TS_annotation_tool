#!/bin/bash

# download data
svn checkout https://github.com/facebookresearch/asset/trunk/dataset
mv dataset asset

cd asset/
rm -r .svn

# add copyright line and rename files
for filename in ./*; do
    today=$(date '+%Y-%m-%d');
    new_filename=$(basename "$filename");
    new_filename="${new_filename//./_}.txt";
    new_filename="${new_filename//simp/simple}";
    new_filename="${new_filename//orig/complex}";
    metadataline="# &copy; Origin: https://github.com/facebookresearch/asset [last accessed: $today]\t$new_filename";
    sed -i "1i$metadataline" $filename;
    mv $(basename "$filename") $new_filename;
done

# add parallel complex file for each simple file
for i in $(seq 0 9); do
  cp asset_test_complex.txt asset_test_complex_$i.txt;
  sed -i '1d' asset_test_complex_$i.txt;
  metadataline="# &copy; Origin: https://github.com/facebookresearch/asset [last accessed: $today]\tasset_test_complex_$i.txt";
  sed -i "1i$metadataline" asset_test_complex_$i.txt;

  cp asset_valid_complex.txt asset_valid_complex_$i.txt;
  metadataline="# &copy; Origin: https://github.com/facebookresearch/asset [last accessed: $today]\tasset_valid_complex_$i.txt";
  sed -i '1d' asset_valid_complex_$i.txt;
  sed -i "1i$metadataline" asset_valid_complex_$i.txt;
done

# remove original files
rm asset_test_complex.txt
rm asset_valid_complex.txt