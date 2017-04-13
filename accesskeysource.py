import sys
import boto3
from boto3.session import Session
import datetime
import logging
import time


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOGGER.addHandler(ch)


class BotoClientName:
    cloudwatch = "cloudwatch"
    logs = "logs"

    def __init__(self):
        pass


def query_cloudtrail_logs( **kwargs):
    epoch_time_now = int(time.time())
    request_args = {
        'logGroupName' : 'CloudTrail/DefaultLogGroup',
        'logStreamName' : '%s_CloudTrail_%s' % ('601133174511','us-west-2'),
        'startTime' : epoch_time_now - (60 * 60),
        'endTime' : epoch_time_now
    }

    s = Session(**kwargs)
    logs_client = s.client(BotoClientName.logs)
    groups = logs_client.describe_log_groups()['logGroups']
    for group in groups:
        print(group['logGroupName'])
    log_events = logs_client.get_log_events(**request_args)
    request_args['nextToken'] = log_events['nextBackwardToken']
    return logs_client.get_log_events(**request_args)
    # LOGGER.info("Published %s metric data in namespace %s" % (metric_name, namespace))


def lambda_handler(event, _context):
    logs = query_cloudtrail_logs(**_context)
    print(logs)

if __name__ == "__main__":
    print(int(time.time()))
