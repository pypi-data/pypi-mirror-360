from aenum import IntEnum


'''
@ref https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
'''
class HttpStatus(IntEnum):

    # Successful responses (200 – 299)
    Ok_200 = 200
    Created_201 = 201
    Accepted_202 = 202
    No_Content_204 = 204
    Reset_Content_205 = 205
    Partial_Content_206 = 206

    # Client error responses (400 – 499)
    Bad_Request_400 = 400
    Unauthorized_401 = 401
    Forbidden_403 = 403
    Not_Found_404 = 404
    Method_Not_Allowed_405 = 405
    Not_Acceptable_406 = 406
    Conflict_409 = 409
    Unprocessable_Entity_422 = 422
    Upgrade_Required_426 = 426

    # Server error responses (500 – 599)
    Internal_Server_Error_500 = 500
    Not_Implemented_501 = 501
    Bad_Gateway_502 = 502
    Service_Unavailable_503 = 503
    Insufficient_Storage_507 = 507

    Network_Authentication_Required_511 = 511
