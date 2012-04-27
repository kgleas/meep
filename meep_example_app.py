import meeplib
import traceback
import cgi
import meepcookie
from file_server import FileServer
from jinja2 import Environment, FileSystemLoader
import os
import sqlite3 as lite
import uuid

con = lite.connect('meepdb.db')
cur = con.cursor()


def session_get(c, session_cookie):
        username = None
        session_cookie=str(session_cookie)
        cur.execute('SELECT username FROM sessions WHERE cookie=?', [session_cookie])
        con.commit()

        try:
            username = cur.fetchone()[0]
        except:
            pass
        return username
    

        
def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')

    # create a single message
    meeplib.Message('my title', 'This is my message!', u)
    meeplib.load()
    # done.
env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)
	 
class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])


        
        cookie = environ.get("HTTP_COOKIE")
        if cookie is None or (cookie[len('username='):]==''):
				welcome = "You are not logged in"
				return [ render_page('index.html', username="",welcome=welcome) ]
        else:
                                scookie = cookie[9:]
                                username=session_get(cur,scookie)
				welcome = "you are logged in as user:"
				return [ render_page('index.html', username=username,welcome=welcome) ]
        

    def login(self, environ, start_response):
        username = 'sessionuser'
        session_cookie = str(uuid.uuid4())
        username=str(username)
        cur.execute('INSERT INTO sessions (username, cookie) VALUES (?, ?)', (username, session_cookie))
        con.commit()
        print "THE COOKIE",session_cookie
        usernameDB=session_get(cur,session_cookie)
        print "THE USERNAMEDB ",usernameDB



        # hard code the username for now; this should come from Web input!

        # retrieve user
        user = meeplib.get_user(username)

        # set content-type
        headers = [('Content-type', 'text/html')]
        #cookies
        cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',session_cookie)

        headers.append((cookie_name, cookie_val))
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def logout(self, environ, start_response):


        # does nothing
        headers = [('Content-type', 'text/html')]
        cookie_name, cookie_val = meepcookie.make_set_cookie_header('username','')

        cookie = environ.get("HTTP_COOKIE")
        cookie = cookie[9:]
        session_cookie=str(cookie)
        cur.execute('DELETE from sessions WHERE cookie=?', [session_cookie])
        con.commit()

        headers.append((cookie_name, cookie_val))
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"
    
    def list_search(self, environ, start_response):
        results=meeplib.get_search_results()
        s = []
        for result in results:
            s.append(meeplib.get_message(result))
            # replies = meeplib.get_replies(m.id)

            # if (replies!=-1):
                # s.append('<div style="padding-left: 50px;">Replies:</div><br />')
                # for r in replies:
                    
                    # s.append(""" <div style="padding-left: 70px;">&nbsp;%s</div><p>""" % r)

            # s.append('<hr>')
       
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return [ render_page('search_results.html', messages=s) ]
    
    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()
        replies = meeplib.get_replies(2)
        print replies
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        return [ render_page('list_messages.html', messages=messages,replies=replies) ]


    def search_message_action(self, environ, start_response):
        print "searchaction"
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        text=form['text'].value
    
        searchlist=meeplib.search_message_dict(text)
       

        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/search'))
        start_response("302 Found", headers)
        

        return ["message deleted"]

    def add_message(self, environ, start_response):
			headers = [('Content-type', 'text/html')]
        
			start_response("200 OK", headers)
			return [ render_page('add_message.html') ]


    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        
        username = 'test'
        user = meeplib.get_user(username)
        

        with con:
            cur.execute("INSERT INTO messages (title, post, author) VALUES (?, ?, ?)", (title, message, username,))

        con.commit()
        meeplib.load()
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]

    def delete_message(self, environ, start_response):
        qString = cgi.parse_qs(environ['QUERY_STRING'])
        mId = qString.get('id', [''])[0]
        messageID = meeplib.get_message(int(mId))
        mId= int(mId)
        meeplib.delete_message(messageID)
        with con:
            cur.execute("DELETE FROM messages WHERE id = (?)", (mId))

        con.commit()
     
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        
        return ["message deleted"]



    def add_reply(self, environ, start_response):
		qString = cgi.parse_qs(environ['QUERY_STRING'])
		mId = qString.get('id', [''])[0]
		headers = [('Content-type', 'text/html')]
                mId=int(mId);
		start_response("200 OK", headers)
		return [ render_page('add_reply.html', mId=mId) ]



    def add_reply_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        message = form['message'].value
        mId = int(form['id'].value)
        with con:
            cur.execute("INSERT INTO replies (parent, reply) VALUES (?, ?)", (mId, message))

        con.commit()

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        
        return ["Replied"]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/delete_message': self.delete_message,
                      '/m/add_reply': self.add_reply,
                      '/m/add_reply_action':self.add_reply_action,
                      '/m/search_action': self.search_message_action,
                      '/m/search': self.list_search,
							 '/css/style.css': FileServer("css/style.css"),
							 '/img/bg_menu.gif': FileServer("img/bg_menu.gif"),
							 '/img/bg_t.gif': FileServer("img/bg_t.gif"),
							 '/img/bullet.gif': FileServer("img/bullet.gif"),
							 '/img/logo.gif': FileServer("img/logo.gif"),
							 '/img/logo_.gif': FileServer("img/logo_.gif"),
							 '/img/top_bg.gif': FileServer("img/top_gb_.gif")
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]
