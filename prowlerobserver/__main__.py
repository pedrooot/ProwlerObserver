import boto3
import subprocess
import time
from datetime import datetime, timedelta

from prowler.lib.check.check import list_services
from prowlerobserver.lib.service_filter import service_filter
from prowlerobserver.config.config import scan_time

def get_enabled_regions() -> list:
    """
    Get the enabled regions in the account

    Returns:
        - list: List of enabled regions

    """
    ec2_client = boto3.client('ec2')

    response = ec2_client.describe_regions(AllRegions=False)
    
    enabled_regions = [region['RegionName'] for region in response['Regions']]
    
    return enabled_regions

def get_cloudtrail_services(last_time: int, regions: list) -> list:
    """
    Get the services seen in cloudtrail for the last specified minutes

    Args:
        - last_time (int): Last time in minutes
        - regions (list): List of regions to check
    
    Returns:
        - list: List of services seen in cloudtrail for the last specified minutes
    """
    end_time = datetime.now()
    original_last_time_minutes = last_time
    if last_time < 62:
        last_time = 61
    start_time = end_time - timedelta(minutes=last_time)
    services = set()

    for region in regions:
        try:
            client = boto3.client('cloudtrail', region_name=region)
            
            # Check if there are any trails in the region
            describe_trails = client.describe_trails()["trailList"]
            
            # if there are trails, get the events
            if describe_trails:
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
                        actual_time = datetime.now(event["EventTime"].tzinfo)
                        if actual_time - event["EventTime"] < timedelta(minutes=original_last_time_minutes):
                            event_source = event['EventSource']
                            service_name = event_source.split('.')[0]
                            services.add(service_filter(service_name))
        except Exception as e:
            if "AccessDenied" not in str(e):
                print(f"Error getting cloudtrail events in region {region}: {e}")
            continue
    
    return list(services)

def run_prowler(services: list, regions: list):
    """
    Run prowler for the services in the regions

    Args:
        - services (list): List of services
        - regions (list): List of regions
    """
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
        
        prowler_command = f"prowler aws --service {string_services} -f {string_regions}"
        try:
            subprocess.run(prowler_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            if e.stderr:
                error_message = e.stderr.decode()
                print(f"Error executing Prowler:\n{error_message}")

def prowlerobserver():
    """
    Main function to run the prowler observer
    """
    minutes = scan_time
    regions = get_enabled_regions()
    while True:
        print(f"Getting services seen in cloudtrail for the last {minutes} minutes for the regions: {regions}")
        services = get_cloudtrail_services(minutes, regions)
        
        if services:
            print(f"Found services: {services}")
            run_prowler(services, regions)
            print(f"Sleeping for {minutes} minutes")
        else:
            print(f"No services found in cloudtrail for the last {minutes} minutes")
        
        time.sleep(minutes * 60)
