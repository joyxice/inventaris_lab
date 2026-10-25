from flask import Flask, redirect, render_template

app = Flask(__name__)

@app.route('/')
def main():
    redirect('/login')
    
@app.route('/login')
def login():
    render_template('frontend/login.html')

if __name__ == '__main__':
    app.run(debug=True)