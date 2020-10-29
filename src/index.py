import json
import urllib.parse
import boto3
import argparse
import os
import sys
import time

from datetime import datetime
from botocore.compat import total_seconds

print('Loading function')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    inputFileName = ""
    bucketName = ""

    for record in event['Records']:
      bucketName = record['s3']['bucket']['name']
      inputFileName = record['s3']['object']['key']

    print(bucketName)
    print(inputFileName)

    try:
        response = s3.get_object(Bucket=bucketName, Key=inputFileName)
        print("CONTENT TYPE: " + response['ContentType'])
        filecontent = response['Body'].read().decode('utf-8')
        content = json.loads(filecontent)
        for envs in content['environment']:
            if envs['name'] == 'AWS_REGION':
                region_name = envs['value']

        batch = boto3.client(
            service_name='batch',
            region_name=region_name,
            endpoint_url='https://batch.'+ region_name +'.amazonaws.com')

        cloudwatch = boto3.client(
            service_name='logs',
            region_name=region_name,
            endpoint_url='https://logs.'+ region_name +'.amazonaws.com')

        spin = ['-', '/', '|', '\\', '-', '/', '|', '\\']
        logGroupName = '/aws/batch/job'

        jobName = content['jobName']
        jobQueue = content['jobQueue']
        jobDefinition = content['jobDefinition']
        command = []
        command.append(content['command'])
        wait = None

        envlist = createEnvList(content['environment'])

        submitJobResponse = batch.submit_job(
            jobName=jobName,
            jobQueue=jobQueue,
            jobDefinition=jobDefinition,
            containerOverrides={
                'command': command,
                'environment': envlist
            }
        )

        jobId = submitJobResponse['jobId']
        print ('Submitted job [%s - %s] to the job queue [%s]' % (jobName, jobId, jobQueue))

        spinner = 0
        running = False
        startTime = 0

        while wait:
            time.sleep(1)
            describeJobsResponse = batch.describe_jobs(jobs=[jobId])
            status = describeJobsResponse['jobs'][0]['status']
            if status == 'SUCCEEDED' or status == 'FAILED':
                print ('%s' % ('=' * 80))
                print ('Job [%s - %s] %s' % (jobName, jobId, status))
                break
            elif status == 'RUNNING':
                logStreamName = getLogStream(logGroupName, jobName, jobId)
                if not running and logStreamName:
                    running = True
                    print ('\rJob [%s - %s] is RUNNING.' % (jobName, jobId))
                    print ('Output [%s]:\n %s' % (logStreamName, '=' * 80))
                if logStreamName:
                    startTime = printLogs(logGroupName, logStreamName, startTime) + 1
            else:
                print ('\rJob [%s - %s] is %-9s... %s' % (jobName, jobId, status, spin[spinner % len(spin)]), sys.stdout.flush())
                spinner += 1

        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


def printLogs(logGroupName, logStreamName, startTime):
    kwargs = {'logGroupName': logGroupName,
              'logStreamName': logStreamName,
              'startTime': startTime,
              'startFromHead': True}

    lastTimestamp = 0
    while True:
        logEvents = cloudwatch.get_log_events(**kwargs)

        for event in logEvents['events']:
            lastTimestamp = event['timestamp']
            timestamp = datetime.utcfromtimestamp(lastTimestamp / 1000.0).isoformat()
            print ('[%s] %s' % ((timestamp + ".000")[:23] + 'Z', event['message']))

        nextToken = logEvents['nextForwardToken']
        if nextToken and kwargs.get('nextToken') != nextToken:
            kwargs['nextToken'] = nextToken
        else:
            break
    return lastTimestamp

def getLogStream(logGroupName, jobName, jobId):
    response = cloudwatch.describe_log_streams(
        logGroupName=logGroupName,
        logStreamNamePrefix=jobName + '/' + jobId
    )
    logStreams = response['logStreams']
    if not logStreams:
        return ''
    else:
        return logStreams[0]['logStreamName']

def nowInMillis():
    endTime = long(total_seconds(datetime.utcnow() - datetime(1970, 1, 1))) * 1000
    return endTime

def createEnvList(content):

    envlist = []

    for env in content:
        if env['name'] == 'AWS_REGION':
            value = env['value']
            region = {'name': 'AWS_REGION', 'value': value}
            envlist.append(region)
        elif env['name'] == 'UPLOAD_BOOL':
            value = env['value']
            upload = {'name': 'UPLOAD_BOOL', 'value': value}
            envlist.append(upload)
        elif env['name'] == 'SRC_BUCKET':
            value = env['value']
            src_bucket = {'name': 'SRC_BUCKET', 'value': value}
            envlist.append(src_bucket)
        elif env['name'] == 'AWS_BUCKET_NAME':
            value = env['value']
            aws_bucket_name = {'name': 'AWS_BUCKET_NAME', 'value': value}
            envlist.append(aws_bucket_name)
        elif env['name'] == 'CSV_NAME':
            value = env['value']
            csv_name = {'name': 'CSV_NAME', 'value': value}
            envlist.append(csv_name)
        elif env['name'] == 'ACCESS_DIR':
            value = env['value']
            access_dir = {'name': 'ACCESS_DIR', 'value': value}
            envlist.append(access_dir)
        elif env['name'] == 'CSV_PATH':
            value = env['value']
            csv_path = {'name': 'CSV_PATH', 'value': value}
            envlist.append(csv_path)
        elif env['name'] == 'DEST_BUCKET':
            value = env['value']
            dest_bucket = {'name': 'DEST_BUCKET', 'value': value}
            envlist.append(dest_bucket)
        elif env['name'] == 'DEST_URL':
            value = env['value']
            dest_url = {'name': 'DEST_URL', 'value': value}
            envlist.append(dest_url)

    return envlist