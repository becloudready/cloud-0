import boto3
import pprint
import csv
import pymysql

CLIENT = boto3.client('ce', region_name='us-east-1')
DBS_CONNECT = pymysql.connect('cloud0-mysql-rds.cfdgt090zyck.us-east-1.rds.amazonaws.com',
                              'cloud0_pricing', "NI8@_TA'wlQf")

print(DBS_CONNECT)

def complex_billing():

    response = CLIENT.get_cost_and_usage_with_resources(
        TimePeriod={
            'Start': '2020-10-01',
            'End': '2020-10-05'
        },
        Granularity='DAILY',
        Metrics=[
            'AmortizedCost',
        ],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': [
                    'Amazon Elastic Compute Cloud - Compute',
                ],
            }
        },
        GroupBy=[
            {
                'Type': 'ResourceId',
                'Key': 'i-027025655f265733a'
            }]
    )


def simple_billing():

    response = CLIENT.get_cost_and_usage(
        TimePeriod={
            'Start': '2020-09-20',
            'End': '2020-10-05'
        },
        Granularity='DAILY',
        Metrics=[
            'AmortizedCost',
        ]
    )

    # pprint.pprint(response)

    for item in response['ResultsByTime']:
        print(item)

def bill_writer(response):

    with open('aws_bill.csv', mode='w') as csv_file:
        fieldnames = response.keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
        writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})


if __name__ == "__main__":

    # simple_billing()
    # complex_billing()
    pass
