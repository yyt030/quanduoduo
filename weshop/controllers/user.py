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
from ..utils.permissions import require_visitor, require_teacher, require_parent_or_student
from ..utils._redis import LoginState

bp = Blueprint('', __name__)


@bp.route('/addshop',methods=['GET', 'POST'])
@require_visitor
def index():
    return render_template('shop/setting.html')


