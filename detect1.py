#12/17 юсаж©о
import cv2, time
import rospy
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


tempbellT = False

class DetectSpot:

    def __init__(self,topic):
        # Initialize various class-defined attributes, and then... 
        self.cam_img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)
        self.bridge = CvBridge()
	self.value_threshold = 150

	self.image_width = 640

	self.scan_width, self.scan_height = 200, 240

	self.lmid, self.rmid = self.scan_width, self.image_width - self.scan_width

	self.roi_vertical_pos = 0
	
	self.red_pixel_cnt_threshold = 0.02 * 160 * 320
        
	self.redWidth = 0
	self.greenWidth = 0
        self.green_pixel_cnt_threshold = 0.20 * 160 * 320
	rospy.Subscriber(topic, Image, self.conv_image)
	

    def conv_image(self, data):
	
        self.cam_img = self.bridge.imgmsg_to_cv2(data, 'bgr8')

	self.roi = self.cam_img[50:320, 320:]
	self.roi = cv2.GaussianBlur(self.roi, (5, 5), 0)
	hsv = cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
	lowerGreen = np.array([50,100,0], dtype = np.uint8)
	upperGreen = np.array([85,255,255], dtype=np.uint8)


	lowerRed1 = np.array([0,140,0], dtype = np.uint8)
	upperRed1 = np.array([15,255,255], dtype=np.uint8)
	
	lowerRed2 = np.array([160,140,0], dtype = np.uint8)
	upperRed2 = np.array([180,255,255], dtype=np.uint8)
	
	
	maskGreen = cv2.inRange(hsv, lowerGreen, upperGreen)
	maskRed1 = cv2.inRange(hsv, lowerRed1, upperRed1)
	maskRed2 = cv2.inRange(hsv, lowerRed2, upperRed2)
	
	retGreen = cv2.bitwise_and(self.roi, self.roi, mask=maskGreen)
	redMask = cv2.bitwise_or(maskRed1, maskRed2)	
	retRed = cv2.bitwise_and(self.roi, self.roi, mask = redMask)

	Red = cv2.cvtColor(retRed, cv2.COLOR_BGR2GRAY)
	Green = cv2.cvtColor(retGreen, cv2.COLOR_BGR2GRAY) 
	
	ret, self.finalRed = cv2.threshold(Red, 10, 255, cv2.THRESH_BINARY)
	ret, self.finalGreen = cv2.threshold(Green, 10, 255, cv2.THRESH_BINARY)

        gnum, glabels, gstats, gcentroids = cv2.connectedComponentsWithStats(self.finalGreen)
	rnum, rlabels, rstats, rcentroids = cv2.connectedComponentsWithStats(self.finalRed)
	
	glist = []
	rlist = []

	for i in range(gnum):
	    
	    if i < 1:
	        continue
	    
	    flag = 1
	    area = gstats[i, cv2.CC_STAT_AREA]
	    center_x = int(gcentroids[i, 0])
	    center_y = int(gcentroids[i, 1])
	    left = gstats[i, cv2.CC_STAT_LEFT]
	    top = gstats[i, cv2.CC_STAT_TOP]
	    width = gstats[i, cv2.CC_STAT_WIDTH]
	    height = gstats[i, cv2.CC_STAT_HEIGHT]
	    
	    if width < 100:
	        continue
	    glist.append(width)

	for i in range(rnum):
	
	    if i < 1:
	        continue
	    
	    flag = 1
	    area = rstats[i, cv2.CC_STAT_AREA]
	    center_x = int(rcentroids[i, 0])
	    center_y = int(rcentroids[i, 1])
	    left = rstats[i, cv2.CC_STAT_LEFT]
	    top =rstats[i, cv2.CC_STAT_TOP]
	    width = rstats[i, cv2.CC_STAT_WIDTH]
	    height = rstats[i, cv2.CC_STAT_HEIGHT]
	    rlist.append(width)
	    
	if len(rlist) != 0:
	    self.redWidth = max(rlist)
	if len(glist) != 0:	
	    self.greenWidth = max(glist)
	print(tempbellT)
#	print('r',self.redWidth)
#	print('g',self.greenWidth)
#	gnum, glabels, gstats, hcentroids = cv2.connectedComponentsWith(finalGreen)

#	self.view = cv2.cvtColor(self.maskRed1, cv2.COLOR_GRAY2BGR)


#	cv2.imshow("origin", self.cam_img)
#	cv2.imshow("view", self.finalRed)


    def detectGreen(self):

	global tempbellT
	if (self.greenWidth >110 and tempbellT == True) or  (self.greenWidth >110 and self.redWidth>10):
	    tempbellT = False
	    return 0
	else:
	    return -1
def tempbell(bell):
    global tempbellT
    print("input key : ", bell)
    if bell == 1:
	tempbellT = True
	#cv2.imshow('green', self.finalGreen)
    elif bell == -1:
	tempbellT = False



