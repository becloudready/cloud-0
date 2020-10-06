import pricer
import builder


if __name__ == "__main__":

    # create test pricer
    pricer1 = pricer.Pricer('ec2', 'us-east-1', 't2.micro')
    prices_response = pricer1.get_spot_prices()
    AZ_price_dict = pricer1.format_price_data(prices_response)
    AZ, price = pricer1.get_best_price(AZ_price_dict)

    client = pricer1.return_client()

    # create test instance
    builder1 = builder.Builder(price, client)
    instance_type = 't2.micro'
    builder1.create_spot_instance(instance_type, AZ)





