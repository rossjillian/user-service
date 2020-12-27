import getcredentials as gc
import os

vars = gc.get_cred()
keyid = vars[0]
key = vars[1]

print("co", keyid, key)

__context = {
    "AWSInfo": {
        "aws_access_key_id": keyid,
        "aws_secret_access_key": key,
        "region_name": "us-east-2"
    }
}


def get_ctx_element(e_name):
    return __context.get(e_name, None)

