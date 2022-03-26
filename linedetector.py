#12/19 °­±â¹ü
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import time
import math

class LineDetector:

    def __init__(self, topic):
		
	self.left, self.right = -0.4, 0.4

        # Initialize various class-defined attributes, and then... 
        self.cam_img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)
        self.bridge = CvBridge()
        rospy.Subscriber(topic, Image, self.conv_image)

    def roi(self,img, vertices):
	# blank mask:
	mask = np.zeros_like(img)
	# fill the mask
	cv2.fillPoly(mask, vertices, 255)
	# now only show the area that is the mask
	masked = cv2.bitwise_and(img, mask)
	return masked


    def conv_image(self, data):
	
        self.cam_img = self.bridge.imgmsg_to_cv2(data, 'bgr8')

        vertices = np.array([[(0,380),(640,380),(640,260), (0,260)]], dtype=np.int32)


        processed_img = self.roi(self.cam_img, vertices)
        hsv = cv2.cvtColor(processed_img, cv2.COLOR_BGR2HSV)
        blur = cv2.GaussianBlur(hsv, (3, 3), 0)
        self.edges = cv2.Canny(blur, 70, 210)
	

    def detect_lines(self):
       
        cdst = cv2.cvtColor(self.edges, cv2.COLOR_GRAY2BGR)
	cdsp = np.copy(cdst)

        lines = cv2.HoughLinesP(self.edges, 1, np.pi / 180, 100, None, 50, 8)

        if lines is not None:
	    lcnt = 0
	    rcnt = 0
	    totalLeft, totalRight = 0, 0
            for i in range(0, len(lines)):
		l = lines[i][0]
                if l[1] == l[3]:
                    continue
                # print (abs(l[3] - l[1]), abs(l[2] - l[0]))
                slope = np.polyfit((l[0] , l[2]),(l[1] , l[3]), 1)
                simpleSlope = round(slope[0],2)
		cv2.line(cdsp, (l[0], l[1]), (l[2], l[3]), (0, 255, 255), 3, cv2.LINE_AA)
		if abs(simpleSlope) >= 1:
		    continue
  		if simpleSlope < 0:
		    lcnt += 1
		    totalLeft += simpleSlope			
		else:
		    rcnt += 1
		    totalRight += simpleSlope
	    else:
		#cv2.imshow("Detected Lines (in green) - Standard Hough Line Transform",cdsp)
		#cv2.waitKey(1)                
		if lcnt == 0 and rcnt != 0:
		    self.left = 0
		    self.right = totalRight / rcnt
	    	    return self.left, self.right
		elif rcnt == 0 and lcnt != 0:
		    self.right = 0
		    self.left = totalLeft / lcnt
		    return self.left, self.right
		else:
		    return -0.4, 0.4
        else:
	#    cv2.imshow("Detected Lines (in green) - Standard Hough Line Transform",cdsp)
	    return 0, 0

        
	

    def show_images(self, left, right):
	
	pass
		
	
        

