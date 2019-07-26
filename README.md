# aws-batch-iiif-generator

## Workflow
![Overview](images/overview.png "Overview")
1. Upload task file to the batch bucket
2. Batch bucket trigger a lambda function
3. Lambda function read the content in the task file and submit a batch job
4. Each batch job generates tiles and manifests from the original image and upload to the target S3 bucket

![Batch Job](images/batch_job.png "Batch Job")
1. Pull raw original files from the S3 bucket
2. Generate tiles and manifests
3. Upload to target S3 bucket

## Batch
* Compute environment: [computeenv.json](examples/computeenv.json)
* Job Definition: [jobdefinition.json](examples/jobdefinition.json)
* Job Queue: [jobqueue.json](examples/jobqueue.json)

## S3
* SRC_BUCKET: For raw images and CSV files to be processed
	* Raw image files
	* CSV files
* AWS_BUCKET_NAME: For saving tiles and manifests files
* Batch_Bucket: For task files

## Lambda
* [lambda-example.py](examples/lambda-example.py): Submit a batch job when a task file is upload to a S3 bucket
	* Add S3 trigger: 
		* Event type: ObjectCreated

## IAM
* lambda_function_role: Append Read access to S3 buckets and permission to submit a batch job policy
* ecsInstanceRole: Append Read/Write access to S3 buckets policy

## Task File
* example: [task.json](examples/task.json)
```
    jobName: Batch job name
    jobQueue: Batch job queue name
    jobDefinition: Batch job definition name
    command: "./createiiif.sh"
    AWS_REGION: AWS region, e.g. us-east-1
    SRC_BUCKET: S3 bucket which stores the images need to be processed. (Source S3 bucket)
    AWS_BUCKET_NAME: S3 bucket which stores the generated tile images and manifests files. (Target S3 bucket)
    ACCESS_DIR: Path to the image folder under the SRC_BUCKET
    CSV_NAME: A CSV file with title and description of the images
    CSV_PATH: Path to the csv folder under the SRC_BUCKET
    DEST_BUCKET: Folder to store the generated tile images and manifests files under AWS_BUCKET_NAME
    DEST_URL: Root URL for accessing the manifests e.g. https://s3.amazonaws.com/AWS_BUCKET_NAME
    UPLOAD_BOOL: upload tiles and manifests to S3 (true|false)
```

## IIIF S3 Docker image
* [iiif_s3_docker](docker)
* Image at Docker Hub: [yinlinchen/vtl:iiifs3batch](https://cloud.docker.com/repository/docker/yinlinchen/vtl/tags)
