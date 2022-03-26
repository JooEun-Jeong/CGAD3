#!/usr/bin/env python # 12 / 18 20191665 Á¤¿¬¼ö

import rospy, time, cv2, keyboard, sys, select, termios, tty

from linedetector import LineDetector
from obstacledetector import ObstacleDetector
from motordriver import MotorDriver
from detect1 import DetectSpot, tempbell

class AutoDrive:

    def __init__(self):
        rospy.init_node('xycar_driver')
        self.line_detector = LineDetector('/usb_cam/image_raw')
        self.obstacle_detector = ObstacleDetector('/ultrasonic')
        self.driver = MotorDriver('/xycar_motor_msg')
        self.detector = DetectSpot('/usb_cam/image_raw')
	self.beforeLeft = 0
	self.beforeRight = 0 


    def trace(self):
        obs_l, obs_m, obs_r = self.obstacle_detector.get_distance() #ultrasonic
        line_l, line_r = self.line_detector.detect_lines() #image_raw
        self.line_detector.show_images(line_l, line_r) #show
        angle, speed = self.steer(line_l, line_r)
        #self.accelerate(angle, obs_l, obs_m, obs_r)
	firstDecision = self.detector.detectGreen()	
			
	if firstDecision == 0:
	    time.sleep(1)
	    self.driver.drive(90, 90)
	    time.sleep(5)
	else:        
	    self.driver.drive(angle + 90, speed + 90) #drive

    def steer(self, left, right):
	global before
        after=time.time()
        global angle

	
        if left != 0 and right != 0:
            if abs(left) < abs(right) and abs(abs(left) - abs(right)) < 0.1:
	    	angle = -13
		speed = 50
	    elif abs(left) > abs(right) and abs(abs(left) - abs(right)) < 0.1:
		angle = 13
		speed = 50
	    else:
		angle = 0
		speed = 60
#right
        elif right == 0 and left != 0:
	    if abs(left) > 0.50:
		angle = 13
		speed = 50
	    else:
            	angle = 50
             	speed = 50

#left
        elif left == 0 and right != 0:
	    if abs(right) > 0.50:
		angle = -13
		speed = 50
	    else:            	
		angle = -50
            	speed = 50

        else:
	    if self.beforeLeft == 0 and self.beforeRight != 0:
	        self.beforeLeft = left
	        self.beforeRight = right
	        return -50, 50
	    elif self.beforeRight != 0 and self.beforeLeft == 0:
	        self.beforeRight = right
	        self.beforeLeft = left
	        return 50, 50

            angle = 0
            speed = 40
            
	self.beforeLeft = left
	self.beforeRight = right
        return angle,speed

    '''def accelerate(self, angle, left, mid, right):
        if min(left, mid, right) < 50:
            speed = 0
        elif angle < -20 or angle > 20:
            speed = 20
        else:
            speed = 30
        return speed'''

    def exit(self):
        print('finished')
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
    car = AutoDrive()
    time.sleep(3)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
	ret = cv2.waitKey(1)
        settings = termios.tcgetattr(sys.stdin)
	key = getKey()
	if key == 'a':
	    ret = 1
	    tempbell(ret)
	elif key == 'p':
	    ret = -1
	    tempbell(ret)
	    break	
	car.trace()
        rate.sleep()
    rospy.on_shutdown(car.exit)

