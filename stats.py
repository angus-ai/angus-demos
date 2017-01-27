#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
import json


class Stats(object):
    def __init__(self, f=None):
        self.stats = self.load(f)
        self.file = f

    def save(self, f=None):
        if f is None and self.file is not None:
            f = self.file

        with open(f, "w") as myfile:
            json.dump(self.stats, myfile)

    def load(self, f):
        if os.path.isfile(f):
            with open(f, "r") as myfile:
                return json.load(myfile)
        return dict()

    def add_engaged(self, engaged):
        if engaged is True:
            value = self.stats.setdefault("engaged", 0)
            value += 1
            self.stats["engaged"] = value
            value = self.stats.setdefault("not_engaged", 0)
            value -= 1
            self.stats["not_engaged"] = value
        else:
            value = self.stats.setdefault("not_engaged", 0)
            value += 1
            self.stats["not_engaged"] = value

    def add_age(self, age):
        label = "20-30"
        if age < 10:
            label = "0-10"
        elif age < 20:
            label = "10-20"
        elif age < 30:
            label = "20-30"
        elif age < 40:
            label = "30-40"
        elif age < 50:
            label = "40-50"
        elif age > 50:
            label = "50+"

        value = self.stats.setdefault(label, 0)
        value += 1
        self.stats[label] = value

    def add_gender(self, gender):
        value = self.stats.setdefault(gender, 0)
        value += 1
        self.stats[gender] = value

    def genders(self):
        result = {
            "female": self.stats.get("female", 0),
            "male": self.stats.get("male", 0),
        }
        return result

    def ages(self):
        categories = ["0-10", "10-20", "20-30", "30-40", "40-50", "50+"]
        result = dict([(cat, self.stats.get(cat, 0)) for cat in categories])
        return result

    def engaged(self):
        result = {
            "engaged": self.stats.get("engaged", 0),
            "not_engaged": self.stats.get("not_engaged", 0),
        }
        return result
