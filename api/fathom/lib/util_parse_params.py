# Helper function to get parameter from request
from distutils.util import strtobool

def parse_params(request, arguments):
    request_json = request.get_json(silent=True)
    request_args = request.args

    params = dict()
    for arg in arguments:
        if request_json and arg in request_json:
            # convert string to boolean
            try:
                value = bool(strtobool(request_json[arg]))

            except ValueError:
                value = request_json[arg]

            params[arg] = value
        elif request_args and arg in request_args:
            # convert string to boolean
            try:
                value = request_args[arg]
                value = bool(strtobool(value))
                
            except ValueError:
                value = request_args[arg]

            params[arg] = value
        else:
            # don't add param if not present
            pass
    
    return params