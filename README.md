# Wine Cellar

Simple IoT Architecture designed for the Serverless Computing for IoT Course at the University of Salerno.
It makes use of Docker, Localstack and various utilities in order to manage, in a very simplified and straightforward way, a wine cellar.

- [Wine Cellar](#wine-cellar)
  - [Introduction](#introduction)
  - [Proposed Project Architecture](#proposed-project-architecture)
    - [Services Used](#services-used)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Setting up the environment](#setting-up-the-environment)
    - [Automated Install](#automated-install)
    - [Manual Install](#manual-install)
    - [Playing around with the system](#playing-around-with-the-system)
  - [Future developments](#future-developments)

## Introduction

It is a known fact that fine wines require a certain degree of ageing. For decades, humanity has developed many ways of keeping wine in the perfect condition to do so.
In the IoT era, with people being able to fully computerize their own homes, sensors could also be used in a local environment to construct and operate a small wine cellar.
This project aims at giving a simplified perspective of what a simple IoT architecture could be, by making use of sensors and AWS services emulated through LocalStack.

## Proposed Project Architecture

![Architecture Image](./images/SCIOT-Project.jpg "Project Architecture")

The architecture makes use of Lambda functions to recover sensor data from Amazon SQS Queues.
The data gets saved to an S3 bucket, for archiving purposes and in the form of a "data lake" for future inspection.
The aggregated data between each read is obtained by averaging values and comparing them with the current status. This aggregated data gets saved to the DynamoDB table, to provide a full view of the system through a Telegram bot that interfaces with the system's status through the API Gateway methods.

The DB differentiates the status of each room, by providing estimations of temperature, relative humidity and vibration. Each room is assigned to a certain type of wine, whose characteristics and storage conditions change and must be preserved.

Keeping the door open in one of the rooms could be a source of trouble: that's why the room is constantly monitored through the use of a Kinesis Data Stream, which is periodically checked to see if the door has remained open too long.

Whenever there's an error situation, be it a malfunctioning sensor, the storage conditions aren't met or the door still open after 10 minutes, a message is sent to an SNS topic.

Here, the message is then processed by a Lambda Function, that sends an HTTP request to the Telegram bot, which notifies the subscribed user.

The user can simply manage and keep track of all the data through the use of a Telegram Bot.
He can see the status of all the rooms, or each room individually and check the door status in real-time thanks to Kinesis.
He can also access charts that summarize the history of the measurements, thanks to the information recovered from the S3 Bucket.

All of the relevant user functionalities, such as accessing historical data, or interacting with the status of the system, are done through an API Gateway that exposes the relevant methods, implemented as Lambdas.

### Services Used

Here's a brief list of AWS services used:

- [Amazon SQS](https://aws.amazon.com/sqs/)
- [Amazon Lambda](https://aws.amazon.com/lambda/)
- [Amazon Kinesis Data Stream](https://aws.amazon.com/kinesis/data-streams/)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
- [Amazon S3](https://aws.amazon.com/s3/)
- [Amazon SNS](https://aws.amazon.com/sns/)
- [Amazon EventBridge](https://aws.amazon.com/eventbridge/)
- [Amazon CloudWatch Logs](https://aws.amazon.com/cloudwatch/)
- [Amazon API Gateway](https://aws.amazon.com/api-gateway/)

The project also makes use of a Telegram Bot, and there's a very rough but simple web application with a comprehensive dashboard, powered by Sinatra, a very simple DSL for web app creation.

## Installation

### Requirements

- [Docker](https://www.docker.com)
- [Docker Compose](https://docs.docker.com/compose/)
- [Localstack](https://localstack.cloud)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Python 3.9 or over]
- [boto3](https://aws.amazon.com/it/sdk-for-python/)
- [Telegram Bot](https://core.telegram.org/bots/api)
- [JQ](https://jqlang.github.io/jq/)
- [Ruby](https://www.ruby-lang.org/it)
- [Sinatra](https://sinatrarb.com)

### Setting up the environment

First, clone the repo and start Localstack through the docker-compose.yml.

```shell
git clone https://github.com/blazQ/wine-cellar.git
cd wine-cellar
docker-compose up
```

Then you need to either update config.py with your own Telegram ID and Bot Token or create a .env file with your own BOT_ID and BOT_TOKEN variables.
Then simply

```shell
source .env
```

This is required since the automated install makes use of the BOT_ID and BOT_TOKEN to power up the notification lambda function.

### Automated Install

Open another terminal in the main folder and start the setup.sh script:

```shell
chmod +x ./setup,sh
chmod +x ./zip_lambda.sh
./setup.sh
```

The shell script gets the current AWS region and gets all of the ARNs from the output of the commands, so there's no need to set anything. It should work regardless of your configuration.
For example, there's a lambda function that needs the SNS Topic Arn to be present as an environmental variable. This value is provided to the lambda by the script itself, so there's no need for you to configure it.

Once the setup does its job, it will have appended the API_ID value to the .env.
You can then start the web app with:

```shell
ruby ./src/webapp/app.rb
```

The web app is accessible at localhost:8080.
Then you can start the telegram bot if you want to have a chat with it instead of simply viewing the web app.

```shell
python3 ./src/bot.py
```

The notifications will work regardless of you starting the bot script.

### Manual Install

Assuming you've already set up the environment by creating the .env file, and assuming you've started LocalStack, you need to create all AWS resources by hand.

You can either use [awslocal](https://docs.localstack.cloud/user-guide/integrations/aws-cli/) wrapper script supplied by LocalStack, or use the AWS cli by adding `--endpoint-url==http://localhost:45666` at the beginning of each command.

First, let's create all of the MQTT queues:

```bash
aws sqs create-queue --queue-name errors --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name vaporPressureQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name dewPointQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name temperatureQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name vibrationQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name doorQueue --endpoint-url=http://localhost:4566
```

Take note of each of the queues' ARN and URLs.

Create the bucket:

```bash
aws s3 mb s3://sensorbucket --endpoint-url=http://localhost:4566
```

Create and populate the DB:

```bash
python3 ./src/db.py
```

Create the kinesis streams:

```bash
aws kinesis create-stream --stream-name doorStreamSweets --shard-count 1 --endpoint-url=http://localhost:4566
aws kinesis create-stream --stream-name doorStreamSparklings --shard-count 1 --endpoint-url=http://localhost:4566
aws kinesis create-stream --stream-name doorStreamDry-Whites --shard-count 1 --endpoint-url=http://localhost:4566
aws kinesis create-stream --stream-name doorStreamFull-bodied-reds --shard-count 1 --endpoint-url=http://localhost:4566
aws kinesis create-stream --stream-name doorStreamLight-to-medium-bodied-reds --shard-count 1 --endpoint-url=http://localhost:4566
```

Create the topic and take note of the topic's arn:

```bash
aws sns create-topic --name notificationTopic --endpoint-url=http://localhost:4566
```

Create the role and attach the policy:

```bash
aws iam create-role --role-name lambda-ex --assume-role-policy-document file://./policies/lambda_role_policy.json --endpoint-url=http://localhost:4566
aws iam put-role-policy --role-name lambda-ex --policy-name lambdapolicy \
--policy-document file://./policies/sensor_lambda_policy.json --endpoint-url=http://localhost:4566
```

Take note of the role's ARN.

Then zip the lambdas. The script supplied with the directory does it for you, except for the last one which requires adding the storage conditions to the archive:

```bash
sh zip_lambda.sh doorCheckFunc.py doorStatusFunc.py heatIndexFunc.py notifyFunc.py sensErrorFunc.py temperatureFunc.py vaporFunc.py vibrationFunc.py getRooms.py getDoors.py getSensorData.py
zip -j function12.zip ./src/lambdas/storageConditionsFunc.py ./src/config.py ./src/storage_conditions.json
```

Now you need to create all of the lambdas (assuming you took note of the role's arn):

```bash
aws lambda create-function --function-name doorCheckFunc \
--zip-file fileb://function1.zip --handler doorCheckFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:456

aws lambda create-function --function-name doorStatusFunc \
--zip-file fileb://function2.zip --handler doorStatusFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name heatIndexFunc \
--zip-file fileb://function3.zip --handler heatIndexFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name notifyFunc \
--zip-file fileb://function4.zip --handler notifyFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name sensErrorFunc \
--zip-file fileb://function5.zip --handler sensErrorFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name temperatureFunc \
--zip-file fileb://function6.zip --handler temperatureFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name vaporFunc \
--zip-file fileb://function7.zip --handler vaporFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name vibrationFunc \
--zip-file fileb://function8.zip --handler vibrationFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name getRoomsFunc \
--zip-file fileb://function9.zip --handler getRooms.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name getDoorsFunc \
--zip-file fileb://function10.zip --handler getDoors.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name getSensorData \
--zip-file fileb://function11.zip --handler getSensorData.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name storageConditionsFunc \
--zip-file fileb://function12.zip --handler storageConditionsFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566
```

Take note of the function ARN for the getSensorData, getDoorsFunc and getRoomsFunc lambdas, you'll need it to configure the API Gateway.

Update the configuration of some of the functions, by supplying the SNS Topic's arn:

```bash
aws lambda update-function-configuration --function-name storageConditionsFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566)

aws lambda update-function-configuration --function-name sensErrorFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name doorCheckFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566
```

And by supplying the BOT_ID and BOT_TOKEN env variables:

```bash
aws lambda update-function-configuration --function-name notifyFunc \
--timeout 60 --environment "Variables={BOT_ID=$BOT_ID,BOT_TOKEN=$BOT_TOKEN}" --endpoint-url=http://localhost:4566
```

Then you need to create all of the event-source mappings, I'll list only a few:

```bash
aws lambda create-event-source-mapping --function-name vaporFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $DEWPOINT_ARN \
 --endpoint-url=http://localhost:4566

 aws lambda create-event-source-mapping --function-name vibrationFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $VIBRATION_ARN \
 --endpoint-url=http://localhost:4566

 ....

 aws lambda create-event-source-mapping --function-name sensErrorFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $ERRORS_ARN \
 --endpoint-url=http://localhost:4566

```

Create the execution rules for all of the timed functions:

```bash
aws events put-rule \
--name door-schedule-rule \
--schedule-expression 'rate(5 minutes)' \
--endpoint-url=http://localhost:4566)

aws events put-rule \
--name storage-schedule-rule \
--schedule-expression 'rate(2 minutes)' \
--endpoint-url=http://localhost:4566)
```

Take note of both rule's ARN and then give permissions and put targets:

```bash
aws lambda add-permission \
--function-name doorCheckFunc \
--statement-id door-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn $rule_door_ARN \
--endpoint-url=http://localhost:4566

aws lambda add-permission \
--function-name storageConditionsFunc \
--statement-id storage-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn $rule_storage_ARN \
--endpoint-url=http://localhost:4566

aws events put-targets --rule door-schedule-rule --targets file://src/door_targets.json --endpoint-url=http://localhost:4566

aws events put-targets --rule storage-schedule-rule --targets file://src/storage_targets.json --endpoint-url=http://localhost:4566

```

Assuming you've noted the Topic's ARN, get the notifyFunction's ARN and then subscribe to the topic:

```bash
aws sns subscribe --protocol lambda \
--region $current_region \
--topic-arn $TOPIC_ARN \
--notification-endpoint $NOTIFY_ARN \
--endpoint-url=http://localhost:4566)
```

Now you only need to create the API Gateway, by creating the parent resource and then the 3 path parts:

```bash
aws --endpoint-url=http://localhost:4566 apigateway create-rest-api --name 'API Gateway Lambda integration'
```

Take note of the API's ID and then get the root resource ID with:

```bash
aws --endpoint-url=http://localhost:4566 apigateway get-resources --rest-api-id $api_id
```

Take note of the root resource and then create the path parts:

```bash
aws --endpoint-url=http://localhost:4566 apigateway create-resource --rest-api-id $api_id --parent-id $parent_id --path-part room

aws --endpoint-url=http://localhost:4566 apigateway create-resource --rest-api-id $api_id --parent-id $parent_id --path-part doors

aws --endpoint-url=http://localhost:4566 apigateway create-resource --rest-api-id $api_id --parent-id $parent_id --path-part sensor
```

Take note of all the resource ids, and then put method and integration for all of them (now you'll need the three function ARNs that you took note of earlier):

```bash
# Put the methods
aws --endpoint-url=http://localhost:4566 apigateway put-method --rest-api-id $api_id --resource-id $resource_id1 --http-method GET --request-parameters 'method.request.path.room=true' --authorization-type "NONE"

aws --endpoint-url=http://localhost:4566 apigateway put-method --rest-api-id $api_id --resource-id $resource_id2 --http-method GET --request-parameters 'method.request.path.doors=true' --authorization-type "NONE"

aws --endpoint-url=http://localhost:4566 apigateway put-method --rest-api-id $api_id --resource-id $resource_id3 --http-method GET --request-parameters 'method.request.path.sensors=true' --authorization-type "NONE"

# Integrate with lambda
aws --endpoint-url=http://localhost:4566 apigateway put-integration --rest-api-id $api_id --resource-id $resource_id1 --http-method GET --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:$current_region:lambda:path/2015-03-31/functions/$function1_arn/invocations" --passthrough-behavior WHEN_NO_MATCH

aws --endpoint-url=http://localhost:4566 apigateway put-integration --rest-api-id $api_id --resource-id $resource_id2 --http-method GET --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:$current_region:lambda:path/2015-03-31/functions/$function2_arn/invocations" --passthrough-behavior WHEN_NO_MATCH

aws --endpoint-url=http://localhost:4566 apigateway put-integration --rest-api-id $api_id --resource-id $resource_id3 --http-method GET --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:$current_region:lambda:path/2015-03-31/functions/$function3_arn/invocations" --passthrough-behavior WHEN_NO_MATCH
```

### Playing around with the system

You can use the sensor.py and the sensorTestSuite.py to create massive tests for all of the components of the architecture and you can configure the waiting times, queue names and table names from the config.py script and the .env.
In order to use sensorTestSuite, you can start by invoking a very simple door sensor or temperature sensor:

```shell
python3 ./src/sensorTestSuite.py -st Door -r Sweets
python3 ./src/sensorTestSuite.py -st Temperature -r Sparklings
```

Or maybe massively sending random door data to all of the rooms (will fill you up with notifications):

```shell
python3 ./src/sensorTestSuite.py -all
```

You can also specify with -n how many repetitions you want to make.
For example, by calling in a specific sensor and then putting -n x, the script will activate the same sensor in the same room for x times.
By calling the complete test suite, you will see x reps for each sensor type.

Finally, you can also specify an error threshold, to experiment with what happens if the sensor fails more often or less often.

```shell
python3 ./src/sensorTestSuite.py -all -n 10 -e 0.3
```

## Future developments

The project could be improved by adding another data pipeline regarding the light sensors since it's also a very important metric in the context of wine storage.
It could also be improved by developing a more complex web application, including registration and notifications, which as of now are available through the telegram bot endpoint.
It could be expanded and more functionality could be offered to the user, by making it possible to add more rooms and by simplifying the interface and the general usage flow.
While this is clearly an oversimplification of an incredibly complex domain, there are plenty of things to improve and it shouldn't be difficult thanks to the robustness of AWS' service architecture.
