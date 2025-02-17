from flask import Flask, render_template
from api import api  # 導入 api Blueprint

app = Flask(__name__)
app.register_blueprint(api)  # 註冊 api Blueprint


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
