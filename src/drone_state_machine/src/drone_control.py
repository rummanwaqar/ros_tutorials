#!/usr/bin/env python

import rospy
import smach
import smach_ros
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from smach import CBState


@smach.cb_interface(input_keys=[], output_keys=[], outcomes=['finished', 'failed'])
def takeoff_cb(user_data):
    rospy.loginfo('Taking off')
    takeoff_topic = rospy.Publisher('/drone/takeoff', Empty, queue_size=1)
    rospy.sleep(1)
    msg = Empty()
    result = takeoff_topic.publish(msg)
    if result == None:
        return 'finished'
    else:
        return 'failed'


@smach.cb_interface(input_keys=[], output_keys=[], outcomes=['finished', 'failed'])
def land_cb(user_data):
    rospy.loginfo('Landed')
    land_topic = rospy.Publisher('/drone/land', Empty, queue_size=1)
    rospy.sleep(1)
    msg = Empty()
    result = land_topic.publish(msg)
    if result == None:
        return 'finished'
    else:
        return 'failed'


@smach.cb_interface(input_keys=['lspeed'], output_keys=[], outcomes=['finished', 'failed'])
def move_cb(user_data):
    rospy.loginfo('Moving')
    move_topic = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    rospy.sleep(1)
    vel = Twist()
    vel.linear.x = user_data.lspeed
    result = move_topic.publish(vel)
    rospy.sleep(2)
    if result == None:
        return 'finished'
    else:
        return 'failed'


if __name__ == '__main__':
    rospy.init_node('drone_state_machine')

    sm = smach.StateMachine(outcomes=['completed'])
    sm.userdata.lspeed = 0.5

    with sm:
        smach.StateMachine.add('TAKEOFF', CBState(takeoff_cb),
                               {'finished': 'MOVE', 'failed': 'completed'})
        smach.StateMachine.add('MOVE', CBState(move_cb),
                               {'finished': 'LAND', 'failed': 'completed'})
        smach.StateMachine.add('LAND', CBState(land_cb),
                               {'finished': 'completed', 'failed': 'completed'})

    outcome = sm.execute()
