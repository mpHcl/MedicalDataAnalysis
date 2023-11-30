import os

from flask_cors import CORS
from flask import Flask,  jsonify, request, abort
from sqlalchemy.exc import IntegrityError

import datetime
from functions import *


def create_app(database_uri="sqlite:///project.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    db.init_app(app)

    CORS(app)

    @app.route("/")
    def hello_world():
        return "Hello World!"

    @app.route("/login", methods=["POST"])
    def login_user():
        login = request.json["login"]
        password = request.json["password"]

        try:
            user = db.session.execute(db.select(User).filter_by(login=login, password=hash_password(password))).scalar_one()
        except NoResultFound:
            abort(400, description="Invalid login or password.")

        token = generate_token(user.id)
        return jsonify({"token": token})

    @app.route("/permissions")
    def get_permissions():
        token = request.headers.get("Authorization")
        status, result = authorize(token)

        if status != 200:
            abort(status, description=result)

        user = result
        return jsonify({"permissions": [permission.name for permission in user.groups.permissions]})

    @app.route("/create_user", methods=["POST"])
    def create_user():
        token = request.headers.get("Authorization")
        status, result = authorize_permissions(token,["CREATE_USER_ACCOUNT"])

        if status != 200:
            abort(status, description=result)

        expected_keys = ["login", "password", "group"]
        if not all(key in request.json for key in expected_keys):
            abort(400, description="Missing or incorrect keys in the request")

        login = request.json["login"]
        password = request.json["password"]
        group_name = request.json["group"]

        if not login or not password or not group_name:
            abort(400, description="Invalid input data")
        try:
            group = db.session.execute(db.select(Group).filter_by(name=group_name)).scalar_one()
        except NoResultFound:
            abort(400, description="Invalid group name.")

        try:
            user = User(login=login,
                        password=hash_password(password),
                        password_expire_date=datetime.utcnow() + timedelta(days=30),
                        group=group.id)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(409, description="User with that login already exists.")

        return jsonify("Successfully created user")


    @app.route("/delete_user", methods=["DELETE"])
    def delete_user():
        token = request.headers.get("Authorization")
        status, result = authorize_permissions(token, ["DELETE_USER_ACCOUNT"])

        if status != 200:
            abort(status, description=result)

        if "id" not in request.json:
            abort(400, description="Missing or incorrect keys in the request")

        id = request.json["id"]
        try:
            user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
        except NoResultFound:
            abort(404, description="User with that id not found.")
        try:
            db.session.delete(user)
            db.session.commit()
        except IntegrityError:
            abort(409, description="Error while deleting the user.")

        return jsonify("Successfully deleted user")

    @app.route("/update_user", methods=["PUT"])
    def update_user():
        token = request.headers.get("Authorization")
        status, result = authorize_permissions(token, ["UPDATE_USER_ACCOUNT"])
        changed=0
        if status != 200:
            abort(status, description=result)

        if "id" not in request.json:
            abort(400, description="Missing or incorrect keys in the request")

        id = request.json["id"]

        try:
            user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
        except NoResultFound:
            abort(404, description="User with that id not found.")

        if "group" in request.json:
            group_name = request.json["group"]
            try:
                group = db.session.execute(db.select(Group).filter_by(name=group_name)).scalar_one()
            except NoResultFound:
                abort(400, description="Invalid group name.")

            try:
                user.group = group.id
                db.session.commit()
                changed=1
            except IntegrityError:
                abort(409, description="Error while updating the user.")

        if "password" in request.json:
            password = request.json["group"]
            try:
                user.password = hash_password(password)
                user.password_expire_date=datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                changed=1
            except IntegrityError:
                abort(409, description="Error while updating the user.")
        if changed==0:
            abort(400, description="Missing values")
        return jsonify("Successfully updated user")

    return app


if __name__ == "__main__":
    app = create_app()
    isInitialized = os.path.exists("instance/project.db")

    with app.app_context():
        db.create_all()

        if not isInitialized:
            initialize_database()

    app.run()
