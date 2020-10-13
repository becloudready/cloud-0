import boto3

class Pricer():

    # TODO: add ability to
    #  1) ask client if their needs align with on-demand, spot, or reserved
    #  2) convert client needs in terms of compute (and others) into server type (on AWS, Azure, GCP)
    #  3) get prices for each cloud provider and compare them

    api = 'ec2'
    region_name = 'us-east-1'
    instance_type = 't2.micro'
    client = ''

    def __init__(self, api='ec2', region_name='us-east-1', instance_type='t2.micro'):
        """
        Create new instance with default values:
        api = 'ec2'
        region_name = 'us-east-1'
        instance_type = 't2.micro
        """

        self.api = api
        self.region_name = region_name
        self.instance_type = instance_type
        self.client = boto3.client(api, region_name=region_name)

    def get_spot_prices(self):
        """Return raw data on spot prices. To be processed by get_best_spot_price"""

        max_results = 20
        product_description = 'Linux/UNIX (Amazon VPC)'
        client = self.client
        instance_type = self.instance_type

        prices_response = client.describe_spot_price_history(InstanceTypes=[instance_type],
                                                    MaxResults=max_results,
                                                    ProductDescriptions=[product_description]
                                                    )

        return prices_response

    def format_price_data(self, prices_response):
        """Format API response into dictionary with availabilty zones and prices."""

        AZ_price_dict = {}

        for result in prices_response['SpotPriceHistory']:
            price = result['SpotPrice']
            AZ = result['AvailabilityZone']
            # TODO: make this logic better: want to keep adding zones without overriding the most recent prices
            if not AZ in AZ_price_dict.keys():
                AZ_price_dict[AZ] = price

        return AZ_price_dict

    def get_best_price(self, AZ_price_dict):
        """Takes a dictionary of availablity zones to price and returns the lowest price with AZ."""

        best_price = min(AZ_price_dict.values())

        for AZ, price in AZ_price_dict.items():
            if __name__ == '__main__':
                if price == best_price:
                    return AZ, price

    def return_client(self):
        """Give access to client, for builder."""
        return self.client

if __name__ == "__main__":

    p1 = Pricer('ec2', 'us-east-1', 't2.micro')
    prices_response = p1.get_spot_prices()
    AZ_price_dict = p1.format_price_data(prices_response)
    print(p1.get_best_price(AZ_price_dict))
