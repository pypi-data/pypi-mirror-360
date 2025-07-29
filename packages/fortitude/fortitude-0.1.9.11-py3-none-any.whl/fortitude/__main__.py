#!/usr/bin/env python3
import http.server
import http.client
import http.cookies
import time
import random
import threading
import struct
import base64
import ipaddress
import socket
import ssl
import json
import re
import argparse
import gzip
import logging

from base64 import b64encode
from socketserver import ThreadingMixIn
from hashlib import sha1, md5
from datetime import datetime
import requests
import websocket

from fortitude.default_page import error_page, reload_page

parser = argparse.ArgumentParser(description='Smart loadbalancer for Odoo')
parser.add_argument('-c','--config', help='configuration file (json format)', required=True)
args = vars(parser.parse_args())


GZIP_TYPE = ["application/json",  
             "application/pdf", 
             "text/html", 
             "text/plain",
             "text/css", 
             "text/xml", 
             "text/javascript", 
             "image/png"]
CONFIG ={}
IP_ACTIVITY = {}

def load_conf():
    global CONFIG
    with open(args['config'], "r") as f :
        CONFIG = json.load(f)

def is_static_path(path):
    for rule in  CONFIG.get('read_rules', []) :
        if re.match(rule, path) : return True
    return False

def is_longpolling(path):
    if re.match("^/longpolling/(.*)", path) : return True
    return False

def select_srv(type, session=False):
    global CONFIG

    if CONFIG['distribution'] == 'random'  or ( CONFIG['distribution'] == 'session' and not session ):
        return CONFIG[type][random.randint(0, len(CONFIG[type])-1)]
    
    if CONFIG['distribution'] == 'robin' :
        key = type + '_' + CONFIG['distribution']
        next = CONFIG.get(key, 0)
        next = (next + 1) if (next + 1) < len(CONFIG[type]) else 0
        CONFIG[key] = next
        return CONFIG[type][CONFIG[key]]

    if CONFIG['distribution'] == 'session' :
        affected = 10000
        cible  = 0
        for index, value in enumerate(CONFIG[type]) :
            if not CONFIG['distribution'] in CONFIG[type][index].keys() : CONFIG[type][index][CONFIG['distribution']] = []
            if session in CONFIG[type][index][CONFIG['distribution']] :
                return CONFIG[type][index]
            
            if len(CONFIG[type][index][CONFIG['distribution']]) <= affected :
                cible = index
                affected = len(CONFIG[type][index][CONFIG['distribution']])
        
        CONFIG[type][cible][CONFIG['distribution']].append(session)
        return CONFIG[type][cible]


    if CONFIG['distribution'] == 'availability' :
        active = 10000
        cible  = 0
        for index, value in enumerate(CONFIG[type]) :
            if not CONFIG['distribution'] in CONFIG[type][index].keys() : CONFIG[type][index][CONFIG['distribution']] = 0
            if CONFIG[type][index][CONFIG['distribution']] <= active :
                cible = index
                active = CONFIG[type][index][CONFIG['distribution']]
        
        CONFIG[type][cible][CONFIG['distribution']] += 1
        return CONFIG[type][cible]


class WebSocketError(Exception):
    pass

class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    pass


class ForceRedirect(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - REDIRECT - %s" % (self.client_address[0], format%args))

    def log_error(self, format, *args):
        logging.error("%s - REDIRECT - %s" % (self.client_address[0], format%args))

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def do_HEAD(self):
        self.handle_request()

    def do_OPTIONS(self):
        self.handle_request()

    def handle_request(self):
       self.send_response(301)
       self.send_header('Location', 'https://%s:%s' %(self.headers.get('Host'), CONFIG['http_port']))
       self.end_headers()


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    _ws_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    _opcode_continu = 0x0
    _opcode_text = 0x1
    _opcode_binary = 0x2
    _opcode_close = 0x8
    _opcode_ping = 0x9
    _opcode_pong = 0xa
    
    server_version = "Fortitude/0.1"
    protocol_version = "HTTP/1.1"

    ws = None
    daemon_threads = True
    mutex = threading.Lock()

##############################################
#
#               COMMON
#
##############################################                        
    def send_response(self, *args):
        self.log_data['status'] = args[0]
        super().send_response(*args)

    def log_message(self, format, *args):
        self.log_data['remote_addr'] = self.client_address[0]
        self.log_data['time_local'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_data['request_time'] != 0.00 : self.log_data['request_time'] = round(time.time() - self.log_data['request_time'], 2)
        logging.info('%(remote_addr)s - %(remote_user)s [%(time_local)s] "%(request)s" %(status)s %(body_bytes_sent)s "%(http_referer)s" "%(http_user_agent)s" %(request_time)ss "%(http_x_forwarded_for)s" %(upstream_addr)s %(upstream_response_length)s %(upstream_response_time)ss %(upstream_status)s' %self.log_data)

    def log_error(self, format, *args):
        self.log_data['remote_addr'] = self.client_address[0]
        self.log_data['time_local'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_data['request_time'] = round(time.time() - self.log_data['request_time'], 2)
        logging.info('%(remote_addr)s - %(remote_user)s [%(time_local)s] "%(request)s" %(status)s %(body_bytes_sent)s "%(http_referer)s" "%(http_user_agent)s" %(request_time)ss "%(http_x_forwarded_for)s" %(upstream_addr)s %(upstream_response_length)s %(upstream_response_time)ss %(upstream_status)s' %self.log_data)

    def setup(self):
        super().setup()
        self.connected = False
        self.log_data ={
            'remote_addr' : '0.0.0.0.0',
            'remote_user' : '',
            'time_local' : '',
            'request' : '/',
            'status' : 200,
            'body_bytes_sent' : 0,
            'http_referer' : '',
            'http_user_agent' : '',
            'request_time' : 0.00,
            'http_x_forwarded_for' : '', 
            'upstream_addr' : '',
            'upstream_response_length' : '',
            'upstream_response_time' : 0.00,
            'upstream_status' : 101
            }


##############################################
#
#               WS
#
##############################################                        

    def on_ws_message(self, message):
        if self.ws : self.ws.send(message)
        pass
        
    def on_ws_connected(self):
        def on_message(clt, message):
            if isinstance(message, str) :
                message = message.encode('utf-8')
            self.send_message(message)

        def on_close(ws):
            pass
        def on_open(ws):
            pass
        
        self.ws = websocket.WebSocketApp("ws://%s:%s/websocket" %(CONFIG['ws_srv']["host"], CONFIG['ws_srv']["port"]), cookie = self.headers.get('Cookie', None), on_message = on_message, on_close = on_close, on_open = on_open)
        tmp = threading.Thread(target=self.ws.run_forever)
        tmp.daemon = True
        tmp.start()
        pass
        
    def on_ws_closed(self):
        if self.ws : self.ws.close()
        pass
        
    def send_message(self, message):
        self._send_message(self._opcode_text, message)

    def _read_messages(self):
        while self.connected == True:
            try:
                self._read_next_message()
            except (socket.error, WebSocketError) as e:
                #websocket content error, time-out or disconnect.
                self.log_message("RCV: Close connection: Socket Error %s" % str(e.args))
                self._ws_close()
            except Exception as err:
                #unexpected error in websocket connection.
                self.log_error("RCV: Exception: in _read_messages: %s" % str(err.args))
                self._ws_close()
        
    def _read_next_message(self):
        try:
            b1, b2 = self.rfile.read(2)
            self.opcode = b1 & 0x0F
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self.rfile.read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self.rfile.read(8))[0]

            masks = [b for b in self.rfile.read(4)]
            decoded = ""
            for char in self.rfile.read(length):
                decoded += chr(char ^ masks[len(decoded) % 4])
            self._on_message(decoded)

        except (struct.error, TypeError) as e:
            #catch exceptions from ord() and struct.unpack()
            if self.connected:
                raise WebSocketError("Websocket read aborted while listening %s " %e) 
            else:
                #the socket was closed while waiting for input
                self.log_error("RCV: _read_next_message aborted after closed connection")
                pass
        
    def _send_message(self, opcode, message):
        try:
            header  = bytearray()
            header.append(0x80 | opcode)
            length = len(message)

            # Petit message
            if length <= 125:
                header.append(length)

            # Message < 16bits
            elif length >= 126 and length <= 65535:
                header.append(0x7e)
                header.extend(struct.pack(">H", length))
            
            # Message < 64bits
            elif length < 18446744073709551616:
                header.append(0x7f)
                header.extend(struct.pack(">Q", length))

            if length > 0:
                self.request.send(header + message)

        except socket.error as e:
            #websocket content error, time-out or disconnect.
            self.log_message("SND: Close connection: Socket Error %s" % str(e.args))
            self._ws_close()
        except Exception as err:
            #unexpected error in websocket connection.
            self.log_error("SND: Exception: in _send_message: %s" % str(err.args))
            self._ws_close()

    def _handshake(self):
        headers=self.headers
        if headers.get("Upgrade", None) != "websocket":
            return

        key = headers['Sec-WebSocket-Key']
        hash = sha1(key.encode() + self._ws_GUID.encode())
        digest = b64encode(hash.digest()).strip()

        with self.mutex :
            self.send_response(101, 'Switching Protocols')
            self.send_header('Upgrade', 'websocket')
            self.send_header('Connection', 'Upgrade')
            self.send_header('Sec-WebSocket-Accept', digest.decode('ASCII'))
            self.end_headers()
            self.connected = True
            self.on_ws_connected()
    
    def _ws_close(self):
        self.mutex.acquire()
        try:
            if self.connected:
                self.connected = False
                self.close_connection = 1
                try: 
                    self._send_close()
                except:
                    pass
                self.on_ws_closed()
            else:
                self.log_message("_ws_close websocket in closed state. Ignore.")
                pass
        finally:
            self.mutex.release()
            
    def _on_message(self, message):
        if self.opcode == self._opcode_close:
            self.connected = False
            self.close_connection = 1
            try:
                self._send_close()
            except:
                pass
            self.on_ws_closed()
        # ping
        elif self.opcode == self._opcode_ping:
            self._send_message(self._opcode_pong, message)
        # pong
        elif self.opcode == self._opcode_pong:
            pass
        # data
        elif (self.opcode == self._opcode_continu or 
                self.opcode == self._opcode_text or 
                self.opcode == self._opcode_binary):
            self.on_ws_message(message)

    def _send_close(self):
        msg = bytearray()
        msg.append(0x80 + self._opcode_close)
        msg.append(0x00)
        self.request.send(msg)

##############################################
#
#               HTTP
#
##############################################                        

    def allowed_ip(self, ):
        ips = CONFIG.get('allowed_ips')
        if not ips : 
            return True
        else :
            for x in ips :
                if ipaddress.ip_address(self.client_address[0]) in ipaddress.ip_network(x) :
                    return True
        return False

    def send_error(self, code, message=""):
        content = error_page.replace('{{code}}', str(code)).replace('{{message}}', message).encode()
        for x in CONFIG.get('custom_errors', []) :
            if x['code'] == code :
                try :
                    if x.get('file') :
                        with open(x['file'], 'br') as f : 
                            content = f.read()
                    elif x.get('url') : 
                        resp = requests.get(x.get('url'))
                        content = resp.content
                except : pass
                code = x.get('code_return', code)
            break

        self.send_response(code)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.headers.get("Upgrade", None) == "websocket":
            self._handshake()
            self._read_messages()
        elif self.path == "/fortitude-reload" :
            load_conf()
            content = reload_page.encode()
            self.send_response(200)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/fortitude-status" :
            content = json.dumps(CONFIG, indent=4).encode()
            self.send_response(200)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_PUT(self):
        self.handle_request('PUT')

    def do_OPTIONS(self):
        self.handle_request('OPTIONS')

    def do_DELETE(self):
        self.handle_request('DELETE')

    def do_HEAD(self):
        self.handle_request('HEAD')

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def handle_request(self, method):
        self.log_data['request_time'] = time.time()
        #Gestion des IP autorisée
        if not self.allowed_ip() :
            self.send_error(403, "IP non autorisée")
            return

        #IP-BAN
        if CONFIG.get('autoban', False) : 
            if not IP_ACTIVITY.get(self.client_address[0]) : 
                IP_ACTIVITY[self.client_address[0]] = {'score' : 0, 'last_request' : time.time()}
            else :
                if time.time() - IP_ACTIVITY[self.client_address[0]]['last_request'] > 300 : 
                    IP_ACTIVITY[self.client_address[0]] = {'score' : 0, 'last_request' : time.time()}
                if IP_ACTIVITY[self.client_address[0]]['score'] > 10:
                    self.send_error(418, "i'm <b>NOT</b> a teapot ;)")
                    return

        auth = False
        credential = False
        for x in CONFIG.get('auth', []) :
            if self.path.find(x['path']) == 0 :
                auth = True
                credential = (x['user'], x['md5'])
                break
        if auth :
            if self.headers.get('Authorization') is None:
                self.do_AUTHHEAD()
                self.wfile.write(bytes('Unauthorized', 'utf8'))
                return 
            else:
                try :
                    user, password = base64.b64decode(self.headers.get('Authorization').replace('Basic ', '')).decode().split(':')
                    password = md5(password.encode()).hexdigest()                    
                    if user != credential[0] or password != credential[1] :
                        self.do_AUTHHEAD()
                        self.wfile.write(bytes('Unauthorized', 'utf8'))
                        return
                except Exception as e :
                    self.do_AUTHHEAD()
                    self.wfile.write(bytes('Unauthorized', 'utf8'))
                    return

        
        #Ajout/update des entêtes de proxy
        request_headers = {x : self.headers[x] for x in self.headers if not x.lower() in ['transfer-encoding']}
        self.log_data['request'] = "%s %s" %(method, self.path.split('?')[0])
        self.log_data['http_user_agent'] = request_headers.get('User-Agent', '')
        self.log_data['body_bytes_sent'] = request_headers.get('Content-Length', 0)
        self.log_data['http_referer'] = request_headers.get('Referer', "")

        if not 'X-Real-IP' in request_headers.keys(): request_headers['X-Real-IP'] = self.client_address[0]


        if not 'X-Forwarded-Proto' in request_headers.keys(): 
            request_headers['X-Forwarded-Proto'] = 'https' if CONFIG['secure'] else 'http'
        else :
            request_headers['X-Forwarded-Proto'] = request_headers['X-Forwarded-Proto'].split(',')[0]
        
        if not 'X-Forwarded-Host' in request_headers.keys(): 
            request_headers['X-Forwarded-Host'] = request_headers.get('Host')
        else : 
            request_headers['X-Forwarded-Host'] = request_headers['X-Forwarded-Host'].split(',')[0]

        if not 'X-Forwarded-For' in request_headers.keys(): 
            request_headers['X-Forwarded-For'] = self.client_address[0]
        else : 
            request_headers['X-Forwarded-For'] = request_headers['X-Forwarded-For'].split(',')[0]
            #request_headers['X-Forwarded-For'] = request_headers['X-Forwarded-For'] + ', %s' %self.client_address[0]

        self.log_data['http_x_forwarded_for'] = request_headers['X-Forwarded-For']

        srv = False
        session = False
        content=""
        headers = {}

        if CONFIG['distribution'] == 'session' and request_headers.get('Cookie') :
            tmp = http.cookies.SimpleCookie()
            tmp.load(request_headers['Cookie'])
            session = tmp['session_id'].value if tmp.get('session_id', False) else False

        longpolling = is_longpolling(self.path)
        if longpolling : 
            srv = CONFIG['ws_srv']
            self.log_data['upstream_response_time'] = time.time()            
            self.log_data['upstream_addr'] = srv["host"]
            conn = http.client.HTTPConnection(srv["host"], srv["port"])
            post_body=""
            content_len = int(request_headers.get('Content-Length', "0"))
            if content_len :
                post_body = self.rfile.read(content_len)
            try :
                conn.request(method, self.path, post_body, headers=request_headers)
                response = conn.getresponse()
                headers = {header : value for header, value in response.getheaders() if not header.lower() in ['transfer-encoding']}
                content = response.read()
                conn.close()
            except :
                self.send_error(502)
                return
        else :
            static = is_static_path(self.path)

            post_body=""
            content_len = int(request_headers.get('Content-Length', "0"))
            if content_len : post_body = self.rfile.read(content_len)

            if static :
                srv = select_srv('read_srv', session)
                self.log_data['upstream_response_time'] = time.time()            
                self.log_data['upstream_addr'] = srv["host"]
                conn = http.client.HTTPConnection(srv["host"], srv["port"])
                try :
                    conn.request(method, self.path, post_body, headers=request_headers)
                    response = conn.getresponse()
                    headers = {header : value for header, value in response.getheaders() if not header.lower() in ['transfer-encoding']}
                    content = response.read()
                    conn.close()
                    if len(content) < 5000 and "psycopg2.errors" in str(content) or response.status == 500  :
                        static = False
                except :
                    self.send_error(502, "Serveur indisponible")
                    return
            
            if not static :
                srv = select_srv('write_srv', session)
                self.log_data['upstream_response_time'] = time.time()            
                self.log_data['upstream_addr'] = srv["host"]
                conn = http.client.HTTPConnection(srv["host"], srv["port"])
                try :
                    conn.request(method, self.path, post_body, headers=request_headers)
                    response = conn.getresponse()
                    headers = {header : value for header, value in response.getheaders() if not header.lower() in ['transfer-encoding']}
                    content = response.read()
                    conn.close()
                except :
                    self.send_error(502)
                    return

            if CONFIG.get('autoban', False) : 
                if response.status >= 500 : 
                    IP_ACTIVITY[self.client_address[0]]['score'] += 3
                elif response.status >= 400 : 
                    IP_ACTIVITY[self.client_address[0]]['score'] += 2
                elif response.status >= 300 and response.status != 304 : 
                    IP_ACTIVITY[self.client_address[0]]['score'] += 1
                elif response.status == 200 : 
                    if self.path  == "/web/login" :
                        IP_ACTIVITY[self.client_address[0]]['score'] += 1
                    elif IP_ACTIVITY[self.client_address[0]]['score'] > 0 :
                        IP_ACTIVITY[self.client_address[0]]['score'] -= 1


        self.log_data['upstream_response_length'] = len(content)
        self.log_data['upstream_status'] = response.status
        self.log_data['upstream_response_time'] = round(time.time() - self.log_data['upstream_response_time'], 2)

        ###############################################
        #           Réponse au client
        ###############################################
        if len(content) > 4096 :
            if 'accept-encoding' in request_headers:
                if 'gzip' in request_headers['accept-encoding']:
                    if headers.get('Content-Type', '').split(';')[0] in GZIP_TYPE:
                        content = gzip.compress(content)
                        headers['Content-Encoding'] = 'gzip'

        self.send_response(response.status)
        headers['Content-Length'] = len(content)
        for header, value in headers.items():
                self.send_header(header, value)
        self.end_headers()
        if len(content) > 0 : 
            self.wfile.write(content)

        if CONFIG['distribution'] == 'availability' and srv.get(CONFIG['distribution'], False) :
            srv[CONFIG['distribution']] -= 1

if __name__ == '__main__':
    load_conf()
    
    server_address = (CONFIG.get('http_bind', '0.0.0.0'), CONFIG.get('http_port', 80))
    httpd = ThreadingHTTPServer(server_address , ProxyHandler)

    if CONFIG.get("secure", False) :
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CONFIG['secure_cert'], CONFIG['secure_key'])
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        if CONFIG.get("secure_port_redirect", False) :
            redirect_httpd = http.server.HTTPServer((CONFIG.get('http_bind', '0.0.0.0'), CONFIG['secure_port_redirect']), ForceRedirect)
            tmp = threading.Thread(target=redirect_httpd.serve_forever)
            tmp.daemon = True
            tmp.start()

    logging.basicConfig(level=logging.INFO, format="")
    logger = logging.getLogger('Fortitude')
    logger.info('Reverse proxy server running on port %s...', CONFIG.get('http_port', 80))

    httpd.serve_forever() 