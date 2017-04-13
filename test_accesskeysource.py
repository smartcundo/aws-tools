from accesskeysource import *
import os
from ConfigParser import ConfigParser
import argparse


COMPANY_NAME = "SmartTech"
CLOUDWATCH_NAMESPACE = "%s/ReservedInstances" % COMPANY_NAME
CLOUDWATCH_NAMESPACE_REGION = "%s/ReservedInstancesByRegion" % COMPANY_NAME
CLOUDWATCH_NAMESPACE_FOOTPRINT_REGION = "%s/FootprintByRegion" % COMPANY_NAME
RUNNING_INSTANCES_METRIC_NAME = "Running Instances"
RESERVED_INSTANCES_METRIC_NAME = "Reserved Instances"
RUNNING_FOOTPRINT_METRIC_NAME = "Running Instance Footprint"
RESERVED_FOOTPRINT_METRIC_NAME = "Reserved Instance Footprint"


def test_handle(lambda_context):
    # describe_running_instance_family_metrics(RUNNING_FOOTPRINT_METRIC_NAME, "m4", "None", **lambda_context)
    test_event = {
        "awslogs": {
            "data": "H4sIAAAAAAAAAHWPwQqCQBCGX0Xm7EFtK+smZBEUgXoLCdMhFtKV3akI8d0bLYmibvPPN3wz00CJxmQnTO41whwWQRIctmEcB6sQbFC3CjW3XW8kxpOpP+OC22d1Wml1qZkQGtoMsScxaczKN3plG8zlaHIta5KqWsozoTYw3/djzwhpLwivWFGHGpAFe7DL68JlBUk+l7KSN7tCOEJ4M3/qOI49vMHj+zCKdlFqLaU2ZHV2a4Ct/an0/ivdX8oYc1UVX860fQDQiMdxRQEAAA=="
        }
}
    lambda_handler(test_event, lambda_context)


if __name__ == "__main__":

    description = "Test Lambda function for optimizing EC2 instance pricing"
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Default region name", default="us-west-2")
    parser.add_argument('-s', "--select", help='For each AWS account, prompt to apply change',
                        action='store_true', default=False)
    parser.add_argument("-a", "--accounts", help="Name of AWS accounts to apply to (,-separated)")
    parser.add_argument("-c", "--config", help="Path to local existing config file",
                        default=os.path.join(os.getenv("HOME"),".aws", "credentials"))
    args = parser.parse_args()

    region_name = args.region
    config_file = args.config
    conf = ConfigParser()
    conf.read(config_file)
    account = "profile amp"
    aws_access_key_id = conf.get(account,'aws_access_key_id')
    aws_secret_access_key = conf.get(account,'aws_secret_access_key')

    lambda_args = {
        "region_name": region_name,
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key
    }
    test_handle(lambda_args)
