"""WHEELIE RACER - 메인 진입점"""
import queue
from ursina import (
    Ursina, Entity, camera, color, time, window,
    held_keys, Text, Vec3, application,
)

from hand_tracker import HandTracker
from gesture import GestureData
from bike import Bike
from track import Track

# === 앱 초기화 ===
app = Ursina(title='WHEELIE RACER', borderless=False, size=(1280, 720))
window.color = color.rgb(133, 210, 254)  # 하늘색 배경
window.fps_counter.enabled = True

# === MediaPipe 스레드 시작 ===
gesture_queue = queue.Queue(maxsize=1)
tracker = HandTracker(gesture_queue)
tracker.start()

# === 게임 오브젝트 ===
bike = Bike()
track = Track()

# === 카메라 설정 ===
camera.orthographic = True
camera.fov = 20
camera.position = (0, 15, -10)
camera.rotation_x = 50

# === 조명 ===
from ursina import DirectionalLight, AmbientLight
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

# === HUD ===
score_text = Text(
    text='SCORE: 0',
    position=(-0.85, 0.45),
    scale=1.5,
    color=color.rgb(255, 214, 0),
    font='VeraMono.ttf',
)

speed_text = Text(
    text='0 km/h',
    position=(0.55, 0.45),
    scale=1.2,
    color=color.white,
    font='VeraMono.ttf',
)

wheelie_text = Text(
    text='WHEELIE: 0%',
    position=(0.55, 0.38),
    scale=1,
    color=color.rgb(76, 175, 80),
    font='VeraMono.ttf',
)

status_text = Text(
    text='[HAND TRACKING]',
    position=(-0.85, 0.38),
    scale=0.8,
    color=color.rgb(76, 175, 80),
    font='VeraMono.ttf',
)

death_text = Text(
    text='',
    position=(0, 0.05),
    scale=3,
    color=color.rgb(229, 57, 53),
    font='VeraMono.ttf',
    origin=(0, 0),
)

taunt_text = Text(
    text='',
    position=(0, -0.1),
    scale=4,
    color=color.rgb(168, 85, 247),
    font='VeraMono.ttf',
    origin=(0, 0),
)

# === 윌리 게이지 바 ===
gauge_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgb(34, 34, 68),
    scale=(0.25, 0.02),
    position=(0.68, 0.35),
)
gauge_fill = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgb(76, 175, 80),
    scale=(0, 0.016),
    position=(0.555, 0.35),
    origin=(-0.5, 0),
)

# === 도발 쿨다운 ===
taunt_cooldown = 0
taunt_display_timer = 0

# === 마지막 제스처 상태 ===
last_gesture = GestureData()


def update():
    global taunt_cooldown, taunt_display_timer, last_gesture

    dt = time.dt
    if dt == 0:
        return

    # === MediaPipe 제스처 읽기 ===
    try:
        gesture = gesture_queue.get_nowait()
        last_gesture = gesture
    except queue.Empty:
        gesture = last_gesture

    # 바이크에 제스처 적용
    bike.apply_gesture(gesture)

    # 바이크 업데이트 (내부에서 물리 처리)
    # bike.update()는 Ursina가 자동 호출

    # === 트랙 업데이트 ===
    track.update(bike.z)

    # === 충돌 체크 ===
    if not bike.is_dead and track.check_collision(bike.position):
        bike.die()

    # === 카메라 팔로우 ===
    target_y = 15
    target_z = bike.z - 10
    # 윌리 시 살짝 줌아웃
    if bike.wheelie_angle > 40:
        target_y += (bike.wheelie_angle - 40) * 0.05
    camera.y += (target_y - camera.y) * 3 * dt
    camera.z += (target_z - camera.z) * 5 * dt
    camera.x += (bike.x * 0.3 - camera.x) * 3 * dt

    # 위험 구간 화면 흔들림
    if bike.wheelie_angle > 60 and not bike.is_dead:
        import random
        shake = (bike.wheelie_angle - 60) / 100
        camera.x += random.uniform(-shake, shake)
        camera.y += random.uniform(-shake, shake)

    # === HUD 업데이트 ===
    score_text.text = f'SCORE: {bike.score}'
    speed_text.text = f'{int(bike.speed * bike.wheelie_speed_mult * 3.6)} km/h'

    # 윌리 게이지
    wp = bike.wheelie_angle / 90
    wheelie_text.text = f'WHEELIE: {int(wp * 100)}%'
    gauge_fill.scale_x = 0.25 * wp

    if wp < 0.45:
        gauge_fill.color = color.rgb(76, 175, 80)    # 초록
        wheelie_text.color = color.rgb(76, 175, 80)
    elif wp < 0.7:
        gauge_fill.color = color.rgb(255, 214, 0)     # 노랑
        wheelie_text.color = color.rgb(255, 214, 0)
    elif wp < 0.85:
        gauge_fill.color = color.rgb(251, 140, 0)     # 주황
        wheelie_text.color = color.rgb(251, 140, 0)
    else:
        gauge_fill.color = color.rgb(229, 57, 53)     # 빨강
        wheelie_text.color = color.rgb(229, 57, 53)

    # 손 감지 상태
    if gesture.hand_detected:
        status_text.text = '[HAND TRACKING]'
        status_text.color = color.rgb(76, 175, 80)
    else:
        status_text.text = '[KEYBOARD MODE]'
        status_text.color = color.rgb(251, 140, 0)

    # 사망 텍스트
    if bike.is_dead:
        death_text.text = 'WRECKED!'
    else:
        death_text.text = ''

    # === 도발 ===
    taunt_cooldown = max(0, taunt_cooldown - dt)
    taunt_display_timer = max(0, taunt_display_timer - dt)

    if gesture.is_taunt and taunt_cooldown <= 0 and not bike.is_dead:
        taunt_cooldown = 3.0
        taunt_display_timer = 1.5

    if taunt_display_timer > 0:
        taunt_text.text = '* TAUNT! *'
    else:
        taunt_text.text = ''


def input(key):
    """키 입력 처리"""
    if key == 'escape':
        application.quit()

    # F키 = 뻐큐 (키보드 모드)
    global taunt_cooldown, taunt_display_timer
    if key == 'f' and taunt_cooldown <= 0 and not bike.is_dead:
        taunt_cooldown = 3.0
        taunt_display_timer = 1.5


print("=" * 50)
print("  WHEELIE RACER")
print("  Hand Tracking: ON (webcam)")
print("  Keyboard Fallback: WASD/Arrows + Space + F")
print("=" * 50)

app.run()
