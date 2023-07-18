from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from bcrypt import hashpw, gensalt, checkpw


from dotenv import load_dotenv, find_dotenv
import os
import pprint
load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'rama'  # Change this to your desired secret key
jwt = JWTManager(app)

# password=os.environ.get("MONGODB_PWD")
print(password)
# MongoDB Atlas connection configuration
connectionstr=f"mongodb+srv://flask:Balaji99.@flask.dfs8idt.mongodb.net/"
client = MongoClient(connectionstr)
print(client.list_database_names())
# client = MongoClient('<mongodb-atlas-connection-string>')  # Replace with your MongoDB Atlas connection string

db = client['test']
print(client['test'].list_collection_names())
  # Replace with your database name
collection = db['test']  # Replace with your collection name


@app.route('/',methods=['GET'])
def home():
  return "home"
User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    password = request.json.get('password')

    if not first_name or not last_name or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    if collection.find_one({'email': email}):
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    collection.insert_one({
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': hashed_password
    })

    return jsonify({'message': 'User registered successfully'})

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = collection.find_one({'email': email})

    if not user or not checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({'access_token': access_token})

# Template endpoints
@app.route('/template', methods=['POST'])
@jwt_required()
def create_template():
    template_name = request.json.get('template_name')
    subject = request.json.get('subject')
    body = request.json.get('body')

    if not template_name or not subject or not body:
        return jsonify({'message': 'All fields are required'}), 400

    current_user = get_jwt_identity()

    template_id = collection.insert_one({
        'user_id': ObjectId(current_user),
        'template_name': template_name,
        'subject': subject,
        'body': body
    }).inserted_id

    return jsonify({'message': 'Template created successfully', 'template_id': str(template_id),"ObjId":ObjectId(current_user)})

@app.route('/template', methods=['GET'])
@jwt_required()
def get_all_templates():
    current_user = get_jwt_identity()

    templates = []
    for template in collection.find({'user_id': ObjectId(current_user)}):
        templates.append({
            'template_id': str(template['_id']),
            'template_name': template['template_name'],
            'subject': template['subject'],
            'body': template['body']
        })

    return jsonify(templates)

@app.route('/template/<template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    current_user = get_jwt_identity()

    template = collection.find_one({'_id': ObjectId(template_id), 'user_id': ObjectId(current_user)})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    return jsonify({
        'template_id': str(template['_id']),
        'template_name': template['template_name'],
        'subject': template['subject'],
        'body': template['body']
    })

@app.route('/template/<template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    current_user = get_jwt_identity()

    template = collection.find_one({'_id': ObjectId(template_id), 'user_id': ObjectId(current_user)})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    template_name = request.json.get('template_name')
    subject = request.json.get('subject')
    body = request.json.get('body')

    if not template_name or not subject or not body:
        return jsonify({'message': 'All fields are required'}), 400

    collection.update_one(
        {'_id': ObjectId(template_id)},
        {'$set': {'template_name': template_name, 'subject': subject, 'body': body}}
    )

    return jsonify({'message': 'Template updated successfully'})

@app.route('/template/<template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    current_user = get_jwt_identity()

    template = collection.find_one({'_id': ObjectId(template_id), 'user_id': ObjectId(current_user)})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    collection.delete_one({'_id': ObjectId(template_id)})

    return jsonify({'message': 'Template deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5000",debug=True)
