import json
import time
from flask import Flask, request, jsonify, redirect
from kafka import KafkaProducer
from kafka.errors import KafkaError
from pymemcache.client import base as memcache
import boto3
from botocore.exceptions import ClientError
import hashlib
import logging
import redis
from multiprocessing import Pool

app = Flask(__name__)
kafka_bootstrap_servers = 'localhost:9092'
dynamodb_table_name = 'url_mapping'
memcache_host = 'localhost'
memcache_port = 11211
redis_host = 'localhost'
redis_port = 6379
redis_ttl = 7 * 24 * 60 * 60  # 7 days in seconds

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
memcache_client = memcache.Client((memcache_host, memcache_port))
dynamodb_client = boto3.client('dynamodb')
redis_client = redis.Redis(host=redis_host, port=redis_port)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def write_batch_to_dynamodb(batch_items):
    with dynamodb_client.batch_write_item(
            RequestItems={
                dynamodb_table_name: batch_items
            }
    ):
        pass

def fetch_long_urls(short_ids):
    response = dynamodb_client.batch_get_item(
        RequestItems={
            dynamodb_table_name: {
                'Keys': [{'id': {'S': short_id}} for short_id in short_ids],
                'ProjectionExpression': 'id, long_url'
            }
        }
    )
    return {item['id']['S']: item['long_url']['S'] for item in response['Responses'][dynamodb_table_name]}

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.json.get('long_url')

    try:
        unique_id = str(uuid.uuid4().int)[:6]  # Generate a UUID and take the first 6 characters
        short_url = generate_short_url(long_url)

        # Check if the long URL is in cache
        cached_long_url = redis_client.get(short_url)
        if cached_long_url:
            long_url = cached_long_url.decode('utf-8')
        else:
            kafka_message = {
                'id': unique_id,
                'short_url': short_url,
                'long_url': long_url
            }
            send_kafka_message(kafka_message)

            # Store data in Memcache
            memcache_client.set(short_url, long_url, time=redis_ttl)

            # Cache the long URL
            redis_client.set(short_url, long_url, ex=redis_ttl)

        return jsonify({'short_url': short_url}), 201
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode('utf-8'))  # Generate SHA-256 hash
    hex_digest = hash_object.hexdigest()  # Get hexadecimal digest
    short_url = hex_digest[:6]  # Take the first 6 characters from the digest
    return short_url

def send_kafka_message(message):
    retry_count = 0
    while retry_count < 3:
        try:
            producer.send('url_topic', json.dumps(message).encode('utf-8'))
            producer.flush()
            return
        except KafkaError:
            retry_count += 1
            time.sleep(1)

    raise Exception('Failed to send Kafka message')

@app.route('/<short_id>')
def redirect_url(short_id):
    # Check if the long URL is in cache
    long_url = redis_client.get(short_id)

    if not long_url:
        try:
            # Fetch the long URLs in parallel
            with Pool() as pool:
                long_urls = pool.map(fetch_long_urls, [short_id])[0]

            long_url = long_urls.get(short_id)

            if long_url:
                # Increment the redirection count in DynamoDB
                dynamodb_client.update_item(
                    TableName=dynamodb_table_name,
                    Key={'id': {'S': short_id}},
                    UpdateExpression='SET redirection_count = redirection_count + :val',
                    ExpressionAttributeValues={':val': {'N': '1'}}
                )

                # Cache the long URL
                redis_client.set(short_id, long_url, ex=redis_ttl)
        except ClientError as e:
            logger.error(f"DynamoDB error occurred: {str(e)}")
            return jsonify({'error': str(e)}), 500

    if long_url:
        return redirect(long_url, code=301)  # Permanent redirect (301)
    else:
        return jsonify({'error': 'URL not found.'}), 404

if __name__ == '__main__':
    app.run()
