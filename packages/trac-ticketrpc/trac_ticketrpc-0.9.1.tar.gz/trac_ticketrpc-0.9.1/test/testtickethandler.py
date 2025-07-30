# -*- coding: utf-8 -*-

"""
Simple test of JSON-RPC interface for Trac ticket management.
Requires a running Trac server and the following environment variables set:
TEST_TRPC_PROJECT - name of Trac project
TEST_TRPC_VERSION - version of Trac project
TEST_TRPC_TRAC_USER - Trac user
TEST_TRPC_TRAC_PWD - Trac user's password
TEST_TRPC_TRAC_SERVER - Trac server URL
"""

import os
import sys
import time

from requests import request
from requests.auth import HTTPBasicAuth

from tracticketrpc import HTTP_OK


PROJECT = os.environ.get('TEST_TRPC_PROJECT')
VERSION = os.environ.get('TEST_TRPC_VERSION')
TRAC_USER = os.environ.get('TEST_TRPC_TRAC_USER')
TRAC_PWD = os.environ.get('TEST_TRPC_TRAC_PWD')
TRAC_SERVER = os.environ.get('TEST_TRPC_TRAC_SERVER')
AUTH = HTTPBasicAuth(TRAC_USER, TRAC_PWD)
HTTP_HEADERS = {'Accept': 'application/json', 'Content-type': 'application/json'}
SERVER_URL = f'{TRAC_SERVER}/{PROJECT}/ticketrpc'


def send_request(req_data: dict) -> dict:
    """
    Send a request to the Trac API.
    :param req_data: JSON-RPC request data
    :return: JSON-RPC response data
    """
    _resp = request('POST', SERVER_URL, timeout=30, headers=HTTP_HEADERS,
                    auth=AUTH, json=req_data, verify=False)
    if _resp.status_code != HTTP_OK:
        raise RuntimeError(f'HTTP code {_resp.status_code}: {_resp.reason}')
    _json_resp = _resp.json()
    _error = _json_resp.get('error')
    if _error is not None:
        raise RuntimeError(str(_error))
    return _json_resp.get('result')


# create ticket
ticket_id = None
try:
    create_params = {'type': 'defect',
                     'priority': 'major',
                     'summary': 'ticketrpc defect',
                     'description': 'test ticket creation',
                     'project': PROJECT,
                     'version': VERSION,
                     'component': PROJECT,
                    }
    req = {'jsonrpc': '2.0', 'method': 'ticket.create', 'params': create_params,
           'id': str(time.time_ns())}
    result = send_request(req)
    ticket_id = result.get('id')
    print(f'ticket with id {ticket_id} created')
except BaseException as _e:
    print(f'create ticket failed: {_e}')
    sys.exit(1)

# ticket details
try:
    details_params = {'id': ticket_id,
                      'project': PROJECT,
                     }
    req = {'jsonrpc': '2.0', 'method': 'ticket.details', 'params': details_params,
           'id': str(time.time_ns())}
    result = send_request(req)
    print(f'ticket details: {result}')
except BaseException as _e:
    print(f'get ticket details failed: {_e}')
    sys.exit(1)

# add comment
try:
    comment_params = {'id': ticket_id,
                      'text': 'ticket comment',
                      'project': PROJECT,
                     }
    req = {'jsonrpc': '2.0', 'method': 'ticket.add_comment', 'params': comment_params,
           'id': str(time.time_ns())}
    result = send_request(req)
    print(f'comment #{result["cnum"]} added to ticket ID {result["id"]}')
except BaseException as _e:
    print(f'add ticket comment failed: {_e}')
    sys.exit(1)

# ticket comments
try:
    comments_params = {'id': ticket_id,
                       'project': PROJECT,
                      }
    req = {'jsonrpc': '2.0', 'method': 'ticket.comments', 'params': details_params,
           'id': str(time.time_ns())}
    result = send_request(req)
    print(f'ticket comments: {result}')
except BaseException as _e:
    print(f'get ticket comments failed: {_e}')
    sys.exit(1)

# close ticket
try:
    close_params = {'id': ticket_id,
                    'resolution': 'fixed',
                    'text': 'test case succeeded',
                    'project': PROJECT,
                   }
    req = {'jsonrpc': '2.0', 'method': 'ticket.close', 'params': close_params,
           'id': str(time.time_ns())}
    result = send_request(req)
    print(f'ticket ID {result["id"]} closed')
except BaseException as _e:
    print(f'close ticket failed: {_e}')
    sys.exit(1)
