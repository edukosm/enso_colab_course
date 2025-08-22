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
# 세션 상태
# -----------------------
if "team_name" not in st.session_state:
    st.session_state.team_name = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "mission" not in st.session_state:
    st.session_state.mission = 1
if "finished" not in st.session_state:
    st.session_state.finished = False

st.markdown(f"**진행 상황:** 미션 {st.session_state.mission}/4")

# -----------------------
# 팀 이름
# -----------------------
if not st.session_state.team_name:
    st.subheader("팀 이름을 입력하세요")
    t = st.text_input("팀 이름")
    if st.button("시작하기"):
        if t.strip():
            st.session_state.team_name = t.strip()
            st.session_state.start_time = time.time()
            st.rerun()
    st.stop()
else:
    st.caption(f"현재 팀: **{st.session_state.team_name}**")

# -----------------------
# 미션 1
# -----------------------
if st.session_state.mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 1️⃣ : Nino 3.4 해역 탐색")

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Nino-regions.png/800px-Nino-regions.png", 
             caption="Nino 3.4 해역 위치")

    st.write("**질문 1:** 언제 Nino3.4 해역에서 **8월의 수온 평균값**이 가장 높았나요?")
    ans1 = st.text_input("질문 1 답: (예: 2015년)")

    st.write("**질문 2:** 언제 Nino3.4 해역에서 **8월의 수온 평년평균값**이 가장 높았나요?")
    ans2 = st.text_input("질문 2 답: (예: 1997년)")

    # ✅ 월 선택
    selected_month = st.selectbox("월 선택", list(range(1, 13)), index=0)  # 기본값: 1월
    filtered = df[df["Month"] == selected_month]

    # ✅ 연도 슬라이더
    yr_range = st.slider("연도 범위", min_year, max_year, (min_year, max_year))
    filtered = filtered[(filtered["Year"] >= yr_range[0]) & (filtered["Year"] <= yr_range[1])]

    # ✅ y축 범위 자동 계산
    y_min_avg = filtered["nino3.4 수온 평균"].min() - 1
    y_max_avg = filtered["nino3.4 수온 평균"].max() + 1

    y_min_clim = filtered["nino3.4 수온 평년평균"].min()
    y_max_clim = filtered["nino3.4 수온 평년평균"].max()

    # ✅ 첫 번째 그래프: 수온 평균
    fig_avg = px.line(filtered, x="date", y="nino3.4 수온 평균",
                      labels={"nino3.4 수온 평균": "수온 평균(°C)", "date": "날짜"},
                      title=f"{selected_month}월 Nino3.4 해역 수온 평균 변화")
    fig_avg.update_traces(mode="lines+markers")
    fig_avg.update_layout(yaxis=dict(range=[y_min_avg, y_max_avg]))

    st.plotly_chart(fig_avg, use_container_width=True)

    # ✅ 두 번째 그래프: 수온 평년평균
    fig_clim = px.line(filtered, x="date", y="nino3.4 수온 평년평균",
                       labels={"nino3.4 수온 평년평균": "수온 평년평균(°C)", "date": "날짜"},
                       title=f"{selected_month}월 Nino3.4 해역 수온 평년평균 변화")
    fig_clim.update_traces(mode="lines+markers")
    fig_clim.update_layout(yaxis=dict(range=[y_min_clim, y_max_clim]))

    st.plotly_chart(fig_clim, use_container_width=True)

    # ✅ 정답 확인 로직
    if st.button("제출 (미션 1)"):
        # 전체 데이터에서 8월 데이터 기준으로 가장 높은 연도 계산
        august_data = df[df["Month"] == 8]
        correct1 = str(august_data.loc[august_data["nino3.4 수온 평균"].idxmax(), "Year"])
        correct2 = str(august_data.loc[august_data["nino3.4 수온 평년평균"].idxmax(), "Year"])

        if ans1.strip() == correct1 and ans2.strip() == correct2:
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 2
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------
# 미션 2 (평균 + 기준선)
# -----------------------
elif st.session_state.mission == 2:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 2️⃣ : 연도 구간 평균 지수")
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    avg_val = round(filt["지수"].dropna().mean(), 2)

    fig = px.line(filt, x="date", y="지수", title="월별 지수 변화")
    fig.add_hline(y=0.5, line_dash="dot", line_color="red", annotation_text="엘니뇨(≥0.5)")
    fig.add_hline(y=-0.5, line_dash="dot", line_color="blue", annotation_text="라니냐(≤-0.5)")
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"👉 선택한 구간의 평균 지수: **{avg_val:.2f}**")

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

# -----------------------
# 미션 3
# -----------------------
elif st.session_state.mission == 3:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 3️⃣ : 월별 최대 지수의 연도 찾기")

    sel_month = st.selectbox("월 선택", options=sorted(df_display["Month"].unique()))
    md = df_display[df_display["Month"] == sel_month].dropna(subset=["지수"])

    if len(md) > 0:
        # 그래프 추가: 선택한 월의 연도별 지수 변화
        fig3 = px.line(md, x="Year", y="지수", markers=True,
                       title=f"{sel_month}월의 연도별 지수 변화")
        st.plotly_chart(fig3, use_container_width=True)

        # 데이터 테이블 제공
        st.dataframe(md[["Year", "지수"]])

        # 정답 계산
        max_idx = md["지수"].idxmax()
        max_year_for_month = int(df_display.loc[max_idx, "Year"])

        st.write(f"질문: {sel_month}월에서 가장 높은 지수를 기록한 연도는?")
        a3 = st.text_input("정답 입력 (예: 1997)")
        if st.button("제출 (미션 3)"):
            if a3.strip() == str(max_year_for_month):
                st.success("정답입니다! 다음 미션으로 이동합니다.")
                st.session_state.mission = 4
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
    else:
        st.warning("해당 월에 데이터가 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------
# 미션 4 (새로운 분석형)
# -----------------------
elif st.session_state.mission == 4:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 4️⃣ : 가장 강한 엘니뇨가 있었던 연도는?")

    # 연도 범위 선택 슬라이더
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))

    # 선택된 범위의 데이터 필터링
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    if len(filt) > 0:
        # 연도별 최대 지수 계산
        yearly_max = filt.groupby("Year")["지수"].max().reset_index()

        # 꺾은선 그래프 생성
        fig4 = px.line(yearly_max, x="Year", y="지수", title="연도별 최대 지수 (가장 강한 엘니뇨 후보)", markers=True)

        # 엘니뇨 / 라니냐 기준선 추가
        fig4.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="엘니뇨 기준 (+0.5)", annotation_position="bottom right")
        fig4.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준 (-0.5)", annotation_position="top right")
      
       # Y축 범위 고정 (-3 ~ 3)
        fig4.update_yaxes(range=[-3, 3])

      
        # 그래프 표시
        st.plotly_chart(fig4, use_container_width=True)

        # 데이터 테이블
        st.dataframe(yearly_max)

        # 정답 계산: 선택 구간에서 가장 큰 지수의 연도
        strongest_year = int(yearly_max.loc[yearly_max["지수"].idxmax(), "Year"])

        st.write("질문: 이 기간 동안 가장 강한 엘니뇨(지수가 가장 높은) 연도는?")
        a4 = st.text_input("정답 입력 (예: 1997)")
        if st.button("제출 (미션 4)"):
            if a4.strip() == str(strongest_year):
                st.success("정답입니다! 모든 미션을 완료했습니다.")
                st.balloons()
                st.session_state.finished = True
                st.session_state.end_time = time.time()
                st.rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
    else:
        st.warning("선택한 기간에 데이터가 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)



# -----------------------
# 완료 화면
# -----------------------
elif st.session_state.finished:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("🎉 미션 완료")
    dur_sec = (st.session_state.end_time - st.session_state.start_time) if st.session_state.start_time else 0
    m = int(dur_sec // 60); s = int(dur_sec % 60)
    st.write(f"✅ **총 소요 시간: {m}분 {s}초**")
    st.markdown("</div>", unsafe_allow_html=True)
elif st.session_state.finished:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("🎉 미션 완료")
    dur_sec = (st.session_state.end_time - st.session_state.start_time) if st.session_state.start_time else 0
    m = int(dur_sec // 60); s = int(dur_sec % 60)
    st.write(f"✅ **총 소요 시간: {m}분 {s}초**")

    st.write("마지막 단계: 암호를 입력하세요.")
    code = st.text_input("최종 암호")
    if st.button("암호 해독"):
        if code.strip().upper() == "ENSO":
            st.success("🎯 암호해독 성공!")
            st.balloons()
        else:
            st.error("❌ 암호가 틀렸습니다. 다시 시도하세요.")

    st.markdown("</div>", unsafe_allow_html=True)
