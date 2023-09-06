from flask import  request
from utils.ldap_util import LdapUtils
from flask_restful import Api, Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)

class LoginResource(Resource):
    def post(self):
        # Get the username and password from the request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Find the user by username
        user = LdapUtils().authenticate_user(username, password)
        print(user)

        if user :
            # Generate the access token and refresh token
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            # Return the tokens in the response
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        # Return an error response if authentication fails
        return {'message': 'Invalid username or password'}, 401
