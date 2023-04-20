import boto3

# Create the DynamoDB client
dynamodb = boto3.resource('dynamodb')


def create_item(tweet_id, username, display_name, content, num_likes, tweet_time, created_at):
    item = {
        'tweet_id': tweet_id,
        'username': username,
        'display_name': display_name,
        'content': content,
        'num_likes': num_likes,
        'tweet_time': tweet_time,
        'created_at': created_at
    }
    return item


if __name__ == "__main__":
    # Define the schema for the DynamoDB table
    table = dynamodb.create_table(
        TableName='tweets',
        KeySchema=[
            {
                'AttributeName': 'tweet_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'created_at',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'tweet_id',
                'AttributeType': 'S'  # String attribute
            },
            {
                'AttributeName': 'created_at',
                'AttributeType': 'S'  # String attribute for timestamp
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
