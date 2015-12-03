# coding: utf-8
import os
# import daemon
from flask.ext.script import Manager
import random
from weshop import create_app
from weshop.models import db, User
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def run():
    """启动网站"""
    app.run(host="localhost", port=5000)


@manager.command
def run_80():
    """启动网站"""
    app.run(host="0.0.0.0", port=80)


@manager.command
def create_ucode():
    """生成5-6位用户id,u_code"""
    users = User.query
    for u in users:
        u_code = (random.randint(10000, 1000000))
        user = User.query.filter(User.id == u.id).first()
        while (user.u_code == u_code):
            print (user.id)
            u_code = (random.randint(10000, 1000000))
        user.u_code = u_code
        print ("user_id:" + str(u.id) + " u_code:" + str(u_code))
        db.session.add(user)
        db.session.commit()


@manager.command
def create_admin():
    """Create admin."""

    user = User(role='admin', name="admin", email="admin@qq.com", mobile="18812345678")
    user.password = "admin"
    user.hash_password()
    user.gene_token()
    db.session.add(user)
    db.session.commit()


@manager.command
def createdb():
    """Create database."""
    db.create_all()

@manager.command
def delete_version():
    """Create database."""
    version=AlembicVersion.query.first()
    db.session.delete(version)
    db.session.commit()

@manager.command
def reset_users_token():
    with app.app_context():
        for u in User.query:
            u.gene_token()
            db.session.add(u)
            db.session.commit()


@manager.command
def clean_exercises():
    """删除图片文件不存在的"""
    with daemon.DaemonContext():
        with app.app_context():
            pass


if __name__ == "__main__":
    manager.run()
