from flask import Flask
from flask_classy import FlaskView
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class IndexView(FlaskView):
    def index(self):
        return 'Hello'


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/api/v1')
IndexView.register(app, route_base='/')



if __name__ == '__main__':
    app.run(debug=True)
