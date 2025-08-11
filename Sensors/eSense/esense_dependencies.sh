#!/bin/bash

## empty package

sudo apt update

EMPTY_TAR_URL="https://sourceforge.net/projects/empty/files/empty/empty-0.6.23c/empty-0.6.23c.tgz/download"

EMPTY_TAR_FILE="empty.tgz"

# downloading it in download directory

DIR="$HOME/Downloads"

wget -O "$DIR/$EMPTY_TAR_FILE" "$EMPTY_TAR_URL"

sudo tar -xzf "$DIR/$EMPTY_TAR_FILE" -C "$DIR"

cd "$DIR/empty-0.6.23c"

# echo current directory
echo "Current directory: $(pwd)"

sudo make

sudo make install

# # check if the installation was successful

# if command which empty; then
#     echo "Empty package installed successfully."
# else
#     echo "Failed to install the empty package."
#     exit 1
# fi
