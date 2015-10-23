#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from ._base import db


class Charge(db.Model):
    """授课费用"""
    id = db.Column(db.Integer, primary_key=True)
    range = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Charge %s>' % self.show