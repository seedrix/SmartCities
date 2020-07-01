from werkzeug.exceptions import HTTPException

class InternalServerError(HTTPException):
    code = 500
    description = "Something went wrong"

class SchemaValidationError(HTTPException):
    code = 400
    desciption = "Request does not fulfill the expected schema"

class EmailAlreadyExistsError(HTTPException):
    code = 400
    description = "User with given email address already exists"

class UnauthorizedError(HTTPException):
    code = 401
    description = "User with given email address already exists"

class NoJsonError(HTTPException):
    code = 400
    description =  "Request body must be JSON"

class ResourceDoesNotExist(HTTPException):
    code = 404
    description = "The requested resource does not exist"

errors = {}