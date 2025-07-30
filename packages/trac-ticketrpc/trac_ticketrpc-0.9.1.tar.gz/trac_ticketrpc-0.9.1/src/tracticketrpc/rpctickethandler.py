# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------
# trac-ticketrpc - JSON-RPC Plugin to manage tickets in Trac SCM
#
# Copyright (c) 2025, Frank Sommer.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# --------------------------------------------------------------------------------------------------

"""
JSON-RPC interface for Trac ticket management.
Allows creation, update or information retrieval of a ticket.
"""

import json
from typing import Union, Optional

import trac.ticket.model
from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.api import Request, RequestDone

from tracticketrpc import *


class RpcException(BaseException):
    """
    Exceptions within plugin.
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, req_id: Union[str, int, None], rpc_code: int, http_code: int,
                 message: str, details: str = None):
        """
        Constructor.
        :param req_id: JSON-RPC request ID
        :param rpc_code: JSON-RPC error code
        :param http_code: HTTP response code
        :param message: error message
        :param details: optional detail error message
        """
        super().__init__(req_id, rpc_code, http_code, message, details)

    def request_id(self) -> Union[str, int, None]:
        """
        :returns: JSON-RPC request ID
        """
        return self.args[0]

    def rpc_code(self) -> int:
        """
        :returns: JSON-RPC error code
        """
        return self.args[1]

    def http_code(self) -> int:
        """
        :returns: HTTP response code
        """
        return self.args[2]

    def message(self) -> str:
        """
        :returns: error message
        """
        return self.args[3]

    def details(self) -> Optional[str]:
        """
        :returns: detail error message
        """
        return self.args[4]

    def __str__(self) -> str:
        """
        :returns: exception info
        """
        _details = self.details()
        return self.message() if _details is None else f'{self.message()}. {_details}'


class RpcTicketHandler(Component):
    """
    Handles JSON-RPC calls from HTTP clients.
    Supported methods are ticket.create, ticket.add_comment, ticket.close,
    ticket.comments and ticket.details.
    """
    implements(IRequestHandler)

    # noinspection PyMethodMayBeStatic
    def match_request(self, req: Request) -> bool:
        """
        :param req: HTTP request
        :returns: True, if the request is a call to the JSON-RPC ticket management
        """
        return req.path_info == HTTP_REQUEST_PATH

    def process_request(self, req: Request):
        """
        Process JSON-RPC ticket management request.
        :param req: HTTP request
        """
        _request_id = None
        # pylint: disable=broad-exception-caught
        try:
            _content_type = req.get_header('Content-Type')
            if _content_type != 'application/json':
                # cannot handle non JSON request
                _msg = f'Content-Type {_content_type} not supported, application/json required'
                raise RpcException(None, JSON_RPC_CONTENT_TYPE_ERROR,
                                   HTTP_UNSUPPORTED_MEDIA_TYPE, _msg)
            _req_method = req.method
            if _req_method != 'POST':
                # request methods other than POST are not supported
                _msg = f'Request method {_req_method} not supported, POST required'
                raise RpcException(None, JSON_RPC_INVALID_REQUEST, HTTP_METHOD_NOT_ALLOWED, _msg)
            _request_id, _result = self._handle(req)
            if _request_id is None:
                # missing JSON request ID is treated as notification,
                # i.e. no response expected by client
                req.send_no_content()
                return
            _resp_data = {'jsonrpc': '2.0', 'result': _result, 'id': _request_id}
            # pylint: disable=no-member
            self.log.debug(f'Sending response {_resp_data}') # noqa
            req.send(json.dumps(_resp_data, default=str).encode('utf-8'), 'application/json')
        except RequestDone:
            raise
        except RpcException as _e:
            # pylint: disable=no-member
            self.log.error(_e) # noqa
            if _e.http_code() != HTTP_OK:
                req.send_error(None, str(_e).encode('utf-8'), 'text/plain', _e.http_code())
                return
            if _e.request_id() is None:
                req.send_no_content()
                return
            _err = {'code': _e.rpc_code(), 'message': _e.message()}
            _resp_data = {'jsonrpc': '2.0', 'error': _err, 'id': _request_id}
            req.send(json.dumps(_resp_data).encode('utf-8'), 'application/json', _e.http_code())
        except BaseException as _e:
            # pylint: disable=no-member
            self.log.error(str(_e)) # noqa
            req.send_error(None, str(_e).encode('utf-8'), content_type = 'text/plain')

    def _handle(self, req: Request) -> tuple[Union[str, int, None], dict]:
        """
        Process ticket management request.
        :param req: HTTP request
        :returns: JSON-RPC request ID, response data
        :raises RpcException: if request cannot be processed
        """
        try:
            _req_data = json.loads(req.read(req.get_header('Content-Size')))
        except BaseException as _e:
            raise RpcException(None, JSON_RPC_PARSE_ERROR, HTTP_OK, str(_e)) from _e
        # pylint: disable=no-member
        self.log.debug(f'Processing request {_req_data}') # noqa
        if not isinstance(_req_data, dict):
            raise RpcException(None, JSON_RPC_INVALID_REQUEST, HTTP_OK,
                               'Dictionary content required')
        _req_id = _req_data.get('id')
        _method = _req_data.get('method')
        if _method is None:
            raise RpcException(_req_id, JSON_RPC_INVALID_REQUEST, HTTP_OK,
                               'RPC method not specified')
        if _method == 'ticket.create':
            if 'TICKET_CREATE' not in req.perm:
                raise RpcException(_req_id, JSON_RPC_ACCESS_DENIED, HTTP_OK,
                                   'TICKET_CREATE permission required')
            return _req_id, self._create_ticket(_req_data, req.authname)
        if _method == 'ticket.add_comment':
            if 'TICKET_APPEND' not in req.perm:
                raise RpcException(_req_id, JSON_RPC_ACCESS_DENIED, HTTP_OK,
                                   'TICKET_APPEND permission required')
            return _req_id, self._add_ticket_comment(_req_data, req.authname)
        if _method == 'ticket.close':
            if 'TICKET_MODIFY' not in req.perm:
                raise RpcException(_req_id, JSON_RPC_ACCESS_DENIED, HTTP_OK,
                                   'TICKET_MODIFY permission required')
            return _req_id, self._close_ticket(_req_data, req.authname)
        if _method == 'ticket.comments':
            if 'TICKET_VIEW' not in req.perm:
                raise RpcException(_req_id, JSON_RPC_ACCESS_DENIED, HTTP_OK,
                                   'TICKET_VIEW permission required')
            return _req_id, self._ticket_comments(_req_data)
        if _method == 'ticket.details':
            if 'TICKET_VIEW' not in req.perm:
                raise RpcException(_req_id, JSON_RPC_ACCESS_DENIED, HTTP_OK,
                                   'TICKET_VIEW permission required')
            return _req_id, self._ticket_details(_req_data)
        raise RpcException(_req_id, JSON_RPC_METHOD_NOT_FOUND, HTTP_OK,
                           f'RPC method {_method} not supported')

    def _create_ticket(self, req_data: dict, user: str) -> dict:
        """
        Creates a new ticket.
        :param req_data: HTTP request contents
        :param user: authenticated Trac user
        :returns: ID of created Trac ticket
        :raises RpcException: if request cannot be processed
        """
        _params = self._validated_params(_RPC_PARAMS_CREATE, req_data.get('params'),
                                         req_data.get('id'))
        # pylint: disable=no-member
        _ticket = trac.ticket.model.Ticket(self.env) # noqa
        for _param, _value in _params.items():
            _ticket[_param] = _value
        _ticket['reporter'] = user
        _ticket['owner'] = user
        _ticket['status'] = 'new'
        _ticket['resolution'] = ''
        _ticket_id = _ticket.insert()
        return {'id': str(_ticket_id)}

    def _add_ticket_comment(self, req_data, user) -> dict:
        """
        Adds a comment to an existing ticket.
        :param req_data: HTTP request contents
        :param user: authenticated Trac user
        :returns: ID of Trac ticket and comment number
        :raises RpcException: if request cannot be processed
        """
        _params = self._validated_params(_RPC_PARAMS_ADD_COMMENT, req_data.get('params'),
                                         req_data.get('id'))
        # pylint: disable=no-member
        _ticket = trac.ticket.model.Ticket(self.env, _params['id']) # noqa
        _comment_nr = _ticket.save_changes(author=user, comment=_params['text'])
        return {'id': _params['id'], 'cnum': _comment_nr}

    def _close_ticket(self, req_data: dict, user: str) -> dict:
        """
        Closes a ticket.
        :param req_data: HTTP request contents
        :param user: authenticated Trac user
        :returns: ID of created Trac ticket
        :raises RpcException: if request cannot be processed
        """
        _params = self._validated_params(_RPC_PARAMS_CLOSE, req_data.get('params'),
                                         req_data.get('id'))
        _ticket_id = _params['id']
        # pylint: disable=no-member
        _ticket = trac.ticket.model.Ticket(self.env, _ticket_id) # noqa
        _ticket['status'] = 'closed'
        _ticket.save_changes(author=user, comment=_params.get('text'))
        return {'id': _ticket_id}

    def _ticket_comments(self, req_data: dict) -> dict:
        """
        Returns all comments of an existing ticket.
        :param req_data: HTTP request contents
        :returns: ID and all comments of specified Trac ticket
        :raises RpcException: if request cannot be processed
        """
        _params = self._validated_params(_RPC_PARAMS_COMMENTS, req_data.get('params'),
                                         req_data.get('id'))
        _ticket_id = _params['id']
        _sql = f'''SELECT newvalue FROM ticket_change WHERE ticket = {_ticket_id}
                   AND field = 'comment' ORDER BY oldvalue asc'''
        _comments = []
        # pylint: disable=no-member
        for _comment in self.env.db_query(_sql): # noqa
            _comments.extend(_comment)
        return {'id': _ticket_id, 'comments': _comments}

    def _ticket_details(self, req_data: dict) -> dict:
        """
        Returns detail information about an existing ticket.
        :param req_data: HTTP request contents
        :returns: all fields of specified Trac ticket
        :raises RpcException: if request cannot be processed
        """
        _params = self._validated_params(_RPC_PARAMS_DETAILS, req_data.get('params'),
                                         req_data.get('id'))
        # pylint: disable=no-member
        t = trac.ticket.model.Ticket(self.env, _params['id']) # noqa
        return t.values

    def _validated_params(self, desc: dict, params: dict, req_id: Union[str, int, None]) -> dict:
        """
        Validates RPC parameters.
        Unsupported parameters are not contained in the result,
        as are parameters not applicable for Trac project.
        :param desc: validation descriptor
        :param params: RPC parameters sent from client
        :param req_id: JSON-RPC request ID
        :returns: validated parameters
        :raises RpcException: if parameters are not specified at all, mandatory parameters
                              are missing or parameter values have invalid type
        """
        if params is None:
            _msg = 'RPC parameters not specified'
            raise RpcException(req_id, JSON_RPC_INVALID_PARAMS, HTTP_OK, _msg)
        _validated_params = {}
        for _attr, _attr_desc in desc.items():
            if _attr_desc[1] and _attr not in params:
                # mandatory parameter missing
                _msg = f'Mandatory parameter {_attr} not specified'
                raise RpcException(req_id, JSON_RPC_INVALID_PARAMS, HTTP_OK, _msg)
        for _p_name, _p_value in params.items():
            _p_desc = desc.get(_p_name)
            if _p_desc is None:
                # unsupported parameter
                continue
            if not isinstance(_p_value, _p_desc[0]):
                # wrong parameter type
                _msg = f'Invalid type for parameter {_p_name},  requires {_p_desc[0].__name__}'
                raise RpcException(req_id, JSON_RPC_INVALID_PARAMS, HTTP_OK, _msg)
            if not self._param_applicable(_p_name, _p_value):
                # parameter value refers to undefined object (e.g. version does not exist)
                continue
            _validated_params[_p_name] = _p_value
        return _validated_params

    def _param_applicable(self, param_name: str, param_value) -> bool:
        """
        Indicates, whether specified parameter is applicable for Trac project environment.
        For parameters type, priority, version and component, the parameter value must refer to
        an existing entity in Trac. All other parameters are always applicable.
        :param param_name: parameter name
        :param param_value: parameter value
        :returns: True, if parameter value is applicable
        """
        _referenced_class = _PARAM_CLASSES.get(param_name)
        if _referenced_class is None:
            return True
        # pylint: disable=no-member
        _objects = _referenced_class.select(self.env) # noqa
        for _object in _objects:
            if param_value == _object.name:
                return True
        return False


_PARAM_CLASSES = {'component': trac.ticket.model.Component,
                  'priority': trac.ticket.model.Priority,
                  'resolution': trac.ticket.model.Resolution,
                  'type': trac.ticket.model.Type,
                  'version': trac.ticket.model.Version
                 }

_RPC_PARAMS_CREATE = {'type': (str, False),
                      'priority': (str, False),
                      'summary': (str, True),
                      'description':  (str, True),
                      'project':  (str, True),
                      'version':  (str, False),
                      'component': (str, False)
                     }
_RPC_PARAMS_ADD_COMMENT = {'id': (str, True),
                           'text':  (str, True),
                           'project':  (str, True)
                          }
_RPC_PARAMS_CLOSE = {'id': (str, True),
                     'resolution': (str, True),
                     'text': (str, False),
                     'project':  (str, True)
                    }
_RPC_PARAMS_DETAILS = {'id': (str, True),
                       'project':  (str, True)
                      }
_RPC_PARAMS_COMMENTS = {'id': (str, True),
                        'project':  (str, True)
                       }
