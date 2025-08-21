import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64

# ✅ 페이지 기본 설정
st.set_page_config(page_title="해양 기후 미션", layout="wide")

# ✅ CSS 스타일 추가 (배경, 카드, 버튼 색상)
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.card {
    background: rgba(255, 255, 255, 0.85);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    color: black;
}
.stButton button {
    background-color: black !important;
    color: white !important;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ 데이터 불러오기
url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
df = pd.read_csv(url)
df['date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))

min_year, max_year = int(df['date'].dt.year.min()), int(df['date'].dt.year.max())

# ✅ 세션 상태 초기화
if 'team_name' not in st.session_state:
    st.session_state.team_name = None
if 'current_mission' not in st.session_state:
    st.session_state.current_mission = 1
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
if 'mission_log' not in st.session_state:
    st.session_state.mission_log = []  # (team, mission, time)

# ✅ CSV 기반 팀 상태 저장 (임시로 session에서만)
progress_data = {}

# ✅ 제목
st.markdown("<h1 style='text-align: center; color: white;'>🌊 해양 기후 미션 챌린지 🌊</h1>", unsafe_allow_html=True)

# ✅ 팀 이름 입력 (처음 화면)
if not st.session_state.team_name:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("팀 이름을 입력하세요")
        team_name = st.text_input("팀 이름")
        if st.button("시작하기"):
            if team_name.strip() != "":
                st.session_state.team_name = team_name
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # ✅ 진행 상황 표시
    st.markdown(f"### ✅ 현재 팀: **{st.session_state.team_name}** | 진행 상황: 미션 {st.session_state.current_mission}/4")

    # ✅ 미션 1~4
    if st.session_state.current_mission == 1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("미션 1️⃣ : 데이터 탐색하기")
            st.write("다음 표는 해양 표면 온도 이상치 데이터입니다. 전체 데이터를 확인하세요.")
            st.dataframe(df)  # 전체 데이터 표시

            st.write("질문: 데이터에서 **가장 첫 번째 연도**는 무엇입니까?")
            answer = st.text_input("정답 입력")
            if st.button("제출", key="m1"):
                correct = str(min_year)
                if answer.strip() == correct:
                    st.success("정답입니다! 다음 미션으로 이동합니다.")
                    st.session_state.current_mission = 2
                    st.rerun()
                else:
                    st.error("틀렸습니다. 다시 시도하세요.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_mission == 2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("미션 2️⃣ : 연도별 데이터 분석")
            year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
            filtered = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
            avg_anomaly = filtered['Anomaly'].mean()
            fig = px.line(filtered, x='date', y='Anomaly', title='연도별 이상치 변화')
            st.plotly_chart(fig)

            st.write("질문: 선택한 구간의 평균 이상치는 소수점 둘째 자리까지 얼마입니까?")
            answer = st.text_input("정답 입력")
            if st.button("제출", key="m2"):
                correct = f"{avg_anomaly:.2f}"
                if answer.strip() == correct:
                    st.success("정답입니다! 다음 미션으로 이동합니다.")
                    st.session_state.current_mission = 3
                    st.rerun()
                else:
                    st.error("틀렸습니다. 다시 시도하세요.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_mission == 3:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("미션 3️⃣ : 특정 달의 이상치 찾기")
            selected_month = st.selectbox("월 선택", sorted(df['Month'].unique()))
            month_data = df[df['Month'] == selected_month]
            max_anomaly_year = month_data.loc[month_data['Anomaly'].idxmax(), 'Year']
            st.write(f"{selected_month}월 데이터의 최대값이 있는 연도를 맞히세요.")
            answer = st.text_input("정답 입력")
            if st.button("제출", key="m3"):
                correct = str(max_anomaly_year)
                if answer.strip() == correct:
                    st.success("정답입니다! 다음 미션으로 이동합니다.")
                    st.session_state.current_mission = 4
                    st.rerun()
                else:
                    st.error("틀렸습니다. 다시 시도하세요.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_mission == 4:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("미션 4️⃣ : 최종 암호 찾기")
            st.write("이제까지의 답을 조합해 최종 암호를 입력하세요.")
            final_code = st.text_input("최종 암호")
            if st.button("제출", key="m4"):
                if final_code.strip().upper() == "ENSO":
                    st.success("축하합니다! 모든 미션을 완료했습니다.")
                    st.balloons()
                else:
                    st.error("틀렸습니다. 다시 입력하세요.")
            st.markdown("</div>", unsafe_allow_html=True)
