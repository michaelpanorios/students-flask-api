from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if users.find({"username":data['username']}).count() == 0 :
        user =  {
                    "username": data['username'],
                    "password": data['password']

                }
        users.insert_one(user)
        return Response(data['username']+" was added to the MongoDB", status=200, mimetype='application/json')
    else:
        return Response("A user with the given username already exists", status=400, mimetype='application/json')



# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if users.find({"username":data['username']},{"password":data['password']}).count() == 1:
        user_uuid = create_session(data['username'])
        res = {"uuid": user_uuid, "username": data['username']}
        return Response(json.dumps(res), status=200, mimetype='application/json') 
    else:
        return Response("Wrong username or password", status=400, mimetype='application/json')



# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            student = {'name':student["name"],'email':student["email"],'yearOfBirth':student["yearOfBirth"]}
            return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype='application/json')
    else: 
        return Response("Non authenticated user", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
    uuid = request.headers.get('authorization')
    if (is_session_valid(uuid)):
        iterable = students.find({"yearOfBirth":1991})
        students_list = []
        for student in iterable:
            students_list.append(student)

        return Response(json.dumps(students_list), status=200, mimetype='application/json')
    else:
        return Response("Non authenticated user", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_atleast_thirty():
    uuid = request.headers.get('authorization')
    if (is_session_valid(uuid)):
        iterable = students.find({"yearOfBirth":{"$lte": 1991}})
        students_list = []
        for student in iterable:
            students_list.append(student)

        return Response(json.dumps(students_list), status=200, mimetype='application/json')
    else: 
        return Response("Non authenticated user", status=401, mimetype='application/json')



# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_student_address():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if (is_session_valid(uuid)):
        student = students.find_one({"$and":[{"email":data['email']},{"address":{'$exists': True}}]})
        if(student != None):
                student = {'name':student["name"],'street':student['address'][0]['street'],'postcode':student['address'][0]['postcode']}
                return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("There is no student that match with that email", status=400, mimetype='application/json')
    else: 
        return Response("Non authenticated user", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            msg = (student['name']+" was deleted.")
            students.delete_one({"email":data['email']})
            return Response(msg, status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype='application/json')
    else:
        return Response("Non authenticated user", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")


    if (is_session_valid(uuid)):
        if students.find({"email":data['email']}).count() == 1:
            students.update_one({"email":data['email']},{'$set':{"courses":data['courses']}})
            msg = ("Courses were added succesfully to database.")
            return Response(msg, status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype='application/json')
    else:
        return Response("Non authenticated user", status=401, mimetype='application/json')

@app.route('/checkCourses',methods=['GET'])
def get_all_courses():
# Request JSON data
    data = None
    try: 
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None: 
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            student = {'name':student["name"],'courses':student["courses"]}
            return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("Student not found", status=400, mimetype='application/json')
    else: 
        return Response("Non authenticated user", status=401, mimetype='application/json')


# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
        uuid = request.headers.get('authorization')
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if (is_session_valid(uuid)):
        student = students.find_one({"$and":[{"email":data['email']},{"courses":{'$exists': True}}]})
        if (student != None):
            output = {"name":student['name']}
            for course in student['courses']:
                for grade in course.values():
                    if (grade>=5):
                        output.update(course)
            if (output != None):
                return Response(json.dumps(output), status=200, mimetype='application/json')
            else:
                return Response("There are no courses available for this student", status=400, mimetype='application/json')
        else:
            return Response("Student not found")
    else:
        return Response("Non authenticated user", status=401, mimetype='application/json')




# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
