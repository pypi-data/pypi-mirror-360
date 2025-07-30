#!/bin/bash

SNAPSHOT_DIR="$1"
OUTPUT_FILE="$2"

if [ -z "$SNAPSHOT_DIR" ]; then
    echo "Usage: $0 <directory_to_snapshot> [output_file.snap | --diff <old_snap> <new_snap> <output_diff.txt>]"
    exit 1
fi

# Function to create a snapshot
create_snapshot() {
    local target_dir="$1"
    local output_file="$2"
    echo "Creating snapshot of '$target_dir' to '$output_file'..."
    find "$target_dir" -type f -print0 | xargs -0 stat --format="%n %s %X" > "$output_file"
    echo "Snapshot created."
}

# Function to diff snapshots by atime
diff_snapshots() {
    local old_snap="$1"
    local new_snap="$2"
    local output_diff="$3"
    echo "Diffing snapshots '$old_snap' and '$new_snap' to '$output_diff' by atime..."

    # Read snapshots into associative arrays for efficient lookup
    declare -A old_files new_files

    while IFS= read -r line; do
        read -r path size atime <<< "$line"
        old_files["$path"]="$atime"
    done < "$old_snap"

    while IFS= read -r line; do
        read -r path size atime <<< "$line"
        new_files["$path"]="$atime"
    done < "$new_snap"

    # Compare atimes and write changed paths to output
    > "$output_diff" # Clear the output file
    for path in "${!new_files[@]}"; do
        if [[ -n "${old_files[$path]}" && "${old_files[$path]}" != "${new_files[$path]}" ]]; then
            echo "$path" >> "$output_diff"
        elif [[ -z "${old_files[$path]}" ]]; then
            # File is new, consider it changed too (or filter if not desired)
            echo "$path (new)" >> "$output_diff"
        fi
    done

    for path in "${!old_files[@]}"; do
        if [[ -z "${new_files[$path]}" ]]; then
            # File was deleted, also consider it changed (or filter)
            echo "$path (deleted)" >> "$output_diff"
        fi
    done

    echo "Diff completed."
}

if [ "$2" = "--diff" ]; then
    if [ -z "$5" ]; then
        echo "Usage: $0 <directory_to_snapshot> --diff <old_snap> <new_snap> <output_diff.txt>"
        exit 1
    fi
    diff_snapshots "$3" "$4" "$5"
else
    create_snapshot "$1" "$2"
fi