# Sourcing .env variables 
set -a
source .env
set +a

# Create SQS Queues
echo "Creating the queues..."

output_errors=$(aws sqs create-queue --queue-name errors --endpoint-url=http://localhost:4566)
ERRORS_URL=$(echo "$output_errors" | jq -r '.QueueUrl')
ERRORS_ARN=$(aws sqs get-queue-attributes --queue-url $ERRORS_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

output_vapor=$(aws sqs create-queue --queue-name vaporPressureQueue --endpoint-url=http://localhost:4566)
VAPOR_URL=$(echo "$output_vapor" | jq -r '.QueueUrl')
VAPOR_ARN=$(aws sqs get-queue-attributes --queue-url $VAPOR_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

output_dewpoint=$(aws sqs create-queue --queue-name dewPointQueue --endpoint-url=http://localhost:4566)
DEWPOINT_URL=$(echo "$output_dewpoint" | jq -r '.QueueUrl')
DEWPOINT_ARN=$(aws sqs get-queue-attributes --queue-url $DEWPOINT_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

output_temperature=$(aws sqs create-queue --queue-name temperatureQueue --endpoint-url=http://localhost:4566)
TEMP_URL=$(echo "$output_temperature" | jq -r '.QueueUrl')
TEMP_ARN=$(aws sqs get-queue-attributes --queue-url $TEMP_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

output_vibration=$(aws sqs create-queue --queue-name vibrationQueue --endpoint-url=http://localhost:4566)
VIBRATION_URL=$(echo "$output_vibration" | jq -r '.QueueUrl')
VIBRATION_ARN=$(aws sqs get-queue-attributes --queue-url $VIBRATION_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

output_door=$(aws sqs create-queue --queue-name doorQueue --endpoint-url=http://localhost:4566)
DOOR_URL=$(echo "$output_door" | jq -r '.QueueUrl')
DOOR_ARN=$(aws sqs get-queue-attributes --queue-url $DOOR_URL \
--attribute-name QueueArn --endpoint-url=http://localhost:4566 | jq -r '.Attributes.QueueArn')

echo "Creating the bucket..."

# Create the S3 Bucket
output_bucket=$(aws s3 mb s3://sensorbucket --endpoint-url=http://localhost:4566)

echo "Creating and populating db..."

# Create and populate the DB
python3 ./src/db.py

# Create Kinesis Data Stream

# Creating the topic
echo "Creating the notify topic..."
# Create the SNS Topic
output=$(aws sns create-topic --name notificationTopic --endpoint-url=http://localhost:4566)
TOPIC_ARN=$(echo "$output" | jq -r '.TopicArn')

echo "Creating and enabling role and role policy..."
# Create admin role
output_role=$(aws iam create-role --role-name lambda-ex --assume-role-policy-document file://./policies/lambda_role_policy.json --endpoint-url=http://localhost:4566)
output_role_ARN=$(echo "$output_role" | jq -r '.Role.Arn')

# Attach policy to the role
output_role_attach=$(aws iam put-role-policy --role-name lambda-ex --policy-name lambdapolicy \
--policy-document file://./policies/sensor_lambda_policy.json --endpoint-url=http://localhost:4566)

echo "Zipping all lambda functions..."

# Zipping all the functions
sh zip_lambda.sh doorCheckFunc.py doorStatusFunc.py heatIndexFunc.py notifyFunc.py sensErrorFunc.py temperatureFunc.py vaporFunc.py vibrationFunc.py
zip -j function9.zip ./src/lambdas/storageConditionsFunc.py ./src/config.py ./src/storage_conditions.json

echo "Creating lambda functions.."

output_door_func=$(aws lambda create-function --function-name doorCheckFunc \
--zip-file fileb://function1.zip --handler doorCheckFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_door_check_func=$(aws lambda create-function --function-name doorStatusFunc \
--zip-file fileb://function2.zip --handler doorStatusFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_heat_func=$(aws lambda create-function --function-name heatIndexFunc \
--zip-file fileb://function3.zip --handler heatIndexFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_notify=$(aws lambda create-function --function-name notifyFunc \
--zip-file fileb://function4.zip --handler notifyFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)
NOTIFY_ARN=$(echo "$output_notify" | jq -r '.FunctionArn')

output_error_func=$(aws lambda create-function --function-name sensErrorFunc \
--zip-file fileb://function5.zip --handler sensErrorFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_temp_func=$(aws lambda create-function --function-name temperatureFunc \
--zip-file fileb://function6.zip --handler temperatureFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_vapor_func=$(aws lambda create-function --function-name vaporFunc \
--zip-file fileb://function7.zip --handler vaporFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_vib_func=$(aws lambda create-function --function-name vibrationFunc \
--zip-file fileb://function8.zip --handler vibrationFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_storage_func=$(aws lambda create-function --function-name storageConditionsFunc \
--zip-file fileb://function9.zip --handler storageConditionsFunc.lambda_handler  \
--runtime python3.9 --role $output_role_ARN \
--endpoint-url=http://localhost:4566)

output_update_v1=$(aws lambda update-function-configuration --function-name vaporFunc \
--timeout 60 --endpoint-url=http://localhost:4566)

output_update_v2=$(aws lambda update-function-configuration --function-name vibrationFunc \
--timeout 60 --endpoint-url=http://localhost:4566)

output_update_v3=$(aws lambda update-function-configuration --function-name storageConditionsFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566)

output_update_v4=$(aws lambda update-function-configuration --function-name temperatureFunc \
--timeout 60 --endpoint-url=http://localhost:4566)

# Granting the env variable containing the topic arn to the container the lambda is hosted in
output_update_v5=$(aws lambda update-function-configuration --function-name sensErrorFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566)

output_update_v6=$(aws lambda update-function-configuration --function-name doorCheckFunc \
--timeout 60 --environment "Variables={SNSTopicArn=$TOPIC_ARN}" --endpoint-url=http://localhost:4566)

output_update_v7=$(aws lambda update-function-configuration --function-name doorStatusFunc \
--timeout 60 --endpoint-url=http://localhost:4566)

output_update_v8=$(aws lambda update-function-configuration --function-name notifyFunc \
--timeout 60 --environment "Variables={BOT_ID=$BOT_ID,BOT_TOKEN=$BOT_TOKEN}" --endpoint-url=http://localhost:4566)

output_update_v9=$(aws lambda update-function-configuration --function-name heatIndexFunc \
--timeout 60 --endpoint-url=http://localhost:4566)

echo "Creating all event-source mappings..."
# Mapping to get vapor from dewpointqueue
output_e_1=$(aws lambda create-event-source-mapping --function-name vaporFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $DEWPOINT_ARN \
 --endpoint-url=http://localhost:4566)

 # Mapping to get vibration from vibrationqueue
output_e_2=$(aws lambda create-event-source-mapping --function-name vibrationFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $VIBRATION_ARN \
 --endpoint-url=http://localhost:4566)

# Mapping to get temperature from temperaturequeue
output_e_3=$(aws lambda create-event-source-mapping --function-name temperatureFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $TEMP_ARN \
 --endpoint-url=http://localhost:4566)

# mapping to get heat index from vaporPressure
output_e_4=$(aws lambda create-event-source-mapping --function-name heatIndexFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $VAPOR_ARN \
 --endpoint-url=http://localhost:4566)

# mapping to get door status from doorqueue
output_e_5=$(aws lambda create-event-source-mapping --function-name doorStatusFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $DOOR_ARN \
 --endpoint-url=http://localhost:4566)

# mapping to get sens error status from error queue
output_e_6=$(aws lambda create-event-source-mapping --function-name sensErrorFunc --batch-size 5 \
 --maximum-batching-window-in-seconds 60 --event-source-arn $ERRORS_ARN \
 --endpoint-url=http://localhost:4566)

echo "Creating EventBridge rules to enable door checking and storage checking..."
# EventBridge rules
rule_door=$(aws events put-rule \
--name door-schedule-rule \
--schedule-expression 'rate(5 minutes)' \
--endpoint-url=http://localhost:4566)
rule_door_ARN=$(echo "$rule_door" | jq -r '.RuleArn')

rule_storage=$(aws events put-rule \
--name storage-schedule-rule \
--schedule-expression 'rate(2 minutes)' \
--endpoint-url=http://localhost:4566)
rule_storage_ARN=$(echo "$rule_storage" | jq -r '.RuleArn')

# Add permissions to rule
echo "Adding permissions..."

output_permission_1=$(aws lambda add-permission \
--function-name doorCheckFunc \
--statement-id door-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn $rule_door_ARN \
--endpoint-url=http://localhost:4566)

output_permission_2=$(aws lambda add-permission \
--function-name storageConditionsFunc \
--statement-id storage-schedule-rule \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn $rule_storage_ARN \
--endpoint-url=http://localhost:4566)

# Putting targets
echo "Putting targets..."
output_target_1=$(aws events put-targets --rule door-schedule-rule --targets file://src/door_targets.json --endpoint-url=http://localhost:4566)
output_target_2=$(aws events put-targets --rule storage-schedule-rule --targets file://src/storage_targets.json --endpoint-url=http://localhost:4566)

echo "Subscribing notifyFunc to topic..."
# Making the notifyFunc subscribe to the topic
current_region=$(aws configure get region)
output_subscribe=$(aws sns subscribe --protocol lambda \
--region $current_region \
--topic-arn $TOPIC_ARN \
--notification-endpoint $NOTIFY_ARN \
--endpoint-url=http://localhost:4566)

echo "Cleaning up folders..."
rm -f *.zip