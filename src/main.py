import boto3
import subprocess
import time
from datetime import datetime, timedelta

from prowler.lib.check.check import list_services


def get_enabled_regions():
    ec2_client = boto3.client('ec2')

    response = ec2_client.describe_regions(AllRegions=False)
    
    enabled_regions = [region['RegionName'] for region in response['Regions']]
    
    return enabled_regions

def get_cloudtrail_services(last_minutes, regions):
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=last_minutes)
    services = set()

    for region in regions:
        client = boto3.client('cloudtrail', region_name=region)
        paginator = client.get_paginator('lookup_events')
        response_iterator = paginator.paginate(
            StartTime=start_time,
            EndTime=end_time,
            PaginationConfig={
                'PageSize': 50 
            }
        )
        for page in response_iterator:
            for event in page['Events']:
                event_source = event['EventSource']
                service_name = event_source.split('.')[0]
                services.add(service_name)
    
    return list(services)

def run_prowler(services, regions):
    string_services = ""
    for service in services:
        if service in list_services("aws"):
            string_services += f"{service} "

    string_regions = ""
    for region in regions:
        string_regions += f"{region} "

    if string_services == "":
        print("No services found in cloudtrail for the last specified minutes that are supported by prowler")
    else:
        print(F"Executing prowler for the services: {string_services} in the regions: {string_regions}")
        
        prowler_command = f"prowler aws --service {string_services} --log-level ERROR -f {string_regions}"
        try:
            subprocess.run(prowler_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            if e.stderr:
                error_message = e.stderr.decode()
                print(f"Error executing Prowler:\n{error_message}")

def main():
    minutes = 61
    regions = get_enabled_regions()
    while True:
        print(f"Getting services seen in cloudtrail for the last {minutes} minutes for the regions: {regions}")
        services = get_cloudtrail_services(minutes, regions)
        
        if services:
            print(f"Found services: {services}")
            run_prowler(services, regions)
        else:
            print(f"No services found in cloudtrail for the last {minutes} minutes")
        
        time.sleep(minutes * 60)

if __name__ == "__main__":
    main()