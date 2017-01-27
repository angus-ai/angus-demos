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

from math import sin, cos
import cv2

OFF = -100
BH_SIZE = 40

LOGOS_MALE_FEMALE = [cv2.resize(cv2.imread(x), (0,0), fx=0.2, fy=0.2) for x in ["male.png", "female.png"]]
LOGO_ANGUS = cv2.imread("logo.png")
LOGO_ANGUS = cv2.resize(LOGO_ANGUS, (0,0), fx=0.05, fy=0.05)
LINETH = 3

def display_logo(frame, lx, ly):
    if ly+LOGO_ANGUS.shape[0] < frame.shape[0] and ly > 0 and lx+LOGO_ANGUS.shape[1] < frame.shape[1] and lx > 0:
        sub = frame[ly:ly+LOGO_ANGUS.shape[0],lx:lx+LOGO_ANGUS.shape[1]]
        cv2.addWeighted(sub, 0, LOGO_ANGUS, 1, 0.0, dst=sub)

def rotateLine(ptx, pty, centerx, centery, alpha):
    s = sin(alpha)
    c = cos(alpha)
    ptxn = (+c*(ptx-centerx) + s*(pty-centery)) + centerx
    ptyn = (-s*(ptx-centerx) + c*(pty-centery)) + centery
    return (int(ptxn), int(ptyn))

def rect(frame, p1, p2, rect_color=None, thickness=1):
    x1, y1 = p1
    x2, y2 = p2
    sub = frame[y1:y2, x1:x2]
    if rect_color:
        cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, thickness=thickness)

def blur(frame, p1, p2, rect_color=None, thickness=1):
    x1, y1 = p1
    x2, y2 = p2
    sub = frame[y1:y2, x1:x2]
    cv2.GaussianBlur(sub, (31, 31), 130, dst=sub)
    if rect_color:
        cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, thickness=thickness)

def get_age(age):
    label ="20-30"
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
    elif age >= 50:
        label = "50+"
    return label

def displayAge(frame, idx, h, f_roi_conf, f_age_conf):
    if h['face_roi_confidence'] > f_roi_conf:
        roi = h['face_roi']
        x1 = int(roi[0])
        x2 = int(roi[0]+roi[2])
        y1 = int(roi[1])
        y2 = int(roi[1]+roi[3])
        sub = frame[y1:y2,x1:x2]
        age = h['age']
        gender = h['gender']
        ih = idx
        if h['age_confidence'] > f_age_conf:
            age = h["age"]
            color = (100, 100, 100)
            cv2.putText(frame, get_age(age) + " ans",
                        (int(roi[0]+ 10), int(roi[1] + OFF - int(BH_SIZE*2))), cv2.FONT_HERSHEY_SIMPLEX,
                        1, color, 2)
        x = int(roi[0]+0.5*roi[2])
        y = int(roi[1])
        return (x,y)
    else:
        return None


def displayHair(frame, idx, h):
    el_x = h['face_eye'][0][0]
    el_y = h['face_eye'][0][1]
    er_x = h['face_eye'][1][0]
    er_y = h['face_eye'][1][1]
    m_x = h['face_mouth'][0]
    m_y = h['face_mouth'][1]

    em_x = (0.5*(el_x + er_x))
    em_y = (0.5*(el_y + er_y))

    v_x = m_x - em_x
    v_y = m_y - em_y

    h_x =int(em_x - 1.3*v_x)
    h_y = int(em_y - 1.3*v_y)

    dim = frame.shape
    if h_x < dim[1] and h_y < dim[0]:
        ch = frame[h_y, h_x]
        return (int(ch[0]), int(ch[1]), int(ch[2]))
    else:
        return None

def mo(color, strength):
    c1, c2, c3 = color
    strength = strength * 70 + 30
    return (c1*strength/100,
            c2*strength/100,
            c3*strength/100)

def drawHalCircleRounded(image, center, radius, c, s_angle, e_angle, thickness):
    axes = (radius, radius)
    angle = 0
    cv2.ellipse(image, center, axes, angle, s_angle, e_angle, (c[2], c[1], c[0]), thickness)

def displayAvatar(frame, h, pt, ch):
    if pt is not None:
        conf = max(h["full_body_roi_confidence"], h["face_roi_confidence"])
        #hair
        if ch is not None:
            cv2.circle(frame, (pt[0], pt[1] - int(BH_SIZE*0.5) + OFF), int(BH_SIZE*1.2), mo((ch[2], ch[1], ch[0]), conf), -5)
        #face
        cv2.circle(frame, (pt[0], pt[1] + OFF), BH_SIZE, mo((102, 178, 255), conf), -5)


def displayEmotion(frame, h, pt):
    if h['emotion_smiling_degree'] > 0.30:
        rr = h['emotion_smiling_degree']*90

        drawHalCircleRounded(frame, (pt[0], pt[1] + int(BH_SIZE*0.3) + OFF), int(BH_SIZE*0.5), (0, 0, 0), 90-rr, 90+rr, 4)
        return

    if h['emotion_surprise'] > 0.50:
        drawHalCircleRounded(frame, (pt[0], pt[1] + int(BH_SIZE*0.5) + OFF), int(BH_SIZE*0.3), (0, 0, 0), 0, 360, 2)
        return

    if h['emotion_anger'] > 0.40:
        cv2.line(frame, (pt[0] - int(BH_SIZE*0.3), pt[1] - int(BH_SIZE*0.2) + OFF), (pt[0] - int(BH_SIZE*0.6), pt[1] - int(BH_SIZE*0.3) + OFF), (0, 0, 0), 2)
        cv2.line(frame, (pt[0] + int(BH_SIZE*0.3), pt[1] - int(BH_SIZE*0.2) + OFF), (pt[0] + int(BH_SIZE*0.6), pt[1] - int(BH_SIZE*0.3) + OFF), (0, 0, 0), 2)
        drawHalCircleRounded(frame, (pt[0], pt[1] + int(BH_SIZE*1) + OFF), 15, (0, 0, 0), 240, 300, 4)
        return

    if h['emotion_smiling_degree'] < 0.20:
        drawHalCircleRounded(frame, (pt[0], pt[1] + int(BH_SIZE*0.3) + OFF), 15, (0, 0, 0), 60, 120, 4)
        return

def displayGender(frame, h, pt):
    conf = h['gender_confidence']
    if conf > 0.5 and pt is not None:
        logo = LOGOS_MALE_FEMALE[h['gender'] == "female"]
        lx = pt[0] + int(BH_SIZE*1.5)
        ly = pt[1] + OFF - int(BH_SIZE*1)
        if ly+logo.shape[0] < frame.shape[0] and ly > 0 and lx+logo.shape[1] < frame.shape[1] and lx > 0:
            sub = frame[ly:ly+logo.shape[0],lx:lx+logo.shape[1]]
            cv2.addWeighted(sub, 1, logo, conf, 0.0, dst=sub)


def displayGaze(frame, idx, h, pt, f_roi_conf):
    if h['face_roi_confidence'] > f_roi_conf:
        nose = (pt[0], pt[1] + OFF)
        eyel = (pt[0] - int(BH_SIZE*0.5), pt[1] - int(BH_SIZE*0.2) + OFF)
        eyer = (pt[0] + int(BH_SIZE*0.5), pt[1] - int(BH_SIZE*0.2) + OFF)

        theta = - h['head'][0]
        phi = h['head'][1]
        psi = h['head'][2]

        length = 50
        xvec = int(length*(sin(phi)*sin(psi) - cos(phi)*sin(theta)*cos(psi)))
        yvec = int(- length*(sin(phi)*cos(psi) - cos(phi)*sin(theta)*sin(psi)))
        cv2.line(frame, nose, (nose[0]+xvec, nose[1]+yvec), (10, 10, 10), LINETH)

        psi = 0
        theta = - h['gaze'][0]
        phi = h['gaze'][1]


        length = 150
        xvec = int(length*(sin(phi)*sin(psi) - cos(phi)*sin(theta)*cos(psi)))
        yvec = int(- length*(sin(phi)*cos(psi) - cos(phi)*sin(theta)*sin(psi)))
        cv2.line(frame, eyel, (eyel[0]+xvec, eyel[1]+yvec), (132, 70, 39), LINETH)

        xvec = int(length*(sin(phi)*sin(psi) - cos(phi)*sin(theta)*cos(psi)))
        yvec = int(- length*(sin(phi)*cos(psi) - cos(phi)*sin(theta)*sin(psi)))
        cv2.line(frame, eyer, (eyer[0]+xvec, eyer[1]+yvec), (132, 70, 39), LINETH)


def computeConversion(res, events, entities, engaged, stats, animation, g_conf, eng_conf):
    for e in events:
        if e["entity_type"] == "appearance":
            stats.add_engaged(False)

    for idx, h in entities.iteritems():
        if h['gaze_confidence'] > g_conf:
            length = 150
            psi = 0
            theta = - h['gaze'][0]
            phi = h['gaze'][1]
            xvec = int(length*(sin(phi)*sin(psi) - cos(phi)*sin(theta)*cos(psi)))
            yvec = int(- length*(sin(phi)*cos(psi) - cos(phi)*sin(theta)*sin(psi)))
            if xvec*xvec + yvec*yvec < eng_conf:
                if idx not in engaged:
                    engaged.append(idx)
                    stats.add_engaged(True)
                    stats.add_age(h["age"])
                    stats.add_gender(h["gender"])
                    animation.append({"title":"+1 !", "counter":0})

def displayConversion(frame, stats, pt):
    data = stats.engaged()
    tot = data["engaged"] + data["not_engaged"]
    if tot != 0:
        a = 100*data["engaged"]/float(tot)
        b = 100*data["not_engaged"]/float(tot)
        datap = [{"title": "Has looked" + " (" + '%s'%int(data["engaged"]) + ")", "width": a, "color": (221,155,30)},
                 {"title":"Not looked"  + " (" + '%s'%int(data["not_engaged"]) + ")", "width": b, "color": (0, 140, 255)}]
        displayNumber(frame, (pt[0], pt[1] - 150), 60, int(100*data["engaged"]/(data["engaged"]+abs(data["not_engaged"]))), "Engagement", 30)

    data = stats.ages()
    tot = 0
    for key, value in data.iteritems():
        tot += value

    datap = []
    color = [(100,255,100), (100,255,100), (255,0,255), (0,255,255), (255,255,0), (255,100,100), (100,100,255)]
    if tot != 0:
        i = 0
        for key, value in data.iteritems():
            a = 100*value/float(tot)
            datap.append({"title": key, "width": a, "color": color[i]})
            i += 1
        displayPieChartBlock(frame, (pt[0], pt[1]), 40, datap, "Age", 20)


    data = stats.genders()
    tot = 0
    for key, value in data.iteritems():
        tot += value

    datap = []
    color = [(255,128,0), (127,0,255)]
    if tot != 0:
        i = 0
        for key, value in data.iteritems():
            a = 100*value/float(tot)
            datap.append({"title": key, "width": a, "color": color[i]})
            i += 1
        displayPieChartBlock(frame, (pt[0], pt[1] + 200), 40, datap, "Sexe", 20)

def displayAnimation(frame, animation):
    # pprint.pprint(animation)
    for a in animation:
        if a["counter"] < 30:
            if a["title"] == "+1 passing":
                cv2.putText(frame, a["title"],
                            (500, 500 - 15*a["counter"]), cv2.FONT_HERSHEY_SIMPLEX,
                            5, (0, 140, 255), 3)
            elif a["title"] == "+1 !":
                cv2.putText(frame, a["title"],
                            (500, 500 - 25*a["counter"]), cv2.FONT_HERSHEY_SIMPLEX,
                            3, mo((255,255,255),1.0 - 0.002*25*a["counter"]), 5)
            a["counter"] += 1
        else:
            animation.remove(a)

def displayPieChartBlock(frame, pt, size, data, title, thickness):
    textSize = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0];

    cv2.putText(frame, title,
            (int(pt[0] - 0.5*textSize[0]), pt[1] - int(1.5*size)), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2)

    displayPieChart(frame, pt, size, data, thickness)

def displayNumber(frame, pt, size, data, title, thickness):
    textSize = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0];

    cv2.putText(frame, title,
            (int(pt[0] - 0.5*textSize[0]), pt[1] - int(1.5*size)), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2)

    ss = str(data) + "%"
    textSize = cv2.getTextSize(ss, cv2.FONT_HERSHEY_SIMPLEX, 3, 2)[0];
    cv2.putText(frame, ss,
            (int(pt[0] - 0.5*textSize[0]), pt[1]), cv2.FONT_HERSHEY_SIMPLEX,
            3, (255, 255, 255), 2)



def displayPieChart(frame, pt, size, data, thickness):
    axes = (size, size)
    alpha = 0.0
    s_angle = alpha
    for cat in data:
        if cat["width"] > 0:
            e_angle = s_angle + 360*cat["width"]/100.0
            cv2.ellipse(frame, pt, axes, alpha, s_angle, e_angle, cat["color"], thickness)
            mid_angle = 0.5*(e_angle + s_angle)
            s_angle = e_angle
            tg = rotateLine(pt[0]+size+50, pt[1], pt[0], pt[1], -3.1415/180.0*mid_angle)
            tt = cat["title"]

def blur(frame, p1, p2, rect_color=None, thickness=1):
    x1, y1 = p1
    x2, y2 = p2
    sub = frame[y1:y2, x1:x2]
    cv2.GaussianBlur(sub, (31,31), 130, dst=sub)
    if rect_color:
        cv2.rectangle(frame, (x1, y1), (x2, y2), rect_color, thickness=thickness)
