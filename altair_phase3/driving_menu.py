import sys
import termios
import tty
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Each pattern is a list of steps containing values in a tuple: (forward_speed, turn_speed, duration_in_seconds)
PATTERNS = {
    # Patrol: forward 3 s, then turn about 180 degrees 
    'P': [(0.5, 0.0, 3.0), (0.0, 1.57, 2.0)],	# 1.57rad/90degrees for 2sec = 90*2 = 180 turn
    # Rectangle: long side, turn 90, short side, turn 90, repeated twice
    'R': [
        (0.5, 0.0, 2.0), (0.0, 1.57, 1.0),
        (0.5, 0.0, 1.0), (0.0, 1.57, 1.0),
        (0.5, 0.0, 2.0), (0.0, 1.57, 1.0),
        (0.5, 0.0, 1.0), (0.0, 1.57, 1.0),
    ],
    # Zigzag: forward, left, forward, right, forward
    'Z': [
        (0.5, 0.0, 1.5), (0.0, 1.57, 0.8),
        (0.5, 0.0, 1.5), (0.0, -1.57, 0.8),
        (0.5, 0.0, 1.5),
    ],
}


class DrivingMenu(Node):
    def __init__(self):
        super().__init__('driving_menu_node')
        # creates a publisher sending Twist msg type to the topic
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz

	# Initial state
        self.state = 'IDLE'
        self.step = 0
        self.step_start_time = 0.0

        # Saves the terminal stream ID so python knows which terminal is called 
        self.fd = sys.stdin.fileno()
        # Saves terminal settings so main() can restore them on exit (clean exit) 
        self.old_settings = termios.tcgetattr(self.fd)

	# Starts a background thread running a function
	# Setting daemon=True makes sure the thread shuts on program exit
        self.key_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.key_thread.start()
 
    def restore_terminal(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def keyboard_listener(self):
    	# switches the terminal to cbreak mode
    	# each key is delivered immediately, so we don't need to press Enter
        tty.setcbreak(self.fd)  
        # While ROS running, wait until a key pressed and convert to uppercase
        while rclpy.ok():
        
            ch = sys.stdin.read(1).upper()
            # Any other key is ignored, doesnt crash the program
            if ch in ('P', 'R', 'Z', 'Q'):
                self.get_logger().info(f'Command received: {ch}')
                if ch == 'Q':
                    self.send_stop()
                    rclpy.shutdown()
                    break
                # If not Q then start pattern with arg=ch (input)
                self.start_pattern(ch)

    def start_pattern(self, pattern_char):
    	# Stops and start a new pattern, step=0
        self.send_stop()
        self.step = 0
        self.step_start_time = self.get_clock().now().nanoseconds / 1e9
        self.state = pattern_char  # set LAST so the timer never sees a half-reset state

    def control_loop(self):
        if self.state == 'IDLE':
            return
	
	# This looks up the current pattern's List* of steps in the dictionary
        sequence = PATTERNS[self.state]
        if self.step >= len(sequence):
            self.send_stop()
            self.state = 'IDLE'
            return

        current_time = self.get_clock().now().nanoseconds / 1e9
        elapsed = current_time - self.step_start_time

	# Sets values for the current step
        lin, ang, duration = sequence[self.step]
        # Every tick, we send the speed for the current step, so movement in continuous
        self.send_twist(lin, ang)
        # If all steps not finished, runs a step until its duration
        if elapsed > duration:
            self.send_stop()
            self.step += 1
            self.step_start_time = current_time

    def send_twist(self, linear_x, angular_z):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publisher_.publish(msg)

    def send_stop(self):
        self.send_twist(0.0, 0.0)


def main(args=None):
    # Starts ROS and builds the node 
    rclpy.init(args=args)
    node = DrivingMenu()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    # Always restores the terminal to default state
    finally:
        node.restore_terminal()
        node.destroy_node()
        if rclpy.ok():  # avoid shutting down twice
            rclpy.shutdown()


if __name__ == '__main__':
    main()
    
