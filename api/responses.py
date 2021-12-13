from datetime import datetime


class Responses:
    @staticmethod
    def build_data_response(data, meta={}):
        return {
            'data': data,
            'meta': meta
        }

    @staticmethod
    def build_error_response(errors):
        return {
            'errors': errors
        }

    @staticmethod
    def profile_response(user, include_email=False):
        return {
            'id': user.id,
            'type': 'profile',
            'attributes': {
                'email': user.email if include_email else None,
                'created_at': user.created_at.isoformat()
            }
        }

    @staticmethod
    def signal_responses(signals):
        response = []

        for signal in signals:
            response.append(Responses.signal_response(signal))

        return response

    @staticmethod
    def signal_response(signal):
        return {
            'id': signal.id,
            'type': 'signal',
            'attributes': {
                'ticker': signal.symbol,
                'change': signal.total_change,
                'close': signal.close,
                'created_at': signal.created_at.isoformat(),
                'pattern': signal.pattern,
                'pattern_type': signal.pattern_type,
                'sentiment': signal.sentiment,
                'strength': signal.strength,
                'window_mins': signal.window_mins,
                'avg_3d_perf': signal.avg_3d_perf
            }
        }

    @staticmethod
    def stock_responses(stocks):
        response = []

        for stock in stocks:
            response.append(Responses.stock_response(stock))

        return response

    @staticmethod
    def stock_response(stock):
        return {
            'id': stock.id,
            'type': 'stock',
            'attributes': {
                'ticker': stock.symbol,
                'name': stock.name
            }
        }
