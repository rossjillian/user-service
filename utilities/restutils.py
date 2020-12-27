import jwt
import os
import hashlib
from datetime import datetime


def generate_jwt(body, secret_key, admin_user):
    address = body["address"]
    address_split = address.split(",")
    body["address_1"] = address_split[0]
    if len(address_split) == 3:
        body["address_2"] = address_split[1]
    else:
        city_state = address_split[1].split(" ")  # separating City and State
        body["city"] = city_state[0]
        body["state"] = city_state[1]
    del body["address"]
    salt = os.urandom(32)  # Remember this
    password = body["password"]
    key = hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        password.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )
    body["salt"] = salt.hex()
    body["hash_key"] = key.hex()
    body['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if admin_user:
        if body['email'].lower() != admin_user:
            body['role'] = 'user'
        else:
            body['role'] = 'admin'
    else:
        body['role'] = 'user'
    del body["password"]
    encoded_jwt = jwt.encode({'first_name': body['first_name'], 'last_name': body['last_name'],
                              'email': body['email'], 'role': body['role'],
                              'created_date': body['created_date']}, secret_key, algorithm='HS256')
    return encoded_jwt


def pagination_support(query_param):
    offset = None
    limit = None
    if 'offset' in query_param:
        offset = query_param['offset']
    if 'limit' in query_param:
        limit = query_param['limit']
    return offset, limit


def paginated_rsp(table, info, rsp_data, offset, limit):
    rsp = {}
    offset = int(offset)
    limit = int(limit)
    count = table.get_count()
    rsp['data'] = rsp_data
    rsp['pagination'] = {'offset': offset, 'limit': limit, 'total': count}
    next_link = info['headers']['Host'] + info['path'] + '?offset=%d&limit=%d' % (offset + limit, limit)
    prev_link = info['headers']['Host'] + info['path'] + '?offset=%d&limit=%d' % (offset - limit, limit)
    rsp['links'] = {'next': next_link, 'prev': prev_link}
    return rsp
