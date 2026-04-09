"""제스처 데이터 클래스 + 분류 로직"""
import math
from dataclasses import dataclass, field

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]


@dataclass
class GestureData:
    steer: float = 0.0            # -1 (좌) ~ 1 (우)
    wheelie_height: float = 0.0   # 0 (내림) ~ 1 (최대)
    is_fist: bool = False         # 가속
    is_open: bool = False         # 브레이크
    is_taunt: bool = False        # 뻐큐
    hand_detected: bool = False


def get_finger_states(landmarks):
    """각 손가락 펴짐 상태 반환 [엄지, 검지, 중지, 약지, 새끼]"""
    states = []
    for tip, pip_joint in zip(FINGER_TIPS, FINGER_PIPS):
        states.append(landmarks[tip].y < landmarks[pip_joint].y)
    # 엄지는 X축
    thumb = landmarks[4].x < landmarks[3].x
    return [thumb] + states


def get_hand_tilt(landmarks):
    """손 기울기 각도 계산 (스티어링) -> -1.0 ~ 1.0"""
    wrist = landmarks[0]
    mcp = landmarks[9]
    angle = math.atan2(mcp.y - wrist.y, mcp.x - wrist.x)
    deg = math.degrees(angle)
    # -90도(수직)를 기준으로 좌우 매핑
    steer = (deg + 90) / 45  # 대략 -1 ~ 1 범위
    return max(-1.0, min(1.0, steer))


def get_hand_height(landmarks):
    """손 높이 반환 (0=하단, 1=상단)"""
    return 1.0 - landmarks[0].y


def is_fist(landmarks):
    """모든 손가락 접힘 = 주먹 = 가속"""
    states = get_finger_states(landmarks)
    return not any(states[1:])  # 검지~새끼 모두 접힘


def is_open_hand(landmarks):
    """모든 손가락 펴짐 = 펼침 = 브레이크"""
    states = get_finger_states(landmarks)
    return all(states[1:])  # 검지~새끼 모두 펴짐


def is_middle_finger(landmarks):
    """중지만 펴지고 나머지 접힘 = 뻐큐"""
    states = get_finger_states(landmarks)
    return (not states[1] and     # 검지 접힘
            states[2] and         # 중지 펴짐
            not states[3] and     # 약지 접힘
            not states[4])        # 새끼 접힘


def classify_gesture(results):
    """MediaPipe 결과 → GestureData 변환"""
    gesture = GestureData()

    if not results or not results.multi_hand_landmarks:
        return gesture

    hands = results.multi_hand_landmarks
    gesture.hand_detected = True

    if len(hands) >= 1:
        lm = hands[0].landmark

        # 스티어링 (첫 번째 손 기울기)
        gesture.steer = get_hand_tilt(lm)

        # 윌리 높이 (손 높이)
        gesture.wheelie_height = get_hand_height(lm)

        # 주먹 = 가속
        if is_fist(lm):
            gesture.is_fist = True

        # 펼침 = 브레이크
        if is_open_hand(lm):
            gesture.is_open = True

    # 오른손 뻐큐 체크 (두 번째 손이 있으면 그쪽도 체크)
    for hand_lm in hands:
        lm = hand_lm.landmark
        if is_middle_finger(lm):
            gesture.is_taunt = True
            break

    # 양손이면 스티어링을 양손 평균으로
    if len(hands) >= 2:
        lm1 = hands[0].landmark
        lm2 = hands[1].landmark
        tilt1 = get_hand_tilt(lm1)
        tilt2 = get_hand_tilt(lm2)
        gesture.steer = (tilt1 + tilt2) / 2.0

        # 윌리 높이도 양손 평균
        h1 = get_hand_height(lm1)
        h2 = get_hand_height(lm2)
        gesture.wheelie_height = (h1 + h2) / 2.0

        # 양손 다 주먹이면 가속
        gesture.is_fist = is_fist(lm1) and is_fist(lm2)
        # 양손 다 펼침이면 브레이크
        gesture.is_open = is_open_hand(lm1) and is_open_hand(lm2)

    return gesture
