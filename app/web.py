from flask import Blueprint, send_file, url_for, request, abort, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.question import Question
import os
from secrets import token_urlsafe


web = Blueprint("web", __name__)

ROOT_PATH = os.path.dirname(__file__)
ALLOWED_FORMATS = ["jpeg", "jpg", "png"]


@web.route("/avatar/<string:file_name>", methods=["GET"])
def avatar(file_name):
    file_path = ROOT_PATH + url_for("static", filename="avatar/{}".format(file_name))

    return send_file(file_path)


@web.route("/avatar", methods=["POST"])
@jwt_required
def upload_avatar():
    if 'avatar' not in request.files:
        print("'avatar' key not found")
        abort(404)  # Not Found

    file = request.files['avatar']
    if file.filename == '':
        abort(400)  # Bad Request

    current_user = get_jwt_identity()
    user = User.find_by_id(current_user["id"])

    if not user:
        abort(404)  # Not Found

    file_name = file.filename
    _, ext = file_name.rsplit('.', 1)
    
    if ext.lower() not in ALLOWED_FORMATS:
        abort(406)  # Not Acceptable

    file_name = "{}.{}".format(token_urlsafe(16), ext)
    path = ROOT_PATH + url_for("static", filename="avatar/{}".format(file_name))

    file.save(path)

    if user.avatar:
        old_path = ROOT_PATH + url_for("static", filename="avatar/{}".format(user.avatar))
        os.remove(old_path)

    user.avatar = file_name
    user.save()

    return redirect(url_for("web.avatar", file_name=file_name))


@web.route("/img/<string:file_name>", methods=["GET"])
def img(file_name):
    file_path = ROOT_PATH + url_for("static", filename="img/{}".format(file_name))

    return send_file(file_path)


@web.route("/img/<string:question_id>", methods=["POST"])
@jwt_required
def upload_img(question_id):
    if 'img' not in request.files:
        print("'img' key not found")
        abort(404)  # Not Found

    file = request.files['img']
    if file.filename == '':
        abort(400)  # Bad Request

    question = Question.find_by_id(question_id)
    if not question:
        print("Question not found")
        abort(404)  # Not Found

    file_name = file.filename
    _, ext = file_name.rsplit('.', 1)

    if ext.lower() not in ALLOWED_FORMATS:
        abort(406)  # Not Acceptable

    file_name = "{}.{}".format(token_urlsafe(16), ext)
    path = ROOT_PATH + url_for("static", filename="img/{}".format(file_name))

    file.save(path)

    if question.images:
        question.images.append(file_name)
    else:
        question.images = [file_name]

    question.save()

    return redirect(url_for("web.img", file_name=file_name))
