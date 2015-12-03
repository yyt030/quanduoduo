# -*- coding: UTF-8 -*-
from flask import Blueprint, request, jsonify, url_for, redirect, current_app
from flask_wtf.csrf import generate_csrf
from weshop import csrf
from ..models import db, User, follow, Notification, ChatOrder



bp = Blueprint('api', __name__)


def _get_current_user():
    """
    uid=282
    token=F0orXSAWtwJSr6Tdfk8H
    """
    uid = request.args.get('uid')
    token = request.args.get('token')
    user = User.query.filter(User.id == uid, User.token == token).first()
    return user


@bp.route('/')
def index():
    app_key = request.args.get('app_key')
    if app_key:
        return jsonify({'result': 'Welcome to tm api page!' + app_key})
    return jsonify({'result': 'Missing app_key...'})


@bp.route('/get_token')
def get_token():
    """
    post key csrf_token with cookie
    """
    return generate_csrf()


@bp.route('/login', methods=['GET'])
def login():
    """
    RESTful Authentication 不使用cookie和session，而是采用和OAuth2.0类似的token机制
    """
    email = request.args.get('email')
    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify({'result': False, 'message': '用户邮箱不存在'})
    psw = request.args.get('psw')
    if not user.check_password(psw):
        return jsonify({'result': False, 'message': '用户密码错误'})
    u = user.get_user_info_dict()
    u['auth_token'] = user.token
    u['email'] = user.email
    return jsonify({'result': True, 'message': '登陆成功', 'user': u})


@bp.route('/get_neighbours')
def get_neighbours():
    """
    http://www.tuomeng.com.cn/api/get_neighbours?uid=282&token=F0orXSAWtwJSr6Tdfk8H
    """
    user = _get_current_user()
    if not user:
        return jsonify({'result': False, 'message': '用户认证失败'})
    users = user.get_neighbours().limit(300)
    if users is None:
        return jsonify({'result': False, 'message': '请设置你所在的位置'})
    data = []
    for u in users:
        user_dict = u.get_user_info_dict()
        user_dict['has_followed'] = user.has_followed(u.id)
        data.append(user_dict)
    return jsonify({'result': True, 'message': '获取用户成功', 'users': data})


@bp.route('/get_recommend_users')
def get_recommend_users():
    user = _get_current_user()
    if not user:
        return jsonify({'result': False, 'message': '用户认证失败'})

    ret = User.query
    if User.role == 'teacher':
        ret = ret.filter(User.role != 'teacher')
    else:
        ret = ret.filter(User.role == 'teacher')
    ret = ret.order_by(User.sort_value.desc()).limit(20)

    # 推荐用户:后面再加上更多的筛选条件
    data = []
    for u in ret:
        user_dict = u.get_user_info_dict()
        user_dict['has_followed'] = user.has_followed(u.id)
        data.append(user_dict)
    return jsonify({'result': True, 'message': '获取推荐用户成功', 'users': data})


@bp.route('/get_notifications')
def get_notifications():
    user = _get_current_user()
    if not user:
        return jsonify({'result': False, 'message': '用户认证失败'})
    notifies = Notification.query.filter(Notification.receiver_id == user.id). \
        order_by(Notification.created_at.desc())
    q_notifies = notifies.filter(Notification.action == 100).all()
    ques = [n.get_notify_message() for n in q_notifies]
    a_notifies = notifies.filter(Notification.action == 101).all()
    ans = [n.get_notify_message() for n in a_notifies]
    ac_notifies = notifies.filter(Notification.action == 102).all()
    ac = [n.get_notify_message() for n in ac_notifies]
    d_count = notifies.filter(Notification.action == 103).count()
    sys_notifies = notifies.filter(Notification.action == 104).all()
    sys_msg = [n.get_notify_message() for n in sys_notifies]

    data = {
        'questions': ques,
        'answers': ans,
        'answer_comments': ac,
        'dialog_count': d_count,
        'system_messages': sys_msg
    }
    return jsonify({'result': True, 'message': '获取消息成功', "notifies": data})


# user settings


# follow
@bp.route('/add_follow/<int:uid>')
def add_follow(uid):
    user = _get_current_user()
    if not user:
        return jsonify({'result': False, 'message': '用户认证失败'})
    follow_to = User.query.get(uid)
    if not follow_to:
        return jsonify({'result': False, 'message': '你关注的用户不存在'})
    if user.followees.filter(User.id == uid).count() == 0:
        user.followees.append(follow_to)
        db.session.commit()
    return jsonify({'result': True, 'message': '你已关注该用户'})


@bp.route('/delete_follow/<int:uid>')
def delete_follow(uid):
    user = _get_current_user()
    if not user:
        return jsonify({'result': False, 'message': '用户认证失败'})
    follow_to = User.query.get(uid)
    if not follow_to:
        return jsonify({'result': False, 'message': '你没有关注该用户'})
    user.followees.remove(follow_to)
    db.session.commit()
    return jsonify({'result': True, 'message': '你已取消对该用户的关注'})


@bp.route('/test_data')
def test_data():
    """
    生成测试数据：
    """
    return '<a href=' + url_for('site.index') + '>跳转</a>'


@csrf.exempt
@bp.route('/post_test', methods=['POST'])
def post_test():
    user = request.form.get('post_data')
    return jsonify({'result': True, 'message': '返回' + str(user)})


