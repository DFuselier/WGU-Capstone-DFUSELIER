#!/bin/bash

MAX_RETRIES=5000             # Maximum number of retries
RETRY_DELAY=2                # Delay in seconds between retries

function download_file() {
    read -p "Enter the URL: " URL
    read -p "Enter the download directory (default: ./downloads): " DOWNLOAD_DIR
    DOWNLOAD_DIR=${DOWNLOAD_DIR:-"./downloads"}
    read -p "Enter the new file name (including the file format, e.g., file.zip): " NEW_FILENAME

    # Ensure the download directory exists
    mkdir -p "$DOWNLOAD_DIR"

    # Extract original filename from URL
    ORIGINAL_FILENAME=$(basename "$URL")
    OUTPUT_PATH="$DOWNLOAD_DIR/$ORIGINAL_FILENAME"
    RENAMED_PATH="$DOWNLOAD_DIR/$NEW_FILENAME"

    echo "Downloading: $URL"
    echo "Download directory: $DOWNLOAD_DIR"
    echo "New file name: $NEW_FILENAME"

    retry=0
    while [ $retry -lt $MAX_RETRIES ]; do
        echo "Attempt: $((retry+1))"
        torsocks wget -O "$OUTPUT_PATH" "$URL"

        if [ $? -eq 0 ]; then
            echo "Download successful!"
            mv "$OUTPUT_PATH" "$RENAMED_PATH"
            echo "File renamed to: $NEW_FILENAME"
            break
        else
            echo "Download failed. Retrying in $RETRY_DELAY seconds..."
            sleep $RETRY_DELAY
            retry=$((retry+1))
        fi
    done

    if [ $retry -eq $MAX_RETRIES ]; then
        echo "Max retries reached. Download failed."
        exit 1
    fi

    process_file "$RENAMED_PATH" "$DOWNLOAD_DIR"
}

function process_file() {
    local FILE_PATH=$1
    local DIRECTORY=$2

    # Check if the file is a ZIP file and unzip it
    if [[ "$FILE_PATH" == *.zip ]]; then
        echo "Extracting ZIP file: $FILE_PATH"
        unzip -o "$FILE_PATH" -d "$DIRECTORY"

        if [ $? -eq 0 ]; then
            echo "Extraction successful!"
            search_directory "$DIRECTORY"
        else
            echo "Extraction failed!"
        fi
    else
        echo "The file is not a ZIP archive. Skipping extraction."
        search_directory "$DIRECTORY"
    fi
}

function search_directory() {
    local DIRECTORY=$1
    read -p "Enter keywords to search for (comma-separated, no spaces): " KEYWORDS

    IFS=',' read -r -a keyword_array <<< "$KEYWORDS"
    echo "Searching for keywords in directory: $DIRECTORY"

    for keyword in "${keyword_array[@]}"; do
        echo "Searching for keyword: $keyword"
        grep -iR "$keyword" "$DIRECTORY" > "${DIRECTORY}/search_results_$keyword.txt"
        if [ $? -eq 0 ]; then
            echo "Keyword '$keyword' found! Results saved in ${DIRECTORY}/search_results_$keyword.txt"
        else
            echo "Keyword '$keyword' not found in the directory."
        fi
    done
}

function main_menu() {
    echo "Choose an option:"
    echo "1) Download a file and process it"
    echo "2) Skip downloading and process an existing file"
    echo "3) Skip unzipping and search a specific directory"
    echo "4) Exit"

    read -p "Enter your choice: " CHOICE

    case $CHOICE in
        1)
            download_file
            ;;
        2)
            read -p "Enter the path of the file to process (including the file name): " FILE_PATH
            read -p "Enter the directory for extracted files (default: ./downloads): " DIRECTORY
            DIRECTORY=${DIRECTORY:-"./downloads"}
            process_file "$FILE_PATH" "$DIRECTORY"
            ;;
        3)
            read -p "Enter the directory to search in: " DIRECTORY
            search_directory "$DIRECTORY"
            ;;
        4)
            echo "Exiting script. Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Start the menu
main_menu