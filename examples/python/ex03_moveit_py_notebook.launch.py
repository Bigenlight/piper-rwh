"""moveit_py 인터랙티브 노트북 런치 — 로봇 스택 + 주피터 서버를 함께 띄운다.

ex03_moveit_py.launch.py 의 '한 번 돌고 죽는 스크립트' 대신, 이 런치는
mock 로봇 스택(rsp + mock ros2_control + 컨트롤러 + RViz)만 올리고 마지막에
**주피터 노트북 서버**를 띄운다. move_group 은 여기서 안 띄운다 —
노트북 셀 안에서 MoveItPy 가 in-process move_group 을 직접 올리기 때문이다.
(공식 jupyter_notebook_prototyping 튜토리얼과 동일한 구조.)

핵심 이득: 커널이 살아있는 동안 셀만 다시 실행하면 로봇이 실시간으로 움직인다.
목표/포즈/플래닝 파라미터를 바꾸는 파이썬 반복은 colcon 재빌드도, 런치 재시작도 필요 없다.
(URDF/SRDF/컨트롤러 YAML 을 바꿀 때만 이 런치를 Ctrl-C 후 재실행하면 된다.)

실행:
  # (최초 1회) 주피터 설치 — Ubuntu 24.04 PEP668
  pip3 install --user --break-system-packages notebook ipykernel

  source /opt/ros/jazzy/setup.bash
  source ~/piper-rwh/ros2_ws/install/setup.bash
  LC_NUMERIC=C ros2 launch ~/piper-rwh/examples/python/ex03_moveit_py_notebook.launch.py

  → 브라우저가 자동으로 안 열리면 터미널에 찍힌 http://localhost:8888/?token=... 로 접속.
  → examples/python/ 의 ex03_nb01_basics.ipynb 부터 위 셀부터 순서대로 실행.
  → 헤드리스(RViz 없이): use_rviz:=false

주의:
  - run-mock.sh(demo.launch.py)와 동시에 띄우지 말 것 (move_group/컨트롤러 충돌).
  - LC_NUMERIC=C 는 이 런치의 자식 프로세스(주피터 서버 → 커널)까지 상속되므로
    커맨드 앞에만 붙이면 된다.
  - 컨트롤러가 전부 active 되기까지 ~30초. RViz 에 로봇이 뜨거나
    `ros2 control list_controllers` 가 active 로 나오면 노트북 첫 셀을 실행.
"""

import sys
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

THIS_DIR = Path(__file__).resolve().parent

# ros2 launch 는 런치 파일 디렉터리를 sys.path 에 넣지 않는다 → 형제 모듈
# moveit_py_params 를 못 찾음. 직접 경로를 추가한 뒤 import 한다.
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

# 런치 파일과 노트북이 공유하는 단일 설정 소스
from moveit_py_params import build_moveit_configs  # noqa: E402
RVIZ_CONFIG = str(THIS_DIR / "ex03_moveit_py.rviz")


def generate_launch_description():
    pkg = "agx_arm_moveit"
    moveit_config = build_moveit_configs()

    # 리포에 이미 있는 ros2_control 컨트롤러 정의(arm/gripper/broadcaster)
    ros2_controllers = str(
        Path(get_package_share_directory(pkg)) / "config" / "ros2_controllers.yaml"
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    # mock 하드웨어 컨트롤러 매니저
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[moveit_config.robot_description, ros2_controllers],
    )

    def spawner(name):
        return Node(
            package="controller_manager",
            executable="spawner",
            arguments=[name, "--controller-manager", "/controller_manager"],
            output="screen",
        )

    # 관전용 RViz (RobotModel+TF). use_rviz:=false 면 헤드리스.
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", RVIZ_CONFIG],
        output="screen",
        parameters=[moveit_config.robot_description],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    # 주피터 노트북 서버 — examples/python/ 을 노트북 디렉터리로.
    # ExecuteProcess 라 이 런치의 자식 프로세스로 뜨고, 사용한 ROS 환경/LC_NUMERIC 을 상속한다.
    # 노트북 셀 안에서 `import moveit_py_params` 가 되도록 cwd 를 이 디렉터리로 맞춘다.
    jupyter = ExecuteProcess(
        cmd=["jupyter", "notebook", "--notebook-dir", str(THIS_DIR)],
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_rviz",
            default_value="true",
            choices=["true", "false"],
            description="팔 움직임을 볼 RViz 를 띄운다(기본 true). 헤드리스면 false.",
        ),
        rsp,
        ros2_control_node,
        spawner("joint_state_broadcaster"),
        spawner("arm_controller"),
        spawner("gripper_controller"),
        rviz_node,
        jupyter,
    ])
