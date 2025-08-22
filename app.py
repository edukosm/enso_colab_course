import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="기후 데이터 미션 챌린지", layout="wide")

# --- CSS (배경 & 카드 스타일 & 버튼) ---
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
}
.block-container {
    color: black;
}
.mission-card {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.stButton > button {
    background-color: black;
    color: white;
    font-weight: bold;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 데이터 로드 ---
@st.cache_data
def load_data():
    df = pd.read_csv("ocean_data.csv", encoding="utf-8-sig")
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
    return df

df = load_data()

# --- 세션 상태 초기화 ---
if "team_name" not in st.session_state:
    st.session_state.team_name = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_mission" not in st.session_state:
    st.session_state.current_mission = 1
if "finished" not in st.session_state:
    st.session_state.finished = False

# --- 헤더 ---
st.title("🌊 기후 데이터 탐험 미션")

# 진행상황 표시
if st.session_state.team_name:
    st.subheader(f"팀명: {st.session_state.team_name} | 현재 미션: {st.session_state.current_mission}/4")

# --- 팀 이름 입력 ---
if not st.session_state.team_name:
    team = st.text_input("팀 이름을 입력하세요")
    if st.button("시작하기"):
        if team.strip():
            st.session_state.team_name = team
            st.session_state.start_time = time.time()
            st.rerun()

# --- 미션 1 ---
elif st.session_state.current_mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.header("미션 1: 데이터 탐색")
    st.write("다음 표는 바다 표면 온도 데이터를 나타냅니다. 아래 질문에 답하세요.")
    
    # 전체 데이터 표시
    st.dataframe(df.head(15))
    
    # 질문
    st.write("질문: 1998년 7월의 바다 표면 온도는 몇 도였나요?")
    answer = st.text_input("정답을 입력하세요 (소수점 한 자리까지)")
    
    if st.button("정답 제출"):
        correct_value = round(df[(df['Year'] == 1998) & (df['Month'] == 7)]['온도'].values[0], 1)
        if answer.strip() == str(correct_value):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.current_mission = 2
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도해보세요!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 미션 2 ---
elif st.session_state.current_mission == 2:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.header("미션 2: 온도 변화 시각화")
    st.write("아래 그래프는 특정 연도의 온도 변화를 보여줍니다. 연도를 선택하세요.")
    
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_selected = st.slider("연도를 선택하세요", min_year, max_year, 2000)
    
    filtered = df[df['Year'] == year_selected]
    fig = px.line(filtered, x="date", y="온도", title=f"{year_selected}년 월별 바다 표면 온도")
    st.plotly_chart(fig)
    
    question = f"질문: {year_selected}년 중 가장 높은 온도는 몇 도인가요?"
    st.write(question)
    answer = st.text_input("정답을 입력하세요")
    
    if st.button("정답 제출"):
        correct_value = round(filtered['온도'].max(), 1)
        if answer.strip() == str(correct_value):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.current_mission = 3
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 미션 3 ---
elif st.session_state.current_mission == 3:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.header("미션 3: 조건 검색")
    st.write("슬라이더로 온도 조건을 설정하고 데이터를 확인하세요.")
    
    temp_min, temp_max = float(df['온도'].min()), float(df['온도'].max())
    temp_range = st.slider("온도 범위를 선택하세요", temp_min, temp_max, (temp_min, temp_max))
    
    filtered = df[(df['온도'] >= temp_range[0]) & (df['온도'] <= temp_range[1])]
    st.write(f"조건에 맞는 데이터 개수: {len(filtered)}")
    
    st.dataframe(filtered.head(10))
    
    st.write("질문: 조건을 (24~26도)로 설정했을 때 데이터는 몇 개?")
    answer = st.text_input("정답을 입력하세요 (숫자)")
    
    if st.button("정답 제출"):
        correct_count = len(df[(df['온도'] >= 24) & (df['온도'] <= 26)])
        if answer.strip() == str(correct_count):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.current_mission = 4
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 미션 4 ---
elif st.session_state.current_mission == 4:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.header("미션 4: 전체 평균 계산")
    st.write("전체 기간의 평균 바다 표면 온도를 구하세요.")
    
    answer = st.text_input("정답을 입력하세요 (소수점 한 자리까지)")
    
    if st.button("정답 제출"):
        correct_value = round(df['온도'].mean(), 1)
        if answer.strip() == str(correct_value):
            st.success("축하합니다! 모든 미션 완료!")
            st.session_state.finished = True
            st.session_state.end_time = time.time()
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 완료 화면 ---
elif st.session_state.finished:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.header("🎉 모든 미션 완료!")
    total_time = round(st.session_state.end_time - st.session_state.start_time, 1)
    st.write(f"총 소요 시간: {total_time}초")
    st.markdown('</div>', unsafe_allow_html=True)
