#!/bin/bash
# Create directory structure (IIIF script requires it)
mkdir -p ${ACCESS_DIR}
# Fetch the images
aws s3 sync s3://${SRC_BUCKET}/${ACCESS_DIR} ${ACCESS_DIR}
# Fetch the CSV file
aws s3 sync s3://${SRC_BUCKET}/${CSV_PATH} .
# Generate the tiles
ruby create_iiif_s3.rb ${CSV_NAME} ${ACCESS_DIR} ${DEST_URL} ${DEST_BUCKET} --upload_to_s3=${UPLOAD_BOOL}
# Upload generated tiles
aws s3 sync tmp/${DEST_BUCKET}/ s3://${AWS_BUCKET_NAME}/${DEST_BUCKET}