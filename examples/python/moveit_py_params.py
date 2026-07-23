"""공유 MoveIt 설정 빌더 — 런치 파일과 주피터 노트북이 함께 쓰는 단일 소스.

ex03_moveit_py.launch.py 가 인라인으로 만들던 moveit_config / moveit_py 파라미터
빌드 로직을 여기로 뽑아냈다. 이유:

  - 노트북(ex03_nb*.ipynb)은 자기 커널 안에서 MoveItPy 를 직접 띄운다. 그러려면
    노트북 첫 셀에서 URDF/SRDF/kinematics/파이프라인이 담긴 '설정 dict' 를 만들어
    MoveItPy(config_dict=...) 로 넘겨야 한다. (공식 jupyter_notebook_prototyping
    튜토리얼과 동일한 패턴 — 런치가 파라미터를 주입하는 게 아니라, 노트북이 직접 dict 를 만든다.)
  - 런치 파일도 rsp/ros2_control/RViz 노드에 같은 robot_description 을 먹여야 한다.

두 경로가 설정을 각자 만들면 반드시 어긋난다. 그래서 여기 한 곳에서만 만든다.

  build_moveit_configs()      -> MoveItConfigs 객체 (런치가 노드 파라미터로 사용)
  build_moveit_config_dict()  -> MoveItPy(config_dict=...) 에 넣을, 형식 보정까지 끝난 dict

전제: 워크스페이스가 colcon 빌드돼 있고 source 돼 있어야 한다
(get_package_share_directory("agx_arm_moveit") 가 잡혀야 함).
"""

from moveit_configs_utils import MoveItConfigsBuilder

# piper + agx_gripper 조합(리포 기본 프로파일). ex03_moveit_py.launch.py 와 동일.
XACRO_MAPPINGS = {
    "arm_type": "piper",
    "effector_type": "agx_gripper",
    "revo2_type": "left",
    "tcp_offset_xyz": "0.0 0.0 0.1425",  # link6 -> 그리퍼 EEF(파지 끝단) TCP, +z 방향
    "tcp_offset_rpy": "0.0 0.0 0.0",     # 회전 0: 접근축이 곧 link6 +z (gripper_base 가 flange +z 에 정렬)
}
SRDF_MAPPINGS = {
    "arm_type": "piper",
    "effector_type": "agx_gripper",
    "revo2_type": "left",
}

# MultiPipelinePlanRequestParameters 가 참조하는 파이프라인별 계획 파라미터.
# (이름 그룹 "ompl_rrtc"/"pilz_ptp" → 실제 로드된 파이프라인 매핑)
PLAN_REQUEST_PARAMS = {
    "plan_request_params": {
        "planning_attempts": 1,
        "planning_pipeline": "ompl",
        "planner_id": "RRTConnectkConfigDefault",
        "max_velocity_scaling_factor": 0.2,
        "max_acceleration_scaling_factor": 0.2,
    },
    "ompl_rrtc": {
        "plan_request_params": {
            "planning_attempts": 1,
            "planning_pipeline": "ompl",
            "planner_id": "RRTConnectkConfigDefault",
            "max_velocity_scaling_factor": 0.2,
            "max_acceleration_scaling_factor": 0.2,
        }
    },
    "pilz_ptp": {
        "plan_request_params": {
            "planning_attempts": 1,
            "planning_pipeline": "pilz_industrial_motion_planner",
            "planner_id": "PTP",
            "max_velocity_scaling_factor": 0.2,
            "max_acceleration_scaling_factor": 0.2,
        }
    },
}


def build_moveit_configs():
    """MoveItConfigs 객체를 만든다 (런치가 rsp/ros2_control/RViz 노드 파라미터로 사용).

    ex03_moveit_py.launch.py 의 MoveItConfigsBuilder 블록과 1:1 동일하게 유지할 것.
    """
    pkg = "agx_arm_moveit"
    return (
        MoveItConfigsBuilder("agx_arm", package_name=pkg)
        .robot_description(
            file_path="config/agx_arm.urdf.xacro", mappings=XACRO_MAPPINGS
        )
        .robot_description_semantic(
            file_path="config/agx_arm.srdf.xacro", mappings=SRDF_MAPPINGS
        )
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .trajectory_execution(file_path="config/moveit_controllers_gripper.yaml")
        .planning_pipelines(  # ompl + pilz(다중 파이프라인용) 명시 로드
            default_planning_pipeline="ompl",
            pipelines=["ompl", "pilz_industrial_motion_planner"],
        )
        .pilz_cartesian_limits(file_path="config/pilz_cartesian_limits.yaml")
        .to_moveit_configs()
    )


def build_moveit_config_dict():
    """MoveItPy(config_dict=...) 에 넣을, 형식 보정까지 끝난 dict 를 만든다.

    노트북 첫 셀에서:
        from moveit_py_params import build_moveit_config_dict
        robot = MoveItPy(node_name="moveit_py", config_dict=build_moveit_config_dict())

    보정 내용(ex03_moveit_py.launch.py 와 동일):
      - planning_pipelines: to_dict() 의 '평탄 리스트' → MoveItPy(moveit_cpp) 가 요구하는
        {"pipeline_names": [...]} 중첩 형식으로 변환.
      - sensors / point_cloud_sensor: 3D 옥토맵 센서는 이 셋업에 불필요 → 로드 에러 방지 위해 제거.
      - PLAN_REQUEST_PARAMS: 기본 + 파이프라인별 계획 파라미터 주입(다중 파이프라인용).
    """
    params = build_moveit_configs().to_dict()

    pipeline_names = params.pop("planning_pipelines", ["ompl"])
    params["planning_pipelines"] = {"pipeline_names": pipeline_names}

    params.pop("sensors", None)
    params.pop("point_cloud_sensor", None)

    params.update(PLAN_REQUEST_PARAMS)
    return params
