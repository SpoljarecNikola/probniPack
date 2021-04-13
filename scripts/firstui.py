#!/usr/bin/env python3
import rospy
import sys
import numpy as np
from nav_msgs.msg import Odometry
from PIL import Image as PILImage, ImageFont,ImageDraw
from sensor_msgs.msg import Image as ROSImage
#http://docs.ros.org/en/api/sensor_msgs/html/msg/Image.html
class PrintPosition():
    def __init__ (self, frequency): 
        self.frequency = int(frequency) 
        self.image_pub = rospy.Publisher('/uav/gui', ROSImage, queue_size=1) 
        #https://answers.ros.org/question/243855/how-do-publishersubscriber-message-queues-work/
        
        rospy.init_node('drone_odom', anonymous=True)
        self.odom_sub = rospy.Subscriber('/firefly/ground_truth/odometry', Odometry, self.odom_callback)
        
        self.odom_msg_recv = False
        
        # ROS Image
        self.ros_img = ROSImage()
        
    def odom_callback(self, data):
        self.odom_msg_recv = True
        self.odom=Odometry()
        height=str(data.pose.pose.position.z)
        pil_img = PrintPosition.draw_gui(height)
        self.ros_img = PrintPosition.convert_pil_to_ros_img(self, pil_img)

    @staticmethod
    def convert_pil_to_ros_img(self, img):
        img=img.convert('RGB')
        msg = ROSImage()
        stamp = rospy.Time.now()
        msg.height = img.height
        msg.width = img.width
        msg.encoding = "rgb8"
        msg.is_bigendian = False
        msg.step = 3 * img.width
        msg.data = np.array(img).tobytes()
        return msg 

    def run(self):
        rate = rospy.Rate(self.frequency)
        print("Entered run")
        while not rospy.is_shutdown():
            rate.sleep()
            print("running")
            
            # Publish saved msg 
            if self.odom_msg_recv:
                self.image_pub.publish(self.ros_img)

    @staticmethod
    def draw_gui(drone_height):
        pil_img=PILImage.new("RGBA", (900,900), 'white')
        font=ImageFont.load_default()
        draw=ImageDraw.Draw(pil_img)
        draw.text((0,150), drone_height, (0,0,0), font=font)
        return pil_img

if __name__ == '__main__':
    try:
        p = PrintPosition(sys.argv[1])
        print("Here")
        p.run()
    except rospy.ROSInterruptException: pass