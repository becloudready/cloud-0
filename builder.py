import boto3
import string
import random
import pricer

class Builder():

    price = ''
    client = ''

    def __init__(self, price, client):

        self.price = price
        self.client = client

    def create_spot_instance(self, instance_type, cheapest_AZ, new_instance=True, *args, **kwargs):
        """Create a spot request that, if accepted, will create a ec2 instance for that price."""

        DryRun = False
        SpotPrice = self.price
        client = self.client
        InstanceCount=1
        Type='one-time'
        security_group = 'flask_group'
        KeyName = 'FirstKey'
        ImdageId = 'ami-0947d2ba12ee1ff75'
        SecurityGroupIds = 'sg-037901ad326336e81'

        # request_spot_instances is idempotent on the string token
        # for a new request, a new string is needed
        # for a repeated request that that shouldn't be duplicated, should use the same token
        if new_instance:
            ClientToken = self.str_generator()
        else:
            ClientToken = 'default'

        response = client.request_spot_instances(
            DryRun=DryRun,
            SpotPrice=SpotPrice,
            ClientToken=ClientToken,
            InstanceCount=InstanceCount,
            Type=Type,
            LaunchSpecification={
                'ImageId': ImdageId,
                'KeyName': KeyName,
                'SecurityGroups': [security_group],
                'InstanceType': instance_type,
                'Placement': {
                    'AvailabilityZone': cheapest_AZ,
                },
                'SecurityGroupIds': [
                    SecurityGroupIds,
                ]
            }
        )
        print(response)

    def str_generator(self):
        """Generate a range string of length size"""
        size = 6
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))


if __name__ == "__main__":

    # create test pricer
    pricer1 = pricer.Pricer('ec2', 'us-east-1', 't2.micro')
    prices_response = pricer1.get_spot_prices()
    AZ_price_dict = pricer1.format_price_data(prices_response)
    AZ, price = pricer1.get_best_price(AZ_price_dict)

    client = pricer1.return_client()

    builder1 = Builder(price, client)
    instance_type = 't2.micro'

    builder1.create_spot_instance(instance_type, AZ)
