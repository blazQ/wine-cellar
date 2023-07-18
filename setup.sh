# Create SQS Queues
echo "Creating the queues..."

aws sqs create-queue --queue-name errors --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name vaporPressureQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name dewPointQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name temperatureQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name vibrationQueue --endpoint-url=http://localhost:4566
aws sqs create-queue --queue-name doorQueue --endpoint-url=http://localhost:4566

echo "Creating the bucket..."

# Create the S3 Bucket
aws s3 mb s3://sensorbucket --endpoint-url=http://localhost:4566

echo "Creating and populating db..."

# Create and populate the DB
python3 ./src/db.py

# Create Kinesis Data Stream


echo "Creating and enabling role and role policy..."
# Create admin role
aws iam create-role --role-name lambda-ex --assume-role-policy-document file://./policies/lambda_role_policy.json \
--query 'Role.Arn' --endpoint-url=http://localhost:4566

# Attach policy to the role
aws iam put-role-policy --role-name lambda-ex --policy-name lambdapolicy \
--policy-document file://./policies/sensor_lambda_policy.json --endpoint-url=http://localhost:4566

echo "Zipping all lambda functions..."

# Zipping all the functions
sh zip_lambda.sh doorCheckFunc.py doorStatusFunc.py heatIndexFunc.py notifyFunc.py sensErrorFunc.py temperatureFunc.py vaporFunc.py vibrationFunc.py
zip -j function9.zip ./src/lambdas/storageConditionsFunc.py ./src/config.py ./src/storage_conditions.json

echo "Creating lambda functions.."

aws lambda create-function --function-name doorCheckFunc \
--zip-file fileb://function1.zip --handler doorCheckFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name doorStatusFunc \
--zip-file fileb://function2.zip --handler doorStatusFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name heatIndexFunc \
--zip-file fileb://function3.zip --handler heatIndexFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name notifyFunc \
--zip-file fileb://function4.zip --handler notifyFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name sensErrorFunc \
--zip-file fileb://function5.zip --handler sensErrorFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name temperatureFunc \
--zip-file fileb://function6.zip --handler temperatureFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name vaporFunc \
--zip-file fileb://function7.zip --handler vaporFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name vibrationFunc \
--zip-file fileb://function8.zip --handler vibrationFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda create-function --function-name storageConditionsFunc \
--zip-file fileb://function9.zip --handler storageConditionsFunc.lambda_handler  \
--runtime python3.9 --role arn:aws:iam::000000000000:role/lambda-ex \
--endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name vaporFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name vibrationFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name storageConditionsFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name temperatureFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name sensErrorFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name doorCheckFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name doorStatusFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name notifyFunc \
--timeout 60 --endpoint-url=http://localhost:4566

aws lambda update-function-configuration --function-name heatIndexFunc \
--timeout 60 --endpoint-url=http://localhost:4566

echo "Creating all event-source mappings..."
# Mapping to get vapor from dewpointqueue
 aws lambda create-event-source-mapping --function-name vaporFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:dewPointQueue \
 --endpoint-url=http://localhost:4566

 # Mapping to get vibration from vibrationqueue
  aws lambda create-event-source-mapping --function-name vibrationFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:vibrationQueue \
 --endpoint-url=http://localhost:4566

# Mapping to get temperature from temperaturequeue
  aws lambda create-event-source-mapping --function-name temperatureFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:temperatureQueue \
 --endpoint-url=http://localhost:4566

# mapping to get heat index from vaporPressure
  aws lambda create-event-source-mapping --function-name heatIndexFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:vaporPressureQueue \
 --endpoint-url=http://localhost:4566

# mapping to get door status from doorqueue
  aws lambda create-event-source-mapping --function-name doorStatusFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:doorQueue \
 --endpoint-url=http://localhost:4566

# mapping to get sens error status from error queue
  aws lambda create-event-source-mapping --function-name sensErrorFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn arn:aws:sqs:us-west-2:000000000000:errors \
 --endpoint-url=http://localhost:4566

echo "Creating EventBridge rules to enable door checking and storage checking..."
# EventBridge rules
aws events put-rule \
--name door-schedule-rule \
--schedule-expression 'rate(5 minutes)' \
--endpoint-url=http://localhost:4566

aws events put-rule \
--name storage-schedule-rule \
--schedule-expression 'rate(2 minutes)' \
--endpoint-url=http://localhost:4566

# Add permissions to rule
echo "Adding permissions..."

aws lambda add-permission \
--function-name doorCheckFunc \
--statement-id door-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:us-west-2:000000000000:rule/door-schedule-rule \
--endpoint-url=http://localhost:4566 

aws lambda add-permission \
--function-name storageConditionsFunc \
--statement-id storage-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:us-west-2:000000000000:rule/door-schedule-rule \
--endpoint-url=http://localhost:4566 

# Putting targets
echo "Putting targets..."
aws events put-targets --rule door-schedule-rule --targets file://src/door_targets.json --endpoint-url=http://localhost:4566
aws events put-targets --rule storage-schedule-rule --targets file://src/storage_targets.json --endpoint-url=http://localhost:4566

echo "Creating the notify topic..."
# Create the SNS Topic
output=$(aws sns create-topic --name notificationTopic --endpoint-url=http://localhost:4566)
TOPIC_ARN=$(echo "$output" | jq -r '.TopicArn')

echo "Subscribing notifyFunc to topic..."
# Making the notifyFunc subscribe to the topic
aws sns subscribe --protocol lambda \
--region us-west-2 \
--topic-arn $TOPIC_ARN \
--notification-endpoint arn:aws:lambda:us-west-2:000000000000:function:notifyFunc \
--endpoint-url=http://localhost:4566

echo "Cleaning up folders..."
rm -f *.zip