# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import random
import hashlib
import time
from werkzeug import security
from ._base import db



# class AlembicVersion(db.Model):
#     """数据迁移表"""
#
#     version_num = db.Column(db.String(50))
#
#     def __repr__(self):
#         return '<AlembicVersion %s>' % self.version_num