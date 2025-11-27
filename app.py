import streamlit as st
import time
from datetime import datetime, timedelta

# ------------------------------
# 초기 세팅
# ------------------------------
if 'subjects' not in st.session_state:
    st.session_state.subjects = {
        '국어': 0,
        '영어': 0,
        '수학': 0,
        '과학': 0,
        '사회': 0,
        '한문': 0,
        '역사': 0,
        '기타': 0
    }

if 'pomodoro_sec' not in st.session_state:
    st.session_state.pomodoro_sec = 25*60
if 'break_sec' not in st.session_state:
    st.session_state.break_sec = 5*60
if 'timer_sec' not in st.session_state:
    st.session_state.timer_sec = st.session_state.pomodoro_sec
if 'running' not in st.session_state:
    st.session_state.running = False
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = None
if 'on_break' not in st.session_state:
    st.session_state.on_break = False
if 'day_records' not in st.session_state:
    st.session_state.day_records = []  # 하루 총 공부 시간 기록

# ------------------------------
# 함수 정의
# ------------------------------
def start_subject(subject):
    st.session_state.current_subject = subject
    st.session_state.running = True
    st.session_state.timer_sec = st.session_state.pomodoro_sec
    st.session_state.on_break = False

def stop_timer():
    st.session_state.running = False
    st.session_state.current_subject = None
    st.session_state.on_break = False
    st.session_state.timer_sec = st.session_state.pomodoro_sec

def format_time(sec):
    mins, secs = divmod(sec, 60)
    return f"{mins:02d}:{secs:02d}"

def update_timer():
    if st.session_state.running:
        st.session_state.timer_sec -= 1
        # 과목별 누적 시간 증가
        st.session_state.subjects[st.session_state.current_subject] += 1
        # 타이머 종료 시
        if st.session_state.timer_sec <= 0:
            if st.session_state.on_break:
                st.session_state.timer_sec = st.session_state.pomodoro_sec
                st.session_state.on_break = False
                st.success(f"{st.session_state.current_subject} 집중 시작!")
            else:
                st.session_state.timer_sec = st.session_state.break_sec
                st.session_state.on_break = True
                st.warning(f"{st.session_state.current_subject} 휴식 시간!")

def total_time_today():
    return sum(st.session_state.subjects.values())

def daily_grade(total_sec):
    if total_sec == 0:
        return 'F'
    elif total_sec < 30*60:
        return 'D'
    elif total_sec < 60*60:
        return 'C'
    elif total_sec < 2*60*60:
        return 'B'
    else:
        return 'A'

def monthly_grade(daily_av_sec):
    if daily_av_sec == 0:
        return 'F'
    elif daily_av_sec < 10*60:
        return 'D'
    elif daily_av_sec < 30*60:
        return 'C'
    elif daily_av_sec < 60*60:
        return 'B'
    else:
        return 'A'

# ------------------------------
# 화면 구성
# ------------------------------
st.title("스터디 뽀모도로 타이머 📚")

# 총 공부 시간
total_sec = total_time_today()
st.subheader(f"총 공부 시간: {format_time(total_sec)}")

# 과목별 타이머
st.subheader("과목별 타이머")
for subject, sec in st.session_state.subjects.items():
    col1, col2 = st.columns([2,1])
    with col1:
        st.write(f"{subject}: {format_time(sec)}")
    with col2:
        if st.button(f"시작/{subject}"):
            start_subject(subject)

# 타이머 상태
if st.session_state.running:
    status_text = "휴식 중" if st.session_state.on_break else "집중 중"
    st.write(f"현재 {st.session_state.current_subject}: {status_text} ({format_time(st.session_state.timer_sec)})")
    if st.button("정지"):
        stop_timer()

# 하루 평가
st.markdown("---")
st.subheader("오늘 하루 평가")
st.write(daily_grade(total_sec))

# 월간 평균 평가 (예시: 지난 30일 기록)
st.markdown("---")
st.subheader("월간 평균 평가")
if len(st.session_state.day_records) > 0:
    avg_sec = sum(st.session_state.day_records)/len(st.session_state.day_records)
    st.write(monthly_grade(avg_sec))
else:
    st.write("기록 없음")

# 하루 기록 저장 버튼
if st.button("오늘 기록 저장"):
    st.session_state.day_records.append(total_sec)
    st.success("오늘 공부 시간 기록 완료!")

# ------------------------------
# 자동 업데이트
# ------------------------------
if st.session_state.running:
    time.sleep(1)
    update_timer()
    st.experimental_rerun()
