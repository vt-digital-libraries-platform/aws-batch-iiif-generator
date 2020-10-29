# aws-batch-iiif-generator
## Publication
* [Code4Lib Journal - Scaling IIIF Image Tiling in the Cloud](https://journal.code4lib.org/articles/14933)

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

### Deploy aws-batch-iiif-generator using CloudFormation stack
#### Step 1: Launch CloudFormation stack
[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?&templateURL=https://vtdlp-dev-cf.s3.amazonaws.com/awsiiifs3batch.template)

Click *Next* to continue

#### Step 2: Specify stack details

| Name | Description |
|----------|-------------|
| Stack name | any valid name |
| BatchRepositoryName | any valid name for Batch process repository |
| DockerImage | any valid Docker image. E.g. yinlinchen/vtl:iiifs3_v3 |
| JDName | any valid name for Job definition |
| JQName | any valid name for Job queue |
| LambdaFunctionName | any valid name for Lambda function |
| LambdaRoleName | any valid name for Lambda role  |
| S3BucketName | any valid name for S3 bucket |

#### Step 3: Configure stack options
Leave it as is and click **Next**

#### Step 4: Review
Make sure all checkboxes under Capabilities section are **CHECKED**

Click *Create stack*

### Deploy aws-batch-iiif-generator using AWS CLI

Run the following in your shell to deploy the application to AWS:
```bash
aws cloudformation create-stack --stack-name awsiiifs3batch --template-body file://awsiiifs3batch.template --capabilities CAPABILITY_NAMED_IAM
```

See [Cloudformation: create stack](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-stack.html) for `--parameters` option

### Usage
* Prepare [task.json](examples/task.json)
* Prepare [dataset](examples/sample_dataset.zip) and upload to S3 `SRC_BUCKET` bucket
* Upload [task.json](examples/task.json) to the S3 bucket created after the deployment.
* Go to `AWS_BUCKET_NAME` to see the end results for generated IIIF tiles and manifests.
* Test manifests in [Mirador](https://projectmirador.org/demo/) (Note: you need to configure S3 access permission and CORS settings)
* See our [Live Demo](https://d2fmsr62h737j1.cloudfront.net/index.html)

### Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name stackname
```

## Batch Configuration
* Compute Environment: Type: `EC2`, MinvCpus: `0`, MaxvCpus: `128`, InstanceTypes: `optimal`
* Job Definition: Type: `container`, Image: `DockerImage`, Vcpus: `2`, Memory: `2000`
* Job Queue: Priority: `10`

## S3
* SRC_BUCKET: For raw images and CSV files to be processed
	* Raw image files
	* CSV files
* AWS_BUCKET_NAME: For saving tiles and manifests files

## Lambda function
* [index.py](src/index.py): Submit a batch job when a task file is upload to a S3 bucket

## Task File
* example: [task.json](examples/task.json)

| Name | Description |
|----------|-------------|
| jobName | Batch job name |
| jobQueue | Batch job queue name |
| jobDefinition | Batch job definition name |
| command | "./createiiif.sh" |
| AWS_REGION | AWS region, e.g. us-east-1 |
| SRC_BUCKET | S3 bucket which stores the images need to be processed. (Source S3 bucket) |
| AWS_BUCKET_NAME | S3 bucket which stores the generated tile images and manifests files. (Target S3 bucket) |
| ACCESS_DIR | Path to the image folder under the SRC_BUCKET |
| CSV_NAME | A CSV file with title and description of the images |
| CSV_PATH | Path to the csv folder under the SRC_BUCKET |
| DEST_BUCKET | Folder to store the generated tile images and manifests files inside `AWS_BUCKET_NAME` |
| DEST_URL | Root URL for accessing the manifests e.g. https://s3.amazonaws.com/AWS_BUCKET_NAME |
| UPLOAD_BOOL | Default is `false`. Set it to `true` if you want to use upload_to_s3 [iiifS3](https://github.com/cmoa/iiif_s3) feature and use your customized docker image. |

## IIIF S3 Docker image
* [iiif_s3_docker](https://github.com/vt-digital-libraries-platform/iiif_s3_docker)
* Image at Docker Hub: [yinlinchen/vtl:iiifs3_v3](https://cloud.docker.com/repository/docker/yinlinchen/vtl/tags)
