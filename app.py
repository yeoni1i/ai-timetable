from flask import Flask

from routes.main_routes import main_bp
from routes.recommend_routes import recommend_bp
from routes.chatbot_routes import chatbot_bp

app = Flask(__name__)
app.secret_key = "secret-key"

app.register_blueprint(main_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(chatbot_bp)


print(app.url_map)

if __name__ == "__main__":
    app.run(debug=False)




