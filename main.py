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
    def render_NewPost(self, title="", blogpost="", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_NewPost()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            a = Blogpost(title=title, blogpost=blogpost)
            a.put()
            id = Blogpost.key().id()
            self.redirect("/blog/'%s'"%sid)
        else:
            error = "We need both a title and some content in the body of your blogpost!"
            self.render_NewPost(title, blogpost, error)

class Recent5(Handler):
    def render_blogposts(self, title="", blogpost="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC LIMIT 5")

        self.render("blogposts.html", title=title, blogpost=blogpost, blogposts=blogposts)

    def get(self):
        self.render_blogposts()

class ViewPostHandler(Handler):
    def get(self, id, title="", blogpost=""):
        blogposts = Blogpost.get_by_id(int(id), parent=None)
        if blogposts:
            self.render("blogposts.html", title=title, blogpost=blogpost, id=id, blogposts=blogposts)
        else:
            self.write("There is no blogpost with that ID.")


class FrontPage(Handler):
    def render_blogposts(self, title="", blogpost="", error="", id = ""):
        blogposts = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC")
        # id = Blogpost.key().id()

        self.render("blogposts.html", title=title, blogpost=blogpost, blogposts=blogposts)

    def get(self):
        self.render_blogposts()

app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/newpost', NewPost),
    ('/blog', Recent5),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
