#!/bin/bash
set -e

target_dir=$TRIAGE_BY_CASR
reports_dir=$target_dir/reports
reports_dedup_dir=$target_dir/reports_dedup
reports_dedup_cluster_dir=$target_dir/reports_dedup_cluster
summary_path=$target_dir/summary_by_unique_line
failed_dir=$target_dir/failed
reports_unique_line=$target_dir/reports_unique_line

cd $SHARED
if [ ! -f "target_args" ]; then
    echo "Error: target_args not found"
    exit 1
fi
target_args="$OUT/$(cat target_args)"
crashes_dir=$(find "$(pwd)" -type d -name "crashes" -print)
if [ -z "$crashes_dir" ]; then
    echo "Error: crashes_dir not found"
    exit 1
fi
mkdir -p $reports_dir $failed_dir
for file in "$crashes_dir"/*; do
    if [ -f "$file" ]; then          # if file
        filename=$(basename "$file") # get the filename
        if [ "$filename" != "README.txt" ] && [ ! -e "$reports_dir/$filename".casrep ] && [ ! -e "$failed_dir/$filename" ]; then
            if [[ $target_args == *"@@"* ]]; then
                casr-san -o "$reports_dir/$filename".casrep -- ${target_args//@@/$file} 2>$failed_dir/$filename || true
            else
                casr-san -o "$reports_dir/$filename".casrep -- $target_args <$file 2>$failed_dir/$filename || true
            fi
        fi
    fi
done
if [ -d "$failed_dir" ] && [ -z "$(ls -A $failed_dir)" ]; then
    rmdir "$failed_dir"
fi
rm -rf $reports_dedup_dir $reports_dedup_cluster_dir $summary_path $summary_by_unique_line
if [ -n "$(ls -A $reports_dir)" ]; then
    casr-cluster -d $reports_dir $reports_dedup_dir || true
fi
if [ -n "$(ls -A $reports_dedup_dir)" ]; then
    casr-cluster -c $reports_dedup_dir $reports_dedup_cluster_dir || true
fi
if [ -n "$(ls -A $reports_dedup_dir)" ]; then
    casr-cli -u $reports_dedup_dir >$summary_path || true
else
    casr-cli -u $reports_dir >$summary_path || true
fi
mkdir -p $reports_unique_line
grep -oP 'Crash: \S+' $summary_path | awk -F' ' '{print $2}' | xargs -I {} cp {} "$reports_unique_line"/
