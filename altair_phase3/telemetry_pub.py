import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

# TelemetryPublisher(child) inheriting all functionalities of a ROS 2 Node(parent class)
class TelemetryPublisher(Node):
    def __init__(self):
    	# calls the parent and gives the node a Unique name
        super().__init__('mars_telemetry_publisher')
        # Creates a publisher(built-in) obj sending msg into a (virtual) topic
        self.publisher_ = self.create_publisher(String, '/rover_telemetry', 10)
        # creates a timer to call a func every 1 sec
        self.timer = self.create_timer(1.0, self.timer_callback)

	# initial state 
        self.battery = 100.0
        self.temperature = 25.0
        self.start_time = self.get_clock().now()
        self.count = 0

    def timer_callback(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        # Simulate battery depletion and temperature rise
        self.battery -= 2.0
        self.temperature += 0.5

	# telemetry dict
        data = {
            "battery_pct": round(self.battery, 2),
            "temperature_c": round(self.temperature, 2),
            "wheel_speed_mps": 0.3,
            "elapsed_s": round(elapsed, 1)
        }

        msg = String()
        # converting data to string to output cleanly
        msg.data = json.dumps(data)
        self.publisher_.publish(msg)
        # Calling ROS 2's built in logging system to print info from a dict
        self.get_logger().info(f"Count: {self.count}, Published: {msg.data}")
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = TelemetryPublisher()
    # keeps running the code continuously 
    rclpy.spin(node)
    # stops the node manually or if script ran directly 
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
