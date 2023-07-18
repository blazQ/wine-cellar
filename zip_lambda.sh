#!/bin/bash

# This script zips all lambdas in the project by assuming that there's a config file in the source folder and 
# all command-line arguments are contained in the src/lambdas folder

# Source folder containing the files
source_folder="./src"
lambdas_folder="/lambdas"

if [[ $# -eq 0 ]]; then
    echo "Error: Please provide at least one filename as a command-line argument."
    exit 1
fi

# Initialize a counter to generate unique zip file names
counter=1

# Loop through each filename passed as a command-line argument
for filename in "$@"; do
    # Check if the file exists in the source folder
    if [[ -f "$source_folder/$lambdas_folder/$filename" ]]; then
        # Zip the files without including the parent directory
        zip -j "function$counter.zip" "$source_folder/$lambdas_folder/$filename" "$source_folder/config.py"

        echo "Created function$counter.zip"
    else
        echo "File '$filename' not found in the source folder. Skipping."
    fi

    # Increment the counter for the next iteration
    ((counter++))
done
