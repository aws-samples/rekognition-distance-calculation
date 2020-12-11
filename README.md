# rekognition-distance-calculation

Repository with the focus of measure the distance form people based on a picture

# Architecture

<p align="center"> 
<img src="images/rekognition_social_distance_pt2.jpg">
</p>

# Setup instructions

## Provision the infrastructure

You just need to run the cloudformation template to provision the infraestructure and all components

First you need to create a S3 bucket to store our application lambda code.

``` shell
aws s3 mb s3://<MY_BUCKET_NAME>
```

ZIP lambda code.

``` shell
zip ./lambda_package_crowd.zip process_distance/lambda_function.py
```

``` shell
zip ./lambda_package_notify.zip lambda-sns-notify/lambda_function.py
```

Upload the lambda packages to the S3 bucket that we created before.

``` shell
aws s3 cp lambda_package_crowd.zip s3://<MY_BUCKET_NAME>/lambda_code/
```

``` shell
aws s3 cp pillow-layer/pillow-layer.zip s3://<MY_BUCKET_NAME>/lambda_layer/
```

``` shell
aws s3 cp lambda_package_notify.zip s3://<MY_BUCKET_NAME>/lambda_code/
```

Now we need to create the stack using our Cloudformation template available in **cloudformation/** folder

``` shell
aws cloudformation create-stack --stack-name crowd-rekognition-stack --template-body file://template/cloudformation.yml --parameters ParameterKey=StackName,ParameterValue=crowd-rekognition-stack ParameterKey=BucketPictures,ParameterValue=<NEW_BUCKET_NAME_PICTURES> ParameterKey=BucketWarning,ParameterValue=<NEW_BUCKET_NAME_WAWRNINGS> ParameterKey=BucketLambdaCode,ParameterValue=<BUCKET_NAME_THAT_WE_PROVISIONED_BEFORE> ParameterKey=SnsSubscriptionEmail,ParameterValue=<YOUR_EMAIL_ADDRESS> --capabilities CAPABILITY_IAM
```

Wait for the stack to be created.
