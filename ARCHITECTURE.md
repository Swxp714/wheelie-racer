# WHEELIE RACER - 기술 아키텍처 문서

---

## 기술 스택

```
pip install ursina mediapipe opencv-python
```

| 구성요소 | 기술 | 역할 |
|----------|------|------|
| **게임 엔진** | Ursina 8.3.0+ | 3D 렌더링, 엔티티 시스템, 오디오 |
| **3D 백엔드** | Panda3D (Ursina 내장) | C++ 렌더러, Bullet 물리 |
| **손 추적** | MediaPipe Hands | 21개 랜드마크 실시간 감지 |
| **카메라** | OpenCV (cv2) | 웹캠 캡처 + BGR→RGB 변환 |
| **수학** | numpy, math | 각도 계산, 벡터 연산 |
| **에셋** | MagicaVoxel | .vox → OBJ 변환 |

---

## 시스템 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                    MAIN PROCESS                       │
│                                                       │
│  ┌──────────────────┐     ┌───────────────────────┐  │
│  │  URSINA GAME LOOP │     │  MEDIAPIPE THREAD     │  │
│  │  (Main Thread)    │     │  (Daemon Thread)      │  │
│  │                   │     │                       │  │
│  │  ┌─────────────┐ │     │  ┌─────────────────┐  │  │
│  │  │ Game State   │ │     │  │ cv2.VideoCapture│  │  │
│  │  │ Manager      │ │     │  │ (640x480)       │  │  │
│  │  └──────┬──────┘ │     │  └────────┬────────┘  │  │
│  │         │        │     │           │            │  │
│  │  ┌──────▼──────┐ │     │  ┌────────▼────────┐  │  │
│  │  │ Bike Physics│ │     │  │ mp.hands.Hands  │  │  │
│  │  │ Controller  │ │     │  │ (Lite model)    │  │  │
│  │  └──────┬──────┘ │     │  └────────┬────────┘  │  │
│  │         │        │     │           │            │  │
│  │  ┌──────▼──────┐ │     │  ┌────────▼────────┐  │  │
│  │  │ Track       │ │     │  │ Gesture         │  │  │
│  │  │ Generator   │ │     │  │ Classifier      │  │  │
│  │  └──────┬──────┘ │     │  └────────┬────────┘  │  │
│  │         │        │     │           │            │  │
│  │  ┌──────▼──────┐ │     │           │            │  │
│  │  │ Renderer    │ │◄────┼── Queue(maxsize=1) ◄──┘  │
│  │  │ + HUD       │ │     │   (GestureData)         │
│  │  └──────┬──────┘ │     │                       │  │
│  │         │        │     └───────────────────────┘  │
│  │  ┌──────▼──────┐ │                                │
│  │  │ Audio       │ │                                │
│  │  │ Manager     │ │                                │
│  │  └─────────────┘ │                                │
│  └──────────────────┘                                │
└──────────────────────────────────────────────────────┘
```

---

## 모듈 설계

### main.py - 진입점
```python
"""앱 초기화, 게임 루프 시작"""
# Ursina 앱 생성
# MediaPipe 스레드 시작
# 게임 상태 초기화
# update() 루프에서 제스처 읽기 + 게임 로직 실행
```

### hand_tracker.py - MediaPipe 스레드
```python
"""데몬 스레드로 실행, 웹캠에서 손 감지 후 Queue로 전달"""
class HandTracker(threading.Thread):
    - daemon = True
    - 640x480 해상도
    - model_complexity=0 (Lite)
    - max_num_hands=2 (양손)
    - Queue(maxsize=1)로 최신 프레임만 유지
```

### gesture.py - 제스처 분류
```python
"""MediaPipe 랜드마크 → 게임 입력 데이터 변환"""
@dataclass
class GestureData:
    steer: float          # -1.0 ~ 1.0
    wheelie_height: float # 0.0 ~ 1.0
    is_fist: bool         # 브레이크
    is_open: bool         # 가속
    is_taunt: bool        # 뻐큐
    hand_detected: bool

분류 함수:
  - get_hand_tilt() → steer
  - get_hand_height() → wheelie_height
  - is_fist() → brake
  - is_middle_finger() → taunt
```

### bike.py - 바이크 엔티티
```python
"""바이크 물리 + 렌더링"""
class Bike(Entity):
    물리 파라미터:
      - speed, max_speed, acceleration
      - wheelie_angle (0~90)
      - lean_angle (-35~35)
      - balance_wobble (랜덤 흔들림)
    
    update(gesture):
      1. 제스처 → 속도/방향 적용
      2. 윌리 각도 계산 (손 높이 기반)
      3. 균형 체크 (사망 판정)
      4. 위치 업데이트
      5. 모델 회전 업데이트
```

### track.py - 트랙 생성
```python
"""절차적 트랙 세그먼트 생성"""
class Track:
    세그먼트 유형: 직선, 커브(좌/우), 언덕, 램프
    장애물 스포너: 차량, 콘, 바리케이드
    아이템 스포너: 수리킷, 스타, 부스트, 쉴드
    청크 시스템: 플레이어 앞으로 생성, 뒤로 삭제
```

### camera_controller.py - 카메라
```python
"""3인칭 팔로우 카메라"""
- 직교 또는 약간의 원근
- 바이크 뒤쪽에서 따라감
- 윌리 시 줌아웃 + 화면 흔들림
- 사망 시 슬로우 줌인
```

### hud.py - UI
```python
"""게임 내 HUD"""
- 속도계
- 점수
- 윌리 게이지 (색상 변화: 초→노→주→빨)
- 웹캠 미리보기 (좌하단)
- 미니맵 (선택사항)
```

### game_state.py - 상태 관리
```python
"""게임 상태 FSM"""
States:
  MENU → CALIBRATION → RACING → PAUSED → GAME_OVER
  
CALIBRATION: 손 인식 확인 + 기본 포즈 캘리브레이션
```

### taunt.py - 도발 시스템
```python
"""뻐큐 이펙트"""
- 화면 이펙트 (이모지 팝업)
- 사운드 재생
- NPC 반응 트리거
- 3초 쿨다운
```

---

## 성능 최적화 전략

### MediaPipe 최적화
| 설정 | 값 | 이유 |
|------|-----|------|
| 해상도 | 640x480 | MP 내부에서 256x256으로 리사이즈함 |
| model_complexity | 0 (Lite) | 가장 빠른 모델 (~2MB) |
| max_num_hands | 2 | 양손 필수 (1이면 한손만 감지) |
| min_detection_confidence | 0.7 | 너무 낮으면 오감지 |
| min_tracking_confidence | 0.5 | 트래킹 유지 |

### 렌더링 최적화
- **정적 환경 메시 합치기**: 건물, 도로 등 변하지 않는 오브젝트 → 하나의 메시로 결합
- **오브젝트 풀링**: 장애물/아이템 재사용 (생성/삭제 반복 방지)
- **LOD 불필요**: 복셀 스타일은 이미 로우폴리 → LOD 없어도 됨
- **청크 시스템**: 플레이어 주변만 활성화, 먼 거리 청크 비활성화
- **플랫 셰이딩**: 버텍스 컬러 사용 → 텍스처 로딩 없음

### 스레딩 전략
```
Main Thread (Ursina):
  - 60 FPS 목표
  - 게임 로직 + 렌더링
  - Queue에서 제스처 읽기 (non-blocking)

Daemon Thread (MediaPipe):
  - 25-30 FPS
  - 웹캠 캡처 + 손 감지
  - Queue에 최신 결과만 유지

통신: queue.Queue(maxsize=1)
  - put: 새 결과가 오면 이전 결과 drop
  - get: get_nowait()로 논블로킹 읽기
```

---

## 에셋 파이프라인

```
MagicaVoxel (.vox)
    │
    ├── Export OBJ ──→ models/bike.obj + textures/palette.png
    │                    └→ Ursina: Entity(model='bike', texture='palette')
    │
    └── Export GLB (Blender 경유) ──→ 애니메이션 있는 모델
                                      └→ Ursina: Entity(model='bike.glb')

모델 배치:
  wheelie-racer/
    models/     ← .obj, .glb 파일
    textures/   ← .png 팔레트
    audio/      ← .ogg, .wav 사운드
```

---

## 키보드 폴백

MediaPipe 인식 실패 시 키보드로 대체 가능:

| 키 | 동작 |
|----|------|
| W / ↑ | 가속 |
| S / ↓ | 브레이크 |
| A / ← | 좌회전 |
| D / → | 우회전 |
| Space | 윌리 (누르는 동안 각도 증가) |
| F | 뻐큐 도발 |
| ESC | 일시정지 |

---

## 개발 의존성

```
# requirements.txt
ursina>=8.0.0
mediapipe>=0.10.0
opencv-python>=4.8.0
numpy>=1.24.0
```

---

## 파일 구조 (최종)

```
wheelie-racer/
├── main.py                  # 진입점
├── bike.py                  # 바이크 엔티티 + 물리
├── hand_tracker.py          # MediaPipe 스레드
├── gesture.py               # 제스처 데이터 + 분류
├── track.py                 # 트랙 생성 + 장애물
├── camera_controller.py     # 카메라 시스템
├── hud.py                   # HUD UI
├── game_state.py            # 상태 관리 (FSM)
├── taunt.py                 # 뻐큐 도발 시스템
├── items.py                 # 아이템 시스템
├── npc.py                   # NPC 차량/보행자
├── effects.py               # 파티클 + 화면 이펙트
├── audio_manager.py         # 사운드 관리
├── settings.py              # 게임 설정 (민감도 등)
├── models/
│   ├── bike.obj
│   ├── wheel.obj
│   ├── car_sedan.obj
│   ├── car_truck.obj
│   ├── cone.obj
│   ├── barricade.obj
│   ├── building_small.obj
│   ├── building_tall.obj
│   ├── tree.obj
│   ├── ramp.obj
│   └── road_segment.obj
├── textures/
│   └── palette.png
├── audio/
│   ├── engine_loop.ogg
│   ├── race_music.ogg
│   ├── wheelie_start.ogg
│   ├── wheelie_loop.ogg
│   ├── crash.ogg
│   ├── taunt.ogg
│   ├── warning_beep.ogg
│   ├── item_pickup.ogg
│   └── boost.ogg
├── GDD.md                   # 게임 기획서
├── REFERENCES.md            # 코드 레퍼런스
├── ARCHITECTURE.md          # 이 파일
└── requirements.txt         # 의존성
```
