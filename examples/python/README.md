# Python MoveIt2 예제

Piper 팔을 파이썬으로 MoveIt2 제어하는 예제 모음입니다. 개요·배경은 메인 README 의
**"## Python 으로 MoveIt2 제어 (예제)"** 섹션을 참고하세요.

## 파일

| 파일 | API | 내용 |
|---|---|---|
| `ex01_pymoveit2_basic.py` | `pymoveit2` | 관절공간 목표 이동, 홈 복귀, 두 번째 MoveIt2 인스턴스로 그리퍼 열기/닫기, 속도/가속 스케일링 |
| `ex02_pymoveit2_cartesian_scene.py` | `pymoveit2` | IK POSE 목표 + 직선 Cartesian PATH, 플래닝 씬 충돌 박스 추가/우회/제거 |
| `ex03_moveit_py_official.py` | `moveit_py` | 공식 바인딩. SRDF 이름 상태 계획, 관절/포즈 목표, 충돌물체 회피, 다중 파이프라인 |
| `ex03_moveit_py.launch.py` | — | ex03 을 in-process `move_group`(+mock ros2_control, 컨트롤러)으로 띄우는 런치 |
| `moveit_py_params.py` | — | 런치·노트북이 공유하는 MoveIt 설정 빌더(`build_moveit_config_dict()` / `build_moveit_configs()`) |
| `ex03_moveit_py_notebook.launch.py` | — | mock 스택 + **주피터 서버**를 띄우는 런치 (아래 노트북용) |
| `ex03_nb01_arm_motions.ipynb` | `moveit_py` | **[노트북]** 팔 모션 총집합 — 이름상태/관절/포즈(IK)/속도 스케일링 |
| `ex03_nb02_gripper_and_scene.ipynb` | `moveit_py` | **[노트북]** 그리퍼(open/half/close/raw) + pick&place 시퀀스 + 플래닝 씬 충돌물체 |
| `ex03_nb03_interactive_playground.ipynb` | `moveit_py` | **[노트북]** 라이브 놀이터 — 재사용 헬퍼로 셀만 바꿔 실시간 조종 + 상태 조회 + 다중 파이프라인 |

## 사전 준비

```bash
sudo apt install ros-jazzy-pymoveit2 ros-jazzy-moveit-py
```

## 실행

### pymoveit2 (ex01, ex02) — `run-mock.sh` 가 먼저 떠 있어야 함

`pymoveit2` 는 이미 떠 있는 `move_group` 의 클라이언트입니다.

```bash
# 터미널 1
./scripts/run-mock.sh        # "You can start planning now!" 대기
```

그 다음 **터미널 2** 에서:

```bash
# 터미널 2
source /opt/ros/jazzy/setup.bash
source ~/piper-rwh/ros2_ws/install/setup.bash
python3 examples/python/ex01_pymoveit2_basic.py            # 또는 ex02_pymoveit2_cartesian_scene.py
```

### moveit_py (ex03) — 단독 실행 (`run-mock.sh` 와 같이 띄우지 말 것)

`moveit_py` 는 자체 `move_group` 을 in-process 로 띄웁니다. 실행 대상은 스크립트가 아니라 런치 파일입니다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/piper-rwh/ros2_ws/install/setup.bash
LC_NUMERIC=C ros2 launch ~/piper-rwh/examples/python/ex03_moveit_py.launch.py
```

기본으로 RViz 가 떠서 팔 움직임을 볼 수 있습니다(모션은 RViz 가 뜬 뒤 ~6초부터). 헤드리스면 `use_rviz:=false`. `예제 완료` 후에도 런치는 계속 떠 있으니 **Ctrl-C** 로 종료.

---

## moveit_py 인터랙티브 노트북 (`ex03_nb0{1,2,3}.ipynb`) ⭐ 추천

스크립트를 매번 고치고 런치를 재시작하는 대신, **주피터 커널을 살려둔 채 셀만 다시
실행**하면 로봇이 실시간으로 움직입니다. 커널이 죽지 않으니 `move_group`·컨트롤러도 안
꺼지고, **목표/포즈/파라미터를 바꾸는 파이썬 반복은 colcon 재빌드도, 런치 재시작도 필요
없습니다.** (공식 [jupyter_notebook_prototyping](https://moveit.picknik.ai/main/doc/examples/jupyter_notebook_prototyping/jupyter_notebook_prototyping_tutorial.html) 튜토리얼과 같은 방식.)

> 무엇이 재시작/재빌드를 부르나:
> - **목표·포즈·플래닝 파라미터(파이썬 셀)** → 아무것도 필요 없음. 셀 고쳐 **Shift+Enter** 뿐.
> - **URDF/SRDF/컨트롤러 YAML** → 런치를 Ctrl-C 후 재실행(커널 재시작 포함).
> - **최초 1회** → 워크스페이스 colcon 빌드 + 이 런치 부팅은 여전히 필요(반복이 사라질 뿐).

### 사전 준비 (최초 1회)

```bash
# Ubuntu 24.04 PEP668 — --user 와 --break-system-packages 를 둘 다
pip3 install --user --break-system-packages notebook ipykernel
```

(`ros-jazzy-moveit-py` 는 위 "사전 준비" 에서 이미 설치. `scipy` 는 기본 존재 — nb01 포즈 예제에서 사용.)

### 방법 A — 런치가 주피터 서버를 띄움

```bash
source /opt/ros/jazzy/setup.bash
source ~/piper-rwh/ros2_ws/install/setup.bash
LC_NUMERIC=C ros2 launch ~/piper-rwh/examples/python/ex03_moveit_py_notebook.launch.py
```

- mock 스택(rsp + ros2_control + 컨트롤러 + RViz) + 주피터 서버가 함께 뜹니다.
- 브라우저가 자동으로 안 열리면 터미널의 `http://localhost:8888/?token=...` 로 접속.
- 컨트롤러가 active 되면(~30초, RViz 에 로봇) `ex03_nb01_arm_motions.ipynb` 를 열고 **위 셀부터 순서대로** 실행.
- 헤드리스: `use_rviz:=false`.

### 방법 B — VS Code 로 실행 (편함)

VS Code 의 **Jupyter/Python 확장**으로 `.ipynb` 를 바로 열어 셀을 실행할 수 있습니다.
단, **커널이 ROS 환경을 상속**해야 하고 mock 스택이 떠 있어야 합니다:

1. **소싱된 터미널에서 VS Code 를 띄웁니다** (커널이 그 환경을 물려받도록):
   ```bash
   source /opt/ros/jazzy/setup.bash
   source ~/piper-rwh/ros2_ws/install/setup.bash
   export LC_NUMERIC=C
   code ~/piper-rwh
   ```
2. **mock 스택만 따로 띄웁니다** (노트북 자체가 in-process `move_group` 을 올리므로, 스택은
   rsp+컨트롤러만 있으면 됨). 위 방법 A 런치를 그대로 쓰되 주피터 창은 무시하거나,
   `use_rviz:=false` 로 헤드리스 실행:
   ```bash
   LC_NUMERIC=C ros2 launch ~/piper-rwh/examples/python/ex03_moveit_py_notebook.launch.py use_rviz:=false
   ```
3. VS Code 에서 `examples/python/ex03_nb01_arm_motions.ipynb` 를 열고, 커널을 `python3`
   (위에서 소싱한 환경)로 고른 뒤 셀을 실행합니다. `import moveit_py_params` 가 되려면
   노트북이 `examples/python/` 안에 있어야 합니다(이미 그렇게 배치됨).

> VS Code 커널이 ROS 를 못 찾으면(`ModuleNotFoundError: moveit` 등) 거의 항상 **소싱 안 된
> 환경에서 code 를 띄운 것**입니다. 반드시 위 1번처럼 소싱된 터미널에서 `code` 로 여세요.

### 세 노트북

| 노트북 | 보여주는 동작 |
|---|---|
| `ex03_nb01_arm_motions.ipynb` | 이름상태 `home`, 관절목표 4종(좌/우/숙임/손목), 포즈 IK(FK 유도 + 리터럴), 속도 스케일링(느리게 vs 빠르게) |
| `ex03_nb02_gripper_and_scene.ipynb` | 그리퍼 open/half/close + raw 값, 팔↔그리퍼 pick&place 시퀀스, 충돌 박스 add/plan/remove |
| `ex03_nb03_interactive_playground.ipynb` | `go_named/go_joints/grip` 헬퍼로 라이브 포킹, 현재 관절·tcp 포즈 조회, 다중 파이프라인 |

### 노트북 gotcha

- **설정 셀(`MoveItPy(...)`)은 커널당 딱 한 번만.** 다시 실행하면 커널이 죽을 수 있음(알려진
  MoveItPy 소멸자 이슈). ex03 스크립트가 `os._exit(0)` 를 쓴 이유이기도 함 — 노트북에선
  그 대신 "생성은 한 번, 이후엔 목표 셀만 반복" 규칙으로 회피.
- **한 번에 한 노트북/커널만** 컨트롤러를 구동. `run-mock.sh`(demo.launch.py)와 동시 실행 금지.
- 커널 종료 시 "Kernel died" 가 떠도 정상(위 소멸자 이슈).
- 자기충돌하는 관절 목표는 계획이 실패(`GOAL_STATE_INVALID`)하고 팔이 안 움직입니다 — 로그를 보세요.

> 세 노트북 모두 mock 스택에서 `nbconvert --execute` 로 셀 전량 실행 검증됨(전 모션 계획·실행 성공).
