#!/bin/bash
# Generate random directory and enter it
TMPDIR=$(mktemp -d --tmpdir=$(pwd)/tmp)
cd ${TMPDIR}
cp ../../*.* .
# Create directory structure (IIIF script requires it)
mkdir -p ${ACCESS_DIR}
# Fetch the images
aws s3 sync s3://${SRC_BUCKET}/${DIR_PREFIX}/${ACCESS_DIR} ${ACCESS_DIR}
# Fetch the CSV file
aws s3 cp s3://${SRC_BUCKET}/${CSV_PATH}/${CSV_NAME} .
# Generate the tiles
ruby create_iiif_s3.rb ${CSV_NAME} ${ACCESS_DIR}/ ${DEST_URL} ${DEST_PREFIX} --upload_to_s3=${UPLOAD_BOOL}
# Put CSV files in the proper place
cp ${CSV_NAME} tmp/${DEST_PREFIX}/${COLLECTION_NAME}/${CSV_NAME::-4}/
# Upload generated tiles
aws s3 sync tmp/${DEST_PREFIX}/ s3://${DEST_BUCKET}/${DEST_PREFIX}/
# Delete tmpdir
rm -rf ${TMPDIR}
