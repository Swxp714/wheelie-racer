"""바이크 엔티티 - 물리, 윌리, 사망/리스폰"""
import random
from ursina import Entity, Vec3, color, time, held_keys


class Bike(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(249, 88, 88),
            scale=(0.8, 0.5, 1.5),
            position=(0, 0.5, 0),
            **kwargs,
        )

        # 뒷바퀴
        self.rear_wheel = Entity(
            parent=self,
            model='sphere',
            color=color.rgb(51, 51, 51),
            scale=(0.7, 0.7, 0.7),
            position=(0, -0.4, -0.5),
        )
        # 앞바퀴
        self.front_wheel = Entity(
            parent=self,
            model='sphere',
            color=color.rgb(51, 51, 51),
            scale=(0.7, 0.7, 0.7),
            position=(0, -0.4, 0.5),
        )

        # 물리 파라미터
        self.speed = 0
        self.base_speed = 15
        self.max_speed = 40
        self.acceleration = 12
        self.deceleration = 8
        self.brake_power = 20

        # 윌리
        self.wheelie_angle = 0       # 0 ~ 90
        self.wheelie_target = 0
        self.wheelie_speed_mult = 1.0
        self.balance_wobble = 0

        # 스티어링
        self.lean_angle = 0          # -35 ~ 35
        self.steer_value = 0

        # 상태
        self.is_dead = False
        self.death_timer = 0
        self.respawn_pos = Vec3(0, 0.5, 0)
        self.score = 0
        self.distance = 0

        # 키보드 모드 (MediaPipe 실패 시)
        self.keyboard_mode = False

    def apply_gesture(self, gesture):
        """제스처 데이터 적용"""
        if self.is_dead:
            return

        if not gesture.hand_detected:
            self.keyboard_mode = True
            return

        self.keyboard_mode = False

        # 스티어링
        self.steer_value = gesture.steer

        # 윌리 높이 → 타겟 각도 (0~90)
        self.wheelie_target = gesture.wheelie_height * 90

        # 주먹 = 가속
        if gesture.is_fist:
            self.speed += self.acceleration * time.dt
        # 펼침 = 브레이크
        elif gesture.is_open:
            self.speed -= self.brake_power * time.dt
        else:
            # 자연 감속
            self.speed -= self.deceleration * 0.3 * time.dt

    def apply_keyboard(self):
        """키보드 폴백"""
        if self.is_dead:
            return

        # 가속/브레이크
        if held_keys['w'] or held_keys['up arrow']:
            self.speed += self.acceleration * time.dt
        elif held_keys['s'] or held_keys['down arrow']:
            self.speed -= self.brake_power * time.dt
        else:
            self.speed -= self.deceleration * 0.3 * time.dt

        # 스티어링
        steer = 0
        if held_keys['a'] or held_keys['left arrow']:
            steer = -1
        elif held_keys['d'] or held_keys['right arrow']:
            steer = 1
        self.steer_value = steer

        # 윌리
        if held_keys['space']:
            self.wheelie_target = min(self.wheelie_target + 120 * time.dt, 90)
        else:
            self.wheelie_target = max(self.wheelie_target - 90 * time.dt, 0)

    def update(self):
        dt = time.dt
        if dt == 0:
            return

        # 사망 처리
        if self.is_dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.respawn()
            return

        # 키보드 모드
        if self.keyboard_mode:
            self.apply_keyboard()

        # === 속도 ===
        self.speed = max(0, min(self.speed, self.max_speed))

        # 윌리 속도 보너스
        if self.wheelie_angle < 20:
            self.wheelie_speed_mult = 1.0
        elif self.wheelie_angle < 40:
            self.wheelie_speed_mult = 1.2
        elif self.wheelie_angle < 60:
            self.wheelie_speed_mult = 1.5
        elif self.wheelie_angle < 75:
            self.wheelie_speed_mult = 2.0
        else:
            self.wheelie_speed_mult = 2.5

        effective_speed = self.speed * self.wheelie_speed_mult

        # === 윌리 각도 ===
        # 타겟 각도로 부드럽게 이동
        diff = self.wheelie_target - self.wheelie_angle
        self.wheelie_angle += diff * 5 * dt

        # 60도 이상이면 흔들림 추가
        if self.wheelie_angle > 60:
            wobble_strength = (self.wheelie_angle - 60) / 30  # 0~1
            self.balance_wobble = random.uniform(-wobble_strength, wobble_strength) * 15
        else:
            self.balance_wobble = 0

        # 사망 판정 (85도 이상)
        if self.wheelie_angle >= 85:
            self.die()
            return

        # === 스티어링 ===
        turn_reduction = 1.0 - (effective_speed / self.max_speed) * 0.5
        target_lean = self.steer_value * 35 * turn_reduction
        self.lean_angle += (target_lean - self.lean_angle) * 5 * dt

        # === 이동 ===
        import math
        self.z += effective_speed * dt
        self.x += math.sin(math.radians(self.lean_angle)) * effective_speed * 0.03

        # X 범위 제한 (도로 폭)
        self.x = max(-4, min(4, self.x))

        # === 비주얼 회전 ===
        self.rotation_x = -(self.wheelie_angle + self.balance_wobble)
        self.rotation_z = -self.lean_angle * 0.5

        # === 점수 ===
        self.distance = self.z
        self.score = int(self.z * 10)

    def die(self):
        """사망 처리"""
        self.is_dead = True
        self.death_timer = 2.0
        self.speed = 0
        self.rotation_x = -110  # 뒤로 넘어짐 비주얼

    def respawn(self):
        """리스폰"""
        self.is_dead = False
        self.speed = 0
        self.wheelie_angle = 0
        self.wheelie_target = 0
        self.lean_angle = 0
        self.balance_wobble = 0
        self.rotation_x = 0
        self.rotation_z = 0
        self.y = 0.5
        # 현재 위치에서 리스폰 (점수 유지)
        self.respawn_pos = Vec3(0, 0.5, self.z)
        self.x = 0
