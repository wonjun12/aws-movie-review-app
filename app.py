from flask import Flask
from flask_restful import Api

from resources.user import UserRegistorResource, UserLoginResource, UserLogoutResource, UserAboutResource, jwt_blocklist
from resources.movie import MovieAllViewResource, MovieViewResource, MovieSearchResource
from resources.review import ReviewResource


app = Flask(__name__)

from flask_jwt_extended import JWTManager
from config import Setting
app.config.from_object(Setting)
jwt = JWTManager(app)

# 로그아웃 모음
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

# 유저
api.add_resource( UserRegistorResource , '/user/registor')
api.add_resource( UserLoginResource , '/user/login')
api.add_resource( UserLogoutResource, '/user/logout')
api.add_resource( UserAboutResource , '/user/mypage')
# 영화
api.add_resource(MovieAllViewResource, '/movie')
api.add_resource( MovieViewResource, '/movie/<int:movie_id>')
# 영화 조회
api.add_resource( MovieSearchResource, '/movie/search')
# 영화 리뷰 작성, 조회
api.add_resource( ReviewResource , '/movie/<int:movie_id>/review')

if __name__ == '__main__':
    app.run()