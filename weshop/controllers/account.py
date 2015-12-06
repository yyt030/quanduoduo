# coding: utf-8
import random
import uuid
from urllib import unquote
import json
import os
import datetime
from flask_wtf.csrf import generate_csrf
from weshop import csrf
from flask import render_template, Blueprint, request, url_for, redirect, flash, abort, jsonify, \
    session, g
from ..models import db, User
from ..utils.account import signin_user, signout_user
from ..utils.permissions import require_visitor
from ..utils._redis import LoginState

bp = Blueprint('', __name__)


@bp.route('/signup', defaults={'role': 'student'}, methods=['GET', 'POST'])
@bp.route('/signup/<role>', methods=['GET', 'POST'])
@require_visitor
def signup(role):
    """注册"""
    form = SignupForm(role=role)
    finish = request.args.get('finish')
    if finish == 'finish':
        # 点击确认后，返回原页面
        email = request.args.get('email')
        email_domain = request.args.get('email_domain')
        return render_template('account/signup.html', finish=True, email=email,
                               email_domain=email_domain)
    else:
        if form.validate_on_submit():
            # 基本信息
            name = form.name.data.replace(' ', '')
            email = form.email.data
            u_code = (random.randint(9999, 999999))
            user = User.query.filter(User.u_code == u_code).first()
            while user:
                u_code = (random.randint(9999, 999999))
            user = User(name=name, email=email, password=form.password.data,
                        role=form.role.data, is_active=False, u_code=u_code)
            user.hash_password()
            user.gene_token()
            db.session.add(user)
            db.session.commit()
            # 寻找邮箱登陆URL
            email_domains = {
                'qq.com': 'mail.qq.com',
                'foxmail.com': 'mail.qq.com',
                'gmail.com': 'www.gmail.com',
                '126.com': 'www.126.com',
                '163.com': 'www.163.com',
                '189.cn': 'www.189.cn',
                '263.net': 'www.263.net',
                'yeah.net': 'www.yeah.net',
                'sohu.com': 'mail.sohu.com',
                'tom.com': 'mail.tom.com',
                'hotmail.com': 'www.hotmail.com',
                'yahoo.com.cn': 'mail.cn.yahoo.com',
                'yahoo.cn': 'mail.cn.yahoo.com',
                '21cn.com': 'mail.21cn.com',
            }

            email_domain = ""
            for key, value in email_domains.items():
                if email.count(key) >= 1:
                    email_domain = value
                    break
            return redirect(url_for('account.signup', finish='finish', email=email,
                                    email_domain=email_domain))
        return render_template('account/signup.html', form=form, role=role)


