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
def analyze(bucket='yakov-my-upload-bucket-01', image='cocktails.jpg'):
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



@application.route('/get_objects' , methods=['GET'])
def get1():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('items')
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), minetype='application/json', status=200)
    
# curl -i http://"localhost:8000/get_object?objectId=1"
@application.route('/get_object', methods=['GET'])
def get_obj():
    objectId = request.args.get('objectId')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('items')
    resp = table.get_item(
    Key={
        'item_id': objectId,
    }
    ) 
    print(str(resp))
    return Response(json.dumps(resp['Item']), mimetype='application/json', status=200) 
    
# curl -i http://"localhost:8000/set_object?objectId=11-08-2021-18-50-27.jpg&name=amichai&constanse=96"
@application.route('/set_object', methods=['GET', 'POST'])
def set_obj():
    objectId = request.args.get('objectId')
    name = request.args.get('name')
    constanse = request.args.get('constanse')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('items')
    item={
        'item_id': objectId,
        'name':name,
        'constanse':constanse,
        
    }
     
    table.put_item(Item=item)
    return Response(json.dumps(item), mimetype='application/json', status=200)
    
@application.route('/set_object/<obj_id>', methods=['POST'])
def get_temp(obj_id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('object')
    data = request.data
    data_dict = json.loads(data)
    object_name = data_dict.get('object_name', 'default')
    object_confidance = data_dict.get('object_confidance', 'default')
    
    item={
        'object_id' : obj_id,
        'object_name' : object_name,
        'object_confidance' : object_confidance
    }
    table.put_item(Item=item)
    
    
if __name__ == '__main__':
    flaskrun(application)
    
    
    
    