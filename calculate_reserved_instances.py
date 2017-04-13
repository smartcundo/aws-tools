import boto3
import os
import boto3
import ConfigParser
import argparse
import ec2instancespricing
import logging as logger

class InstancePricing:
    def __init__(self,account_name, aws_access_key_id, aws_secret_access_key, region, instance_type, dry_run=True):
        self._aws_account_name = account_name
        self._dry_run = dry_run
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_region = region
        self._instance_type = instance_type
        self._aws_availability_zones = None
        self._ec2_client = boto3.client(
            'ec2',
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._aws_region)

    def describe_offerings(self, availability_zone, instance_type):
        response = self._ec2_client.describe_reserved_instances_offerings(
            AvailabilityZone= availability_zone,
            InstanceType=instance_type,
            InstanceTenancy='default',
            ProductDescription='Linux/UNIX (Amazon VPC)',
            OfferingType='Partial Upfront',
            IncludeMarketplace=False,
            OfferingClass='standard',
            MaxDuration=31536000)
        return  response['ReservedInstancesOfferings']

    def _available_availability_zones(self):
        if self._aws_availability_zones is not None:
            return self._aws_availability_zones
        response = self._ec2_client.describe_availability_zones()
        az_list = [az['ZoneName'] for az in response['AvailabilityZones']]
        self._aws_availability_zones = az_list
        return az_list

    def describe_effective_pricing(self):
        seconds_in_a_minute = 60
        minutes_in_an_hour = 60

        effective_pricing = {}
        for az in self._available_availability_zones():
            offering = self.describe_offerings(az, self._instance_type)[0]
            fixed_price = offering['FixedPrice']
            recurring_charges = offering['RecurringCharges'][0]['Amount']
            duration_in_hours = offering['Duration'] / seconds_in_a_minute / minutes_in_an_hour
            fixed_price_spread = fixed_price / duration_in_hours
            effective_pricing[az] = "{:.3f}".format(recurring_charges + fixed_price_spread)
        return effective_pricing

    def describe_yearly_reserved_pricing(self):
        seconds_in_a_minute = 60
        minutes_in_an_hour = 60
        seconds_in_a_year = 31536000

        yearly_price = {}
        for az in self._available_availability_zones():
            offering = self.describe_offerings(az, self._instance_type)[0]
            fixed_price = offering['FixedPrice']
            recurring_charges_amount = offering['RecurringCharges'][0]['Amount']
            duration_in_hours = offering['Duration'] / seconds_in_a_minute / minutes_in_an_hour
            count_years = offering['Duration'] / seconds_in_a_year
            y_price = (fixed_price + duration_in_hours * recurring_charges_amount) / count_years
            yearly_price[az] = "{:.2f}".format(y_price)
        return yearly_price

    def describe_on_demand_pricing(self):
        seconds_in_a_minute = 60
        minutes_in_an_hour = 60
        seconds_in_a_year = 31536000
        hours_in_a_year = seconds_in_a_year / seconds_in_a_minute / minutes_in_an_hour

        yearly_price = {}
        for az in self._available_availability_zones():
            price = ec2instancespricing.get_ec2_ondemand_instances_prices(
                filter_region=self._aws_region,
                filter_instance_type=self._instance_type,
                use_cache=True
                )

            try:
                y_price = price['regions'][0]['instanceTypes'][0]['prices']['ondemand']['hourly'] * hours_in_a_year
                yearly_price[az] = "{:.2f}".format(y_price)
            except IndexError:
                y_price = price['regions'][1]['instanceTypes'][0]['prices']['ondemand']['hourly'] * hours_in_a_year
                yearly_price[az] = "{:.2f}".format(y_price)
        return yearly_price


if __name__ == "__main__":

    description = "Quickly list EC2 instance pricing"
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Default region name", default="us-west-2")
    parser.add_argument('-s', "--select", help='For each AWS account, prompt to apply change',
                        action='store_true', default=False)
    parser.add_argument("-a", "--accounts", help="Name of AWS accounts to apply to (,-separated)")
    parser.add_argument("-c", "--config", help="Path to local existing config file",
                        default=os.path.join(os.getenv("HOME"),".aws", "credentials"))
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

            for t in ["t2.micro", "t2.medium", "t2.small", "t2.large"]:
                # print(az, t, calc.describe_offerings(az, t))
                calc = InstancePricing(
                    account,
                    aws_access_key_id,
                    aws_secret_access_key,
                    region,
                    instance_type=t,dry_run=dry_run)
                reserved_pricing = calc.describe_yearly_reserved_pricing()
                az = reserved_pricing.keys()[0]
                print("Yearly reserved pricing for instance type %s: %f" % (t, reserved_pricing[az]))
                print(t, calc.describe_on_demand_pricing())

        except ConfigParser.NoOptionError as e:
            print("%s is not properly configured in %s" % (account, config_file))
        break
