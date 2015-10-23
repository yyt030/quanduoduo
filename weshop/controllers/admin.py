# coding:utf-8
import json
import datetime
from datetime import  datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, g, current_app, url_for
from ..models.user import User

from ..utils.account import signin_user
from ..utils.permissions import require_admin, ADMIN_PSW, ADMIN_EMAIL

bp = Blueprint("admin", __name__)

"""
首先需要登录管理员账号：
admin@tuomeng.com tuomeng2014
写在permissions.py里面了
"""


@bp.route("/", methods=('GET', 'POST'))
def login():
    form = SigninForm()
    status = ""
    if g.user:
        return redirect("admin/teacher_sta")
    if request.method == 'POST':
        if form.email.data == ADMIN_EMAIL and form.password.data == ADMIN_PSW:
            user = User.query.filter(User.email == ADMIN_EMAIL, User.name == "admin").first()
            if user:
                signin_user(user, True)
                return redirect("admin/teacher_sta")
        else:
            status = "登录失败"
    return render_template("admin/login.html", form=form, status=status)
