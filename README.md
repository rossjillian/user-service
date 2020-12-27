# UserService Sample

This repository contains a sample microservice for users. It runs Flask and implements RESTful APIs.

The application can be run locally but is designed to be run on AWS:
- Compute on EC2
- Data Access Layer on RDS
- Middleware on SNS, Lambda, and SES deployed via the API Gateway

AWS credentials are set in `setcredentials.py`.

To run the service: `python3 -m application`
