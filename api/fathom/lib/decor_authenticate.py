import functools
from flask import current_app, request

def authenticate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = current_app.logger

        logger.info(f"Request: {func.__name__}")
        
        auth_header = request.headers.get('Authorization')
        id_token = auth_header.split(" ")[1]

        ip_address = request.remote_addr
        logger.debug(f"IP Address:\n{ip_address}-----\n")

        if (id_token is not None):
            decoded_token = current_app.extensions['auth'].verify_id_token(id_token)
            uid = decoded_token['uid']
            db = current_app.extensions["db"]
            users_ref = db.collection('users').where('uid','==', uid)
            results = users_ref.get()
            if (len(list(results)) == 0):
                user = dict()
            else:
                for doc in results:
                    user = doc.to_dict()
        else:
            raise Exception('No authorization sent on request') 

        return func(user, *args, **kwargs)

    return wrapper

