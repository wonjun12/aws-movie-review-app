from flask_restful import Resource
from flask import request

from mysql_connection import movie_mysql_connection
from mysql.connector import Error

from flask_jwt_extended import jwt_required

def decimal_format(data):
    for i in range(len(data)):
        data[i]['rating'] = float(data[i]['rating'])
    return data

def date_format(data):
    for i in range(len(data)):
        try:
            data[i]['createdAt'] = data[i]['createdAt'].isoformat()
            data[i]['updatedAt'] = data[i]['updatedAt'].isoformat()
            data[i]['year'] = data[i]['year'].isoformat()
        except:
            pass
    return data

class MovieSearchResource(Resource):
    def get(self):

        title = request.args.get('movie_title')
        
        try:
            connection = movie_mysql_connection()

            query = f'''
                select m.id, m.title, count(r.id) as counting, round(avg(r.rating), 1) as rating
                from movie m
                    left join rating r
                    on m.id = r.movieId
                where title like '%{title}%'
                group by m.id;
            '''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }
        
        return {
            'result' : 'success',
            'items' : decimal_format(result_list)
        }

class MovieViewResource(Resource):
    def get(self, movie_id):

        try:
            connection = movie_mysql_connection()

            query = '''
                select m.*, count(r.id) as counting, round(avg(r.rating), 1) as rating
                from movie m
                    left join rating r
                    on m.id = r.movieId
                group by m.id having m.id = %s;
            '''
            record = (movie_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }
        
        result = decimal_format(result)
        result = date_format(result)

        return {
            'result' : 'success',
            'item' : result[0]
        }

class MovieAllViewResource(Resource):
    def get(self):
        # {
        #   offset : 5
        #   order : 'counting' , 'rating' 
        # }
        param = request.args
        offset = param.get('offset')
        order = param.get('order')

        try:
            connection = movie_mysql_connection()

            query = f'''
                select m.id, m.title, count(r.id) as counting, round(avg(r.rating), 1) as rating
                from movie m
                    left join rating r
                    on m.id = r.movieId
                group by m.id
                order by {order} desc
                limit {offset * 25}, 25;
            '''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error ': str(e)
            }
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : decimal_format(result_list)
        }