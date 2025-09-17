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


## LSL package

#!/bin/bash

## liblsl package

sudo apt update

sudo apt install -y libpugixml1v5 wget

# wget https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-jammy_amd64.deb

# sudo dpkg -i liblsl-1.16.2-jammy_amd64.deb

# sudo apt-get install -f -y


LIBLSL_URL="https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-jammy_amd64.deb"

LIBLSL_FILE="liblsl.deb"

# temp directory for downloading the package
TEMP_DIR=$(mktemp -d)

wget -O "$TEMP_DIR/$LIBLSL_FILE" "$LIBLSL_URL"

sudo dpkg -i "$TEMP_DIR/$LIBLSL_FILE"

sudo apt-get install -f -y

# clean up
rm -rf "$TEMP_DIR"


