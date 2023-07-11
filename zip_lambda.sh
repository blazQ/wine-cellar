#!/bin/bash

# Define the source and destination folders
src_folder="src"
dest_folder="destination"

# Create the destination folder if it doesn't exist
mkdir -p "$dest_folder"

# Copy the files from src folder to the destination folder
cp "$src_folder/vaporFunc.py" "$dest_folder"
cp "$src_folder/config.py" "$dest_folder"

# Navigate to the destination folder
cd "$dest_folder"

# Create a zip file of the files
zip -j ../function.zip *

# Return to the previous directory
cd ..

# Delete the destination folder
rm -r "$dest_folder"

echo "Files copied, zipped, and destination folder deleted successfully."

