import streamlit as st
import pandas as pd
import plotly.express as px
import time
from pathlib import Path

# ===== 기본 설정 =====
st.set_page_config(page_title="해양 기후 미션", layout="wide")

# 배경 이미지 설정 (CSS 방식)
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# 진행 상황 저장 파일
progress_file = "team_progress.csv"

# ===== CSV 초기화 =====
if not Path(progress_file).exists():
    df_progress = pd.DataFrame(columns=["team", "mission", "timestamp"])
    df_progress.to_csv(progress_file, index=False)

# ===== 상태 로딩 =====
@st.cache_data
def load_progress():
    return pd.read_csv(progress_file)

def save_progress(team, mission):
    df = load_progress()
    new_row = pd.DataFrame([[team, mission, time.time()]], columns=["team", "mission", "timestamp"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(progress_file, index=False)

# ===== 팀 이름 입력 =====
if "team" not in st.session_state:
    st.session_state["team"] = ""

if st.session_state["team"] == "":
    st.title("🌊 해양 기후 미션 챌린지")
    team_name = st.text_input("팀 이름을 입력하세요:")
    if st.button("시작하기"):
        if team_name.strip() != "":
            st.session_state["team"] = team_name.strip()
            st.experimental_rerun()
else:
    team = st.session_state["team"]
    st.title(f"🌊 해양 기후 미션 챌린지 | 팀: {team}")

# 진행 상황 표시
progress_data = load_progress()
team_progress = progress_data[progress_data["team"] == st.session_state["team"]]
completed_missions = team_progress["mission"].unique().tolist()
st.subheader(f"진행 상황: {len(completed_missions)}/4 단계 완료")

# ===== 데이터 로딩 =====
data_url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
df = pd.read_csv(data_url)

# 날짜 변환 (안전 변환)
df['date'] = pd.to_datetime(df['날짜'], errors='coerce')
df = df.dropna(subset=['date'])

# ===== 미션 페이지 =====
mission = len(completed_missions) + 1

if mission == 1:
    st.markdown("### 🧩 미션 1: 데이터 탐험")
    st.markdown("아래 표는 지난 수십 년간의 해양 기후 데이터를 보여줍니다.")
    st.markdown("**질문:** 가장 오래된 데이터의 연도는 무엇인가요?")

    # 전체 데이터 표시 + 슬라이더로 기간 필터
    min_year, max_year = int(df['date'].dt.year.min()), int(df['date'].dt.year.max())
    year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filtered_df = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]
    st.dataframe(filtered_df)

    answer = st.text_input("정답(연도):")
    if st.button("제출"):
        correct_answer = str(min_year)
        if answer.strip() == correct_answer:
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            save_progress(team, 1)
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

elif mission == 2:
    st.markdown("### 🧩 미션 2: 데이터 시각화")
    st.markdown("아래 그래프는 특정 기간의 해양 기후 지수를 보여줍니다.")
    st.markdown("**질문:** 2015년 중 가장 값이 높은 달은 몇월인가요?")

    year_select = st.selectbox("연도 선택", sorted(df['date'].dt.year.unique()))
    year_data = df[df['date'].dt.year == year_select]

    fig = px.line(year_data, x='date', y='값', title=f"{year_select}년 기후 지수")
    st.plotly_chart(fig)

    answer = st.text_input("정답(월):")
    if st.button("제출"):
        max_month = year_data.loc[year_data['값'].idxmax(), 'date'].month
        if answer.strip() == str(max_month):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            save_progress(team, 2)
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

elif mission == 3:
    st.markdown("### 🧩 미션 3: 값의 평균 찾기")
    st.markdown("**질문:** 선택한 기간의 평균 기후 지수는 소수점 첫째자리까지 얼마인가요?")

    year_range = st.slider("연도 범위 선택", min_year, max_year, (2000, 2020))
    filtered_df = df[(df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])]

    avg_value = filtered_df['값'].mean()
    st.write(f"선택된 데이터 개수: {len(filtered_df)}")

    answer = st.text_input("정답(예: 0.5):")
    if st.button("제출"):
        if abs(float(answer) - round(avg_value, 1)) < 0.01:
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            save_progress(team, 3)
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

elif mission == 4:
    st.markdown("### 🏆 최종 미션: 추세 해석")
    st.markdown("**질문:** 최근 10년간 기후 지수는 전반적으로 상승했나요, 하락했나요? (상승/하락)")

    recent_years = sorted(df['date'].dt.year.unique())[-10:]
    recent_data = df[df['date'].dt.year.isin(recent_years)]

    fig = px.line(recent_data, x='date', y='값', title="최근 10년 추세")
    st.plotly_chart(fig)

    answer = st.text_input("정답(상승/하락):")
    if st.button("제출"):
        trend = "상승" if recent_data['값'].iloc[-1] > recent_data['값'].iloc[0] else "하락"
        if answer.strip() == trend:
            st.success("🎉 모든 미션 완료!")
            save_progress(team, 4)
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

else:
    st.title("✅ 미션 완료!")
    st.markdown("팀별 랭킹:")
    ranking = progress_data.groupby("team")["mission"].max().reset_index()
    ranking = ranking.sort_values(by="mission", ascending=False)
    st.dataframe(ranking)
