class BusinessLogicError(Exception):
    pass


class EntityNotFoundError(BusinessLogicError):
    pass


class SecurityError(Exception):
    pass
