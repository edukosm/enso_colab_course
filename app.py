import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# -----------------------
# 설정 & 초기 세팅
# -----------------------
st.set_page_config(page_title="기후 미션 챌린지", page_icon="🌊", layout="wide")

# 배경 이미지 CSS
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
[data-testid="stSidebar"] {background-color: rgba(255,255,255,0.8);}
.mission-box {
    background-color: rgba(255,255,255,0.8);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# CSV 파일 설정
STATUS_FILE = "status.csv"

# 팀 진행 상태 파일 초기화
if not os.path.exists(STATUS_FILE):
    pd.DataFrame(columns=["team", "stage", "start_time", "end_time"]).to_csv(STATUS_FILE, index=False)

# -----------------------
# 팀 이름 입력
# -----------------------
if "team" not in st.session_state:
    with st.container():
        st.title("🌊 기후 미션 챌린지")
        st.markdown('<div class="mission-box"><h3>팀 이름을 입력하세요</h3></div>', unsafe_allow_html=True)
        team_name = st.text_input("팀 이름", "")
        if st.button("시작하기", use_container_width=True):
            if team_name.strip() != "":
                st.session_state.team = team_name
                status_df = pd.read_csv(STATUS_FILE)
                if team_name not in status_df["team"].values:
                    new_row = pd.DataFrame([{
                        "team": team_name,
                        "stage": 0,
                        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": ""
                    }])
                    status_df = pd.concat([status_df, new_row], ignore_index=True)
                    status_df.to_csv(STATUS_FILE, index=False)
                st.rerun()
        st.stop()

# -----------------------
# 진행 현황 표시
# -----------------------
st.title("🌊 기후 미션 챌린지")
status_df = pd.read_csv(STATUS_FILE)
st.subheader("📊 팀별 진행 상황")
st.dataframe(status_df[["team", "stage"]], hide_index=True, use_container_width=True)

# 현재 팀의 단계
current_stage = int(status_df.loc[status_df["team"] == st.session_state.team, "stage"].values[0])

# 데이터 불러오기
DATA_URL = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
df = pd.read_csv(DATA_URL)
df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')

# -----------------------
# 미션 함수
# -----------------------
def update_stage(stage):
    status_df = pd.read_csv(STATUS_FILE)
    status_df.loc[status_df["team"] == st.session_state.team, "stage"] = stage
    if stage == 5:  # 모든 미션 완료 시
        status_df.loc[status_df["team"] == st.session_state.team, "end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_df.to_csv(STATUS_FILE, index=False)
    st.rerun()

# -----------------------
# 미션 1
# -----------------------
if current_stage == 0:
    st.markdown('<div class="mission-box"><h3>미션 1: 데이터 탐험</h3>', unsafe_allow_html=True)
    st.write("아래 표에서 전체 데이터를 보고, **2020년 이후의 평균 지수를 입력하세요.**")

    # 전체 데이터
    st.dataframe(df, use_container_width=True)

    # 슬라이더로 연도 필터
    min_year, max_year = int(df['date'].dt.year.min()), int(df['date'].dt.year.max())
    year_range = st.slider("연도 범위 선택", min_year, max_year, (2020, max_year))
    filtered_df = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
    st.write(f"선택한 기간 데이터 ({year_range[0]}~{year_range[1]})")
    st.dataframe(filtered_df)

    avg_val = round(filtered_df['지수'].mean(), 2)
    answer = st.text_input("평균 지수를 소수점 둘째 자리까지 입력:")
    if st.button("제출"):
        if answer.strip() == str(avg_val):
            st.success("정답입니다!")
            update_stage(1)
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 미션 2
# -----------------------
if current_stage == 1:
    st.markdown('<div class="mission-box"><h3>미션 2: 데이터 시각화</h3>', unsafe_allow_html=True)
    st.write("아래 그래프에서 2015~2025년 지수의 **최대값**을 입력하세요.")
    
    filtered_df = df[(df['date'].dt.year >= 2015) & (df['date'].dt.year <= 2025)]
    fig = px.line(filtered_df, x='date', y='지수', title="지수 변화 (2015~2025)")
    st.plotly_chart(fig, use_container_width=True)

    max_val = round(filtered_df['지수'].max(), 2)
    answer = st.text_input("최대값을 소수점 둘째 자리까지 입력:")
    if st.button("제출"):
        if answer.strip() == str(max_val):
            st.success("정답입니다!")
            update_stage(2)
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 미션 3
# -----------------------
if current_stage == 2:
    st.markdown('<div class="mission-box"><h3>미션 3: 시기 비교</h3>', unsafe_allow_html=True)
    st.write("2010~2015 평균과 2020~2025 평균을 비교하세요. 어느 기간이 더 높은가요?")

    avg1 = df[(df['date'].dt.year >= 2010) & (df['date'].dt.year <= 2015)]['지수'].mean()
    avg2 = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2025)]['지수'].mean()

    st.write("보기: ① 2010~2015 ② 2020~2025")
    answer = st.radio("어느 기간이 더 높은가요?", ["①", "②"])
    if st.button("제출"):
        if (answer == "①" and avg1 > avg2) or (answer == "②" and avg2 > avg1):
            st.success("정답입니다!")
            update_stage(3)
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 미션 4
# -----------------------
if current_stage == 3:
    st.markdown('<div class="mission-box"><h3>미션 4: 최종 미션</h3>', unsafe_allow_html=True)
    st.write("전체 데이터에서 지수의 **최소값**을 입력하세요.")

    min_val = round(df['지수'].min(), 2)
    answer = st.text_input("최소값:")
    if st.button("제출"):
        if answer.strip() == str(min_val):
            st.success("정답입니다! 모든 미션 완료!")
            update_stage(5)
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 최종 랭킹
# -----------------------
if current_stage == 5:
    st.markdown('<div class="mission-box"><h3>🎉 모든 미션을 완료했습니다!</h3>', unsafe_allow_html=True)
    status_df = pd.read_csv(STATUS_FILE)
    completed = status_df[status_df["end_time"] != ""].copy()
    completed["time_taken"] = pd.to_datetime(completed["end_time"]) - pd.to_datetime(completed["start_time"])
    completed = completed.sort_values("time_taken")
    st.subheader("🏆 랭킹")
    st.dataframe(completed[["team", "time_taken"]], hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
