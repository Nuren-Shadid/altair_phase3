import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Bool
from std_srvs.srv import Trigger


class MissionNode(Node):
    def __init__(self):
        super().__init__('mission_node')
        # the ONLY publisher to /turtle1/cmd_vel, providing movement output
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # Subscribers, Pose gives current position, Bool checks for obstacles
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_cb, 10)
        self.block_sub = self.create_subscription(Bool, '/field_blocked', self.block_cb, 10)
        # Service, Trigger is the service type, '/resume_mission' is its name, and self.resume_cb is the function ROS runs when someone presses it.
        self.resume_srv = self.create_service(Trigger, '/resume_mission', self.resume_cb)
        self.timer = self.create_timer(0.1, self.control_loop)

        # Initial state
        self.state = 'NAVIGATING'
        self.current_pose = None	# not started yet
        self.blocked = False	
        self.targets = [(8.0, 5.5), (8.0, 8.0), (5.5, 5.5)]
        self.target_index = 0	# 0 index represents first target

    # calls this each time the turtle reports its position.
    def pose_cb(self, msg):
        self.current_pose = msg

    # calls this each time a blocked message arrives.
    def block_cb(self, msg):
        self.blocked = msg.data

    # Resume and return the response
    def resume_cb(self, request, response):
    	# if not paused and no obstacles, the mission is resumed (if not just started) 
        if self.state == 'PAUSED' and not self.blocked and self.current_pose is not None:
            self.state = 'NAVIGATING'
            response.success = True
            response.message = 'Mission resumed.'
        # Response if obstacle true
        else:
            response.success = False
            response.message = 'Cannot resume: blocked, not paused, or no pose.'
        return response

    def control_loop(self):
        if self.current_pose is None:
            return  # wait for first pose

        if self.state == 'PAUSED':
            self.publish_stop()
            return

        if self.state == 'DONE':
            self.publish_stop()
            return

        # NAVIGATING
        # if blocked true
        if self.blocked:
            self.state = 'PAUSED'
            self.publish_stop()
            return

	# if all targets hit print DONE 
        if self.target_index >= len(self.targets):
            self.state = 'DONE'
            self.publish_stop()
            self.get_logger().info('DONE')
            return

	# Sets the targets and current location
	# theta is the direction the turtle is facing, in radians
        target_x, target_y = self.targets[self.target_index]
        x = self.current_pose.x
        y = self.current_pose.y
        theta = self.current_pose.theta

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)

	# Arrives at one target and stops to move to the next target
        if distance < 0.3:
            self.get_logger().info(f'Arrived at target {self.target_index}')
            self.target_index += 1
            self.publish_stop()
            return

	# Direction change
        goal_theta = math.atan2(dy, dx)
        heading_error = math.atan2(math.sin(goal_theta - theta), math.cos(goal_theta - theta))


        cmd = Twist()
        if abs(heading_error) > 0.3:
            # Turn in place first if heading error too large
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(2.0 * heading_error, 1.5), -1.5)
        else:
            # Drive and correct heading
            cmd.linear.x = min(0.8 * distance, 1.0)
            cmd.angular.z = max(min(2.0 * heading_error, 1.5), -1.5)
        self.cmd_pub.publish(cmd)

    # Output/Publish 
    def publish_stop(self):
        self.cmd_pub.publish(Twist())  # all zeros


def main(args=None):
    rclpy.init(args=args)
    node = MissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
