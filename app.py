import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time
import os

# ✅ 기본 설정
rcParams['font.family'] = 'DejaVu Sans'
st.set_page_config(page_title="기후 미션 챌린지", layout="wide")

# ✅ CSS 스타일
page_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
}
.fixed-title {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.9);
    text-align: center;
    padding: 15px;
    font-size: 28px;
    font-weight: bold;
    z-index: 1000;
    color: black;
}
.card {
    background: rgba(255, 255, 255, 0.9);
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
}
div.stButton > button {
    background-color: black !important;
    color: white !important;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    padding: 10px 20px;
}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)
st.markdown('<div class="fixed-title">🌍 기후 미션 챌린지</div>', unsafe_allow_html=True)
st.write("\n\n\n")

# ✅ 데이터 로드
df = pd.read_csv("oni_month_20250821.csv")
df.columns = df.columns.str.strip()
df['날짜'] = df['날짜'].str.replace("﻿","").str.strip()
df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월', errors='coerce')
df = df.dropna(subset=['date'])

# ✅ 진행 상황 CSV
progress_file = "progress.csv"
if not os.path.exists(progress_file):
    pd.DataFrame(columns=["team", "mission", "start_time", "end_time"]).to_csv(progress_file, index=False)

# ✅ 세션 상태
if "team_name" not in st.session_state:
    st.session_state["team_name"] = None
if "mission" not in st.session_state:
    st.session_state["mission"] = 0
if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if "hints" not in st.session_state:
    st.session_state["hints"] = []

# ✅ 진행 상황 로드/저장
def load_progress():
    return pd.read_csv(progress_file)

def save_progress(team, mission, start_time=None, end_time=None):
    progress = load_progress()
    if team in progress["team"].values:
        progress.loc[progress["team"] == team, ["mission", "end_time"]] = [mission, end_time]
    else:
        progress = pd.concat([progress, pd.DataFrame([[team, mission, start_time, end_time]], columns=progress.columns)], ignore_index=True)
    progress.to_csv(progress_file, index=False)

# ✅ 팀 이름 입력 화면
if st.session_state["team_name"] is None:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("팀 이름을 입력하세요")
        team_name = st.text_input("팀 이름:")
        if st.button("게임 시작"):
            if team_name.strip():
                st.session_state["team_name"] = team_name.strip()
                st.session_state["mission"] = 1
                st.session_state["start_time"] = time.time()
                save_progress(team_name, 1, start_time=time.time())
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ✅ 사이드바: 현황판
    st.sidebar.header("📊 전체 팀 현황")
    progress = load_progress()
    progress_display = progress.copy()
    progress_display["mission"] = progress_display["mission"].astype(int)
    st.sidebar.table(progress_display.sort_values(by="mission", ascending=False))

    # ✅ 진행률
    st.progress(st.session_state["mission"] / 5)
    st.write(f"**현재 미션:** {st.session_state['mission']} / 5")

    mission = st.session_state["mission"]

    # ✅ 미션 1: 데이터 탐험
    if mission == 1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("미션 1: 기후 데이터 탐험")
        st.write("다음 표는 특정 해양 지수 데이터입니다. 슬라이더로 기간을 조절해 보세요.")
        min_year = df['date'].dt.year.min()
        max_year = df['date'].dt.year.max()
        year_range = st.slider("연도 범위 선택", min_value=int(min_year), max_value=int(max_year), value=(int(min_year), int(max_year)))
        filtered_df = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
        
        # ✅ 그래프
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(filtered_df['date'], filtered_df['지수'], color="blue")
        ax.set_title("기간별 지수 변화")
        ax.set_xlabel("날짜")
        ax.set_ylabel("지수")
        st.pyplot(fig)

        # ✅ 데이터 표
        st.dataframe(filtered_df[['날짜', '지수']])

        # ✅ 정답 입력
        answer1 = st.text_input("질문: 지수가 가장 높은 해는 언제인가?")
        if st.button("정답 제출"):
            if "1997" in answer1 or "1998" in answer1:
                st.success("정답! 힌트: 첫 글자는 E")
                st.session_state["hints"].append("E")
                st.session_state["mission"] = 2
                save_progress(st.session_state["team_name"], 2)
                st.experimental_rerun()
            else:
                st.error("다시 시도하세요!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 미션 2: 원인 맞추기
    elif mission == 2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("미션 2: 원인 찾기")
        st.write("이 현상은 주로 무엇 때문에 발생할까요?")
        answer2 = st.text_input("정답 입력:")
        if st.button("정답 제출", key="m2"):
            if "수온" in answer2 or "해수면" in answer2:
                st.success("정답! 힌트: 두 번째 글자는 N")
                st.session_state["hints"].append("N")
                st.session_state["mission"] = 3
                save_progress(st.session_state["team_name"], 3)
                st.experimental_rerun()
            else:
                st.error("다시 시도하세요!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 미션 3: 데이터 분석 (슬라이더 조작)
    elif mission == 3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("미션 3: 평균값 계산")
        st.write("슬라이더로 연도 범위를 선택하고, 평균 지수를 확인하세요.")
        range_m3 = st.slider("기간 선택", int(min_year), int(max_year), (2000, 2010))
        df_m3 = df[(df['date'].dt.year >= range_m3[0]) & (df['date'].dt.year <= range_m3[1])]
        avg_val = df_m3['지수'].mean()
        st.write(f"선택 구간 평균 지수: **{avg_val:.2f}**")
        answer3 = st.text_input("질문: 평균 지수가 양수라면 어떤 상태인가?")
        if st.button("정답 제출", key="m3"):
            if "따뜻" in answer3 or "양" in answer3:
                st.success("정답! 힌트: 세 번째 글자는 S")
                st.session_state["hints"].append("S")
                st.session_state["mission"] = 4
                save_progress(st.session_state["team_name"], 4)
                st.experimental_rerun()
            else:
                st.error("다시 시도하세요!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 미션 4: 지도 해석
    elif mission == 4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("미션 4: 전 세계 영향")
        st.write("이 현상이 전 세계에 미치는 영향을 한 가지 적으세요.")
        answer4 = st.text_input("정답 입력:")
        if st.button("정답 제출", key="m4"):
            if "가뭄" in answer4 or "홍수" in answer4 or "폭우" in answer4:
                st.success("정답! 힌트: 네 번째 글자는 O")
                st.session_state["hints"].append("O")
                st.session_state["mission"] = 5
                save_progress(st.session_state["team_name"], 5)
                st.experimental_rerun()
            else:
                st.error("다시 시도하세요!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ 최종 미션: 암호 입력
    elif mission == 5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("최종 암호 도전!")
        st.write("지금까지 얻은 힌트를 조합하세요.")
        st.write(f"힌트: {' - '.join(st.session_state['hints'])}")
        final_answer = st.text_input("최종 암호 입력:")
        if st.button("제출", key="final"):
            if final_answer.strip().upper() == "ENSO":
                st.balloons()
                st.success("축하합니다! 모든 미션 완료!")
                save_progress(st.session_state["team_name"], 5, end_time=time.time())
        st.subheader("🏆 현재 랭킹")
        progress = load_progress()
        progress["duration"] = progress.apply(lambda x: (x["end_time"] - x["start_time"]) if pd.notna(x["end_time"]) else None, axis=1)
        leaderboard = progress.dropna(subset=["duration"]).sort_values(by="duration")
        leaderboard["순위"] = range(1, len(leaderboard)+1)
        st.table(leaderboard[["순위","team", "mission", "duration"]])
        st.markdown('</div>', unsafe_allow_html=True)
