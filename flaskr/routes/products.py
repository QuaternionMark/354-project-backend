import functools
import re
import os
from jsonschema import validate, draft7_format_checker
import jsonschema.exceptions
import json

from flask import (
    Blueprint, g, request, session, current_app, session
)

from passlib.hash import argon2
from sqlalchemy.exc import DBAPIError
from sqlalchemy import or_
from flaskr.db import session_scope
from flaskr.models.Product import Product
from flaskr.models.Cart import Cart, CartLine
from flaskr.models.User import User
from flaskr.models.Order import Order
from flaskr.models.OrderLine import OrderLine
from flaskr.models.price import price

from flaskr.email import send
from flaskr.routes.utils import login_required, not_login, cross_origin, is_logged_in
from datetime import date

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route("/getProduct", methods=['POST'])
def getProduct():

    # Load json data from json schema to variable request.json 'SCHEMA_FOLDER'
    schemas_direcotry = os.path.join(current_app.root_path, current_app.config['SCHEMA_FOLDER'])
    schema_filepath = os.path.join(schemas_direcotry, 'product.schema.json')
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=request.json, schema=schema, format_checker=draft7_format_checker)
            
    except jsonschema.exceptions.ValidationError as validation_error:
        return {
            'code': 400,
            'message': validation_error.message
        }
    
    try:
        with session_scope() as db_session:
            # Create order object
            product = Product(
                                name = request.json.get('name'),
                                description = request.json.get('description'),
                                quantity = request.json.get('quantity'),
                                category_id = request.json.get('category_id'),
                                user_id = request.json.get('user_id'),
                                tax_id = request.json.get('tax_id'),
                                permalink = request.json.get('permalink'),
                                brand_id = request.json.get('brand_id')
                            )
            # Add to database
            db_session.add(product)

        return {
            'code': 200,
            'message': 'success'
        }, 200

    except DBAPIError as db_error:
        # Returns an error in case of a integrity constraint not being followed.
        return {
            'code': 400,
            'message': re.search('DETAIL: (.*)', db_error.args[0]).group(1)
        }, 400



    


