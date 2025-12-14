from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class ComputeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security Group for Ollama Access
        self.ollama_sg = ec2.SecurityGroup(self, "OllamaSecurityGroup",
            vpc=vpc,
            description="Allow inbound traffic for Ollama",
            allow_all_outbound=True
        )
        
        # Allow internal traffic from Lambda (will be restricted later if needed)
        self.ollama_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(11434),
            description="Allow Ollama API access from within VPC"
        )

        # IAM Role for EC2
        role = iam.Role(self, "OllamaInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        # User Data script to install Ollama
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "curl -fsSL https://ollama.com/install.sh | sh",
            "systemctl enable ollama",
            "systemctl start ollama",
            "ollama pull llama3.2:3b-instruct",
            "ollama pull all-minilm"
        )

        # EC2 Instance
        self.instance = ec2.Instance(self, "OllamaInstance",
            instance_type=ec2.InstanceType("t4g.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_group=self.ollama_sg,
            role=role,
            user_data=user_data,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(30)
                )
            ]
        )
