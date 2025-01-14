CDK/PYTHON
# import the necessary classes
import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput
)

# class/function/main code definition 
class EC2InstanceStack(cdk.Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define constants from CLI commands
        AMI_ID = "ami-0c7af5fe939f2677f"
        INSTANCE_TYPE = "t2.micro"
        KEY_NAME = ""
        USER_DATA = "PLEASE ADD YOUR DATA BACK IN HERE"
        VOLUME_SNAPSHOT_ID = "snap-0d00c5462139042b8"
        VOLUME_SIZE = 10
        VOLUME_TYPE = "gp3"
        VOLUME_IOPS = 3000
        VOLUME_THROUGHPUT = 125
        SUBNET_ID = ""
        SECURITY_GROUP_ID = ""
        CPU_CREDITS = "standard"
        INSTANCE_NAME = ""
        ENVIRONMENT = ""
        INSTANCE_PROFILE_ARN = ""

        # Create EC2 Instance
        instance = ec2.Instance(
            self, "EC2Instance",
            instance_type=ec2.InstanceType(INSTANCE_TYPE),
            machine_image=ec2.MachineImage.lookup(
                name=AMI_ID,
                owners=["self"]
            ),
            key_name=KEY_NAME,
            user_data=ec2.UserData(USER_DATA),
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=ec2.BlockDeviceVolume.ebs(
                        snapshot_id=VOLUME_SNAPSHOT_ID,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                        iops=VOLUME_IOPS,
                        throughput=VOLUME_THROUGHPUT,
                        volume_size=VOLUME_SIZE,
                        encrypted=False,
                        delete_on_termination=True
                    )
                )
            ],
            vpc_subnets=ec2.SubnetSelection(subnet_ids=[SUBNET_ID]),
            security_group=ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", SECURITY_GROUP_ID),
            credit_specification=ec2.CreditSpecification.STANDARD,
            instance_name=INSTANCE_NAME,
            instance_profile=iam.InstanceProfile.from_instance_profile_arn(self, "InstanceProfile", INSTANCE_PROFILE_ARN),
            metadata_options=ec2.InstanceMetadataOptions(
                http_endpoint="enabled",
                http_put_response_hop_limit=2,
                http_tokens="required"
            ),
            private_dns_name_options=ec2.PrivateDnsNameOptions(
                hostname_type=ec2.HostnameType.IP_NAME,
                enable_resource_name_dns_a_record=False,
                enable_resource_name_dns_aaaa_record=False
            )
        )

        # Add tags to the instance
        cdk.Tags.of(instance).add("Environment", ENVIRONMENT)

        # Output the instance ID
        CfnOutput(self, "InstanceId", value=instance.instance_id)

if __name__ == "__main__":
    app = cdk.App()
    EC2InstanceStack(app, "EC2InstanceStack")
    app.synth()
