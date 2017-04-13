import boto3
import botocore.exceptions
import ConfigParser
import argparse
import os
import sys
import getpass
import json
import datetime


class BotoClient:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._region = region
        self.add_client_methods()

    def add_client_methods(self):
        for service in ['dynamodb', 'iam']:
            client = boto3.client(
                service,
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
                region_name=self._region)
            setattr(self, 'get_%s_client' % service, client)

    def _partial(self, method_name, service_name):
        def func(self, *args, **kwargs):
            return boto3.client(
            service_name,
            aws_access_key_id = self._aws_access_key_id,
            aws_secret_access_key = self._aws_secret_access_key,
            region_name = self._region)


class Serializer(object):
    @classmethod
    def deserialize(self, data):
        if isinstance(data, list):
            return [self.deserialize(item) for item in data]
        elif isinstance(data, dict):
            if 'Users' in data:
                return [self.deserialize(item) for item in data['Users']]

            processed = {}
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    processed[k] = self.deserialize(v)
                else:
                    processed[k] = v
            return processed
        return data


class Iam:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region):
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._region = region

    def scan_users(self):
        b = BotoClient(self._aws_access_key_id, self._aws_secret_access_key, self._region)
        client = b.get_iam_client
        response = client.list_users()
        users = Serializer.deserialize(response)
        for user in users:
            password = self.has_login_profile(user['UserName'])
            password_age = self.get_password_last_used_date(user)
            account_age = self.get_create_date_age(user)
            access_keys = self.get_access_key_ages(user['UserName'])

            if password and len(access_keys) > 0:
                print(user['UserName'], password, account_age, password_age, access_keys)
        print(users[0].keys())

    def get_password_last_used_date(self, user_data):
        """

        :param user_data:
        :type user_data: dict
        :return:
        """
        return self.get_age_of('PasswordLastUsed', user_data)

    def get_create_date_age(self, user_data):
        """

                :param user_data:
                :type user_data: dict
                :return:
        """
        return self.get_age_of('CreateDate', user_data)

    def get_age_of(self, key, user_data):
        """

        :param key:
        :type key: str
        :param user_data:
        :type user_data: dict
        :return:
        """
        if key in user_data.keys():
            today = datetime.datetime.today()
            last_used = user_data[key].replace(tzinfo=None)
            age = today - last_used
            if age.days >= 0:
                return age.days / 365
            else:
                return 0
        return None

    def has_login_profile(self, username):
        """

        :param username:
        :type username: str
        :return:
        """
        client = BotoClient(self._aws_access_key_id, self._aws_secret_access_key, self._region).get_iam_client
        try:
            client.get_login_profile(UserName=username)
            return True
        except botocore.exceptions.ClientError:
            return False

    def get_access_key_ages(self, username):
        b = BotoClient(self._aws_access_key_id, self._aws_secret_access_key, self._region)
        client = b.get_iam_client
        response = client.list_access_keys(UserName=username)
        ret_val = []
        for key in response['AccessKeyMetadata']:
            status = key['Status']
            create_date = self.get_age_of('CreateDate', key)
            key_id = key['AccessKeyId']
            key_data = client.get_access_key_last_used(AccessKeyId=key_id)
            last_used = self.get_age_of('LastUsedDate', key_data['AccessKeyLastUsed'])
            data = (status, create_date, last_used)
            ret_val.append(data)
        return ret_val


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
    region = 'us-west-2'

    iam = Iam(aws_access_key_id, aws_secret_access_key, region)

    client = BotoClient('a', 'b', 'us-west-2')
    # print(dir(client))
    # print(dir(client.get_iam_client))
    iam.scan_users()