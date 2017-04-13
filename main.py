import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogpost(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
    def render_front(self, title="", blogpost="", error=""):
        self.render("front.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            a = Blogpost(title=title, blogpost=blogpost)
            a.put()

            self.redirect("/")
        else:
            error = "we need both a title and some content in the body of your blogpost!"
            self.render_front(title, blogpost, error)

class Recent5(Handler):
    def render_recent5(self, title="", blogpost="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC LIMIT 5")

        self.render("recent5.html", title=title, blogpost=blogpost, blogposts=blogposts)

    def get(self):
        self.render_recent5()

class ViewPostHandler(Handler):
    def get(self, id):
        self.write(id)

app = webapp2.WSGIApplication([
    ('/', NewPost),
    ('/recent5', Recent5),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
