# WHEELIE RACER - 소스코드 레퍼런스 문서

> GitHub에서 수집한 50+ 레포지토리를 카테고리별로 정리한 응용 가능 코드 레퍼런스

---

## TIER 1: 즉시 활용 가능 (MediaPipe + 레이싱)

### 1. Racing_game_control_with_mediapipe ⭐⭐⭐
- **URL**: https://github.com/martijnfolmer/Racing_game_control_with_mediapipe
- **활용**: 양손 스티어링 각도 계산, 손 거리로 속도 제어
- **핵심 코드 패턴**:
  ```python
  # 양손 사이 각도로 스티어링
  angle = atan2(hand_right.y - hand_left.y, hand_right.x - hand_left.x)
  # 양손 거리로 속도 제어
  velocity = distance(hand_left, hand_right)
  ```
- **우리 게임 적용**: 스티어링 기본 로직 그대로 활용

### 2. Racing-CV ⭐⭐⭐
- **URL**: https://github.com/SubashSK777/Racing-CV
- **활용**: 제스처별 레이싱 컨트롤 전체 세트
- **핵심 코드 패턴**:
  ```python
  # 9시-3시 방향 손 위치로 핸들 회전
  STEER = hand_tilt_angle
  ACCELERATE = both_palms_open
  BRAKE = both_fists
  NITRO = thumb_up
  ```
- **우리 게임 적용**: 가속(주먹펴기)/브레이크(주먹쥐기) 패턴 활용, HUD 디자인 참고

### 3. Hill-Climb-AI ⭐⭐⭐
- **URL**: https://github.com/AmshenShanu07/Hill-Climb-AI
- **활용**: 주먹/펼침 감지 로직 (가장 깔끔한 구현)
- **핵심 코드 패턴**:
  ```python
  # 손가락 접힘 감지 (핵심!)
  # fingertip(8,12,16,20)의 Y > PIP(6,10,14,18)의 Y → 접힘
  is_fist = all(
      landmarks[tip].y > landmarks[pip].y
      for tip, pip in [(8,6), (12,10), (16,14), (20,18)]
  )
  ```
- **우리 게임 적용**: 윌리/브레이크 제스처 감지 기본 로직

### 4. middle-finger-detection ⭐⭐⭐
- **URL**: https://github.com/soyflourbread/middle-finger-detection
- **활용**: 뻐큐 제스처 감지
- **핵심 코드 패턴**:
  ```python
  # 중지만 펴지고 나머지 접힌 상태
  middle_extended = landmark[12].y < landmark[10].y
  others_closed = all(
      landmark[tip].y > landmark[pip].y
      for tip, pip in [(8,6), (16,14), (20,18)]
  )
  is_middle_finger = middle_extended and others_closed
  ```
- **우리 게임 적용**: 도발 기능 **그대로** 활용

### 5. hand-gesture-recognition-using-mediapipe ⭐⭐⭐
- **URL**: https://github.com/Kazuhito00/hand-gesture-recognition-using-mediapipe
- **활용**: 커스텀 제스처 MLP 학습 프레임워크
- **기능**: 21개 랜드마크 → 정규화 → MLP 분류기 → TFLite
- **우리 게임 적용**: 추가 제스처 학습 시 활용 (Jupyter 노트북으로 학습)

### 6. Gesture-Control-Hill-Climb-Racing ⭐⭐
- **URL**: https://github.com/DataRohit/Gesture-Control-Hill-Climb-Racing
- **활용**: MediaPipe → 제스처 분류 → pynput 키보드 파이프라인
- **우리 게임 적용**: 파이프라인 아키텍처 참고 (우리는 직접 Queue로 전달)

### 7. Simple Gesture Recognition Gist ⭐⭐
- **URL**: https://gist.github.com/TheJLifeX/74958cc59db477a91837244ff598ef4a
- **활용**: 가장 간단한 5손가락 상태 감지
- **핵심 코드**:
  ```python
  thumb_open = landmark[3].x < landmark[2].x  # 엄지는 X축 비교
  index_open = landmark[8].y < landmark[6].y   # 나머지는 Y축 비교
  ```
- **우리 게임 적용**: 초기 프로토타입 손가락 감지 템플릿

---

## TIER 2: Ursina 게임 엔진 레퍼런스

### 8. Rally (Ursina 레이싱) ⭐⭐⭐
- **URL**: https://github.com/mandaw2014/Rally
- **활용**: Ursina 3D 레이싱 게임 전체 구조
- **기능**: 멀티플레이어, 3D 레이싱, 차량 물리
- **우리 게임 적용**: 게임 구조, Entity 활용, 카메라 팔로우 패턴

### 9. AR-Python (Ursina + MediaPipe) ⭐⭐⭐
- **URL**: https://github.com/DawoodLaiq/AR-Python
- **활용**: Ursina + MediaPipe + OpenCV 통합 증명
- **우리 게임 적용**: 스레딩 패턴, 카메라 입력 → 게임 렌더링 연동

### 10. SF Rally (Ursina) ⭐⭐
- **URL**: https://github.com/Eric-MK/sf_rally_drifting_game
- **활용**: Ursina 드리프팅 레이싱 게임
- **우리 게임 적용**: 차량 물리, 드리프트 메카닉 참고

### 11. Bullet-for-Ursina ⭐⭐
- **URL**: https://github.com/LooksForFuture/Bullet-for-ursina
- **활용**: Ursina에서 Bullet 물리 엔진 사용
- **우리 게임 적용**: 충돌 감지, 리지드바디 물리 (필요시)

### 12. ursina-voxel-projects ⭐⭐
- **URL**: https://github.com/nurse-the-code/ursina-voxel-projects
- **활용**: 청크 기반 복셀 렌더링, 면 컬링
- **우리 게임 적용**: 복셀 월드 최적화 패턴

---

## TIER 3: 바이크 물리 & 레이싱 메카닉

### 13. MotorcyclePhysics (Unity) ⭐⭐
- **URL**: https://github.com/Kright/MotorcyclePhysics
- **활용**: 오토바이 물리 모델 (밸런스, 기울기, 가속)
- **우리 게임 적용**: 윌리 토크/밸런스 메카닉 수학 공식 참고

### 14. UnityMotorbikeController ⭐⭐
- **URL**: https://github.com/ArcaDone/UnityMotorbikeController
- **활용**: 오토바이 컨트롤러 (스티어링, 스로틀, 기울기)
- **우리 게임 적용**: 바이크 조작 로직 참고

### 15. Bike_dynamic_simulator (Python!) ⭐⭐
- **URL**: https://github.com/JAlcocerT/Bike_dynamic_simulator
- **활용**: Python 바이크 역학 시뮬레이션
- **우리 게임 적용**: 윌리 물리 공식 직접 활용 가능

### 16. Roost (Unity) ⭐
- **URL**: https://github.com/litlabproductions/Roost
- **활용**: 3D 모토크로스 물리 (250/450cc)
- **우리 게임 적용**: 밸런스 시스템 (roll, pitch, yaw) 개념 참고

---

## TIER 4: Pseudo-3D / 트랙 생성

### 17. SwervinMervin ⭐⭐⭐
- **URL**: https://github.com/buntine/SwervinMervin
- **활용**: Python/Pygame Pseudo-3D 레이싱 (OutRun 스타일)
- **기능**: 세그먼트 기반 도로, 커브, 언덕
- **우리 게임 적용**: 2D 폴백 옵션 또는 도로 생성 알고리즘 참고

### 18. RacingPseudo3DPython ⭐⭐
- **URL**: https://github.com/brccabral/RacingPseudo3DPython
- **활용**: Python 3.8 + Pygame 2.1.2 Pseudo-3D 레이싱
- **우리 게임 적용**: 현대 Python pseudo-3D 도로 생성

### 19. procedural-tracks (Python!) ⭐⭐⭐
- **URL**: https://github.com/juangallostra/procedural-tracks
- **활용**: Python 절차적 레이스 트랙 생성
- **기능**: Convex hull + 스플라인 기반 트랙 생성
- **우리 게임 적용**: 트랙 자동 생성 알고리즘 직접 활용

### 20. javascript-racer ⭐⭐
- **URL**: https://github.com/jakesgordon/javascript-racer
- **활용**: 4단계 Pseudo-3D 도로 튜토리얼 (직선→커브→언덕→완성)
- **우리 게임 적용**: Pseudo-3D 개념 학습 최고의 리소스

### 21. PolyRace (Unity) ⭐
- **URL**: https://github.com/vthem/PolyRace
- **활용**: 로우폴리 레이싱 + 절차적 레벨 생성
- **우리 게임 적용**: 로우폴리 지형 + 자동 레벨 생성 참고

---

## TIER 5: 복셀 아트 & 에셋

### 22. Expo-Crossy-Road ⭐⭐
- **URL**: https://github.com/EvanBacon/Expo-Crossy-Road
- **활용**: Crossy Road 클론 (Three.js + React Native, MIT)
- **우리 게임 적용**: 복셀 게임 아키텍처, 카메라 시스템, 게임 루프 참고

### 23. python-voxel-engine ⭐
- **URL**: https://github.com/vibestorming/python-voxel-engine
- **활용**: Pygame + OpenGL 복셀 렌더링
- **우리 게임 적용**: 복셀 렌더링 최적화 기법

### 24. TerraCraft ⭐
- **URL**: https://github.com/XenonLab-Studio/TerraCraft
- **활용**: Python 3 + Pyglet 복셀 엔진
- **우리 게임 적용**: 복셀 월드 구축 참고

### 25. VoxelGame (ModernGL) ⭐
- **URL**: https://github.com/TriLinder/VoxelGame
- **활용**: Python + ModernGL 3D 복셀 빌딩
- **우리 게임 적용**: ModernGL 복셀 렌더링 대안

---

## TIER 6: 무료 에셋 소스

### 복셀 모델 (차량 & 바이크)
| 소스 | URL | 내용 | 라이선스 |
|------|-----|------|----------|
| Voxel Roads & Cars | https://maxparata.itch.io/voxelroads | 도로, 표지판, 차 8종 | 무료 (재배포 불가) |
| Voxel Hover Bike | https://maxparata.itch.io/hover-bike | 호버 바이크 | 무료 기본팩 |
| CC0 3D Vehicles | https://opengameart.org/content/cc0-3d-vehicles-and-cars | CC0 차량 | **CC0 (퍼블릭 도메인)** |
| Free Low Poly Vehicles | https://opengameart.org/content/free-low-poly-vehicles-pack | 경찰차, SUV 등 | **CC0** |
| TurboSquid Voxel Motorcycle | https://www.turbosquid.com/3d-models/motorcycle-voxel-low-poly-3d-model-1262103 | 복셀 오토바이 OBJ | 로열티 프리 |

### 복셀 모델 (환경)
| 소스 | URL | 내용 | 라이선스 |
|------|-----|------|----------|
| itch.io Voxel 에셋 | https://itch.io/game-assets/free/tag-voxel | 건물, 소품 등 | 다양 (다수 무료) |
| Enkisoftware Voxels | https://github.com/enkisoftware/voxel-models | 무료 복셀 모델 | **CC BY 4.0** |
| Sketchfab MagicaVoxel | https://sketchfab.com/tags/magicavoxel | 커뮤니티 모델 | 다양 |
| Voxel Path & Terrain | https://kytric.itch.io/voxel-path-and-terrain | 나무, 바위, 물 | 확인 필요 |

### 복셀 도구
| 도구 | URL | 용도 |
|------|-----|------|
| MagicaVoxel | https://ephtracy.github.io/ | 복셀 모델 제작 (무료) |
| py-vox-io | https://github.com/gromgull/py-vox-io | Python .vox 파서 |
| VoxelFuse | https://pypi.org/project/voxelfuse/ | pip 설치 가능, .vox 임포트 |
| V-Optimizer | https://vailor1.itch.io/v-optimizer | .vox → OBJ/GLTF/GLB 변환 |

---

## 핵심 코드 패턴 요약

### 패턴 1: 손가락 접힘/펴짐 감지
```python
# 각 손가락의 TIP이 PIP보다 아래면 접힘
FINGER_TIPS = [8, 12, 16, 20]  # 검지, 중지, 약지, 새끼
FINGER_PIPS = [6, 10, 14, 18]

def get_finger_states(landmarks):
    states = []
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        states.append(landmarks[tip].y < landmarks[pip].y)  # True = 펴짐
    # 엄지는 X축으로 판별
    thumb = landmarks[4].x < landmarks[3].x  # 오른손 기준
    return [thumb] + states  # [엄지, 검지, 중지, 약지, 새끼]
```

### 패턴 2: 손 기울기 (스티어링 각도)
```python
import math

def get_hand_tilt(landmarks):
    """손의 기울기 각도 계산 (스티어링용)"""
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    angle = math.atan2(
        middle_mcp.y - wrist.y,
        middle_mcp.x - wrist.x
    )
    return math.degrees(angle)  # -180 ~ 180
```

### 패턴 3: 손 높이 (윌리 컨트롤)
```python
def get_hand_height(landmarks):
    """손 높이 반환 (0=화면 하단, 1=화면 상단)"""
    wrist_y = landmarks[0].y  # MediaPipe: 0=상단, 1=하단
    return 1.0 - wrist_y  # 반전: 높을수록 값 큼
```

### 패턴 4: 뻐큐 감지
```python
def is_middle_finger(landmarks):
    """오직 중지만 펴진 상태 감지"""
    finger_states = get_finger_states(landmarks)
    # [엄지, 검지, 중지, 약지, 새끼]
    # 중지만 True, 나머지 False
    return (not finger_states[0] and      # 엄지 접힘
            not finger_states[1] and      # 검지 접힘
            finger_states[2] and          # 중지 펴짐 ✓
            not finger_states[3] and      # 약지 접힘
            not finger_states[4])         # 새끼 접힘
```

### 패턴 5: MediaPipe → Game Input 파이프라인
```python
import threading, queue

class GestureData:
    """MediaPipe에서 게임으로 전달하는 제스처 데이터"""
    def __init__(self):
        self.steer = 0.0          # -1 (좌) ~ 1 (우)
        self.wheelie_height = 0.0  # 0 (내림) ~ 1 (최대)
        self.is_fist = False       # 브레이크
        self.is_open = False       # 가속
        self.is_taunt = False      # 뻐큐
        self.hand_detected = False

# Queue(maxsize=1)로 최신 프레임만 유지
gesture_queue = queue.Queue(maxsize=1)
```

### 패턴 6: Ursina 게임 루프에서 제스처 읽기
```python
from ursina import *

def update():
    try:
        gesture = gesture_queue.get_nowait()
        bike.apply_gesture(gesture)
    except queue.Empty:
        pass  # 이전 프레임 상태 유지
```

---

## MediaPipe Hand Landmark 참조표

```
 0: WRIST              ← 손 높이/위치 기준점
 1: THUMB_CMC
 2: THUMB_MCP
 3: THUMB_IP
 4: THUMB_TIP          ← 엄지 끝
 5: INDEX_FINGER_MCP
 6: INDEX_FINGER_PIP   ← 검지 접힘 비교 기준
 7: INDEX_FINGER_DIP
 8: INDEX_FINGER_TIP   ← 검지 끝
 9: MIDDLE_FINGER_MCP  ← 기울기 계산용 (wrist와 각도)
10: MIDDLE_FINGER_PIP  ← 중지 접힘 비교 기준
11: MIDDLE_FINGER_DIP
12: MIDDLE_FINGER_TIP  ← 중지 끝 (뻐큐 감지 핵심)
13: RING_FINGER_MCP
14: RING_FINGER_PIP
15: RING_FINGER_DIP
16: RING_FINGER_TIP
17: PINKY_MCP
18: PINKY_PIP
19: PINKY_DIP
20: PINKY_TIP
```
