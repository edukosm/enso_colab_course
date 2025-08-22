import streamlit as st
import pandas as pd
import plotly.express as px
import time

# -----------------------
# 페이지 & 스타일
# -----------------------
st.set_page_config(page_title="기후 데이터 미션 챌린지", layout="wide")

CSS = """
<style>
/* 전체 배경 이미지 */
[data-testid="stAppViewContainer"] {
  background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
  background-size: cover;
  background-position: center;
}

/* 헤더 완전 투명 */
[data-testid="stHeader"] {
  background: rgba(0, 0, 0, 0);
}

/* 기본 컨테이너의 흰색 배경 제거 */
[data-testid="block-container"] {
  background: rgba(0, 0, 0, 0) !important;
  padding-top: 0rem !important; /* 상단 여백 최소화 */
}

/* 미션 카드 스타일 */
.mission-card {
  background: rgba(255, 255, 255, 0.85);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
  color: #111;
}

/* 버튼 스타일 */
.stButton button {
  background: #111 !important;
  color: #fff !important;
  font-weight: 700;
  border-radius: 10px;
  padding: 8px 16px;
  border: none;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# 타이틀 유지
st.title("🌊 기후 데이터 탐험 미션")


# -----------------------
# 데이터 로드 (GitHub URL)
# -----------------------
@st.cache_data(show_spinner=True)
def load_data():
    urls = [
        "https://raw.githubusercontent.com/edukosm/enso_colab_course/main/oni_month_20250821.csv",
        "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv",
    ]
    df = None
    for u in urls:
        try:
            df = pd.read_csv(u, encoding="utf-8-sig")
            break
        except Exception:
            continue
    return df

df = load_data()
if df is None:
    st.error("❌ 데이터를 불러올 수 없습니다. GitHub URL을 확인하세요.")
    st.stop()

# -----------------------
# 전처리
# -----------------------
df.columns = df.columns.map(lambda c: str(c).replace("\ufeff", "").strip())

if "날짜" in df.columns:
    df["날짜"] = df["날짜"].astype(str).str.replace("\ufeff", "", regex=False).str.strip()
else:
    st.error("CSV에 '날짜' 컬럼이 필요합니다.")
    st.stop()

# 날짜 파싱
date_parsed = None
for fmt in ["%Y년 %m월", "%Y-%m", "%Y.%m", "%Y/%m"]:
    try:
        date_parsed = pd.to_datetime(df["날짜"], format=fmt, errors="raise")
        break
    except Exception:
        continue
if date_parsed is None:
    date_parsed = pd.to_datetime(df["날짜"], errors="coerce")
df["date"] = date_parsed
df = df.dropna(subset=["date"]).copy()
df["Year"] = df["date"].dt.year
df["Month"] = df["date"].dt.month

# 지수 컬럼 자동 선택
index_candidates = ["nino3.4 index", "ONI index", "Anomaly"]
index_col = None
for c in index_candidates:
    if c in df.columns:
        index_col = c
        break
if index_col is None:
    st.error("지수 컬럼을 찾지 못했습니다. ('nino3.4 index', 'ONI index', 'Anomaly' 중 하나 필요)")
    st.stop()

df_display = df[["날짜", index_col, "date", "Year", "Month"]].rename(columns={index_col: "지수"})
min_year = int(df_display["Year"].min())
max_year = int(df_display["Year"].max())

# -----------------------
# 세션 상태 초기화
# -----------------------
if "mission" not in st.session_state:
    st.session_state.mission = 1
if "finished" not in st.session_state:
    st.session_state.finished = False
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "codes" not in st.session_state:
    st.session_state.codes = []  # 암호 문자 저장

# -----------------------
# 완료 화면 (항상 최상단)
# -----------------------
if st.session_state.finished:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("🎉 미션 완료")

    dur_sec = (st.session_state.end_time - st.session_state.start_time) if st.session_state.start_time else 0
    m = int(dur_sec // 60)
    s = int(dur_sec % 60)
    st.write(f"✅ **총 소요 시간: {m}분 {s}초**")

    st.write("획득한 암호 코드:")
    st.success(" - ".join(st.session_state.codes))

    st.write("마지막 단계: 암호를 입력하세요.")
    code = st.text_input("최종 암호 (예: ENSO)")
    if st.button("암호 해독"):
        if code.strip().upper() == "ENSO":
            st.success("🎯 암호해독 성공!")
            st.balloons()
        else:
            st.error("❌ 암호가 틀렸습니다. 다시 시도하세요.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 1
# -----------------------
elif st.session_state.mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 1️⃣ : Nino3.4 해역과 수온 데이터 탐색")

    # ✅ 월 선택
    months = list(range(1, 13))
    selected_month = st.selectbox("📅 분석할 월을 선택하세요", months, index=7)  # 기본 8월

    # ✅ 연도 범위
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))

    # ✅ 데이터 필터
    filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    filtered = filtered[filtered["Month"] == selected_month]

    # ✅ y축 자동
    y_min_avg = filtered["nino3.4 수온 평균"].min() - 1
    y_max_avg = filtered["nino3.4 수온 평균"].max() + 1

    # ✅ 그래프
    fig_avg = px.line(filtered, x="date", y="nino3.4 수온 평균",
                      labels={"nino3.4 수온 평균": "수온 평균(°C)", "date": "날짜"},
                      title=f"{selected_month}월 Nino3.4 해역 수온 평균 변화")
    fig_avg.update_traces(mode="lines+markers")
    fig_avg.update_layout(yaxis=dict(range=[y_min_avg, y_max_avg]))
    st.plotly_chart(fig_avg, use_container_width=True)

    # ✅ 질문
    st.markdown("#### 질문")
    st.write(f"1️⃣ 언제 Nino3.4 해역에서 {selected_month}월의 수온 평균값이 가장 높았나요? (예: 2024년)")
    q1_answer = st.text_input("정답 입력", key="mission1_q1")

    if st.button("제출 (미션 1)"):
        if q1_answer.strip():
            st.success("정답이 제출되었습니다! 다음 미션으로 이동합니다.")
            st.session_state.codes.append("E")  # ✅ 코드 지급
            st.session_state.mission = 2
            st.rerun()
        else:
            st.error("정답을 입력하세요.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 2
# -----------------------
elif st.session_state.mission == 2:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 2️⃣ : ENSO 지수 탐색")

    # ✅ 연도 범위
    min_year = int(df_display["Year"].min())
    max_year = int(df_display["Year"].max())
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year), key="mission2_slider")

    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]

    if len(filt) > 0:
        fig2 = px.line(filt, x="date", y="지수", title="ENSO 지수 변화", markers=True)
        fig2.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="엘니뇨 기준 (+0.5)")
        fig2.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준 (-0.5)")
        fig2.update_yaxes(range=[-3, 3])
        st.plotly_chart(fig2, use_container_width=True)

        st.write("질문: 이 기간 동안 지수가 가장 높은 해는?")
        a2 = st.text_input("정답 입력 (예: 1997)", key="mission2_q1")

        if st.button("제출 (미션 2)"):
            strongest_year = int(filt.loc[filt["지수"].idxmax(), "Year"])
            if a2.strip() == str(strongest_year):
                st.success("정답입니다! 다음 미션으로 이동합니다.")
                st.session_state.codes.append("N")  # ✅ 코드 지급
                st.session_state.mission = 3
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
    else:
        st.warning("선택한 기간에 데이터가 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 3
# -----------------------
elif st.session_state.mission == 3:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 3️⃣ : 라니냐 탐색")

    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year), key="mission3_slider")
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]

    if len(filt) > 0:
        fig3 = px.line(filt, x="date", y="지수", title="ENSO 지수 변화 (라니냐 탐색)", markers=True)
        fig3.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="엘니뇨 기준 (+0.5)")
        fig3.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준 (-0.5)")
        fig3.update_yaxes(range=[-3, 3])
        st.plotly_chart(fig3, use_container_width=True)

        st.write("질문: 이 기간 동안 가장 강한 라니냐는 몇 년?")
        a3 = st.text_input("정답 입력 (예: 2010)", key="mission3_q1")

        if st.button("제출 (미션 3)"):
            weakest_year = int(filt.loc[filt["지수"].idxmin(), "Year"])
            if a3.strip() == str(weakest_year):
                st.success("정답입니다! 다음 미션으로 이동합니다.")
                st.session_state.codes.append("S")  # ✅ 코드 지급
                st.session_state.mission = 4
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
    else:
        st.warning("선택한 기간에 데이터가 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 4
# -----------------------
elif st.session_state.mission == 4:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 4️⃣ : 가장 강한 라니냐가 있었던 연도는?")

    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year), key="mission4_slider")
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]

    if len(filt) > 0:
        yearly_min = filt.groupby("Year")["지수"].min().reset_index()

        fig4 = px.line(yearly_min, x="Year", y="지수", title="연도별 최소 지수 (가장 강한 라니냐 후보)", markers=True)
        fig4.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="엘니뇨 기준 (+0.5)")
        fig4.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준 (-0.5)")
        fig4.update_yaxes(range=[-3, 3])
        st.plotly_chart(fig4, use_container_width=True)

        st.dataframe(yearly_min)

        strongest_year = int(yearly_min.loc[yearly_min["지수"].idxmin(), "Year"])

        st.write("질문: 이 기간 동안 가장 강한 라니냐(지수가 가장 낮은) 연도는?")
        a4 = st.text_input("정답 입력", key="mission4_q1")

        if st.button("제출 (미션 4)"):
            if a4.strip() == str(strongest_year):
                st.success("정답입니다! 모든 미션을 완료했습니다.")
                st.session_state.codes.append("O")  # ✅ 마지막 코드 지급
                st.session_state.finished = True
                st.session_state.end_time = time.time()
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
    else:
        st.warning("선택한 기간에 데이터가 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)
