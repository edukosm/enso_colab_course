import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ✅ 페이지 설정
st.set_page_config(page_title="기후 탐험 미션", page_icon="🌍", layout="wide")

# ✅ CSS 스타일
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e');
    background-size: cover;
    background-attachment: fixed;
}
.block-container {
    background: rgba(255, 255, 255, 0.85);
    padding: 20px;
    border-radius: 12px;
}
.stButton button {
    background-color: black !important;
    color: white !important;
    font-size: 18px;
    border-radius: 8px;
    padding: 10px 20px;
}
</style>
""", unsafe_allow_html=True)

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("oni_month_20250821.csv")
    df['날짜'] = pd.to_datetime(df['날짜'].str.replace('﻿',''), format='%Y년 %m월')
    return df

enso = load_data()

# ✅ 세션 상태 초기화
if "team" not in st.session_state:
    st.session_state.team = None
if "mission" not in st.session_state:
    st.session_state.mission = 0
if "progress" not in st.session_state:
    st.session_state.progress = {}

# ✅ 팀 이름 입력
if st.session_state.team is None:
    st.title("🌍 기후 탐험 미션")
    st.subheader("팀 이름을 입력하고 시작하세요!")
    team_name = st.text_input("팀 이름")
    if st.button("시작하기") and team_name:
        st.session_state.team = team_name
        st.session_state.progress[team_name] = {"mission": 0, "time": datetime.now()}
        st.rerun()
else:
    st.title(f"🌍 기후 탐험 - {st.session_state.team}팀")

    # ✅ 미션 페이지
    mission = st.session_state.mission

    if mission == 0:
        st.header("미션 1: 데이터 탐험")
        st.write("다음 표를 보고, 가장 최근 달의 '수온 평균' 값을 입력하세요.")
        # ✅ 최근 6개월 데이터
        recent_df = enso.sort_values(by="날짜", ascending=False).head(6)
        st.dataframe(recent_df)

        answer = st.text_input("가장 최근 달의 수온 평균 값은?")
        if st.button("제출"):
            correct = round(recent_df.iloc[0]['nino3.4 수온 평균'], 2)
            if abs(float(answer) - correct) < 0.1:
                st.success("정답입니다!")
                st.session_state.mission += 1
                st.progress(25)
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")

    elif mission == 1:
        st.header("미션 2: 그래프 분석")
        st.write("아래 슬라이더로 연도를 선택하고, 해당 연도의 수온 변화를 관찰하세요.")
        years = sorted(enso['날짜'].dt.year.unique())
        year = st.slider("연도 선택", min_value=min(years), max_value=max(years), value=max(years))
        filtered = enso[enso['날짜'].dt.year == year]

        fig = px.line(filtered, x="날짜", y="nino3.4 수온 평균", title=f"{year}년 수온 변화")
        st.plotly_chart(fig)

        st.write("그래프를 보고, 가장 높은 수온을 입력하세요.")
        answer = st.text_input("최고 수온 값?")
        if st.button("제출"):
            correct = round(filtered['nino3.4 수온 평균'].max(), 2)
            if abs(float(answer) - correct) < 0.1:
                st.success("정답입니다!")
                st.session_state.mission += 1
                st.progress(50)
                st.rerun()
            else:
                st.error("틀렸습니다.")

    elif mission == 2:
        st.header("미션 3: 패턴 찾기")
        st.write("아래 드롭다운에서 월을 선택하고, 해당 월의 평균 수온을 확인하세요.")
        month = st.selectbox("월 선택", list(range(1, 13)))
        month_data = enso[enso['날짜'].dt.month == month]
        avg_temp = round(month_data['nino3.4 수온 평균'].mean(), 2)
        st.write(f"이 월의 평균 수온은 **{avg_temp}°C** 입니다.")
        answer = st.text_input("가장 낮은 월 평균 수온은 몇 월일까요?")
        if st.button("제출"):
            min_month = enso.groupby(enso['날짜'].dt.month)['nino3.4 수온 평균'].mean().idxmin()
            if int(answer) == int(min_month):
                st.success("정답입니다!")
                st.session_state.mission += 1
                st.progress(75)
                st.rerun()
            else:
                st.error("틀렸습니다.")

    elif mission == 3:
        st.header("✅ 최종 미션 완료!")
        st.subheader("팀 순위는?")
        st.write("아직 로컬 상태에서만 기록됩니다.")
        st.write(st.session_state.progress)
        if st.button("처음으로"):
            st.session_state.mission = 0
            st.rerun()
