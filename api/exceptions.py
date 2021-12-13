class BadRequest(Exception):
    pass


class InvalidFormat(Exception):
    pass


class InvalidEmail(InvalidFormat):
    pass


class InvalidPassword(InvalidFormat):
    pass


class NotFound(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserNotFound(NotFound):
    pass


class UserNotVerified(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class UnknownWebhookEvent(BadRequest):
    pass
