import meeplib
import traceback
import cgi


def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')

    # create a single message
    meeplib.Message('my title', 'This is my message NOW!', u)
    meeplib.Message('title', 'lol', u)
    meeplib.Message('my', 'test', u)
    meeplib.Message('test', 'my', u)
    # done.

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])

        username = 'test'

        return ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='/login'>Log in</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (username,)]

    def login(self, environ, start_response):
        # hard code the username for now; this should come from Web input!
        username = 'test'

        # retrieve user
        user = meeplib.get_user(username)

        # set content-type
        headers = [('Content-type', 'text/html')]
        
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def logout(self, environ, start_response):
        # does nothing
        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"
    def list_search(self, environ, start_response):
        results=meeplib.get_search_results()
        s = []
        s.append('Your Search Results')
        s.append('<hr>')
        print "RESULTS"
        print results 
        for result in results:
            m=meeplib.get_message(result)
            s.append('id: %d<p>' % (m.id,))
            s.append('title: %s<p>' % (m.title))
            s.append('message: %s<p>' % (m.post))
            s.append('author: %s<p>' % (m.author.username))
         
            s.append('<hr>')
       
       
        s.append("<form action='delete_action' method='POST'>Delete a Message?<br> Message ID: <input type='text' name='id'><input type='submit'>Delete</form>")    
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        s.append("<form action='search_action' method='POST'>Search for Messages?<br> Message ID: <input type='text' name='text'><input type='submit'>Delete</form>")    

        return ["".join(s)]



        
    def list_messages(self, environ, start_response):


        messages = meeplib.get_all_messages()

        s = []
        for m in messages:
            print m.id
            s.append('id: %d<p>' % (m.id,))
            s.append('title: %s<p>' % (m.title))
            s.append('message: %s<p>' % (m.post))
            s.append('author: %s<p>' % (m.author.username))
         
            s.append('<hr>')
           


        s.append("<form action='delete_action' method='POST'>Delete a Message?<br> Message ID: <input type='text' name='id'><input type='submit'>Delete</form>")    
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        s.append("<form action='search_action' method='POST'>Search for Messages?<br> Message ID: <input type='text' name='text'><input type='submit'>Delete</form>")    

        return ["".join(s)]

    def add_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return """<form action='add_action' method='POST'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='submit'></form>"""

##    def search (self, environ, start_response):
##     
##        headers = [('Content-type', 'text/html')]
##        start_response("200 OK", headers)
##
##        return """<form action='search_action' method='POST'>Message:<input type='text' name='id'><br><input type='submit'></form>"""
##
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















    
    ############################
    def delete_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return """<form action='delete_action' method='POST'>Message:<input type='text' name='message'><br><input type='submit'></form>"""
    
    def delete_message_action(self, environ, start_response):
        print "deleteaction"
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        message=int(form['id'].value)
        messages = meeplib.get_all_messages()
      #  meeplib.delete_message(messages[0])
        meeplib.delete_message(messages[message])
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)

        return ["message deleted"]
    
    ###############################


        
    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        
        username = 'test'
        user = meeplib.get_user(username)
        
        new_message = meeplib.Message(title, message, user)
        #meeplib.delete_message(new_message)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/search': self.list_search,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/delete': self.delete_message,
                      '/m/delete_action': self.delete_message_action,
                      '/m/search_action': self.search_message_action,
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
