"""MoveItPy로 OpenManipulator-X의 arm과 gripper를 제어한다."""

import os
import sys
import time
import math

import rclpy
from geometry_msgs.msg import Pose
from moveit.core.kinematic_constraints import construct_joint_constraint
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy
from moveit_msgs.msg import AttachedCollisionObject, CollisionObject
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


class OpenManipulatorMoveItNode(Node):
    def __init__(self):
        super().__init__("open_manipulator_controller")
        self.moveit = MoveItPy(node_name="open_manipulator_moveit_py")
        self.arm = self.moveit.get_planning_component("arm")
        self.gripper = self.moveit.get_planning_component("gripper")
        self.planning_scene_monitor = self.moveit.get_planning_scene_monitor()
        
        self.object_id = "grasped_box"
        self.attach_link = "end_effector_link"
        self.touch_links = ["end_effector_link", "gripper_left_link", "gripper_right_link"]

        self.get_logger().info("RViz2 통신 연결 대기 중...")
        time.sleep(1.5)

        self.setup_environment()
        self.move_manipulator()

    def setup_environment(self):
        self.add_box_object("base_table", [0.8, 0.8, 0.02], [0.0, 0.0, -0.05])

        partition_length = 0.2
        partition_height = 0.4  
        radius = 0.4  
        
        for i in range(6):
            angle = math.radians(i * 60 + 30)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            qw = math.cos(angle / 2.0)
            qz = math.sin(angle / 2.0)
            
            self.add_box_object(
                f"partition_{i+1}", 
                [partition_length, 0.02, partition_height], 
                [x, y, 0.15], 
                [0.0, 0.0, qz, qw]
            )

    def move_manipulator(self):
        target_radius = 0.3
        coords = []
        
        # 바닥에 생성될 가상 물체의 XYZ 좌표값 연산
        for i in range(6):
            angle = math.radians(i * 60)
            if angle > math.pi:
                angle -= 2 * math.pi
                
            x = target_radius * math.cos(angle)
            y = target_radius * math.sin(angle)
            coords.append([x, y, 0.065])

        # SRDF에 정의된 구역 및 회피 지점 문자열 배열
        zone_poses = [
            "zone_1", "zone_2", "zone_3", "zone_4", "zone_5", "zone_6"
        ]

        via_poses = [
            "via_1", "via_2", "via_3", "via_4", "via_5", "via_6"
        ]

        # 최초 시작 위치 (Zone 1, 0도)에 물체 생성
        self.add_box_object(self.object_id, [0.035, 0.035, 0.08], coords[0])
        
        self.plan_and_execute(self.moveit, self.arm, "init", "arm_controller")
        self.plan_and_execute(self.moveit, self.gripper, "open", "gripper_controller")

        # 전체 6개 구역을 순환하는 횟수 설정
        iterations = 1
        
        for iteration in range(iterations):
            self.get_logger().info(f"--- 전체 순환 반복 횟수: {iteration + 1}/{iterations} ---")
            
            for i in range(6):
                next_index = (i + 1) % 6  # 5에서 6으로 넘어갈 때 0(Zone 1)으로 순환
                
                self.get_logger().info(f"작업 진행: Zone {i+1} -> Zone {next_index+1}")
                self.transfer_object(
                    pick_pose=zone_poses[i],
                    via_pose=via_poses[i],
                    place_pose=zone_poses[next_index],
                    place_coord=coords[next_index]
                )

        # 모든 작업 완료 후 최종 대기 위치 복귀
        self.plan_and_execute(self.moveit, self.arm, "init", "arm_controller")

    def transfer_object(self, pick_pose, via_pose, place_pose, place_coord):
        # 1. 대상 구역으로 접근하여 물체 집기
        self.plan_and_execute(self.moveit, self.arm, pick_pose, "arm_controller")
        self.plan_and_execute(self.moveit, self.gripper, "close", "gripper_controller")
        self.attach_object()
        
        # 2. 벽 충돌을 피하기 위해 상승
        self.plan_and_execute(self.moveit, self.arm, via_pose, "arm_controller")
        
        # 3. 다음 구역으로 하강하여 물체 놓기
        self.plan_and_execute(self.moveit, self.arm, place_pose, "arm_controller")
        self.plan_and_execute(self.moveit, self.gripper, "open", "gripper_controller")
        self.detach_object()
        
        # 4. [핵심 수정] 다음 픽(Pick) 동작을 위해 로봇 팔을 준비 자세로 완전히 빼냄
        # 이 과정이 없으면 팔이 물체에 머물러 있어 다음 반복 시 로봇이 이동하지 않음
        self.plan_and_execute(self.moveit, self.arm, "init", "arm_controller")
        
        # 5. 로봇 팔이 빠져나온 후 다음 구역 바닥에 물체를 렌더링
        self.remove_object(self.object_id)
        self.add_box_object(self.object_id, [0.035, 0.035, 0.08], place_coord)

    def plan_and_execute(
        self,
        moveit: MoveItPy,
        component,
        configuration: str | dict[str, float],
        controller_name: str,
    ) -> bool:
        component.set_start_state_to_current_state()
        if issubclass(type(configuration), str):
            component.set_goal_state(configuration_name=configuration)
        else:
            robot_model = self.moveit.get_robot_model()
            robot_state = RobotState(robot_model)
            robot_state.joint_positions = configuration
            joint_model_group = robot_model.get_joint_model_group("arm")
            joint_constraint = construct_joint_constraint(
                robot_state=robot_state, joint_model_group=joint_model_group
            )
            component.set_goal_state(motion_plan_constraints=[joint_constraint])

        plan_result = component.plan()
        moveit.execute(plan_result.trajectory, controllers=[controller_name])
        return True

    def add_box_object(
        self, 
        object_id: str, 
        dimensions: list[float], 
        position: list[float],
        orientation: list[float] = [0.0, 0.0, 0.0, 1.0]
    ) -> bool:
        collision_object = CollisionObject()
        collision_object.header.frame_id = "world"
        collision_object.header.stamp = self.get_clock().now().to_msg()
        collision_object.id = object_id

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = dimensions

        box_pose = Pose()
        box_pose.position.x = position[0]
        box_pose.position.y = position[1]
        box_pose.position.z = position[2]
        
        box_pose.orientation.x = orientation[0]
        box_pose.orientation.y = orientation[1]
        box_pose.orientation.z = orientation[2]
        box_pose.orientation.w = orientation[3]

        collision_object.primitives.append(box)  # type: ignore
        collision_object.primitive_poses.append(box_pose)  # type: ignore
        collision_object.operation = CollisionObject.ADD

        success = self.planning_scene_monitor.process_collision_object(collision_object)
        return success

    def remove_object(self, object_id: str) -> bool:
        remove_obj = CollisionObject()
        remove_obj.header.frame_id = "world"
        remove_obj.header.stamp = self.get_clock().now().to_msg()
        remove_obj.id = object_id
        remove_obj.operation = CollisionObject.REMOVE

        success = self.planning_scene_monitor.process_collision_object(remove_obj)
        return success

    def attach_object(self):
        attached_object = AttachedCollisionObject()
        attached_object.link_name = self.attach_link
        attached_object.object.id = self.object_id
        
        attached_object.object.operation = CollisionObject.ADD
        attached_object.touch_links = self.touch_links

        with self.planning_scene_monitor.read_write() as scene:
            success = scene.process_attached_collision_object(attached_object)
            scene.current_state.update()

        return success

    def detach_object(self):
        attached_object = AttachedCollisionObject()
        attached_object.link_name = self.attach_link
        attached_object.object.id = self.object_id
        attached_object.object.operation = CollisionObject.REMOVE

        with self.planning_scene_monitor.read_write() as scene:
            success = scene.process_attached_collision_object(attached_object)
            scene.current_state.update()

        return success


def main() -> None:
    rclpy.init()

    node = OpenManipulatorMoveItNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.try_shutdown()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)


if __name__ == "__main__":
    main()