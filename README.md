# Project on Information Systems 
Created with Python using Flask framework. Handling data with MongoDB as JSON format. 

## Creating a user 
Firstly, I'm trying to find if a user with a given `username` exists. If it doesn't I'm adding an account with a `username` and a `password`:

    if users.find({"username":data['username']}).count() == 0 :
        user =  {
                    "username": data['username'],
                    "password": data['password']

                }
        users.insert_one(user)
If that account was succesfully added to the database I'm printing the following message: 

       return Response(data['username']+" was added to the MongoDB", status=200, mimetype='application/json')

If the `username` already exists I'm printing the following message:

        return Response("A user with the given username already exists", status=400, mimetype='application/json')	




## Login function
After an account has been created I'm trying to login to the system. If the given `username` and `password` are correct then with the help of `create_session` function I'm getting an authentication ID:

    if users.find({"username":data['username']},{"password":data['password']}).count() == 1:
       user_uuid = create_session(data['username'])
       res = {"uuid": user_uuid, "username": data['username']}

If an account is succesfully logged in I'm printing the username and the authentication ID:

    return Response(json.dumps(res), status=200, mimetype='application/json') 

If the `username` or `password` are incorrect I'm printing an error message:

    return Response("Wrong username or password", status=400, mimetype='application/json')

## Returning a student based on email
Checking if the account is authenticated. If it is with the `find_one` method I'm searching for a student with a given email. If student has been found I'm adding his `name`, `email,` and `year of birth` in a variable called `student`.

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            student = {'name':student["name"],'email':student["email"],'yearOfBirth':student["yearOfBirth"]}

Returning his information:

    return Response(json.dumps(student), status=200, mimetype='application/json')
If the system didn't find any student with that email I'm printing the following message:

    return Response("Student not found", status=400, mimetype='application/json')
If the account isn't authenticated I'm printing the following error message: 
        
    return Response("Not authenticated user", status=401, mimetype='application/json')

## Returning all the students who are thirty years old
Firstly, I create a `uuid` variable to save the authentication ID to check if the user is authenticated. If it is I'm creating a empty list which is getting filled with the registries of the students whose `yearOfBirth` is equal to 1991. After that, within a for loop I'm appending all the students who are thirty years old in an empty list called `students_list`. Finally, I'm printing the results:

    uuid = request.headers.get('authorization')
    if (is_session_valid(uuid)):
        iterable = students.find({"yearOfBirth":1991})
        students_list = []
        for student in iterable:
            students_list.append(student)

    return Response(json.dumps(students_list), status=200, mimetype='application/json')
    
If the user isn't authenticated I'm printing the following error message:

    return Response("Non authenticated user", status=401, mimetype='application/json')

## Returning all the students who are at least thirty years old
In that implementation I used the same logic as the previous answer. The only change is that I need to find students who were born before 1991:

    uuid = request.headers.get('authorization')
    if (is_session_valid(uuid)):
        iterable = students.find({"yearOfBirth":{"$lte": 1991}})
        students_list = []
        for student in iterable:
            students_list.append(student)

        return Response(json.dumps(students_list), status=200, mimetype='application/json')
    else: 
        return Response("Non authenticated user", status=401, mimetype='application/json')

## Returning student address based on email
I have to check if the account is authenticated from the system. If it is I'm trying to search with `find_one` method an address with the given email exists in a certain registry that has been found. If variable student got filled with the information I'm printing the details of `name`, `street` and `postcod`e. Argument [0] is about printing the line that `find_one` method has found. Finally, I return a message:

    if (is_session_valid(uuid)):
        student = students.find_one({"$and":[{"email":data['email']},{"address":{'$exists': True}}]})
        if(student != None):
                student = {'name':student["name"],'street':student['address'][0]['street'],'postcode':student['address'][0]['postcode']}
                return Response(json.dumps(student), status=200, mimetype='application/json')
       
If a student with the given email doesn't appear into the database I'm printing the following message:

    return Response("There is no student that matches with given email", status=400, mimetype='application/json')
  
If user isn't authenticated I'm printing the following error message:

    return Response("Not authenticated user", status=401, mimetype='application/json')

## Delete a student based on email
Again I have to check if the account is authenticated from the system. I'm searching a student with his email. If the email exists before deleting his registry from JSON I'm printing that this student is going to be deleted. Finally, I delete the registry with the `delete_one` method parsing the given email as an argument:

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            msg = (student['name']+" was deleted.")
            students.delete_one({"email":data['email']})
            return Response(msg, status=200, mimetype='application/json')
If a student with the given email doesn't appear into the database I'm printing the following message:

    return Response("Student not found", status=400, mimetype='application/json')
If user isn't authenticated I'm printing the following error message:

    return Response("Not authenticated user", status=401, mimetype='application/json')

## Insert courses to a student registry based on email
I have to check if the account is authenticated from the system. If it is I'm using the `update_one` method in order to insert the courses to a certain line. Update method requires a `key --> 'email'` and a `value --> 'courses'`. In the tag courses I'm adding from `Postman` a dictionairy filled with the example that was given to us:

    if (is_session_valid(uuid)):
        if students.find({"email":data['email']}).count() == 1:
            students.update_one({"email":data['email']},{'$set':{"courses":data['courses']}})
            msg = ("Courses were added to database.")
            return Response(msg, status=200, mimetype='application/json')
       
If a student with the given email doesn't appear into the database I'm printing the following message:

    return Response("Student not found", status=400, mimetype='application/json')
If user isn't authenticated I'm printing the following error message:

    return Response("Not authenticated user", status=401, mimetype='application/json')

## Returning passed subjects of a student based on email
Again I have to check if the account is authenticated from the system. If he is authenticated I'm searching for a certain `student` based on `email` and valid `courses` available. If `email` and `courses` were found I have two nested for loops. Outter one is to parse all the courses. Inner one is for the grade comparison. If the grade of one course is greater or equal than 5 I'm adding that course next to his name. Finally, after the check is completed I'm printing the results. 

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
            
If courses haven't been added yet:

     return Response("There are no courses available for this student", status=400, mimetype='application/json')
 
If student hasn't been found with the given email:

     return Response("Student not found")

If user isn't authenticated I'm printing the following error message:

     return Response("Non authenticated user", status=401, mimetype='application/json')

## Getting all the courses based on email (extra)

This function was created to check if courses were added succesfully after inserting them with the `insert_courses` function:

    if (is_session_valid(uuid)):
        student = students.find_one({"email":data['email']})
        if(student != None):
            student = {'name':student["name"],'courses':student["courses"]}
            return Response(json.dumps(student), status=200, mimetype='application/json')

## Finally
 Getting the authentication ID line is being added to every `try & except` exactly after json data loading:
          
    uuid = request.headers.get('authorization')

All the functions created have been tested with `Postman`.
