#!/usr/bin/env python3
import os

import aws_cdk as cdk

from launch_new_vpc.launch_new_vpc_stack import LaunchNewVpcStack


app = cdk.App()
LaunchNewVpcStack(
    app, 
    "LaunchNewVpcStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    )

app.synth()
