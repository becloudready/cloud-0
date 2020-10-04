import boto3
import pprint

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