"""
Module 1 (AI Gym Trainer) + feeds Module 6 (Pose-to-Performance Analyzer).

Unlike the browser-JS version, pose detection here runs server-side: each
incoming webcam frame is processed with MediaPipe Pose inside a
streamlit-webrtc VideoProcessor, which computes a joint angle and runs the
same rep-counting state machine, then draws the skeleton back onto the frame
you see in the browser.
"""
import time
from datetime import datetime, timezone

import av
import cv2
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase, RTCConfiguration

from utils import api_client

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# landmark indices = [proximal, joint, distal], e.g. hip-knee-ankle
EXERCISE_CONFIG = {
    "squat": {"label": "Squat", "landmarks": (24, 26, 28), "direction": "flex", "enter": 140, "exit": 150},
    "pushup": {"label": "Push-up", "landmarks": (12, 14, 16), "direction": "flex", "enter": 140, "exit": 150},
    "bicep_curl": {"label": "Bicep Curl", "landmarks": (12, 14, 16), "direction": "flex", "enter": 110, "exit": 120},
    "lunge": {"label": "Lunge", "landmarks": (24, 26, 28), "direction": "flex", "enter": 140, "exit": 150},
    "shoulder_press": {"label": "Shoulder Press", "landmarks": (12, 14, 16), "direction": "extend", "enter": 140, "exit": 130},
}

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})


def angle_between(a, b, c):
    import math
    ab = (a.x - b.x, a.y - b.y)
    cb = (c.x - b.x, c.y - b.y)
    dot = ab[0] * cb[0] + ab[1] * cb[1]
    mag_ab = math.hypot(*ab)
    mag_cb = math.hypot(*cb)
    if mag_ab == 0 or mag_cb == 0:
        return 180.0
    cos_angle = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))
    return math.degrees(math.acos(cos_angle))


class PoseProcessor(VideoProcessorBase):
    def __init__(self):
        import threading
        self.lock = threading.Lock()
        self.exercise = "squat"
        self.pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self.reps = []
        self.phase = "rest"
        self.peak_angle = None
        self.current_angle = None
        self.low_visibility = False
        self.start_time = time.time()

    def reset(self):
        with self.lock:
            self.reps = []
            self.phase = "rest"
            self.peak_angle = None
            self.start_time = time.time()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            cfg = EXERCISE_CONFIG[self.exercise]
            ia, ib, ic = cfg["landmarks"]
            a, b, c = landmarks[ia], landmarks[ib], landmarks[ic]

            min_vis = min(a.visibility, b.visibility, c.visibility)
            angle = angle_between(a, b, c)

            with self.lock:
                self.low_visibility = min_vis < 0.5
                self.current_angle = angle
                if not self.low_visibility:
                    self._update_state_machine(angle, cfg)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def _update_state_machine(self, angle, cfg):
        if cfg["direction"] == "flex":
            if angle < cfg["enter"]:
                self.phase = "down"
                self.peak_angle = angle if self.peak_angle is None else min(self.peak_angle, angle)
            elif angle > cfg["exit"] and self.phase == "down":
                self._complete_rep()
        else:
            if angle > cfg["enter"]:
                self.phase = "up"
                self.peak_angle = angle if self.peak_angle is None else max(self.peak_angle, angle)
            elif angle < cfg["exit"] and self.phase == "up":
                self._complete_rep()

    def _complete_rep(self):
        self.reps.append({
            "exercise": self.exercise,
            "joint_angle": self.peak_angle,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.phase = "rest"
        self.peak_angle = None


st.title("🏋️ AI Gym Trainer")
st.caption("Live server-side pose detection (MediaPipe) counts reps and scores your form.")

exercise_key = st.selectbox(
    "Exercise", options=list(EXERCISE_CONFIG.keys()),
    format_func=lambda k: EXERCISE_CONFIG[k]["label"],
)

webrtc_ctx = webrtc_streamer(
    key="workout-pose",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=PoseProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

col1, col2 = st.columns(2)
reset_clicked = col1.button("🔄 Reset Counter")
save_clicked = col2.button("✅ Stop & Save Session")

if webrtc_ctx.video_processor:
    webrtc_ctx.video_processor.exercise = exercise_key
    if reset_clicked:
        webrtc_ctx.video_processor.reset()

stats_placeholder = st.empty()
result_placeholder = st.empty()

if save_clicked and webrtc_ctx.video_processor:
    processor = webrtc_ctx.video_processor
    with processor.lock:
        reps_snapshot = list(processor.reps)
        duration = time.time() - processor.start_time

    form_issues = []
    if not reps_snapshot:
        form_issues.append("no valid reps detected - make sure your full body is visible and try again")

    try:
        result = api_client.submit_workout_session({
            "exercise": exercise_key,
            "reps": reps_snapshot,
            "duration_seconds": duration,
            "form_issues": form_issues,
        })
        with result_placeholder.container(border=True):
            st.subheader("Session Result")
            st.metric("Valid reps counted", result["rep_count"])
            c1, c2 = st.columns(2)
            c1.metric("Form score", f"{result['form_score']}/100")
            c2.metric("Tempo consistency", f"{result['tempo_consistency']}/100")
            for f in result["feedback"]:
                st.write(f"• {f}")
    except RuntimeError as e:
        st.error(str(e))

elif webrtc_ctx.state.playing:
    while webrtc_ctx.state.playing:
        processor = webrtc_ctx.video_processor
        if processor:
            with processor.lock:
                reps = len(processor.reps)
                angle = processor.current_angle
                low_vis = processor.low_visibility
            with stats_placeholder.container():
                c1, c2 = st.columns(2)
                c1.metric("Reps", reps)
                c2.metric("Joint angle", f"{angle:.0f}°" if angle is not None else "-")
                if low_vis:
                    st.warning("⚠ Step back so your full body is visible")
        time.sleep(0.3)
