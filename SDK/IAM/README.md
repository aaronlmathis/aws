# Overview
These two scripts use the AWS SDK for Python (boto3) to:

- Discover all managed policies attached to a specific IAM user (either directly or through any IAM groups they belong to).
- Generate a “last accessed” report for each policy and service (or action) allowed by that policy.
    - One script does this at the action level (ACTION_LEVEL), which shows individual API calls such as s3:PutObject.
    - The other script does this at the service level (SERVICE_LEVEL), which only shows the AWS service name (e.g., Amazon S3) and the last time it was used.
- Export the resulting data to one of four formats: CSV, JSON, YAML, or XML.

These scripts can help you audit user permissions and understand which services (or actions) the user has actually used.

# Requirements

- Python 3.7+ (recommended)
- boto3 library for Python:
``
pip install boto3
``
- PyYAML (only if you want to export in YAML format):
``
pip install PyYAML
``
- AWS Credentials with permissions to call the necessary IAM APIs (e.g., GenerateServiceLastAccessedDetails, GetServiceLastAccessedDetails, ListAttachedUserPolicies, GetPolicy, etc.). Typically, running this under a role or user with IAM Full Access or adequate read permissions will work.

# Scripts

1. Action-Level Script - File Name: iam_user_access_action_level.py

Key Features
-
- Uses Granularity='ACTION_LEVEL' to produce a detailed report of every tracked action in each service (e.g., s3:PutObject, s3:GetObject, etc.).
- Each row in the final output shows:
    - UserName
    - PolicyName
    - PolicyArn
    - ServiceName
    - ActionName
    - LastAccessed (timestamp or “Never”)

Usage
-

1. Make sure you have your AWS credentials set (e.g., ~/.aws/credentials or environment variables).
2. Run the script from the command line:
```
python iam_user_access_action_level.py <IAM_USERNAME> [--format {csv,json,yaml,xml}] [--output OUTPUT_BASENAME]
```
- <IAM_USERNAME>: The name of the IAM user you want to audit.
- --format: Optional; sets the output format. Defaults to CSV.
- --output: Optional; sets the base name (without extension) for the report file. Defaults to a timestamped base name (e.g., iam-user-access-action-level-report-01-19-2025).

Examples
-
```
# Output in CSV (default):
python iam_user_access_action_level.py alice

# Output in JSON:
python iam_user_access_action_level.py alice --format json --output alice-action-level
```
After completion, the script will produce a file named something like iam-user-access-action-level-report-01-19-2025.csv (or .json, etc.).

2. Service-Level Script

File Name: iam_service_level_report.py (or however you choose to name it)
Key Features
-
- Uses Granularity='SERVICE_LEVEL' to produce a simpler, high-level view of which AWS services the user can access, and when each was last used.
- Each row in the final output shows:
    - UserName
    - PolicyName
    - PolicyArn
    - ServiceName
     - LastAccessed (timestamp or “Never”)

Usage
-

1. Make sure you have your AWS credentials set (e.g., ~/.aws/credentials or environment variables).
2. Run the script from the command line:
```
python iam_user_access_service_level.py <IAM_USERNAME> [--format {csv,json,yaml,xml}] [--output OUTPUT_BASENAME]
```
- <IAM_USERNAME>: The name of the IAM user you want to audit.
- --format: Optional; sets the output format. Defaults to CSV.
- --output: Optional; sets the base name (without extension) for the report file. Defaults to a timestamped base name (e.g., iam-user-access-action-level-report-01-19-2025).

Examples
-
```
# Output in CSV (default):
python iam_user_access_service_level.py alice

# Output in JSON:
python iam_user_access_service_level.py alice --format json --output alice-action-level
```
After completion, the script will produce a file named something like iam-user-access-action-level-report-01-19-2025.csv (or .json, etc.).