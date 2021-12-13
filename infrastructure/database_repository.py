from datetime import datetime, date, timedelta
from config import Config
from infrastructure.database_models import Signals, Stocks, Users
from sqlalchemy import desc, func
from urllib.parse import quote


class DatabaseRepository:
    """
    Provides an interfaces for database querying.
    """

    @staticmethod
    def connection_string():
        config = Config()
        database_host = config.get('database.host')
        database_name = config.get('database.name')
        database_user = config.get('database.user')
        database_password = config.get('database.password')
        database_port = config.get('database.port')

        return 'mysql+pymysql://' + database_user + ':%s@' % quote(database_password) + database_host + ':' + \
            str(database_port) + '/' + database_name

    def __init__(self, db):
        self._db = db

    def get_user_by_email(self, email):
        return Users.query.filter_by(email=email).first()

    def get_user_by_token(self, token):
        return Users.query.filter_by(verification_token=token).first()

    def get_user_by_reset_token(self, token):
        return Users.query.filter_by(reset_token=token).first()

    def create_user(self, email, hashed_password):
        user = Users()
        user.email = email
        user.hashed_password = hashed_password

        self._db.session.add(user)
        self._db.session.commit()

        return user

    def set_verification_token_for_user(self, user_id, token, exp):
        user = Users.query.get(user_id)
        user.verification_token = str(token)
        user.verification_token_expiration = exp.isoformat()
        self._db.session.commit()

    def verify_user(self, user_id):
        user = Users.query.get(user_id)
        user.verified_at = datetime.now().isoformat()
        self._db.session.commit()

    def set_reset_token_for_user(self, user_id, token, exp):
        user = Users.query.get(user_id)
        user.reset_token = str(token)
        user.reset_token_expiration = exp.isoformat()
        self._db.session.commit()

    def update_password(self, user_id, hashed_password):
        user = Users.query.get(user_id)
        user.hashed_password = hashed_password
        user.reset_token = None
        user.reset_token_expiration = None
        self._db.session.commit()

    def get_signals(self, window_mins, tickers):

        most_recent_created_at = Signals.query.with_entities(Signals.created_at).filter_by(window_mins=window_mins).order_by(Signals.created_at.desc()).limit(1).first().created_at
        query = Signals.query.filter_by(window_mins=window_mins)

        # most_recent_created_at_beginning = datetime.datetime.combine(most_recent_created_at, datetime.datetime.min.time())

        # Filter by tickers if any exist
        if tickers and len(tickers):
            query = query.filter(Signals.symbol.in_(tickers))

        # query = query.filter(Signals.created_at >= most_recent_created_at_beginning)
        query = query.filter(func.date(Signals.created_at) == most_recent_created_at.date())
        # print(Signals.created_at)
        # print(most_recent_created_at)

        return query.order_by(Signals.created_at.desc()).limit(750).all()

    def get_stocks(self):
        return Stocks.query.all()

    def get_top_gainers(self, window_mins, limit=25):

        most_recent_created_at = Signals.query.with_entities(Signals.created_at).filter_by(window_mins=window_mins).order_by(Signals.created_at.desc()).limit(1).first().created_at
        query = Signals.query.filter_by(window_mins=window_mins)
        query = query.filter(func.date(Signals.created_at) == most_recent_created_at.date())

        return query.order_by(Signals.strength.desc()).limit(25).all()

    def get_top_losers(self, window_mins, limit=25):

        most_recent_created_at = Signals.query.with_entities(Signals.created_at).filter_by(window_mins=window_mins).order_by(Signals.created_at.desc()).limit(1).first().created_at
        query = Signals.query.filter_by(window_mins=window_mins)
        query = query.filter(func.date(Signals.created_at) == most_recent_created_at.date())

        return query.order_by(Signals.strength.asc()).limit(25).all()
