import streamlit as st
import pandas as pd
import time
import plotly.express as px

# -------------------
# 앱 기본 설정
# -------------------
st.set_page_config(page_title="기후 미션 챌린지", layout="wide")

# 배경 이미지 CSS (저작권 문제 없는 Unsplash 이미지)
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e') no-repeat center center fixed;
        background-size: cover;
    }
    .mission-card {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: black;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------
# 데이터 로드
# -------------------
@st.cache_data
def load_data():
    df = pd.read_csv("oni_month_20250821.csv")
    # 날짜 파싱
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')
    return df

df = load_data()

# -------------------
# 세션 상태 초기화
# -------------------
if "team_name" not in st.session_state:
    st.session_state.team_name = ""
if "mission" not in st.session_state:
    st.session_state.mission = 1
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None

# -------------------
# 타이틀 + 진행 상황 표시
# -------------------
st.title("🌊 기후 탐험 미션 챌린지")
progress_text = f"현재 미션: {st.session_state.mission}/4"
st.markdown(f"<h4 style='color:black'>{progress_text}</h4>", unsafe_allow_html=True)

# -------------------
# 팀 이름 입력 (처음 한 번)
# -------------------
if st.session_state.team_name == "":
    team = st.text_input("팀 이름을 입력하세요", key="team_input")
    if st.button("시작하기"):
        if team.strip() != "":
            st.session_state.team_name = team
            st.session_state.start_time = time.time()
            st.experimental_rerun()
else:
    st.write(f"**팀 이름:** {st.session_state.team_name}")

# -------------------
# 미션 1: 데이터 탐색
# -------------------
if st.session_state.team_name and st.session_state.mission == 1:
    st.markdown("<div class='mission-card'>", unsafe_allow_html=True)
    st.subheader("미션 1: 데이터 탐험")
    st.write("아래 표는 특정 기후 지수 데이터입니다. 전체 데이터를 살펴보고 질문에 답하세요.")
    
    # 데이터 전체 표시
    st.dataframe(df[['날짜', '지수']])

    # 슬라이더로 연도 필터링
    min_year, max_year = int(df['date'].dt.year.min()), int(df['date'].dt.year.max())
    year_range = st.slider("연도 범위를 선택하세요", min_year, max_year, (min_year, max_year))
    filtered = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
    st.write(f"선택한 범위 데이터 개수: {len(filtered)}")

    # 정답 입력
    st.write("질문: 전체 데이터에서 가장 큰 지수 값은 얼마입니까?")
    ans1 = st.text_input("정답 입력", key="answer1")

    if st.button("제출 (미션 1)"):
        correct = df['지수'].max()
        if ans1.strip() == str(correct):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 2
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------
# 미션 2: 그래프 해석
# -------------------
elif st.session_state.mission == 2:
    st.markdown("<div class='mission-card'>", unsafe_allow_html=True)
    st.subheader("미션 2: 시각화 분석")
    st.write("아래 그래프를 보고 질문에 답하세요.")
    
    fig = px.line(df, x='date', y='지수', title="기후 지수 변화 추이")
    st.plotly_chart(fig)

    ans2 = st.text_input("질문: 데이터에서 지수 값이 양수인 달은 몇 개입니까?", key="answer2")

    if st.button("제출 (미션 2)"):
        correct = (df['지수'] > 0).sum()
        if ans2.strip() == str(correct):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 3
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------
# 미션 3: 조건 탐색
# -------------------
elif st.session_state.mission == 3:
    st.markdown("<div class='mission-card'>", unsafe_allow_html=True)
    st.subheader("미션 3: 조건 찾기")
    st.write("지수가 1.0 이상인 첫 번째 날짜는 언제입니까? (YYYY-MM 형식으로 입력)")

    ans3 = st.text_input("정답 입력", key="answer3")

    if st.button("제출 (미션 3)"):
        first_date = df[df['지수'] >= 1.0]['date'].min()
        correct = first_date.strftime("%Y-%m")
        if ans3.strip() == correct:
            st.success("정답입니다! 마지막 미션으로 이동합니다.")
            st.session_state.mission = 4
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------
# 미션 4: 평균 계산
# -------------------
elif st.session_state.mission == 4:
    st.markdown("<div class='mission-card'>", unsafe_allow_html=True)
    st.subheader("미션 4: 평균 계산")
    st.write("슬라이더로 연도 범위를 선택하고, 그 기간의 평균 지수 값을 입력하세요.")

    year_range = st.slider("연도 선택", min_year, max_year, (min_year, max_year), key="slider_final")
    filtered = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
    st.write(f"선택된 기간의 데이터 개수: {len(filtered)}")

    ans4 = st.text_input("평균값 입력 (소수점 2자리까지)", key="answer4")

    if st.button("제출 (미션 4)"):
        correct = round(filtered['지수'].mean(), 2)
        if ans4.strip() == str(correct):
            st.success("모든 미션 완료!")
            st.session_state.end_time = time.time()
            duration = round((st.session_state.end_time - st.session_state.start_time) / 60, 2)
            st.write(f"총 소요 시간: {duration}분")
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)
