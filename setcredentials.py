import os


def set_cred():
    # Set environment variables
    os.environ['AWSKEYID'] = None
    os.environ['AWSACCESSKEY'] = None
    os.environ['DB_USER'] = "admin"
    os.environ['DB_PW'] = None
    os.environ['DB_HOST'] = None
    os.environ['smartystreets_AuthID'] = None
    os.environ['smartyStreets_AuthToken'] = None
    os.environ['JWT_SECRET_KEY'] = None

