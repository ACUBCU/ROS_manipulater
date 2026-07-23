import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped

class M_pub(Node):
    def __init__(self):
        super().__init__("massage_pub")

        transformation = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        self.tf_static_broadcaster = StaticTransformBroadcaster(self)
        self.make_transforms(transformation)

    def make_transforms(self, transformation):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "world"
        t.child_frame_id = "map"
        t.transform.translation.x = transformation[0]
        t.transform.translation.y = transformation[1]
        t.transform.translation.z = transformation[2]
        t.transform.rotation.x = transformation[3]
        t.transform.rotation.y = transformation[4]
        t.transform.rotation.z = transformation[5]
        t.transform.rotation.w = transformation[6]

        self.tf_static_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = M_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("tf test")

if __name__ == "__main__":
    main()
