import json
import boto3
import aws_credentials as aws_creds
from pkg_resources import resource_filename
import pprint
from datetime import datetime
import pandas as pd
import datetime

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


# Get current price for a given instance, region and os
# price = get_price(get_region_name('us-east-1'), 't2.micro', 'Linux')
# print(price)

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

'''
response = client.describe_spot_price_history(
    Filters=[{
        'Name': 'availability-zone',
        'Values': ['us-east-1a', 'us-east-1c', 'us-east-1d']
        },
        {
            'Name': 'product-description',
            'Values': ['Linux/UNIX (Amazon VPC)']
        }],
    InstanceTypes=['r5.2xlarge'],
    EndTime=datetime.now(),
    StartTime=datetime.now()
)
'''

client = boto3.client('ec2', region_name='us-east-1')

def get_spot_prices(instance_type):
    # (typically) returns the most recent spot price for each availability zone

    prices = client.describe_spot_price_history(InstanceTypes=[instance_type], MaxResults=20,
                                                ProductDescriptions=['Linux/UNIX (Amazon VPC)']
                                                )
    # AvailabilityZone='us-east-1a'


    # dict with AZ's as keys and prices as values
    AZ_price_dict = {}
    for result in prices['SpotPriceHistory']:
        price = result['SpotPrice']
        AZ = result['AvailabilityZone']
        # want to keep adding zones without overriding the most recent prices
        if not AZ in AZ_price_dict.keys():
            AZ_price_dict[AZ] = price

    pprint.pprint(prices['SpotPriceHistory'])
    # print(AZ_price_dict)
    return(AZ_price_dict)


instance_type = 't2.micro'

AZ_price_dict = get_spot_prices(instance_type)
print(AZ_price_dict)

def get_best_AZ(AZ_price_dict):
    # get the best price from the dict
    best_price = min(AZ_price_dict.values())
    for AZ, price in AZ_price_dict.items():
        if price == best_price:
            return AZ, price

cheapest_AZ, price = get_best_AZ(AZ_price_dict)

print("Cheapest AZ:", cheapest_AZ)
print("Lowest price:", float(price) + 0.005)


def create_spot_instance(instance_type, cheapest_AZ):
    response = client.request_spot_instances(
        DryRun=False,
        SpotPrice= str(float(price) + 0.005),
        ClientToken='string1',
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification={
            'ImageId': 'ami-0947d2ba12ee1ff75',
            'KeyName': 'FirstKey',
            'SecurityGroups': ['flask_group'],
            'InstanceType': instance_type,
            'Placement': {
                'AvailabilityZone': cheapest_AZ,
            },
            'SecurityGroupIds': [
                'sg-037901ad326336e81',
            ]
        }
    )
    print(response)

create_spot_instance(instance_type, cheapest_AZ)