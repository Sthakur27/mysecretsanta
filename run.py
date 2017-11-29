from flask import Flask
from ssapp import app
@app.route('/')
def test():
    return("ayylmao")

if __name__=='__main__':
    app.run(
        host='0.0.0.0',
        port=5065,
        threaded=True
    )

