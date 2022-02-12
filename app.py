from flask import Flask

app = Flask(__name__)


@app.route('/')
def index_page():
    return 'This is a tool for show video with dts and eac3 audio'


if __name__ == '__main__':
    app.run()
