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

import cv2
import numpy as np
import StringIO
import datetime
import pytz
import angus
import angus_display as ad
import stats as st


def f(stream_index, width, height):

    camera = cv2.VideoCapture(stream_index)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, int(width))
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, int(height))
    camera.set(cv2.cv.CV_CAP_PROP_FPS, 10)

    if not camera.isOpened():
        print("Cannot open stream of index {}".format(stream_index))
        exit(1)

    print("Video stream is of resolution {} x {}".format(camera.get(3), camera.get(4)))

    stats = st.Stats("stats.json")
    animation = []
    engaged = []

    conn = angus.connect()
    service = conn.services.get_service("scene_analysis", version=1)
    service.enable_session()

    while camera.isOpened():
        ret, frame = camera.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, buff = cv2.imencode(".jpg", gray,  [cv2.IMWRITE_JPEG_QUALITY, 80])
        buff = StringIO.StringIO(np.array(buff).tostring())

        t = datetime.datetime.now(pytz.utc)
        job = service.process({"image": buff,
                               "timestamp" : t.isoformat(),
                               "camera_position": "facing",
                               "sensitivity": {
                                   "appearance": 0.7,
                                   "disappearance": 0.7,
                                   "age_estimated": 0.4,
                                   "gender_estimated": 0.5,
                                   "focus_locked": 0.9,
                                   "emotion_detected": 0.4,
                                   "direction_estimated": 0.8
                               }
        })

        res = job.result

        events = res["events"]
        entities = res["entities"]

        for idx, h in entities.iteritems():
            pt = ad.displayAge(frame, idx, h, 0.50, 0.35)
            ch = ad.displayHair(frame, idx, h)
            ad.displayAvatar(frame, h, pt, ch)
            ad.displayEmotion(frame, h, pt)
            ad.displayGender(frame, h, pt)
            ad.displayGaze(frame, idx, h, pt, 0.50)

        panel = ((width - 180, 40), (width-20, height - 40))
        ad.blur(frame, panel[0], panel[1], (255, 255, 255), 2)
        ad.computeConversion(res, events, entities, engaged, stats, animation, 0.5, 500)
        ad.displayConversion(frame, stats, (width - 100, int(0.3*height)))
        ad.displayAnimation(frame, animation)
        ad.display_logo(frame, 20, height - 60)

        cv2.imshow('window', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stats.save()
            break

    service.disable_session()

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    ### Web cam index might be different from 0 on your setup.
    ### To grab a given video file instead of the host computer cam, try:
    ### main("/path/to/myvideo.avi")
    f(0, 640, 480)
