import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
from flask_cors import CORS
import boto3
from datetime import datetime

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='yakov-my-upload-bucket-01', image='person.jpg'):
    return detect_labels(bucket, image)
    
def detect_labels(bucket, key, max_labels=3, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')
    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image
    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])
    
@application.route('/upload_image', methods=['POST'])
def uploadImage():
    mybucket = 'yakov-my-upload-bucket-01'
    filobject = request.files['file']
    s3 = boto3.resource('s3', region_name='us-east-1')
    date_time = datetime.now()
    dt_string = date_time.strftime("%d-%m-%Y-%H-%M-%S")
    filename = "%s.jpg" % dt_string
    s3.Bucket(mybucket).upload_fileobj(filobject, filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
    return {"imgName": filename}
if __name__ == '__main__':
    flaskrun(application)
