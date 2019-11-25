from flask import g
import socket
import json
import logging


def init_app(app):
    """
    Called by Flask when the application is starting.
    :param app:
    """
    app.teardown_appcontext(close_client)


def get_client():
    """
    Called by UI functions that want an instance of a SysClient
    :return: SysClient
    """
    if 'client' not in g:
        g.client = SysClient('127.0.0.1', 9090)
    return g.client


def close_client(e=None):
    """
    Called by Flask when the application is closing.
    :param e:
    :return:
    """
    client = g.pop('client', None)
    if client is not None:
        client.shutdown()


class SysClient:
    """
    Used to send commands and pull data from the System using its API
    """
    def __init__(self, addr, port):
        self._logger = logging.getLogger('AlarmSystem.sys_client.SysClient')
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((addr, port))
        except socket.error as e:
            self._logger.error('{}'.format(e))

    def get_status(self):
        """
        Pulls the system status from the system from its API
        :return: dict or None
        """
        try:
            self._socket.send(json.dumps({'func': 'status'}).encode('utf-8'))
            packet = self._socket.recv(1024)
            self._logger.debug('received: {}'.format(packet))
            data = json.loads(packet.decode('utf-8'))
            if data is not None and isinstance(data, dict):
                return data
            else:
                return None
        except socket.error as e:
            self._logger.error('{}'.format(e))
            return None
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
            return None

    def set_pin(self, current_pin, new_pin):
        try:
            self._socket.send(json.dumps({'func': 'set_pin', 'current_pin': current_pin,
                                          'new_pin': new_pin}).encode('utf-8'))
            packet = self._socket.recv(1024)
            self._logger.debug('received: {}'.format(packet))
            data = json.loads(packet.decode('utf-8'))
            if data is not None and isinstance(data, dict):
                return data
            else:
                return None
        except socket.error as e:
            self._logger.error('{}'.format(e))
            return None
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
            return None

    def arm_disarm(self, pin):
        try:
            self._logger.debug("Sending arm_disarm with Pin " + str(pin))
            self._socket.send(json.dumps({'func': 'arm_disarm', 'pin': pin}).encode('utf-8'))
            packet = self._socket.recv(1024)
            self._logger.debug('received: {}'.format(packet))
            data = json.loads(packet.decode('utf-8'))
            if data is not None and isinstance(data, dict):
                return data
            else:
                return None
        except socket.error as e:
            self._logger.error('{}'.format(e))
            return None
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
            return None

    def take_photo(self):
        try:
            self._socket.send(json.dumps({'func': 'take_photo'}).encode('utf-8'))
            packet = self._socket.recv(1024)
            self._logger.debug('received: {}'.format(packet))
            data = json.loads(packet.decode('utf-8'))
            if data is not None and isinstance(data, dict):
                return data
            else:
                return None
        except socket.error as e:
            self._logger.error('{}'.format(e))
            return None
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
            return None

    def take_video(self):
        try:
            self._socket.send(json.dumps({'func': 'take_video'}).encode('utf-8'))
            packet = self._socket.recv(1024)
            self._logger.debug('received: {}'.format(packet))
            data = json.loads(packet.decode('utf-8'))
            if data is not None and isinstance(data, dict):
                return data
            else:
                return None
        except socket.error as e:
            self._logger.error('{}'.format(e))
            return None
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
            return None

    def shutdown(self):
        """
        Shutdown this instance
        """
        self._socket.close()
        self._logger.info('client closed')
