from werkzeug.exceptions import HTTPException

class InternalServerError(HTTPException):
    pass

class SchemaValidationError(HTTPException):
    pass

class EmailAlreadyExistsError(HTTPException):
    pass

class UnauthorizedError(HTTPException):
    pass

class NoJsonError(HTTPException):
    pass

class ResourceDoesNotExist(HTTPException):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
     "SchemaValidationError": {
         "message": "Request does not fulfill the expected schema",
         "status": 400
     },
     "EmailAlreadyExistsError": {
         "message": "User with given email address already exists",
         "status": 400
     },
     "UnauthorizedError": {
         "message": "Invalid username or password",
         "status": 401
     },
     "NoJsonError": {
         "message": "Request body must be JSON",
         "status": 400
     },
     "ResourceDoesNotExist": {
         "message": "The requested resource does not exist",
         "status": 404
     }
}