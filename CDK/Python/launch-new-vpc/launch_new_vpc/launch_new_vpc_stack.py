from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class LaunchNewVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Retrieve configuration from context, falling back to defaults if not provided.
        vpc_id = self.node.try_get_context("vpcId") or "LaunchNewVpcStack"

        vpc_cidr = self.node.try_get_context("vpcCidr") or "10.10.0.0/16"
        max_azs = int(self.node.try_get_context("maxAzs") or 2)
        num_nat_gateways = int(self.node.try_get_context("numNatGateways") or 1)

        public_cidr_mask = int(self.node.try_get_context("publicCidrMask") or 24)
        private_cidr_mask = int(self.node.try_get_context("privateCidrMask") or 24)
        
        map_public_ip = self.node.try_get_context("mapPublicIp")
        if map_public_ip is None:
            map_public_ip = False

        create_internet_gateway = self.node.try_get_context("createInternetGateway")
        if create_internet_gateway is None:
            create_internet_gateway = False  

        dns_hostnames = self.node.try_get_context("dnsHostnames")
        if dns_hostnames is None:
            dns_hostnames = False  

        dns_support = self.node.try_get_context("dnsSupport")
        if dns_support is None:
            dns_support = False 

        self.vpc = ec2.Vpc(self, vpc_id,
                           max_azs=max_azs,
                           cidr=vpc_cidr,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   name="Public",
                                   cidr_mask=public_cidr_mask,
                                   map_public_ip_on_launch=map_public_ip
                               ),
                               ec2.SubnetConfiguration(
                                   subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                   name="Private",
                                   cidr_mask=private_cidr_mask
                               )
                           ],
                           enable_dns_support=dns_support,
                           enable_dns_hostnames=dns_hostnames,
                           nat_gateways=num_nat_gateways,
                           )

        CfnOutput(self, "VPCIdOutput", value=self.vpc.vpc_id)


