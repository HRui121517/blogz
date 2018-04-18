from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:ruihuangbuildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)


    def __init__(self, title, content):
        self.title = title
        self.content = content
    
def valid_post(title, content):
    if len(title)==0 or len(content)==0:
        return False
    else:
        return True

posts = []

@app.route('/newpost', methods = ['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        title_error = ''
        content_error = ''

        if valid_post(title, content) is True:
            new_post= Blog(title, content)
            db.session.add(new_post)
            db.session.commit()
            post_url = "/blog?id=" + str(new_post.id)
            return redirect(post_url)

        else:
            if len(title) == 0:
                title_error = 'Please key in the title!'
            if len(content) == 0:
                content_error = 'Please key in the content!'
            return render_template('blog.html', title="BLOG!", title_error=title_error, content_error=content_error)

    else:
        return render_template('blog.html', title="BLOG!")

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    post_value = request.args.get('id')
    if post_value:
        post = Blog.query.get(post_value)
        return render_template('viewpost.html', title= "BLOG!", post  = post)

    else:
        posts = Blog.query.all()
        return render_template('posts.html', title= "BLOG!", posts = posts)


if __name__ == '__main__':
    app.run()