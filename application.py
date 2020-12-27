"""
Application.py

Supports requests to Amazon RDS through MySql using Flask
:Contributors: Derek Wacks, Jillian Ross, Donald Ferguson
:Advisor: Professor Ferguson, Columbia University

"""

import json
import os
import sys
import platform
import socket

import logging
from datetime import datetime

from flask import Flask, Response
from flask import request

from user_service.service_user_info import UserServiceInfo
import data_access.RDSDataTable as rds
from middleware.notification import notify


cwd = os.getcwd()
sys.path.append(cwd)
print("*** PYHTHONPATH = " + str(sys.path) + "***")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

__user_service = UserServiceInfo()


# Create the application server main class instance and call it 'application'
# Specific the path that identifies the static content and where it is.
application = Flask(__name__,
                    static_url_path='/static',
                    static_folder='website/static')


def handle_args(args):
    """
    :param args: dictionary form of request.args.
    :return: values removed from lists if they are in a list.
    """
    result = {}
    if args is not None:
        for k, v in args.items():
            if type(v) == list:
                v = v[0]
            result[k] = v
    return result


def log_and_extract_input(method, path_params=None):
    """
    1. Extract the input information from the requests object.
    2. Log the information
    3. Return extracted information.
    :param method:
    :param path_params:
    :return:
    """
    path = request.path
    args = dict(request.args)
    args = handle_args(args)
    data = None
    headers = dict(request.headers)
    method = request.method

    try:
        if request.data is not None:
            print("request.data exists")
            data = request.json
        else:
            data = None
    except Exception as e:
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs = {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data
        }

    if args.get('fields') == None:
        print("\n T.application.py; fields=None, Someone poisoned the waterhole!\n")

    # potentially remove
    if args and args.get('fields', None):
        fields = args.get('fields')
        fields = fields.split(",")
        del args['fields']
        inputs['fields'] = fields

    print("T.application.py; inputs=", inputs)

    log_message += " received: \n" + json.dumps(inputs, indent=2, default=str)
    logger.debug(log_message)

    return inputs


def log_response(method, status, data, txt):
    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }
    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2, default=str))


@application.after_request
def after_decorator(rsp):
    notify(request, rsp)
    return rsp


@application.route("/")
def home():
    rsp = Response("Hello world! This is a template of User Service.", status=200, content_type="text/plain")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "PUT", "DELETE", "POST"])
def demo(parameter):
    """
    :param parameter: A list of the path parameters.
    :return: None
    """
    inputs = log_and_extract_input(demo, { "parameter": parameter })
    msg = {
        "/demo received the following inputs" : inputs
    }
    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


# Health check
@application.route("/api/health", methods=["GET", "POST", "OPTIONS"])
def health_check():
    req_info = log_and_extract_input("/api/health")
    pf = platform.system()
    rsp_data = {"status": "healthy", "time": str(datetime.now()),
                 "platform": pf,
                 "release": platform.release()}
    if pf == "Darwin":
        rsp_data["note"] = "For some reason, macOS is called 'Darwin'"
    hostname = socket.gethostname()
    IP_addr = socket.gethostbyname(hostname)
    rsp_data["hostname"] = hostname
    rsp_data["IPAddr"] = IP_addr
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


logger.debug("__name__ = " + str(__name__))


@application.route("/registration", methods=["POST", "OPTIONS"])
def registration():
    rsp = None
    req_info = log_and_extract_input("/registration")
    if req_info["method"] == "OPTIONS":
        rsp = Response(status=200, content_type="application/json")
        return rsp  # Address and email, name, password are all valid
    if req_info["method"] == "POST":
        user_info = req_info["body"]
        if "email" not in user_info.keys() or "first_name" not in user_info.keys() or "last_name" not \
                in user_info.keys() or "password" not in user_info.keys():
            rsp = Response("REQUIRED PROPERTY (EMAIL, FULL NAME, PASSWORD) MISSING", status=400, content_type="text/plain")
        else:
            e_check_resp = __user_service.check_registration(user_info['email'])
            if e_check_resp:
                rsp_data = __user_service.insert_user_with_hashed(user_info)
                rsp_str = json.dumps(rsp_data, default=str)
                rsp = Response(rsp_str, status=201, content_type="application/json")
                return rsp  # address and email, name, password are all valid
            else:
                rsp_str = json.dumps({"status": "DUPLICATE REQUEST"}, default=str)
                rsp = Response(rsp_str, status=400, content_type="text/plain")
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")
    return rsp


@application.route("/login", methods=["POST"])
def login():
    rsp = None
    req_info = log_and_extract_input("/login")
    if req_info["method"] == "POST":
        user_info = req_info["body"]
        if "email" not in user_info.keys() or "password" not in user_info.keys():
            rsp = Response("REQUIRED PROPERTY (EMAIL, PASSWORD) MISSING", status=400, content_type="text/plain")
        else:
            rsp_data = __user_service.get_user_with_hashed(user_info)
            rsp = Response(rsp_data['msg'], status=rsp_data['status'], content_type="text/plain")
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")
    return rsp


@application.route("/Users", methods=["GET", "POST"])
def users():
    rsp = None
    req_info = log_and_extract_input("/Users")

    # Return everything in users table
    # sql = "SELECT * FROM USERS"
    if req_info["method"] == "GET":
        fields = req_info.get("fields", None)
        query_params = req_info['query_params']
        rsp_data = __user_service.get_all_users(query_params, fields, req_info)
        rsp_str = json.dumps(rsp_data, default=str)
        rsp = Response(rsp_str, status=200, content_type="application/json")
        return rsp
    # add a new entry to the table as json in the body
    elif req_info["method"] == "POST":
        rsp_data = __user_service.insert_user(req_info["body"])
        rsp_str = json.dumps(rsp_data, default=str)
        rsp = Response(rsp_str, status=201, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")
    return rsp


@application.route("/Users/<id>", methods=["GET", "PUT", "DELETE"])
def user_with_param(id):
    rsp = None
    req_info = log_and_extract_input("/Users", id)
    rds_table = rds.RDSDataTable("Users", key_columns="id")
    if req_info["method"] == "GET":
        fields = req_info.get("fields", None)
        rsp_data = __user_service.get_by_user_id(fields, id)
        rsp_str = json.dumps(rsp_data, default=str)
        rsp = Response(rsp_str, status=200, content_type="application/json")
        return rsp
    elif req_info["method"] == "PUT":
        rsp_data = rds_table.update_by_key(id, req_info["body"])
        rsp_str = json.dumps(rsp_data, default=str)
        rsp = Response(rsp_str, status=200, content_type="application/json")
        return rsp
    elif req_info["method"] == "DELETE":
        rsp_data = rds_table.delete_by_key(id)
        rsp_str = json.dumps(rsp_data, default=str)
        rsp = Response(rsp_str, status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")
    return rsp


if __name__ == "__main__":
    application.run("0.0.0.0", port=5000)

