import cv2
from functools import partial

def set_prop(cap, prop_name, val):
  prop = getattr(cv2, prop_name)
  ret = cap.set(prop, val)
  new_val = cap.get(prop)
  print(f'<{prop_name.ljust(40)}> {val} => {new_val} {ret}')




cap = cv2.VideoCapture(1)
for field in dir(cv2):
  if field.startswith('CAP_PROP'):
    val = None
    try:
      val = cap.get(getattr(cv2, field))
    except Exception as e:
      val = str(e)
    if val == -1.0:
      print(f'{field.ljust(40)}: {val}')
'''
CAP_PROP_AUTOFOCUS                      : 0.0
CAP_PROP_BACKEND                        : 1400.0
CAP_PROP_BACKLIGHT                      : 0.0
CAP_PROP_BRIGHTNESS                     : 0.0
CAP_PROP_CONTRAST                       : 128.0
CAP_PROP_CONVERT_RGB                    : 1.0
CAP_PROP_FOCUS                          : 10.0
CAP_PROP_FOURCC                         : 20.0
CAP_PROP_FPS                            : 30.0
CAP_PROP_FRAME_HEIGHT                   : 480.0
CAP_PROP_FRAME_WIDTH                    : 640.0
CAP_PROP_GAIN                           : 0.0
CAP_PROP_GAMMA                          : 100.0
CAP_PROP_HUE                            : 0.0
CAP_PROP_MODE                           : 0.0
CAP_PROP_POS_FRAMES                     : 0.0
CAP_PROP_POS_MSEC                       : 0.0
CAP_PROP_SAR_DEN                        : 1.0
CAP_PROP_SAR_NUM                        : 1.0
CAP_PROP_SATURATION                     : 100.0
CAP_PROP_SHARPNESS                      : 25.0
CAP_PROP_TEMPERATURE                    : 4500.0
'''

PROP_NAME = 'CAP_PROP_TEMPERATURE'
PROP = getattr(cv2, PROP_NAME)
def callback(p, x):
  set_prop(cap, p, x)

cv2.namedWindow('frame')
props = []
for field in dir(cv2):
  if field.startswith('CAP_PROP'):
    val = cap.get(getattr(cv2, field))
    if val == -1.0:
      props.append(field)
i = 1
_props = props[5 * i: 5 * (i+1)]
for _prop in _props:
  title = _prop.replace('CAP_PROP_', '')
  cv2.createTrackbar(title, 'frame', 0, 255, partial(callback, _prop))

while True:
  ret, im = cap.read()
  cv2.imshow('frame', im)
  key = cv2.waitKey(1)
  if key == ord('q'):
    break
cap.release()
cv2.destroyAllWindows()
