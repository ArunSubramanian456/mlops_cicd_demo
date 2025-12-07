"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Step 1: Get the latest Amazon Linux 2 AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[aws.ec2.GetAmiFilterArgs(
        name="name",
        values=["amzn2-ami-hvm-*-x86_64-ebs"]
    )]
)

# Step 2: Create Security Group for EC2 instance
# Allows inbound HTTP (port 80) and outbound HTTPS/HTTP for package downloads
security_group = aws.ec2.SecurityGroup('web-server-sg',
    description='Enable SSH and HTTP access',
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol='-1',
        from_port=0,
        to_port=0,
        cidr_blocks=['0.0.0.0/0'],
    )],
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
            description='SSH access'
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
            description='HTTP access'
        )
    ]
)

# Step 3: Create IAM Role for EC2 with ECR access
# Define trust policy allowing EC2 to assume this role
assume_role = aws.iam.get_policy_document(statements=[{
    "effect": "Allow",
    "principals": [{
        "type": "Service",
        "identifiers": ["ec2.amazonaws.com"],
    }],
    "actions": ["sts:AssumeRole"],
}])

# Create the IAM role
role = aws.iam.Role("role",
    name="ec2_mlops_role",
    path="/",
    assume_role_policy=assume_role.json)

# Attach ECR full access policy to the role
aws.iam.RolePolicyAttachment("ecr-policy",
    role=role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess")

# Create instance profile to attach role to EC2
instance_profile = aws.iam.InstanceProfile("ec2-profile", role=role.name)

# Step 4: Define user data script to configure EC2 on launch
# Installs Docker and adds ec2-user to docker group
user_data = """#!/bin/bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
usermod -a -G docker ec2-user
docker --version
"""

# Step 5: Create EC2 instance with all configurations
instance = aws.ec2.Instance("mlops-instance",
    instance_type='t2.micro',
    ami=ami.id,
    associate_public_ip_address=True,
    vpc_security_group_ids=[security_group.id],
    iam_instance_profile=instance_profile.name,
    key_name="EC2Tutorial",
    user_data=user_data,
    tags={"Name": "mlops-flask-app"}
)

# Step 6: Create ECR repository for Docker images
ecr_repo = aws.ecr.Repository("mlops-flask-app", name="mlops-flask-app")

# Step 7: Export important values for use after deployment
pulumi.export("ecr_repository_url", ecr_repo.repository_url)
pulumi.export("instance_public_ip", instance.public_ip)
