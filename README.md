# notifhome-serverless

This project allows a user to send an notification creating an alert on a IoT board.

You must have an AWS account.

![Notifhone Architecture](notifhome-architecture.png?raw=true)

### Flow

1. a user sends an HTTP post request containing a message to the AWS API gateway
2. the API gateway verifies the user credentials (IAM)
3. if the user has valid credentials, then a lambda is triggered
4. the lambda adds the message received in a SQS
5. an item added in the SQS triggered another lambda that publishes the message as a IoT topic
6. the board subscribed to the IoT topic receives the message

Some of the benefits using AWS services:
 - High throughput — Support for large number of requests per second
 - Low latency — Response to the API calls within a short period of time
 - Fault tolerance — In case of request payload error or processing error, gracefully store and replay the messages.
 - Monitoring — View the number of API calls along with the latency and numbers of errors
 - Security — Secure API endpoints and support for multiple authorization strategies.
 - Auto scaling — Support for increasing/decreasing (uneven) workloads

## Setup

This application is using the [serverless framework](https://serverless.com/). Read the documentation to install it on your machine.

When creating the user **serverless-agent**, please use the policy in `aws/serverless.policy`. Also add the following policies:
- AmazonSQSFullAccess 
- IAMFullAccess 
- AWSIoTConfigAccess

### Customization

Rename the template file:
```
$ mv my-notifhome.yml.tpl my-notifhome.yml
```

Then edit it with your own values. For `csr`, read the next section.

### Certificates

Create a private key:
```
$ cd aws
$ openssl genrsa -out ./awsiot.key 2048
```

Create a CSR (certificate signing request) for your board:
```
$ openssl req -new -sha256 -key ./awsiot.key -out ./awsiot-board.csr
```

Copy the content of `aws/awsiot-board.csr` in `my-notifhome.yml`, as the value for the key `board.csr`.

## Deploy

Now you are ready to deploy:
```
$ sls deploy
```

Please note the **endpoint** for the POST request, you will need it in Postman.

--In API Gateway, go to Resources, click on POST and on Method Response. Add a new response with code 200 and add the header **Access-Control-Allow-Origin**. Save. Click on Actions and select **Deploy API**.--

## Remove everything

In case you want to remove this project from AWS:
```
$ sls remove
```

## Authentication

### User

In order for your user to send an HTTP request to the API gateway, the user needs to be authenticated.
Sign in to the IAM console, select your user and click on the tab **Security Credentials**.  Click on **Create access key**. A `Access key ID` and a `Secret access key` will be automatically generated. Save them for later.

#### Postman

Open Postman and create a new POST request. The URL is the endpoint specified in the result of the command `sls deploy`. Go to **Authorization** and fill up the following fields:
- Type: AWS Signature
- AccessKey: the access key ID generated earlier
- SecretKey: the secret access key generated earlier
- AWS Region: your region
- Service Name: execute-api
- Session Token: leave it blank

Go to **Body**, select **raw** and enter this text:
```
{
  "message": "hello from Postman!"
}
```

Press **Send** and you should have a status code **200 OK** (and an empty body).

#### Client

So far, there is no application available, but instead there is a simple HTML page with some Javascript files.
Rename the following file and edit it by setting the appropriate values:
```
$ mv client/my-aws-credentials.js.tpl client/my-aws-credentials.js
```

Test everything is OK by opening the page `index.html` with your browser on your computer. If you can send a message then you can copy all the files from the folder `client` to your smartphone. On your phone, launch Firefox and open `index.html`.

Note: it doesn't work with Chrome.


### board

## Board setup

### Omega2

Copy the script file `board/omega2/notifhome_omega2.py` to your Omega2 (using the command `scp` for example).

Install the required libraries:
```
$ opkg update
$ opkg install python-light python-pip pyOnionGpio pyOledExp
$ pip install boto3
```

Go to IOT Core web console, select Things then select **notifhomeBoard**. In **Actions** select **Download** to download the certificate in `aws` folder on your computer. Rename the certificate to `notifhomeBoard.pem.crt`.

On your Omega2, create a folder that will contain the certificates:
```
$ mkdir certs
```

Copy the 3 following files in `/root/certs` on your Omega2:
- `aws/awsiot.key`: private key (created earlier)
- `aws/AmazonRootCA1.pem`: CA certificate 
- `aws/notifhomeBoard.pem.crt`: certicate that you just downloaded

Go to **Settings** in the IoT Core web console to get your endpoint. In the same folder where `notifhome_omega2.py` is located, create a file named `endpoint.txt` and paste your endpoint.


### RaspberryPi
```
$ sudo apt-get update
$ sudo apt-get install nodejs npm
$ sudo ln -s /usr/bin/nodejs /usr/bin/node
$ node -v
v4.8.2
$ npm -v 
1.4.21
```
