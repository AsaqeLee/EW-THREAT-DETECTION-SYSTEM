from flask import Flask
from flask_cors import CORS
from modules.api_routes import api_bp
from modules.ui_routes import ui_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
