import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
        it is a public endpoint
        it contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"], endpoint="get_drinks")
def get_drinks():
    try:
        drinks = Drink.query.all()

        data = {
            "success": True,
            "drinks": [drink.short() for drink in drinks]
        }

        return json.dumps(data), 200

    except:
        return json.dumps({
            "success": False,
            "error": "An error occurred"
        }), 500


'''
    GET /drinks-detail
        it requires the 'get:drinks-detail' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail", methods=["GET"], endpoint="get_drink_details")
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    try:
        drinks = Drink.query.all()

        data = {
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }

        return json.dumps(data), 200

    except:
        return json.dumps({
            "success": False,
            "error": "An error occurred"
        }), 500



'''
    POST /drinks
        it creates a new row in the drinks table
        it requires the 'post:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"], endpoint="post_drink")
@requires_auth('post:drinks')
def post_drink(jwt):

    data = request.get_json()

    name = data.get("title")
    recipe = data.get("recipe")

    # returning all drinks so that there's no need to refresh the page to see the newly created drink
    try:
        drink = Drink(title=name, recipe=json.dumps(recipe))
        drink.insert()

        return json.dumps({
            "success": True,
            "drinks": [drink.long() for drink in Drink.query.all()]
        }), 200

    except:
        return json.dumps({
            "success": False,
            "error": "An error occured"
        }), 500


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it updates the corresponding row for <id>
        it requires the 'patch:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<drink_id>", methods=["PATCH"], endpoint="patch_drink")
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):

    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    data = request.get_json()

    if not drink:
        abort(404)

    title = data.get("title")
    recipe = data.get("recipe")

    # returning all drinks so that there's no need to refresh the page to see the newly created drink
    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return json.dumps({
            "success": True,
            "drinks": [drink.long() for drink in Drink.query.all()]
        }), 200

    except:
        return json.dumps({
            "success": False,
            "error": "An error occured"
        }), 500


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it respond with a 404 error if <id> is not found
        it deletes the corresponding row for <id>
        it requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["DELETE"], endpoint="delete_drink")
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()

        return json.dumps({
            "success": True,
            "delete": drink_id
        }), 200

    except:
        return json.dumps({
            "success": False,
            "error": "An error occured"
        }), 500


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(AuthError)
def handle_auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response
