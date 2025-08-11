#! /bin/bash

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


## pylsl package

pip3 install pylsl

