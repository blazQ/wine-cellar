#!/bin/bash

# Source folder containing the files
source_folder="src"

# Destination folder to store the zipped file
destination_folder="zip"

# Filename passed as a command-line argument
filename="$1"

if [[ -z "$filename" ]]; then
    echo "Error: Please provide a filename as a command-line argument."
    exit 1
fi

# Create the destination folder if it doesn't exist
mkdir -p "$destination_folder"

# Copy the file to the destination folder
cp "$source_folder/lambdas/$filename" "$destination_folder/$filename"
cp "$source_folder/config.py" "$destination_folder/config.py"

# Change to the destination folder
cd "$destination_folder" || exit

# Zip the file without including the parent directory
zip -j function.zip "$filename" "config.py"

mv function.zip ..

# Move back to the original directory
cd - || exit

# Clean up the destination folder
rm -dr zip
