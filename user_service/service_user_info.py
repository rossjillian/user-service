from base_service.service import BaseService
import jwt
import hashlib
from datetime import datetime
import getcredentials as gc
from utilities.restutils import generate_jwt


vars = gc.get_cred()
SECRET_KEY = vars[4]


class UserServiceInfo(BaseService):
    """
    Inherits parent class BaseService.
    Relies on DB instance called Users.
    """
    __table_name_users = "Users"

    def __init__(self, comment_service_link=None, admin_user=None):
        """
        :param comment_service_link: link to compute running CommentService, if applicable, for implementing HATEAOS
        :param admin_user: email of service administrator
        """
        super(UserServiceInfo, self).__init__(UserServiceInfo.__table_name_users, key_columns="id")
        self.comment_service_link = comment_service_link
        self.admin_user = admin_user

    def get_all_users(self, query_params, fields, req_info):
        rsp_data_and_links = self.get_all(query_params, fields, req_info)

        # HATEOAS
        if self.comment_service_link:
            for i in rsp_data_and_links["data"]:
                link = self.comment_service_link + i['email']
                i["links"] = {
                    "rel": "comments",
                    "href": link
                }
            links = {
                "rel": "comments",
                "href": self.comment_service_link
            }

            rsp_data_and_links["link"] = links
        return rsp_data_and_links

    def get_by_user_id(self, fields, user_id):
        rsp_data_and_links = self.get_by_id(fields, user_id)

        # HATEOAS
        if self.comment_service_link:
            email = rsp_data_and_links["email"]
            link = self.comment_service_link + email
            links = {
                "rel": "comments",
                "href": link
            }
            rsp_data_and_links = {
                "data": rsp_data_and_links,
                "comments": links
            }
        return rsp_data_and_links

    def get_user_with_hashed(self, body):
        password = body['password']
        del body['password']
        rsp_data = self._data_table.find_by_template(body)
        for user in rsp_data:
            salt = bytearray.fromhex(user['salt'])
            hash_key = bytearray.fromhex(user['hash_key'])
            key = hashlib.pbkdf2_hmac(
                'sha256',  # The hash digest algorithm for HMAC
                password.encode('utf-8'),  # Convert the password to bytes
                salt,  # Provide the salt
                100000  # It is recommended to use at least 100,000 iterations of SHA-256
            )
            if hash_key == key:
                rsp = {'msg': '201 CREATED', 'status': 201}
                encoded_jwt = jwt.encode({'first_name': user['first_name'], 'last_name': user['last_name'],
                                          'email': user['email'], 'role': user['role'],
                                          'created_date': user['created_date'].isoformat()}, SECRET_KEY,
                                         algorithm='HS256')
                rsp['msg'] += ' ' + str(encoded_jwt)
                return rsp
        rsp = {'msg': '401 NOT AUTHORIZED', 'status': 401}
        return rsp

    def insert_user(self, body, encoded_jwt=None):
        body['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body['status'] = 'PENDING'
        rsp_data, location_id = self._data_table.insert(body)
        headers = {"Location": "/Users/" + location_id}
        if encoded_jwt:
            headers["Authorization"] = encoded_jwt
        rsp_data_id = {
            "data": rsp_data,
            "headers": headers
        }
        return rsp_data_id

    def insert_user_with_hashed(self, body):
        """
        :param body: contains email, first name, last name, email
        :return: encrypted JWT token in Authorization header
        """
        encoded_jwt = generate_jwt(body, SECRET_KEY, self.admin_user)
        rsp_data_id = self.insert_user(body, encoded_jwt)
        return rsp_data_id

    def check_registration(self, email_value):
        res = self._data_table.get_count(table_name='user_service.Users', column='email', value_count=email_value)
        if res > 0:
            return False
        return True

    def update_user(self, template, new_value):
        res = self._data_table.update_by_template(template, new_value)
        return res
