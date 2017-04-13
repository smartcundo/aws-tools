import os
import boto3
import ConfigParser
import argparse


class EC2Instances:
    def __init__(self, account_name, aws_access_key_id, aws_secret_access_key, region, dry_run=True):
        self._aws_account_name = account_name
        self._dry_run = dry_run
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_region = region
        self._ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._aws_region)

        response = self._ec2_client.describe_instances()

        for r in response['Reservations']:
            for i in r['Instances']:
                try:
                    print("[%s] %s" % (self._aws_account_name, str(i['PublicIpAddress'])) )
                    if str(i['PublicIpAddress']) == "52.87.78.26":
                        print("[%s] HERE IT IS!" % self._aws_account_name)
                except KeyError as e:
                    print ("[%s] %s" % (self._aws_account_name, e.message))


def prompt(message, valid_responses=None):
    assert isinstance(valid_responses, list), "valid_responses param must be of list type"
    response = None
    while True:
        try:
            response = raw_input(message)
        except:
            response = input(message)
        if valid_responses is None or response in valid_responses:
            break
    return response


if __name__ == "__main__":

    description = "Quickly list EC2 instances"
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Default region name", default="us-east-1")
    parser.add_argument('-x', "--execute", help='Execute changes (disables dry-run)', action='store_true', default=False)
    parser.add_argument('-s', "--select", help='For each AWS account, prompt to apply change',
                        action='store_true', default=False)
    parser.add_argument("-a", "--accounts", help="Name of AWS accounts to apply to (,-separated)")
    parser.add_argument("-c", "--config", help="Path to local existing config file",
                        default=os.path.join(os.getenv("HOME"),".aws", "credentials"))
    parser.add_argument("-o", "--output", help="Filename of new config file to create",
                        default=os.path.join(os.getcwd(), "tmp_credentials"))
    parser.add_argument('-d', "--delete", help='Delete IAM credentials for specified user',
                        action='store_true', default=False)
    args = parser.parse_args()

    default_region = args.region
    config_file = args.config
    output_file = args.output
    prompt_account_selection = args.select
    region = args.region

    conf = ConfigParser.ConfigParser()
    conf.read(config_file)
    all_aws_accounts = conf.sections()
    credentials = {'regionInfo': {'default_region': default_region},
                   'Accounts': {}}

    delete_user = args.delete

    if args.accounts is not None:
        selected_aws_accounts = ["profile %s" % x for x in args.accounts.split(",")]
    else:
        selected_aws_accounts = all_aws_accounts

    dry_run = not args.execute

    print("Found %i AWS accounts" % len(all_aws_accounts))
    for account in selected_aws_accounts:
        if account not in all_aws_accounts:
            print("[WARNING] Account %s skipped because it is not configured in config file %s" %
                  (account, config_file))
            continue
        if prompt_account_selection:
            apply_to_account = prompt("Apply change to account %s? (y/n): " % account, ['y', 'n'])
            if apply_to_account != 'y':
                continue

        try:
            aws_access_key_id = conf.get(account,'aws_access_key_id')
            aws_secret_access_key = conf.get(account,'aws_secret_access_key')
            EC2Instances(account, aws_access_key_id, aws_secret_access_key, region, dry_run=dry_run)


        except ConfigParser.NoOptionError as e:
            print("%s is not properly configured in %s" % (account, config_file))
