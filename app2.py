import streamlit as st
import pandas as pd
import plotly.express as px
import time

# -----------------------
# 초기 설정
# -----------------------
st.set_page_config(page_title="엘니뇨 사건 파일", layout="wide")

# 세션 상태 초기화
if "mission" not in st.session_state:
    st.session_state.mission = 0
if "codes" not in st.session_state:
    st.session_state.codes = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None

# -----------------------
# 데이터 로드
# -----------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/main/oni_month_20250821.csv"
    df = pd.read_csv(url, encoding="utf-8-sig")
    return df

df = load_data()
df.columns = df.columns.map(lambda c: c.strip())
df["date"] = pd.to_datetime(df["날짜"], errors="coerce")
df["Year"] = df["date"].dt.year
df["Month"] = df["date"].dt.month
index_col = [c for c in df.columns if "index" in c.lower() or "Anomaly" in c]
index_col = index_col[0] if index_col else "지수"
df_display = df[["날짜", index_col, "date", "Year", "Month"]].rename(columns={index_col: "지수"})
min_year, max_year = int(df_display["Year"].min()), int(df_display["Year"].max())

# -----------------------
# 스타일
# -----------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
  background-size: cover;
  background-position: center;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.mission-card { background: rgba(255,255,255,0.85); padding:20px; border-radius:16px; margin-bottom:20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 페이지 흐름
# -----------------------

# 인트로 페이지
if st.session_state.mission == 0:
    st.title("🕵️‍♀️ 엘니뇨 사건 파일: 기후의 흔적을 찾아라")
    st.markdown("""
    세계 기후를 흔드는 정체불명의 힘, **엘니뇨와 라니냐**.  
    최근 지구 곳곳에서 이상 기후 현상이 보고되고 있습니다.  
    **기후 수사국**은 당신에게 중요한 임무를 맡겼습니다.  

    🌊 **미션:**  
    태평양 바다 속에서 숨겨진 기후의 단서를 찾고,  
    기후 코드의 암호를 해독하라!  

    🔍 **단서 수집 방법:**  
    4개의 미션을 수행하고 각 미션에서 **암호 조각**을 획득하세요.  
    모든 조각을 모으면, **최종 암호 해독**에 성공할 수 있습니다!
    """)
    if st.button("🚀 미션 시작"):
        st.session_state.mission = 1
        st.session_state.start_time = time.time()
        st.rerun()

# -----------------------
# 미션 1
# -----------------------
elif st.session_state.mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 1️⃣ : Nino3.4 해역과 수온 데이터 탐색")
    months = list(range(1, 13))
    selected_month = st.selectbox("📅 분석할 월을 선택하세요", months, index=7)
    year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    filtered = filtered[filtered["Month"] == selected_month]
    fig_avg = px.line(filtered, x="date", y="nino3.4 수온 평균",
                      labels={"nino3.4 수온 평균": "수온 평균(°C)", "date": "날짜"},
                      title=f"{selected_month}월 Nino3.4 해역 수온 평균 변화")
    fig_avg.update_traces(mode="lines+markers")
    st.plotly_chart(fig_avg, use_container_width=True)

    q1_answer = st.text_input("질문: 언제 가장 높았나요? (예: 2024년)")
    if st.button("제출 (미션 1)"):
        if q1_answer.strip():
            st.success("정답 제출 완료! 다음 미션으로 이동합니다.")
            st.info("암호 코드: **E**")
            st.session_state.codes.append("E")
            st.session_state.mission = 2
            st.rerun()
        else:
            st.error("정답을 입력하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 2
# -----------------------
elif st.session_state.mission == 2:
    st.subheader("미션 2️⃣ : ENSO 지수 탐색")
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    fig2 = px.line(filt, x="date", y="지수", title="ENSO 지수 변화", markers=True)
    fig2.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="엘니뇨 기준")
    fig2.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준")
    st.plotly_chart(fig2, use_container_width=True)
    a2 = st.text_input("질문: 지수가 가장 높은 해는?")
    if st.button("제출 (미션 2)"):
        strongest_year = int(filt.loc[filt["지수"].idxmax(), "Year"])
        if a2.strip() == str(strongest_year):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.info("암호 코드: **N**")
            st.session_state.codes.append("N")
            st.session_state.mission = 3
            st.rerun()
        else:
            st.error("틀렸습니다.")
            
# -----------------------
# 미션 3
# -----------------------
elif st.session_state.mission == 3:
    st.subheader("미션 3️⃣ : 라니냐 탐색")
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    fig3 = px.line(filt, x="date", y="지수", title="ENSO 지수 변화 (라니냐 탐색)", markers=True)
    fig3.add_hline(y=0.5, line_dash="dash", line_color="red")
    fig3.add_hline(y=-0.5, line_dash="dash", line_color="blue")
    st.plotly_chart(fig3, use_container_width=True)
    a3 = st.text_input("질문: 가장 강한 라니냐는 몇 년?")
    if st.button("제출 (미션 3)"):
        weakest_year = int(filt.loc[filt["지수"].idxmin(), "Year"])
        if a3.strip() == str(weakest_year):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.info("암호 코드: **S**")
            st.session_state.codes.append("S")
            st.session_state.mission = 4
            st.rerun()
        else:
            st.error("틀렸습니다.")
            
# -----------------------
# 미션 4
# -----------------------
elif st.session_state.mission == 4:
    st.subheader("미션 4️⃣ : 가장 강한 라니냐 연도")
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    yearly_min = filt.groupby("Year")["지수"].min().reset_index()
    fig4 = px.line(yearly_min, x="Year", y="지수", title="연도별 최소 지수", markers=True)
    st.plotly_chart(fig4, use_container_width=True)
    a4 = st.text_input("질문: 가장 강한 라니냐 연도는?")
    if st.button("제출 (미션 4)"):
        strongest_year = int(yearly_min.loc[yearly_min["지수"].idxmin(), "Year"])
        if a4.strip() == str(strongest_year):
            st.success("모든 미션 완료!")
            st.info("암호 코드: **O**")
            st.session_state.codes.append("O")
            st.session_state.mission = 5
            st.session_state.end_time = time.time()
            st.rerun()
        else:
            st.error("틀렸습니다.")
            
# -----------------------
# 완료 페이지
# -----------------------
elif st.session_state.mission == 5:
    st.subheader("🎉 미션 완료!")
    dur = int(st.session_state.end_time - st.session_state.start_time)
    st.write(f"총 소요 시간: {dur//60}분 {dur%60}초")
    st.write(f"획득한 암호 조각: {' - '.join(st.session_state.codes)}")
    code = st.text_input("최종 암호를 입력하세요")
    if st.button("암호 해독"):
        if code.strip().upper() == "ENSO":
            st.success("🎯 암호 해독 성공!")
            st.balloons()
        else:
            st.error("❌ 틀렸습니다.")
