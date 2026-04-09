"""MediaPipe 손 추적 데몬 스레드"""
import threading
import queue
import cv2
import mediapipe as mp
from gesture import classify_gesture


class HandTracker(threading.Thread):
    def __init__(self, gesture_queue, camera_index=0):
        super().__init__(daemon=True)
        self.gesture_queue = gesture_queue
        self.camera_index = camera_index
        self.running = True
        self.frame = None  # HUD용 웹캠 프레임 공유
        self.frame_lock = threading.Lock()

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=0,
        )

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            # 좌우 반전 (거울 모드)
            frame = cv2.flip(frame, 1)

            # BGR → RGB (MediaPipe 필수)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            # 제스처 분류
            gesture = classify_gesture(results)

            # 웹캠 프레임 저장 (HUD용)
            with self.frame_lock:
                self.frame = frame

            # Queue에 최신 결과만 유지
            if not self.gesture_queue.empty():
                try:
                    self.gesture_queue.get_nowait()
                except queue.Empty:
                    pass
            try:
                self.gesture_queue.put_nowait(gesture)
            except queue.Full:
                pass

        cap.release()
        hands.close()

    def stop(self):
        self.running = False

    def get_frame(self):
        with self.frame_lock:
            return self.frame
