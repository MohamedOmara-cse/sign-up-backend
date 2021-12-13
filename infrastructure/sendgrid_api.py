import logging
from config import Config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Category, Asm

config = Config()


class SendgridApi:
    def __init__(self):
        self.test_emails = [
            'mpmontanez@gmail.com'
        ]
        self.default_test_email = [
            'mpmontanez@gmail.com'
        ]

    def send_reset_email(self, email, token):
        email = self.validate_email(email)

        message = Mail(
            from_email=config.get('email.support_email'),
            to_emails=email)
        message.template_id = ''
        message.category = Category('reset')
        message.dynamic_template_data = {
            'subject': 'Reset your password',
            'title': 'Reset your password',
            'content': 'Click the button below to create a new password.',
            'cta_text': 'Update Password',
            'cta_url': '{}/auth/reset/{}'.format(config.get('web_app_url'), token)
        }
        # message.asm = Asm(1111)
        try:
            sg = SendGridAPIClient(config.get('sendgrid.api_key'))
            response = sg.send(message)
        except Exception as e:
            logging.debug(e)

    def validate_email(self, email):
        # Only send test emails on staging/dev
        if not config.get('app_env') == 'production':
            if email in self.test_emails:
                return email
            else:
                return self.default_test_email

        return email
