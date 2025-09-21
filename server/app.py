#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_list = [restaurant.to_dict() for restaurant in restaurants]
        response = make_response(restaurant_list, 200)
        return response
    
class RestaurantByID(Resource):
    
    def delete(self,id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            response = make_response({'error': "Restaurant not found"}, 404)
            return response
        db.session.delete(restaurant)
        db.session.commit()
        response = make_response({}, 204)
        return response

    def get(self,id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            response = make_response({'error': "Restaurant not found"},404)
            return response 
        response_dict = restaurant.to_dict()
        response_dict['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        return response_dict
    

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_list =[pizza.to_dict() for pizza in pizzas]
        response = make_response(pizza_list, 200)
        return response
    
    def post(self):
        data = request.get_json()
        pizza = Pizza(
            name = data.get('name'),
            ingredients = data.get('ingredients')
        )
        db.session.add(pizza)
        db.session.commit()
        response = make_response(pizza.to_dict(), 201)
        return response

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            restaurantpizza = RestaurantPizza(
                price=data.get("price"),
                restaurant_id=data.get("restaurant_id"),
                pizza_id=data.get("pizza_id"),
            )
            db.session.add(restaurantpizza)
            db.session.commit()

            # success response
            response_data = {
                "id": restaurantpizza.id,
                "price": restaurantpizza.price,
                "pizza_id": restaurantpizza.pizza_id,
                "restaurant_id": restaurantpizza.restaurant_id,
                "pizza": restaurantpizza.pizza.to_dict(),
                "restaurant": restaurantpizza.restaurant.to_dict(),
            }
            return make_response(response_data, 201)

        except ValueError:
            # validation errors (e.g., price not in 1..30)
            return make_response({"errors": ["validation errors"]}, 400)

        except Exception:
            # generic failure case
            return make_response({"errors": ["validation errors"]}, 400)

    
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)