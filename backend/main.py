from flask import Flask, redirect, render_template, url_for
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../frontend")
)

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR
            )

@app.route('/')
def index():
    return redirect(url_for('login'))
    
@app.route('/login')
def login():
    return render_template('login.html')
    # return "hello"

if __name__ == '__main__':
    app.run(debug=True, port=5001)