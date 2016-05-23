# -*- coding=utf-8 -*-

import cv2
import numpy as np

class VideoProcessor:

    def __init__(self):
        self.source = None
        self.capture = None
        self.processor = None
        self.stop = False
        self.show_input = True
        self.show_output = True
        self.delay = 10
        self.frame_count = 0
        self.frame = None
        self.gray = None


    def set_input(self, n, height=None, width=None):
        self.source = n
        self.capture = cv2.VideoCapture(n)
        if height is not None and width is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        return self.capture.isOpened()


    def set_frame_processor(self, processor):
        self.processor = processor


    def save(self, image, name = None):
        if os.path.exists(self.source):
            name = os.path.dirname(self.source)
            name = os.path.join(name, 'frame-{}.bmp'.format(self.frame_count))
            name = 'frame-{}.bmp'.format(self.frame_count)
            cv2.imwrite(name, image)


    def process_keyevent(self):
        key = cv2.waitKey(self.delay)
        if key == -1:
            return

        if key == ord('e') or key == 'e':
            self.stop = True
        elif key == ord('s'):
            self.save(self.frame)


    def print_cap(self):
        prop = [
            cv2.CAP_PROP_FRAME_COUNT,
            cv2.CAP_PROP_FRAME_HEIGHT,
            cv2.CAP_PROP_FRAME_WIDTH,
            cv2.CAP_PROP_APERTURE,
            cv2.CAP_PROP_AUTO_EXPOSURE,
            cv2.CAP_PROP_AUTOFOCUS,
            cv2.CAP_PROP_BACKLIGHT,
            cv2.CAP_PROP_BRIGHTNESS,
            cv2.CAP_PROP_CONTRAST,
            cv2.CAP_PROP_EXPOSURE,
            cv2.CAP_PROP_GAIN,
            cv2.CAP_PROP_GAMMA,
            cv2.CAP_PROP_SATURATION,
            cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,
            cv2.CAP_PROP_WHITE_BALANCE_RED_V
        ]
        print('camera cap:' + '*' * 10)
        msg = []
        for i in prop:
            val = self.capture.get(cv2.CAP_PROP_APERTURE)
            msg.append(str(val))
        print('\n'.join(msg))


    def run(self):

        self.stop = False
        self.frame_count = 0

        while not self.stop and self.capture.isOpened():

            ret, self.frame = self.capture.read()

            self.print_cap()

            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            if self.show_input:
                cv2.imshow('input', self.frame)

            if self.processor:
                im_output = self.processor.process(self.frame, self.gray)

                if self.show_output:
                    cv2.imshow('output', im_output)

            self.process_keyevent()

            self.frame_count += 1

        cv2.destroyAllWindows()


class FrameProcessor:

    def __init__(self):
        pass

    def process(self, frame, gray):
        return frame


if __name__ == '__main__':

    frameprocessor = FrameProcessor()
    processor = VideoProcessor()
    processor.set_input(0)
    processor.delay = 1
    processor.show_output = False
    processor.set_frame_processor(frameprocessor)
    processor.run()