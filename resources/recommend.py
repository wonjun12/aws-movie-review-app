from flask_restful import Resource
from flask import request

from mysql_connection import movie_mysql_connection
from mysql.connector import Error

from resources.movie import date_format

from flask_jwt_extended import jwt_required, get_jwt_identity

import pandas as pd

class MovieRecommendResource(Resource):
    @jwt_required()
    def get(self):
        
        user_id = get_jwt_identity()

            # 불러올때 기존에 분석할때와 다르게 불러와진다.
            # index가 title이아닌 숫자로 되어 있다.
        corr_movie = pd.read_csv('data/corr_movie.csv', index_col=0)

        # 유저가 준 별점 정보 필요
        try:
            connection = movie_mysql_connection()

            query = '''
                select m.title, r.rating
                from rating r
                    join movie m
                    on r.movieId = m.id
                where r.userId = %s;
            '''
            record = (user_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            # 영화 id, title 값 가져오기
            query = '''
                select id, title
                from movie;
            '''
            cursor.execute(query)
            movie_list = cursor.fetchall()

            cursor.close()
            connection.close()
        except Error as e:
            return {
                'result' : 'fail',
                'error' : str(e)
            }, 500


        # 상관계숙가 있는 데이터프레임에서, 유저가 본 영화만 가져와서 가중치 계산
        # 정렬 후, 클라이언트에게 보내준다.
        # 코렙에서 분석하고, 변경한 코드들 그대로 적용
        user_df = pd.DataFrame(result_list)


        similar_movies_list = pd.DataFrame()
        for i in range( user_df.shape[0] ) :
            movie_title = user_df['title'][i]
            recom_movies = corr_movie[movie_title].dropna().sort_values(ascending=False).to_frame()
            recom_movies.columns = ['correlation']
            recom_movies['weight'] = recom_movies['correlation'] * user_df['rating'][i]
            similar_movies_list = pd.concat(  [similar_movies_list, recom_movies] )
        # 정렬
        similar_movies_list.sort_values('weight', ascending = False, inplace=True)

        # 유저가 본 영화 제거
        for name in user_df['title'] :
            if name in similar_movies_list.index :
                similar_movies_list.drop(name, axis = 0, inplace=True)

        # 중복 제거하면서 중복된 값 중 큰값을 들고온다.
        recom_df = similar_movies_list.groupby('title')['weight'].max().sort_values(ascending=False).head(10).reset_index()
        # movie_id 붙이기
        movie_df = pd.DataFrame(movie_list)
        recom_df = pd.merge( recom_df , movie_df, on = 'title')

        # 데이터 프레임 => dict 형태로 변환
        # 옵션을 넣어야 제대로 나옴
        result_list = recom_df.to_dict(orient='records')
        
        return {
            'result' : 'success',
            'count' : len(result_list),
            'items' : result_list
        }