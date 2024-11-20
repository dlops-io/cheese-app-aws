## Cheese App AWS

## Deployment to AWS

In this section we will deploy the Cheese App to AWS using Ansible Playbooks. We will automate all the deployment steps.

### API's to enable in AWS before you begin

<!-- - ECR (Elastic Container Registry) - to store our docker images
- IAM (Identity and Access Management) - to manage access to our AWS resources
- VPC (Virtual Private Cloud) - to provide a secure and isolated network environment for our resources
- Security Groups - to control the network traffic to our resources
- Load Balancer - to distribute traffic to our resources -->

### Setup AWS Keys for Authentication 

- Here are the steps to setup AWS keys for authentication

- IAM -> Policies -> Create Policy -> Json -> 

Copy and paste the following json into the policy editor
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity",
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:ListImages",
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ],
            "Resource": "*"
        }
    ]
}
```

Click on "Review Policy" -> Name: CheeseAppECRPolicy -> Create Policy

- AWS Console -> IAM -> Users -> Create User  -> Username: deployment-ac215-user -> Attach existing policies directly -> AmazonS3FullAccess , AmazonEC2FullAccess, AmazonBedrockFullAccess -> Next (Leave default) -> Create User

- Also attach the CheeseAppECRPolicy policy to the user

- Click on the user "deployment-ac215-user" ->  Create access key -> Third Party Service (because we will be using GitHub Actions/ Ansible to deploy) -> Click on confirmation -> Next -> Create access key -> Download .csv file

- Save deployment-ac215-user_accessKeys.csv in secrets folder. 
```
        .
        ├── cheese_app_aws
        ├── secrets
        │   └── deployment-ac215-user_accessKeys.csv
```

### Create AWS EC2 Key Pair

- AWS Console -> EC2 -> Key Pairs -> Create Key Pair -> Key Pair Name: cheese-app-ac215-key-pair -> Download .pem file -> Save in secrets folder


### Deployment Setup

- Add ansible user details in inventory.yml file
- AWS Compute instance details in inventory.yml file
- AWS Access Key details in inventory.yml file
- AWS Key Pair details in inventory.yml file

### Deployment Steps
- Go to src/deployment folder
- Change the AWS Access Key details ie. `CSV_FILE="../../../secrets/deployment-ac215-user_accessKeys.csv"` in docker-shell.sh file
- Run `sh docker-shell.sh` 


#### Build and Push Docker Containers to AWS ECR (Elastic Container Registry)
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

#### Create Compute Instance (VM) Server in GCP
```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
```

Once the command runs successfully get the IP address of the compute instance from AWS Console and update the appserver>hosts in inventory.yml file

#### Provision Compute Instance in GCP
Install and setup all the required things for deployment.
```
ansible-playbook deploy-provision-instance.yml -i inventory.yml
```

#### Setup Docker Containers in the  Compute Instance
```
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```


You can SSH into the server from the GCP console and see status of containers
```
sudo docker container ls
sudo docker container logs api-service -f
sudo docker container logs frontend -f
sudo docker container logs nginx -f
```

To get into a container run:
```
sudo docker exec -it api-service /bin/bash
sudo docker exec -it nginx /bin/bash
```



#### Configure Nginx file for Web Server
* Create nginx.conf file for defaults routes in web server

#### Setup Webserver on the Compute Instance
```
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```
Once the command runs go to `http://<External IP>/` 

## **Delete the Compute Instance / Persistent disk**
```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=absent
```
