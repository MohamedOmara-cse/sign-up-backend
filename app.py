import logging
import os
from api.exceptions import BadRequest, InvalidFormat, NotFound, UserAlreadyExists, UserNotVerified, InvalidCredentials
from api.responses import Responses as ApiResponses
from config import Config
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity)
from flask_sqlalchemy import SQLAlchemy
from infrastructure.database_models import Base
from infrastructure.database_repository import DatabaseRepository
from infrastructure.sendgrid_api import SendgridApi
from services.auth import Auth as AuthService

application = Flask(__name__)
CORS(application)
application.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret')
application.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
application.config['SQLALCHEMY_DATABASE_URI'] = DatabaseRepository.connection_string()
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

config = Config()
db = SQLAlchemy(application, model_class=Base)
database_repo = DatabaseRepository(db)
jwt = JWTManager(application)
sendgrid_api = SendgridApi()


@application.route('/')
def hello_world():
    return 'StormIQ!'


@application.route('/auth/register', methods=['POST'])
def register():
    request_data = request.get_json()

    try:
        auth_service = AuthService(database_repo, sendgrid_api)
        access_token, user = auth_service.register(request_data)
    except InvalidFormat as e:
        return (ApiResponses.build_error_response([str(e)]), 400)
    except UserAlreadyExists as e:
        return (ApiResponses.build_error_response([str(e)]), 409)

    return (ApiResponses.build_data_response(ApiResponses.profile_response(user, include_email=True), {'access_token': access_token}), 201)


@application.route('/auth/login', methods=['POST'])
def login():
    request_data = request.get_json()
    auth_service = AuthService(database_repo, sendgrid_api)

    try:
        access_token, user = auth_service.login(request_data)
    except NotFound as e:
        return (ApiResponses.build_error_response([str(e)]), 404)
    except InvalidCredentials as e:
        return (ApiResponses.build_error_response([str(e)]), 401)
    except UserNotVerified as e:
        return (ApiResponses.build_error_response([str(e)]), 401)

    return (ApiResponses.build_data_response(ApiResponses.profile_response(user, include_email=True), {'access_token': access_token}), 200)


@application.route('/auth/verify', methods=['POST'])
def verify():
    request_data = request.get_json()
    auth_service = AuthService(database_repo, sendgrid_api)

    try:
        access_token, user = auth_service.verify(request_data)
    except BadRequest as e:
        return (ApiResponses.build_error_response([str(e)]), 400)

    return (ApiResponses.build_data_response(ApiResponses.profile_response(user, include_email=True), {'access_token': access_token}), 200)


@application.route('/auth/reset-password', methods=['POST'])
@jwt_required(optional=True)
def reset_password():
    request_data = request.get_json()

    email = request_data.get('email')
    token = request_data.get('token')
    new_password = request_data.get('password')

    auth_service = AuthService(database_repo, sendgrid_api)

    try:
        if token and new_password:
            access_token, user = auth_service.reset_password(
                token, new_password)
            return (ApiResponses.build_data_response(ApiResponses.profile_response(user, include_email=True), {'access_token': access_token}), 200)
        elif email:
            auth_service.init_password_reset(email)
        else:
            return (ApiResponses.build_error_response(['Missing required data.']), 400)
    except NotFound as e:
        return (ApiResponses.build_error_response([str(e)]), 404)
    except BadRequest as e:
        return (ApiResponses.build_error_response([str(e)]), 400)

    return ({}, 200)


@application.route('/auth/update-password', methods=['POST'])
@jwt_required()
def update_password():
    return ({}, 200)


@application.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    auth_service = AuthService(database_repo, sendgrid_api)
    user = auth_service.current_user()
    return (ApiResponses.build_data_response(ApiResponses.profile_response(user, include_email=True)), 200)


@application.route('/admin/users', methods=['GET', 'POST'])
@jwt_required()
def admin_users():
    return ({}, 200)


@application.route('/admin/users/<string:user_id>', methods=['DELETE'])
@jwt_required()
def admin_update_user(user_id):
    return ({}, 200)


@application.route('/stocks/tickers', methods=['GET'])
@jwt_required()
def stock_tickers():
    stocks = database_repo.get_stocks()
    return (ApiResponses.build_data_response(ApiResponses.stock_responses(stocks)), 200)


@application.route('/stocks/signals', methods=['GET'])
@jwt_required()
def stock_signals():
    window_mins = request.args.get('window_mins', 5)
    tickers = request.args.get('tickers', '').split(
        ',') if request.args.get('tickers') else None
    signals = database_repo.get_signals(window_mins, tickers)
    return (ApiResponses.build_data_response(ApiResponses.signal_responses(signals)), 200)


@application.route('/stocks/top-gainers', methods=['GET'])
@jwt_required()
def stock_top_gainers():
    window_mins = request.args.get('window_mins', 5)
    # tickers = request.args.get('tickers', '').split(
    #     ',') if request.args.get('tickers') else None
    limit = request.args.get('limit', 25)
    signals = database_repo.get_top_gainers(window_mins, limit=limit)

    # Remove duplicate symbols
    symbols = []
    filtered_signals = []
    for signal in signals:
        if signal.symbol in symbols:
            continue

        symbols.append(signal.symbol)
        filtered_signals.append(signal)

    return (ApiResponses.build_data_response(ApiResponses.signal_responses(filtered_signals)), 200)


@application.route('/stocks/top-losers', methods=['GET'])
@jwt_required()
def stock_top_losers():
    window_mins = request.args.get('window_mins', 5)
    # tickers = request.args.get('tickers', '').split(
    #     ',') if request.args.get('tickers') else None
    limit = request.args.get('limit', 25)
    signals = database_repo.get_top_losers(window_mins, limit=limit)

    # Remove duplicate symbols
    symbols = []
    filtered_signals = []
    for signal in signals:
        if signal.symbol in symbols:
            continue

        symbols.append(signal.symbol)
        filtered_signals.append(signal)

    return (ApiResponses.build_data_response(ApiResponses.signal_responses(filtered_signals)), 200)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    application.run(debug=True, host='0.0.0.0', port=5000)
