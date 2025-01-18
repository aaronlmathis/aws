from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
    CfnTag,
)
from constructs import Construct

class LaunchNewEc2InstanceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        instance_name = self.node.try_get_context('instanceName') or "my-Instance"
        instance_type_str = self.node.try_get_context("instanceType") or "t2.micro"
        instance_type = ec2.InstanceType(instance_type_str)
        machine_image = self.node.try_get_context('machineImage') or ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)
        
        vpc_id = self.node.try_get_context("vpcId")
        if vpc_id:
            vpc = ec2.Vpc.from_lookup(self, "ExistingVPC", vpc_id=vpc_id)
        else:
            vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
        
        
        sg_id = self.node.try_get_context("sgId") or None
        
        if sg_id:
            sec_group = ec2.SecurityGroup.from_security_group_id(
                self,
                "ExistingSG",
                security_group_id=sg_id, 
                mutable=False
            )
        else:
            sec_group = ec2.SecurityGroup(
                self, "MySecurityGroup", vpc=vpc, allow_all_outbound=True
            )

            # Create Security Group Ingress Rule
            sec_group.add_ingress_rule(
                ec2.Peer.any_ipv4(), 
                ec2.Port.tcp(22), 
                "allow SSH access"
            )

        cfn_key_pair = self.node.try_get_context("cfnKeyPair")
        
        if cfn_key_pair:
            key_pair =  ec2.KeyPair.from_key_pair_name(
                            self,
                            "ImportedKeyPair",
                            key_pair_name=cfn_key_pair  
                ) 
        else:
            key_pair = None

        public_ip_enabled = self.node.try_get_context("publicIPEnabled")
        
        public_subnet = self.node.try_get_context("publicSubnet")
        vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC) if public_subnet else ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE) 


        user_data_file = self.node.try_get_context("userDataFile")
        if user_data_file:
            import os
            # Construct the absolute path if necessary
            user_data_file = os.path.join(os.path.dirname(__file__), user_data_file)
            
            with open(user_data_file, "r") as f:
                user_data_script = f.read()

            user_data = ec2.UserData.custom(user_data_script)
        else:
            user_data = None

        instance = ec2.Instance(
            self,
            instance_name,
            instance_type=instance_type,
            machine_image=machine_image,
            vpc=vpc,
            security_group=sec_group,
            associate_public_ip_address=public_ip_enabled,
            key_pair=key_pair,
            ssm_session_permissions=True,
            vpc_subnets=vpc_subnets,
            user_data=user_data
            )
        
        # Existing Elastic IP allocation ID.
        
        eip_allocation_id = self.node.try_get_context("eipAllocationId")
        if eip_allocation_id:
            # Associate the existing Elastic IP with the instance
            eip_association = ec2.CfnEIPAssociation(
                self,
                "ExistingEIPAssociation",
                allocation_id=eip_allocation_id,
                instance_id=instance.instance_id
            )

            # Adding explicit dependencies (optional, but helps ensure proper ordering)
            eip_association.node.add_dependency(instance)

        CfnOutput(self, "InstanceId", value=instance.instance_id)
