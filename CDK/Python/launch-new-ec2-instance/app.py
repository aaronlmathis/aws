#!/usr/bin/env python3
import os

import aws_cdk as cdk

from launch_new_ec2_instance.launch_new_ec2_instance_stack import LaunchNewEc2InstanceStack



app = cdk.App()
LaunchNewEc2InstanceStack(
    app, 
    "LaunchNewEc2InstanceStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
                        region=os.getenv('CDK_DEFAULT_REGION')),

    )

app.synth()
