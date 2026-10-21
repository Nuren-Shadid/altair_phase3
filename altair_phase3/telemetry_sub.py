import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

# calls a child func to inherit from the Node 
class MissionControlMonitor(Node):
    def __init__(self):
    	# calls the parent and provides a unique name to the Node 
        super().__init__('mission_control_monitor')
        # creates a subscription obj listening to a topic for a string type msg
        self.subscription = self.create_subscription(
            String, '/rover_telemetry', self.listener_callback, 10)
	
    # executes every time a new message (msg) is received
    def listener_callback(self, msg):
    	# Takes the raw string inside msg.data 
	# and parses it back into a Python dictionary
        data = json.loads(msg.data)
        self.get_logger().info(
            f"Battery: {data['battery_pct']}% | "
            f"Temp: {data['temperature_c']} C | "
            f"Speed: {data['wheel_speed_mps']} m/s | "
            f"Elapsed: {data['elapsed_s']} s"
        )
        # Low battery warning 
        if data['battery_pct'] < 25.0:
            self.get_logger().warn("LOW BATTERY WARNING!")

def main(args=None):
    rclpy.init(args=args)
    # creates a custom node 
    node = MissionControlMonitor()
    # Keeps the node alive and continuously listening for incoming messages
    rclpy.spin(node)
    # Cleanly destroys the node and shuts down communication when the program is manually stopped
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
