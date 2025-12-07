# MLOps Deployment
This repository demonstrates a production-grade MLOps deployment pipeline for machine learning models. The implementation includes:

- Flask REST API for classification prediction model serving
- Containerization using Docker
- Cloud deployment on AWS EC2
- Container registry integration with Amazon ECR 
- Automated CI/CD pipeline using GitHub Actions
- Infrastructure as Code using Pulumi   

## Infrastructure Setup with Pulumi

```bash
# Install dependencies
pip install -r requirements.txt

# Deploy infrastructure
pulumi up

# Get outputs
pulumi stack output ecr_repository_url
pulumi stack output instance_public_ip
```

## Manual Steps (Alternative)
1. Create ECR repository "mlops-flask-app" using AWS Console
2. Create a EC2 instance using AWS Console
   - Create an instance profile with ECRFullAccess permission as part of the EC2 Launch template
3. Log into the EC2 instance using EC2 instance connect via browser
    - update the server with root user privileges
    - install docker with root user privileges
    - start docker with root user privileges
    - check the status of docker with root user privileges
    - add ec2-user to the 'docker' group granting permission to run docker commands w/o sudo
    - activate the new 'docker' group
    - run docker -- version command to see if everything works perfectly


```bash
# Set up EC2 Instance
sudo yum update -y
sudo yum install -y docker 
sudo systemctl start docker
sudo service docker status 
sudo usermod -a -G docker ec2-user 
newgrp docker
docker —-version
```

## GitHub Actions
1. Setup GitHub repo with app.py, README.md, tests.py and .github\workflows\ci-cd.yml
     a. sync local and remote
     b. Setup Actions secrets in GitHub repo (will be used by ci-cd.yml)
2. Push updates to the remote repo to trigger the actions workflow.


```bash
# local testing
curl -X POST -H "Content-Type: application/json" \
     -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' \
     http://127.0.0.1:5000/predict


# Deployment testing
curl -X POST -H "Content-Type: application/json" -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' http://54.227.183.154/predict
```