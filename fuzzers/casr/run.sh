#!/bin/bash
export PATH=$PATH:${SRC}/cargo/bin

target_dir=$DST
reports_dir=$target_dir/reports
reports_dedup_dir=$target_dir/reports_dedup
reports_dedup_cluster_dir=$target_dir/reports_dedup_cluster
summary_path=$target_dir/summary_by_unique_line
failed_dir=$target_dir/failed
reports_unique_line=$target_dir/reports_unique_line

target_args="$PROGRAM/$(cat $TARGET/target_args)"
crashes_dir=$(find "$SHARED" -type d -name "crashes" -print)
if [ -z "$crashes_dir" ]; then
    echo "Error: crashes_dir not found"
    exit 1
fi
mkdir -p $reports_dir $failed_dir $reports_unique_line

current_jobs=0
for file in "$crashes_dir"/*; do
    if [ -f "$file" ]; then          # if file
        filename=$(basename "$file") # get the filename
        if [[ "$filename" == id* ]] && [ ! -e "$reports_dir/$filename".casrep ] && [ ! -e "$failed_dir/$filename" ]; then
            (
                if [[ $target_args == *"@@"* ]]; then
                    casr-san -t 10 -o "$reports_dir/$filename".casrep -- ${target_args//@@/$file}
                else
                    casr-san -t 10 -o "$reports_dir/$filename".casrep --stdin $file -- $target_args
                fi
                if [ $? -ne 0 ]; then
                    if [[ $target_args == *"@@"* ]]; then
                        casr-san -t 10 -o "$reports_dir/$filename".casrep -- ${target_args//@@/$file} 2>$failed_dir/$filename
                    else
                        casr-san -t 10 -o "$reports_dir/$filename".casrep --stdin $file -- $target_args 2>$failed_dir/$filename
                    fi
                fi
            ) &
            ((current_jobs++))
            if [ "$current_jobs" -ge $(nproc) ]; then
                wait -n
                ((current_jobs--))
            fi
        fi
    fi
done

wait
rm -rf $reports_dedup_dir $reports_dedup_cluster_dir $summary_path $summary_by_unique_line
casr-cluster -d $reports_dir $reports_dedup_dir
casr-cluster -c $reports_dedup_dir $reports_dedup_cluster_dir
if [ -d "$reports_dedup_dir" ]; then
    casr-cli -u $reports_dedup_dir >$summary_path
else
    casr-cli -u $reports_dir >$summary_path
fi
grep -oP 'Crash: \S+' $summary_path | awk -F' ' '{print $2}' | xargs -I {} cp {} "$reports_unique_line"/
find "$target_dir" -type d -empty -delete
