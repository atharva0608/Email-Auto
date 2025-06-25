# Email Automation Project

## Deployment on EC2

1. SSH into EC2:
```
ssh ubuntu@<ec2-ip>
```

2. Install Docker:
```
sudo apt update
sudo apt install docker.io docker-compose -y
```

3. Clone repo and navigate:
```
git clone <your-repo-url>
cd email-automation-full
```

4. Build and run:
```
sudo docker-compose build
sudo docker-compose up -d
```

5. Access dashboard at `http://<ec2-ip>:5000`
