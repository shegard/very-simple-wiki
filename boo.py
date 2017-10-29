import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import psycopg2

try:
    PORT = int(os.environ['PORT'])
except KeyError:
    PORT = 8080


try:
    url = os.environ["DATABASE_URL"]
except KeyError:
    url = "dbname=d7g3lpr5o54kmf host=ec2-54-83-48-188.compute-1.amazonaws.com port=5432 user=pdvwlhbrmgarvc password=79629f60082ce19a06abdbe260fbb33d986127486fc41480ffa47c6167e34aa7 sslmode=require"


class HelloRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == '/':
            self.path = '/def.html'

        ext = self.path[self.path.rfind('.') + 1:]
        sup_ext = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'text/javascript',
            'ico': 'image/x-icon',
            'db': 'text/html'
        }

        if ext not in sup_ext:
            self.send_error(404, "Object not found")
            return

        self.send_response(200)
        self.send_header('Content-type', '{0}; charset=utf-8'.format(sup_ext[ext]))
        self.end_headers()

        with open(self.path[1:]) as f:
            response_text = f.read()
        self.wfile.write(response_text.encode('utf-8'))

    def do_POST(self):

        print(self.path)
        req = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        print('POST: ', req)

        if self.path[1:] == 'secret.boo':

            self.send_response(200)
            self.end_headers()

            if req['query'] == 'update_current_version':

                lconn = psycopg2.connect(url)
                lcur = lconn.cursor()

                lcur.execute("update _articles set version = %s where title = %s;", (req['version'], req['title']))
                lcur.execute("select content from {} where version = %s".format(req['title']), (req['version'],))
                resp = lcur.fetchone()[0]
                lconn.commit()
                lcur.close()
                lconn.close()

                self.wfile.write(resp.encode('utf-8'))

            elif req['query'] == 'get_all':

                lconn = psycopg2.connect(url)
                lcur = lconn.cursor()
                lcur.execute("select version from _articles where title = %s", (req['title'],))
                cver = lcur.fetchone()
                if not cver:
                    cont = ''
                    vers = []
                else:
                    lcur.execute("select content from {} where version = %s".format(req['title']), (cver,))
                    cont = lcur.fetchone()
                    lcur.execute("select version from {}".format(req['title']))
                    vers = [x[0] for x in lcur.fetchall()]

                resp = {'versions': vers, 'current_version': cver, 'content': cont}
                lconn.commit()
                lcur.close()
                lconn.close()
                print("FOR DEBUG", resp)
                print("FOR DEBUG", json.dumps(resp))
                self.wfile.write(json.dumps(resp).encode('utf-8'))

            elif req['query'] == 'add_version':

                lconn = psycopg2.connect(url)
                lcur = lconn.cursor()

                lcur.execute("select version from _articles where title = %s", (req['title'],))
                cver = lcur.fetchone()
                if not cver:
                    lcur.execute("create table {} (version text, content text);".format(req['title']))
                    cver = '001'
                    lcur.execute("insert into _articles values (%s, %s)", (req['title'], cver))
                else:
                    lcur.execute("select version from {}".format(req['title']))
                    cver = lcur.fetchall()[-1]
                    cver = str(int(cver[0]) + 1)
                    while len(cver) < 3:
                        cver = '0' + cver
                    lcur.execute("update _articles set version = %s where title = %s", (cver, req['title']))
                lcur.execute("insert into {} values (%s, %s)".format(req['title']), (cver, req['content']))

                lconn.commit()
                lcur.close()
                lconn.close()

        elif self.path[1:] == 'api':
            self.send_response(200, 'ok')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            lconn = psycopg2.connect(url)
            lcur = lconn.cursor()

            if req['query'] == 'select':
                if req['action'] == 'get_articles':
                    lcur.execute("select title from _articles")
                    response = [x[0] for x in lcur.fetchall()]
                elif req['action'] == 'get_version_list':
                    lcur.execute("select version from {}".format(req['title']))
                    response = [x[0] for x in lcur.fetchall()]
                elif req['action'] == 'get_custom_version':
                    lcur.execute("select content from {} where version = %s".format(req['title']), (req['version'],))
                    response = lcur.fetchone()[0]
                elif req['action'] == 'get_current_version':
                    lcur.execute("select version from _articles where title = %s", (req['title'],))
                    curr = lcur.fetchone()[0]
                    lcur.execute("select content from {} where version = %s".format(req['title']), (curr,))
                    response = lcur.fetchone()[0]

                self.wfile.write(json.dumps(response).encode('utf-8'))

            elif req['query'] == 'alter':
                if req['action'] == 'make_new_version':
                    lcur.execute("select version from {}".format(req['title']))
                    curr = lcur.fetchall()[-1]
                    curr = str(int(curr[0]) + 1)
                    while len(curr) < 3:
                        curr = '0' + curr

                    lcur.execute("update _articles set version = %s where title = %s", (curr, req['title']))
                    lcur.execute("insert into {} values (%s, %s)".format(req['title']), (curr, req['content']))

                    self.wfile.write(json.dumps('new version created').encode('utf-8'))

                elif req['action'] == 'set_current_version':
                    lcur.execute("update _articles set version = %s where title = %s", (req['version'], req['title']))
                    self.wfile.write(json.dumps('current version updated').encode('utf-8'))

            lconn.commit()
            lcur.close()
            lconn.close()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


server_address = ('', PORT)
httpd = HTTPServer(server_address, HelloRequestHandler)
httpd.serve_forever()
