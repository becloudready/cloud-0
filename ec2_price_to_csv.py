import json
import boto3
import aws_credentials as aws_creds
from pkg_resources import resource_filename
import pprint
from datetime import datetime
import pandas as pd

def test_credentials():
    s3 = boto3.resource('s3', aws_access_key_id = aws_creds.access_key,
                    aws_secret_access_key = aws_creds.secrete_key)

    # create

    for bucket in s3.buckets.all():
        print(bucket.name)

# test_credentials()


# Search product filter
FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'\
      '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'\
      '{{"Field": "instanceType", "Value": "{t}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'

# cody-pasta
# TODO: speed this up by asking for less data
# Get current AWS price for an on-demand instance
def get_price(region, instance, os):
    f = FLT.format(r=region, t=instance, o=os)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))
    # print("raw data:", data)
    pprint.pprint(data["PriceList"])
    od = json.loads(data['PriceList'][0])['terms']['OnDemand']
    id1 = list(od)[0]
    id2 = list(od[id1]['priceDimensions'])[0]
    return od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']

# Translate region code to region name
# Cody-pasta: not sure why this is necessary over passing a string
def get_region_name(region_code):
    default_region = 'us-east-1'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description']
    except IOError:
        return default_region


# Use AWS Pricing API at US-East-1
client = boto3.client('pricing', region_name='us-east-1', aws_access_key_id = aws_creds.access_key,
                    aws_secret_access_key = aws_creds.secrete_key)
'''
# list containing ec2 instances, copied from webpage
with open("ec2_to_fetch_list.txt", 'r') as file:
    ec2_gen_purpose_list = file.readlines()

# ---main: lookup data and save it to csv---
ec2_price_list = []

now = datetime.now()
region_name = get_region_name('us-east-1')
for instance in ec2_gen_purpose_list:
    price = get_price(region_name, instance.strip(), 'Linux')
    row = [instance.strip(), price, r'{}:{}:{}'.format(now.year, now.month, now.day), r'{}:{}'.format(now.hour % 12, now.minute)]
    ec2_price_list.append(row)

#  columns=['name', 'price', 'date', 'time']
ec2_price_df = pd.DataFrame(data=ec2_price_list)


name = r'ec2 instance price {}-{}-{}.csv'.format(now.year, now.month, now.day)
name = 'ec2prices.csv'
ec2_price_df.to_csv(name, index=False)
'''

# Get current price for a given instance, region and os
price = get_price(get_region_name('us-east-1'), 't2.micro', 'Linux')
print(price)


def get_all_instance_names():

    """Pulls a lot of instance types and prints them"""

    def ec2_instance_types(region_name):
        '''Yield all available EC2 instance types in region <region_name>'''
        ec2 = boto3.client('ec2', region_name=region_name, aws_access_key_id=aws_creds.access_key,
                           aws_secret_access_key=aws_creds.secrete_key)
        describe_args = {}
        while True:
            describe_result = ec2.describe_instance_types(**describe_args)
            yield from [i['InstanceType'] for i in describe_result['InstanceTypes']]
            if 'NextToken' not in describe_result:
                break
            describe_args['NextToken'] = describe_result['NextToken']

    for ec2_type in ec2_instance_types('us-east-1'):
        print(ec2_type)

# get_all_instance_names()