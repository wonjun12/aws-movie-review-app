from flask_restful import Resource
from flask import request

from mysql_connection import movie_mysql_connection
from mysql.connector import Error

from resources.movie import date_format

from flask_jwt_extended import jwt_required, get_jwt_identity

class ReviewResource(Resource):

    @ jwt_required()
    def post(self, movie_id):
        data = request.get_json()
        user_id = get_jwt_identity()

        try:
            connection = movie_mysql_connection()

            query = '''
                insert into rating
                (userId, movieId, rating)
                values
                (%s, %s, %s);
            '''
            record = (user_id, movie_id, data['rating'])

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error ': str(e)
            }, 500

        return {
            'result' : 'success'
        }
    


    def get(self, movie_id):
        
        param = request.args
        offset = param.get('offset')
        
        try:
            connection = movie_mysql_connection()

            query = f'''
                select r.rating, r.createdAt, r.updatedAt , u.name, u.gender
                from rating r
                    join user u 
                    on r.userId = u.id
                where r.movieId = %s
                limit {offset * 25}, 25;
            '''
            record = (movie_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500
        
        return {
            'result' : 'success',
            'items' : date_format(result_list)
        }