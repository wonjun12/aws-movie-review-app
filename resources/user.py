from flask_restful import Resource
from flask import request


from mysql_connection import movie_mysql_connection
from mysql.connector import Error

from email_validator import validate_email, EmailNotValidError
from utils import check_password, password_hash_change

from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity

from resources.movie import date_format

jwt_blocklist = set()
class UserLogoutResource(Resource):
    @jwt_required()
    def delete(self):
        jwt_blocklist.add(get_jwt()['jti'])

        return {
            'result' : 'success'
        }

class UserAboutResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        try:
            connection = movie_mysql_connection()

            query = '''
                select id, email, name, gender, createdAt, updatedAt
                from user 
                where id = %s;
            '''
            record = (user_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_user = cursor.fetchall()

            query = '''
                select r.id as review_id, r.rating, r.createdAt, r.updatedAt, m.id as movie_id, m.title
                from rating r
                    join movie m
                    on r.movieId = m.id
                where r.userId = %s;
            '''
            record = (user_id, )

            cursor.execute(query, record)
            result_reviews = cursor.fetchall()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500

        return {
            'result' : 'success',
            'items' : {
                'user' : date_format(result_user)[0],
                'reviews' : date_format(result_reviews)
            }
        }

class UserLoginResource(Resource):
    
    def post(self):
        # {"email" : "againor0@instagram.com", 
        # "password" : "oXWdDAFWWqVm"}
        data = request.get_json()
        
        try:
            connection = movie_mysql_connection()

            query = '''
                select *
                from user
                where email = %s;
            '''
            record = (data['email'], )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchall()

            if len(result) == 0:
                return {
                    'result' : 'fail',
                    'error' : '회원이 없음'
                }, 400
            
            if not check_password(data['password'], result[0]['password']):
                return {
                    'result' : 'fail',
                    'error' : 'password failed'
                }, 400

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500

        access_token = create_access_token(result[0]['id'])
        return {
            'result' : 'success',
            'access_token' : access_token
        }

class UserRegistorResource(Resource):
    def post(self):
        # {"email" : "againor0@instagram.com", 
        # "password" : "oXWdDAFWWqVm", 
        # "name" : "Aurthur Gainor", 
        # "gender" : "Male"}

        data = request.get_json()

        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 400

        hashed_password = password_hash_change(data['password'])
       
        try:
            connection = movie_mysql_connection()

            query = '''
                select *
                from user
                where email = %s;
            '''
            record = (data['email'], )

            cursor = connection.cursor()
            cursor.execute(query, record)
            result = cursor.fetchall()

            if len(result) != 0:
                return {
                    'result' : 'fail',
                    'error' : '이미 회원이 있음'
                }, 400
            
            query = '''
                insert into user
                (email, password, name, gender)
                values
                (%s, %s ,%s, %s)
            '''
            record = (data['email'], hashed_password, data['name'], data['gender'])

            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return {
            'result' : 'success'
        }