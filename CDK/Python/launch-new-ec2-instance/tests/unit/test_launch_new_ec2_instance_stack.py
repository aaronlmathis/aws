import aws_cdk as core
import aws_cdk.assertions as assertions

from launch_new_ec2_instance.launch_new_ec2_instance_stack import LaunchNewEc2InstanceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in launch_new_ec2_instance/launch_new_ec2_instance_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LaunchNewEc2InstanceStack(app, "launch-new-ec2-instance")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
