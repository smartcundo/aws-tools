import os
import json
import six
import ConfigParser
import argparse
from calculate_reserved_instances import InstancePricing


all_accounts_dict = {'AWS nbexdev': [{'EC2': ({}, {}, 0, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS kapp': [{'EC2': ({}, {(u'm3.large', u'us-west-2a'): 1, (u'm3.medium', u'us-west-2c'): 1, (u't1.micro', u'us-west-2a'): 1, (u'm2.xlarge', u'us-west-2a'): 2, (u'm2.xlarge', u'us-west-2c'): 2, (u'm3.medium', u'us-west-2b'): 1, (u'm1.small', u'us-west-2a'): 6, (u'm2.xlarge', u'us-west-2b'): 2, (u'm3.medium', u'us-west-2a'): 2, (u'm1.small', u'us-west-2c'): 5, (u'm1.small', u'us-west-2b'): 8, (u'c3.2xlarge', u'us-west-2b'): 1}, 32, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS amp': [{'EC2': ({}, {(u'm1.large', u'us-west-2c'): 1, (u'c3.large', u'us-west-2a'): 1, (u't2.small', u'us-west-2a'): 1, (u'c1.medium', u'us-west-2b'): 1, (u'c4.large', u'us-west-2a'): 11, (u'm1.small', u'us-west-2a'): 6, (u't2.medium', u'us-west-2a'): 1, (u'm3.medium', u'us-west-2a'): 15, (u'c3.large', u'us-west-2c'): 3, (u't1.micro', u'us-west-2a'): 1, (u'c3.xlarge', u'us-west-2c'): 1, (u'm2.xlarge', u'us-west-2b'): 2, (u'm1.large', u'us-west-2a'): 1, (u't2.large', u'us-west-2b'): 1, (u't2.micro', u'us-west-2c'): 1, (u't1.micro', u'us-west-2b'): 2, (u't2.medium', u'us-west-2c'): 1, (u'c3.xlarge', u'us-west-2b'): 2, (u't2.small', u'us-west-2c'): 1, (u'm1.large', u'us-west-2b'): 4, (u'c3.2xlarge', u'us-west-2a'): 1, (u'c4.large', u'us-west-2c'): 14, (u'm1.small', u'us-west-2c'): 7, (u't2.micro', u'us-west-2b'): 1, (u'm3.medium', u'us-west-2c'): 17, (u't1.micro', u'us-west-2c'): 1, (u'm1.small', u'us-west-2b'): 8, (u'm1.medium', u'us-west-2c'): 1, (u't2.medium', u'us-west-2b'): 1, (u'c4.xlarge', u'us-west-2a'): 1, (u'c4.large', u'us-west-2b'): 15, (u'm3.medium', u'us-west-2b'): 16, (u't2.small', u'us-west-2b'): 1, (u'c3.large', u'us-west-2b'): 1}, 142, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {(u'cache.m1.large', u'redis'): 1, (u'cache.m1.small', u'redis'): 9}, 10, 0)}], 'AWS kapploadtesting': [{'EC2': ({}, {(u't2.micro', u'us-west-2a'): 1}, 1, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS swops': [{'EC2': ({}, {(u't2.nano', u'us-west-2a'): 6, (u't2.medium', u'us-west-2a'): 2, (u't2.small', u'us-west-2a'): 3, (u't1.micro', u'us-west-2c'): 1, (u'm3.medium', u'us-west-2a'): 1}, 13, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS nbweb': [{'EC2': ({}, {}, 0, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS nbex': [{'EC2': ({}, {}, 0, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS wallstreetdemo': [{'EC2': ({}, {}, 0, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS pedro': [{'EC2': ({}, {}, 0, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {}, 0, 0)}], 'AWS play': [{'EC2': ({}, {(u'm4.xlarge', u'us-west-2b'): 1, (u't1.micro', u'us-west-2c'): 1, (u't2.micro', u'us-west-2a'): 1, (u't1.micro', u'us-west-2a'): 4, (u'c4.large', u'us-west-2a'): 1, (u'm1.small', u'us-west-2a'): 1, (u'm3.medium', u'us-west-2a'): 3, (u'm1.small', u'us-west-2b'): 1}, 13, 0)}, {'RDS': ({}, {}, 0, 0)}, {'ElastiCache': ({}, {(u'cache.r3.large', u'redis'): 2}, 2, 0)}]}

reserved_instances_needed = {}


def add_count(availability_zone, instance_type, count):
    region = availability_zone[:-1]
    instance_family, instance_size = instance_type.split(".")
    if region not in reserved_instances_needed.keys():
        reserved_instances_needed[region] = {}
    if availability_zone not in reserved_instances_needed[region].keys():
        reserved_instances_needed[region][availability_zone] = {}
    if instance_family not in reserved_instances_needed[region][availability_zone].keys():
        reserved_instances_needed[region][availability_zone][instance_family] = {}
    try:
        reserved_instances_needed[region][availability_zone][instance_family][instance_type] += count
    except KeyError:
        reserved_instances_needed[region][availability_zone][instance_family][instance_type] = count


def add_region_data(data):
    # print("region data: ", data)
    ((instance_type, availability_zone), count) = data
    add_count(availability_zone, instance_type, count)


def process_ec2(ec2_data):
    unused_reservations_dict, not_reserved_dict, on_demand_count, reservations_count = ec2_data
    for item in six.iteritems(not_reserved_dict):
        # print("item", item)
        add_region_data(item)
    pass


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
    prompt_account_selection = args.select
    region = args.region

    conf = ConfigParser.ConfigParser()
    conf.read(config_file)
    all_aws_accounts = conf.sections()
    credentials = {'regionInfo': {'default_region': default_region},
                   'Accounts': {}}

    if args.accounts is not None:
        selected_aws_accounts = ["profile %s" % x for x in args.accounts.split(",")]
    else:
        selected_aws_accounts = all_aws_accounts

    # dry_run = not args.execute
    dry_run = False
    print("Found %i AWS accounts" % len(all_aws_accounts))
    use_account = all_aws_accounts[0]

    for account in all_accounts_dict.keys():
        # print(account, all_accounts_dict[account])
        for component in all_accounts_dict[account]:
            for service, data in six.iteritems(component):
                if service == 'EC2':
                    process_ec2(data)
                else:
                    pass
                    # print(service, data)
    try:
        aws_access_key_id = conf.get(use_account,'aws_access_key_id')
        aws_secret_access_key = conf.get(use_account,'aws_secret_access_key')
        total_on_demand_compute_costs = 0
        combined_savings = 0
        for region in reserved_instances_needed.keys():
            region_data = reserved_instances_needed[region]
            for availability_zone in region_data.keys():
                availability_zone_data = region_data[availability_zone]
                for family in availability_zone_data.keys():
                    family_data = availability_zone_data[family]
                    for instance_type in family_data.keys():
                        count = family_data[instance_type]
                        calc = InstancePricing(
                            use_account,
                            aws_access_key_id,
                            aws_secret_access_key,
                            region,
                            instance_type=instance_type,
                            dry_run=dry_run)
                        pricing = calc.describe_yearly_reserved_pricing()
                        total_yearly_reserved_pricing = count * float(pricing[availability_zone])
                        print("[%s] Yearly reserved pricing for %i %s: %s" %
                              (availability_zone, count, instance_type, "{:.2f}".format(total_yearly_reserved_pricing)))

                        single_ondemand_pricing = calc.describe_on_demand_pricing()
                        total_yearly_ondemand_pricing = \
                            count * float(single_ondemand_pricing[availability_zone])
                        total_on_demand_compute_costs += total_yearly_ondemand_pricing

                        print("[%s] Yearly on-demand pricing for %i %s: %s" %
                              (availability_zone, count, instance_type, "{:.2f}".format(total_yearly_ondemand_pricing)))
                        total_yearly_savings = float(total_yearly_ondemand_pricing) - \
                                               float(total_yearly_reserved_pricing)
                        combined_savings += total_yearly_savings
                        print("[%s] Yearly savings for %i %s: %s" %
                              (availability_zone, count, instance_type, total_yearly_savings))
            print("Combined yearly AWS compute costs in %s is: %s" % (region, "${:,.2f}".format(total_on_demand_compute_costs)))
            print("Combined yearly AWS savings in %s is: %s" % (region, "${:,.2f}".format(combined_savings)))
        print(json.dumps(reserved_instances_needed))

    except ConfigParser.NoOptionError as e:
        print("%s is not properly configured in %s" % (use_account, config_file))

