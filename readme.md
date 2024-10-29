# ProwlerObserver

ProwlerObserver is a project designed to scan your AWS infrastructure, identifying services associated with events shown in CloudTrail and analyzing the services found within those events.

You can configure the scan interval in prowlerobserver/config/config.py by modifying the scan_time variable.

## Prerequisites

It’s recommended to use `Python 3` to run this project.

Additionally, make sure to set your AWS credentials as environment variables before running the scan. You can do this with the following commands:

```
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=your_aws_region
```

## Usage 
To start the scan, run the following command from the project root:
```
python3 prowlerobserver.py
```

