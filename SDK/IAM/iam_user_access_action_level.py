# AWS SDK Scripts - IAM 
# Copyright (C) 2025 Aaron Mathis
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import boto3
import csv
import json
import time
import sys
from datetime import datetime


# For YAML output (requires "pip install PyYAML")
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# For XML output (standard library)
import xml.etree.ElementTree as ET


def get_managed_policies_for_user(iam_client, username):
    """
    Return a set of ARNs for all managed policies attached directly to the user
    or through any groups the user is in.
    """
    policy_arns = set()

    # 1. Attached managed policies at the user level
    attached_user_policies = iam_client.list_attached_user_policies(UserName=username)
    for p in attached_user_policies['AttachedPolicies']:
        policy_arns.add(p['PolicyArn'])

    # 2. Groups for the user
    groups_for_user = iam_client.list_groups_for_user(UserName=username)
    for group in groups_for_user['Groups']:
        group_name = group['GroupName']
        attached_group_policies = iam_client.list_attached_group_policies(GroupName=group_name)
        for gp in attached_group_policies['AttachedPolicies']:
            policy_arns.add(gp['PolicyArn'])

    return policy_arns


def generate_action_level_report(iam_client, policy_arn):
    """
    For a single managed policy, run generate_service_last_accessed_details with Granularity='ACTION_LEVEL'.
    Return a list of dictionaries where each dict contains:

        {
          "PolicyArn": policy_arn,
          "ServiceName": <string>,
          "ActionName": <string>,
          "LastAccessed": <datetime or None>
        }
    """
    job_response = iam_client.generate_service_last_accessed_details(
        Arn=policy_arn,
        Granularity='ACTION_LEVEL'
    )
    job_id = job_response['JobId']

    # Poll until the job completes
    while True:
        job_details = iam_client.get_service_last_accessed_details(JobId=job_id)
        if job_details['JobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(1)

    if job_details['JobStatus'] == 'FAILED':
        print(f"[ERROR] Failed to get service last accessed details for {policy_arn}", file=sys.stderr)
        return []

    # Now parse the results
    services_last_accessed = job_details.get('ServicesLastAccessed', [])
    results = []

    for service_info in services_last_accessed:
        service_name = service_info.get('ServiceName', 'UnknownService')
        tracked_actions = service_info.get('TrackedActionsLastAccessed', [])
        
        if not tracked_actions:
            # Possibly no recorded usage for that service or no tracked actions found
            # We'll log a single row showing the service with "NO_ACTION_DATA"
            last_authenticated = service_info.get('LastAuthenticated')
            results.append({
                "PolicyArn": policy_arn,
                "ServiceName": service_name,
                "ActionName": "NO_ACTION_DATA",
                "LastAccessed": last_authenticated
            })
        else:
            # If there are tracked actions, list them all
            for action_info in tracked_actions:
                action_name = action_info.get('ActionName', 'UnknownAction')
                last_access_time = action_info.get('LastAccessedTime')  # may be None
                results.append({
                    "PolicyArn": policy_arn,
                    "ServiceName": service_name,
                    "ActionName": action_name,
                    "LastAccessed": last_access_time
                })

    return results


def generate_user_permissions_report(username):
    """
    Main logic to:
      1. Fetch all managed policy ARNs for the user
      2. For each policy, fetch policy name and action-level last-access details
      3. Produce a list of dicts with columns:
         ["UserName", "PolicyName", "PolicyArn", "ServiceName", "ActionName", "LastAccessed"]
    """
    iam_client = boto3.client("iam")

    policy_arns = get_managed_policies_for_user(iam_client, username)

    rows = []
    for policy_arn in policy_arns:
        # Get the policy name
        policy_info = iam_client.get_policy(PolicyArn=policy_arn)
        policy_name = policy_info['Policy']['PolicyName']

        # Generate an action-level usage report for this policy
        action_level_data = generate_action_level_report(iam_client, policy_arn)

        for item in action_level_data:
            last_access_ts = item["LastAccessed"]
            # Convert to string for consistency
            last_access_str = last_access_ts.isoformat() if last_access_ts else "Never"
            rows.append({
                "UserName": username,
                "PolicyName": policy_name,
                "PolicyArn": item["PolicyArn"],
                "ServiceName": item["ServiceName"],
                "ActionName": item["ActionName"],
                "LastAccessed": last_access_str
            })

    return rows


def export_csv(report_data, output_file):
    """
    Export the report data to a CSV file.
    `report_data` should be a list of dicts with consistent keys.
    """
    if not report_data:
        print("[WARN] No data to export to CSV.")
        return

    fieldnames = list(report_data[0].keys())  # e.g. ["UserName", "PolicyName", ...]

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)

    print(f"[INFO] CSV report written to {output_file}")


def export_json(report_data, output_file):
    """
    Export the report data to a JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, default=str)  # default=str to handle datetime if any remain

    print(f"[INFO] JSON report written to {output_file}")


def export_yaml(report_data, output_file):
    """
    Export the report data to a YAML file.
    Requires PyYAML to be installed.
    """
    if not HAS_YAML:
        print("[ERROR] PyYAML is not installed. Install via 'pip install PyYAML' to enable YAML export.")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(report_data, f, sort_keys=False, default_flow_style=False)

    print(f"[INFO] YAML report written to {output_file}")


def export_xml(report_data, output_file):
    """
    Export the report data to an XML file using xml.etree.ElementTree.
    We'll create a root <Report> element, and each item is an <Record> with sub-elements.
    """
    root = ET.Element("Report")

    for record in report_data:
        record_el = ET.SubElement(root, "Record")
        for key, value in record.items():
            # For convenience, store everything as string
            child_el = ET.SubElement(record_el, key)
            child_el.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print(f"[INFO] XML report written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate IAM user action-level permissions report and export to CSV, JSON, YAML, or XML."
    )
    parser.add_argument("username", help="IAM username to analyze")
    parser.add_argument(
        "--format",
        default="csv",
        choices=["csv", "json", "yaml", "xml"],
        help="Output format (default: csv)"
    )
    parser.add_argument(
        "--output",
        default="iam-user-access-action-level-report-"+datetime.now().strftime('%m-%d-%Y'),
        help="Base name (without extension) for the output file. Example: 'report' => 'report.csv'"
    )
    args = parser.parse_args()

    # 1. Generate the user permissions (action-level) report
    report_data = generate_user_permissions_report(args.username)

    # 2. Export based on chosen format
    if args.format == "csv":
        export_csv(report_data, f"{args.output}.csv")
    elif args.format == "json":
        export_json(report_data, f"{args.output}.json")
    elif args.format == "yaml":
        export_yaml(report_data, f"{args.output}.yaml")
    elif args.format == "xml":
        export_xml(report_data, f"{args.output}.xml")


if __name__ == "__main__":
    main()
