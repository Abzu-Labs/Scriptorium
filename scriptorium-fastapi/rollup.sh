#!/bin/bash

# Output file
output_file="combined.txt"

# Base directory to start from
base_dir="."

# List of files and directories to ignore
declare -a ignore_list=("node_modules" "yarn.lock" "package-lock.json" "content-rollups" "/env")

# Function that checks if a file or directory should be ignored
is_ignored() {
  for i in "${ignore_list[@]}"; do
    if [[ "$1" == *"$i"* ]]; then
      return 0
    fi
  done
  return 1
}

# Function that checks if a file has a specific extension
has_extension() {
  if [[ "$1" == *"$2"* ]]; then
    return 0
  fi
  return 1
}

# Function that combines files
combine_files() {
  for file in "$1"/*; do
    # If it's a directory, recursively call this function
    if [ -d "${file}" ]; then
      # If directory is not a hidden one and not in the ignore list, process it
      if [[ $(basename "${file}") != .* ]] && ! is_ignored "${file}"; then
        combine_files "${file}"
      fi
    # If it's a file, append the filename as a comment and the file's contents to the output file
    elif [ -f "${file}" ]; then
      # If file is not a hidden one, not in the ignore list, and not a .png file, process it
      if [[ $(basename "${file}") != .* ]] && ! is_ignored "${file}" && ! has_extension "${file}" ".png"; then
        echo "Processing ${file}"
        echo -e "\n# Filename: ${file}\n" >> "${output_file}"
        cat "${file}" >> "${output_file}"
      fi
    fi
  done
}

# Remove the output file if it already exists
if [ -f "${output_file}" ]; then
  rm "${output_file}"
fi

# Start the file combination
combine_files "${base_dir}"
