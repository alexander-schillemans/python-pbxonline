def request_not_succesful(status_code: int) -> bool:
    """ Returns True if the given status code is not in the 200 range. """
    
    return status_code < 200 or status_code > 299