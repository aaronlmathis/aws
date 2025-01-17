import aws_cdk as core
import aws_cdk.assertions as assertions

from launch_new_vpc.launch_new_vpc_stack import LaunchNewVpcStack

# example tests. To run these tests, uncomment this file along with the example
# resource in launch_new_vpc/launch_new_vpc_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LaunchNewVpcStack(app, "launch-new-vpc")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
