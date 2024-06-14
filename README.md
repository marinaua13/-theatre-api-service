# theatre-api-service  :relaxed:
____

## Overview and Features
1. I created a project TheatreApiService where we can:
- read and create actor,
- read and create genre,
- read and create actor,
- read and create theatre-hall,
- read, create, update play model,
- create and check reservation,
- Control how many places are left and how many place in a hall,
- load image to play model.

2. You can use admin (http://127.0.0.1:8000/admin)
3. You have possibility to make registration and get you personal JWT token
    3.1 http://127.0.0.1:8000/api/user/register/
    3.2 http://127.0.0.1:8000/api/user/token/

4. I did possibility to load all documentation with swagger, and if you want You can load it to Postman without any problem;)
5. You can use docker, You just need: 
    5.1 unblock Postgres DB in settings
    5.2 load Docker to your PC
    5.3 in terminal write (docker-compose build)
    5.4 After success build - (docker-compose up)

## First Installation of project

You should have already installed Python.
+	git clone 
+	cd theatre_api_service
+	python -m venv venv
+	venv/Scripts/activate
+	pip install -r requirements.txt
+	python manage.py migrate 
+	python manage.py runserver

### Check it out:
    https://github.com/marinaua13/-theatre-api-service

### Additional data:
You can use the following data to get token:
    email: test@gmail.com
    password: test12345

Or you can make new registration 
:relaxed:
