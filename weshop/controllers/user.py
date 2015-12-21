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
from ..models import db, User, WechatMessage, Profile
from ..utils.account import signin_user, signout_user
from ..utils.permissions import require_visitor, require_user
from ..utils._redis import LoginState

bp = Blueprint('user', __name__)


@bp.route('/profile', methods=['GET', 'POST'])
@require_user
def profile():
    fid = request.args.get("fid", type=int)
    user = User.query.get(fid)
    return render_template('user/profile.html', user=user)


@bp.route('/message', methods=['GET', 'POST'])
@require_user
def message():
    fid = request.args.get("fid", type=int)
    messages = {}
    profile =Profile.query.filter(Profile.user_id==fid).first()
    if fid:
        messages = WechatMessage.query.filter(WechatMessage.user_id == fid)
    return render_template('user/message.html', profile=profile,messages=messages)
