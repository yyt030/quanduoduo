# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import random
import hashlib
import time
from werkzeug import security
from ._base import db


class Site(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address = db.Column(db.String(100))
    icp = db.Column(db.String(50), default='')

    def __repr__(self):
        return '<Site %s>' % self.url