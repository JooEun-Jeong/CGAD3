#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32MultiArray

import sys, select, termios, tty

ROSCAR_MAX_ACCELL_VEL = 255
ROSCAR_MAX_STEERING_VEL = 180

ROSCAR_MIN_ACCELL_VEL = 0
ROSCAR_MIN_STEERING_VEL = 0

msg = """
Control Your ROSCAR!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease accell velocity 
a/d : increase/decrease steering velocity 

space key, s : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)
    while True:
	key = getKey()
	print("key :", key)

