import boto3
import botocore.exceptions
import ConfigParser
import argparse
import os
import time


def get_dynamodb_client(aws_access_key_id, aws_secret_access_key, region):
    client = boto3.client(
        'dynamodb',
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key,
        region_name = region)
    return client


class DynamoDb(object):
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='us-west-2'):
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._region_name = region_name

    def list_tables(self):
        client = get_dynamodb_client(self._aws_access_key_id, self._aws_secret_access_key, self._region_name)
        response = client.list_tables()
        for table in response['TableNames']:
            self.output_table_details(table)

    def output_table_details(self, table_name):
        client = get_dynamodb_client(self._aws_access_key_id, self._aws_secret_access_key, self._region_name)
        response = client.describe_table(TableName=table_name)
        table_size = response['Table']['TableSizeBytes']
        # print('ARN: %s' % response['Table']['TableName'])
        print('%s\t%s' % (table_name, table_size))

    def delete_tables(self, file_path):
        print(file_path)
        client = get_dynamodb_client(self._aws_access_key_id, self._aws_secret_access_key, self._region_name)
        with open(file_path, 'r') as to_delete:
            for table_name in to_delete.readlines():
                table_name = table_name.strip()
                try:
                    print(table_name),
                    response = client.delete_table(TableName=table_name)
                    print(response['TableDescription']['TableStatus'])
                    time.sleep(3)
                except botocore.exceptions.ClientError:
                    continue


if __name__ == "__main__":

    description = "Quickly reduce autoscaling groups down to zero instances"
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Default region name", default="us-west-2")
    parser.add_argument("-a", "--account", help="Name of AWS account to apply")
    parser.add_argument("-c", "--config", help="Path to local existing config file",
                        default=os.path.join(os.getenv("HOME"),".aws", "credentials"))
    parser.add_argument("-f", "--file", help="Path to local existing file with list of tables to delete",
                        default=os.path.join(os.getcwd(), "to_delete.txt"))
    args = parser.parse_args()

    config_file = args.config
    account = args.account
    conf = ConfigParser.ConfigParser()
    conf.read(config_file)
    aws_access_key_id = conf.get(account, 'aws_access_key_id')
    aws_secret_access_key = conf.get(account, 'aws_secret_access_key')

    dynamodb = DynamoDb(aws_access_key_id, aws_secret_access_key)
    dynamodb.list_tables()
    dynamodb.delete_tables(args.file)

