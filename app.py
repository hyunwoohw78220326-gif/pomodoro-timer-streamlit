import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time

# ------------------------------
# 세션 상태 초기화
# ------------------------------
if 'subjects' not in st.session_state:
    st.session_state.subjects = {
        '국어': 0, '영어': 0, '수학': 0, '과학': 0,
        '사회': 0, '한문': 0, '역사': 0, '기타': 0
    }

if 'pomodoro_sec' not in st.session_state:
    st.session_state.pomodoro_sec = 1500  # 테스트용 30초
if 'break_sec' not in st.session_state:
    st.session_state.break_sec = 300      # 테스트용 5초

if 'running' not in st.session_state:
    st.session_state.running = False
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = '국어'
if 'on_break' not in st.session_state:
    st.session_state.on_break = False
if 'day_records' not in st.session_state:
    st.session_state.day_records = []

if 'timer_sec' not in st.session_state:
    st.session_state.timer_sec = st.session_state.pomodoro_sec
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# ------------------------------
# 자동 갱신 (1초)
# ------------------------------
st_autorefresh(interval=1000, key="timer_refresh")

# ------------------------------
# 함수 정의
# ------------------------------
def format_time(sec):
    hrs, rem = divmod(int(sec), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def update_timer():
    if st.session_state.running:
        now = time.time()
        elapsed = now - st.session_state.last_update
        st.session_state.last_update = now

        # 타이머 감소
        st.session_state.timer_sec -= elapsed
        # 현재 과목에 누적
        st.session_state.subjects[st.session_state.current_subject] += elapsed

        # 타이머가 0 이하가 되면 전환
        while st.session_state.timer_sec <= 0:
            if st.session_state.on_break:
                st.session_state.timer_sec += st.session_state.pomodoro_sec
                st.session_state.on_break = False
                st.success(f"{st.session_state.current_subject} 집중 시작!")
            else:
                st.session_state.timer_sec += st.session_state.break_sec
                st.session_state.on_break = True
                st.warning(f"{st.session_state.current_subject} 휴식 시간!")

def stop_timer():
    st.session_state.running = False

def start_timer():
    if not st.session_state.running:
        st.session_state.running = True
        st.session_state.last_update = time.time()

def change_subject(subject):
    st.session_state.current_subject = subject

def total_time_today():
    return sum(st.session_state.subjects.values())

def daily_grade(total_sec):
    if total_sec == 0:
        return 'F'
    elif total_sec < 1800:
        return 'D'
    elif total_sec < 3600:
        return 'C'
    elif total_sec < 7200:
        return 'B'
    else:
        return 'A'

def monthly_grade(daily_av_sec):
    if daily_av_sec == 0:
        return 'F'
    elif daily_av_sec < 60:
        return 'D'
    elif daily_av_sec < 1800:
        return 'C'
    elif daily_av_sec < 3600:
        return 'B'
    else:
        return 'A'

# ------------------------------
# 화면 구성
# ------------------------------
st.title("뽀모도로 과목 타이머 ⏱️")


# 총 공부 시간
total_sec = total_time_today()
st.subheader(f"총 공부 시간: {format_time(total_sec)}")

# 과목 선택
st.subheader("과목 선택")
cols = st.columns(4)
subjects_list = list(st.session_state.subjects.keys())
for i, subject in enumerate(subjects_list):
    if cols[i % 4].button(subject):
        change_subject(subject)

# 현재 과목 상태
status_text = "휴식 중" if st.session_state.on_break else "집중 중"
st.write(f"현재 과목: {st.session_state.current_subject} ({status_text})")
st.write(f"타이머: {format_time(st.session_state.timer_sec)}")

if not st.session_state.running:
    if st.button("시작"):
        start_timer()

# 정지 버튼
if st.button("정지"):
    stop_timer()

# 과목별 누적 시간
st.subheader("과목별 누적 시간")
for subject, sec in st.session_state.subjects.items():
    st.write(f"{subject}: {format_time(sec)}")

# 하루 평가
st.markdown("---")
st.subheader("오늘 하루 평가")
st.write(daily_grade(total_sec))

# 월간 평균 평가
st.markdown("---")
st.subheader("월간 평균 평가")
if len(st.session_state.day_records) > 0:
    avg_sec = sum(st.session_state.day_records)/len(st.session_state.day_records)
    st.write(monthly_grade(avg_sec))
else:
    st.write("기록 없음")

# 오늘 기록 저장
if st.button("오늘 기록 저장"):
    st.session_state.day_records.append(total_sec)
    st.success("오늘 공부 시간 기록 완료!")

# ------------------------------
# 타이머 업데이트
# ------------------------------
update_timer()
