import streamlit as st
import pandas as pd
import plotly.express as px
import time

# ---------------- 스타일 (CSS) ----------------
CSS = """
<style>
[data-testid="stAppViewContainer"]{
  background-image:url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
  background-size:cover;background-position:center;
}
[data-testid="stHeader"]{background:rgba(0,0,0,0);}
.block-container {
  padding-top: 0rem !important;
}
.mission-card{
  background:rgba(255,255,255,.85);padding:20px;border-radius:16px;margin-bottom:20px;color:#111;
}
.stButton button{
  background:#111 !important;color:#fff !important;font-weight:700;border-radius:10px;padding:8px 16px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------- 기본 설정 ----------------
st.title("🌊 해양 데이터 분석 미션")

# 진행 상태 초기화
if "mission" not in st.session_state:
    st.session_state.mission = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# ---------------- 데이터 로드 ----------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/your-repo/ocean_data.csv"  # 실제 GitHub URL 넣기
    df = pd.read_csv(url, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["날짜"], errors="coerce")
    return df

df = load_data()
min_year, max_year = int(df["date"].dt.year.min()), int(df["date"].dt.year.max())
df_display = df.copy()

# ---------------- 진행 상황 표시 ----------------
progress_text = f"현재 단계: **미션 {st.session_state.mission}**"
if st.session_state.mission == 0:
    progress_text = "현재 단계: 팀 이름 입력"
elif st.session_state.mission == 3:
    progress_text = "✅ 모든 미션 완료!"
st.markdown(f"### {progress_text}")

# ---------------- 미션 0: 팀 이름 입력 ----------------
if st.session_state.mission == 0:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("팀 이름을 입력하세요")
    team_name = st.text_input("팀 이름")
    if st.button("시작"):
        if team_name.strip():
            st.session_state.team = team_name
            st.session_state.start_time = time.time()
            st.session_state.mission = 1
            st.rerun()
        else:
            st.error("팀 이름을 입력하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 미션 1: 데이터 표 + 질문 ----------------
elif st.session_state.mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 1️⃣ : 데이터 탐색")
    st.write("전체 데이터를 확인하세요.")
    st.dataframe(df_display)

    st.write("질문: 1998년 6월의 지수는 얼마입니까?")
    a1 = st.text_input("정답 입력")
    correct_value = df_display[(df_display["date"].dt.year == 1998) & (df_display["date"].dt.month == 6)]["지수"].values
    if len(correct_value) > 0:
        correct_value = round(correct_value[0], 2)
    else:
        correct_value = None

    if st.button("제출 (미션 1)"):
        if correct_value is not None and a1.strip() == f"{correct_value:.2f}":
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 2
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 미션 2: 그래프 + 평균값 + 기준선 ----------------
elif st.session_state.mission == 2:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 2️⃣ : 연도 구간 평균 지수")

    # 연도 범위 슬라이더
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["date"].dt.year >= yr[0]) & (df_display["date"].dt.year <= yr[1])]

    # 평균값 계산
    avg_val = round(filt["지수"].dropna().mean(), 2)
    st.write(f"📊 선택한 구간의 평균 지수: **{avg_val}**")

    # 그래프 생성 (기준선 추가)
    fig = px.line(filt, x="date", y="지수", title="월별 지수 변화")
    fig.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="El Niño (+0.5)")
    fig.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="La Niña (-0.5)")
    st.plotly_chart(fig, use_container_width=True)

    st.write("질문: 선택한 구간의 평균 지수는 소수점 둘째 자리까지 얼마입니까?")
    a2 = st.text_input("정답 입력 (예: 0.15)")
    if st.button("제출 (미션 2)"):
        if a2.strip() == f"{avg_val:.2f}":
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 3
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 미션 3: 완료 화면 ----------------
elif st.session_state.mission == 3:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("🎉 모든 미션 완료!")
    total_time = round(time.time() - st.session_state.start_time, 2)
    st.write(f"팀 **{st.session_state.team}** 완료 시간: {total_time}초")
    st.success("축하합니다! 모든 미션을 성공적으로 완료했습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
