#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

# Set up base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration tool
db.init_app(app)
migrate = Migrate(app, db)

# ---------------- Routes ---------------- #

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_list = [
        {"id": r.id, "name": r.name, "address": r.address}
        for r in restaurants
    ]
    return make_response(jsonify(restaurants_list), 200)


# GET /restaurants/<id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    restaurant_data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients,
                },
            }
            for rp in restaurant.restaurant_pizzas
        ],
    }
    return make_response(jsonify(restaurant_data), 200)


# DELETE /restaurants/<id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    db.session.delete(restaurant)
    db.session.commit()
    return make_response('', 204)


# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [
        {"id": p.id, "name": p.name, "ingredients": p.ingredients}
        for p in pizzas
    ]
    return make_response(jsonify(pizzas_list), 200)


# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"errors": ["Invalid JSON"]}), 400)

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validate price
    if not isinstance(price, int) or price < 1 or price > 30:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    # Validate pizza and restaurant exist
    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not pizza or not restaurant:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id,
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            },
        }
        return make_response(jsonify(response), 201)

    except Exception:
        db.session.rollback()
        return make_response(jsonify({"errors": ["validation errors"]}), 400)


# Run the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
