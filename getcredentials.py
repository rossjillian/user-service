import os
import setcredentials as sc


def get_cred():
    sc.set_cred()
    environment_variables = []
    keyid = os.environ.get('AWSKEYID')
    pw = os.environ.get('AWSACCESSKEY')
    smartystreets_AuthID = os.environ.get('smartystreets_AuthID')
    smartyStreets_AuthToken = os.environ.get('smartyStreets_AuthToken')
    secret_key = os.environ.get('JWT_SECRET_KEY')

    environment_variables.append(keyid)
    environment_variables.append(pw)
    environment_variables.append(smartystreets_AuthID)
    environment_variables.append(smartyStreets_AuthToken)
    environment_variables.append(secret_key)

    return environment_variables

