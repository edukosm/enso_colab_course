import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# -----------------------
# 페이지 & 스타일
# -----------------------
st.set_page_config(page_title="기후 데이터 미션 챌린지", layout="wide")

CSS = """
<style>
[data-testid="stAppViewContainer"]{
  background-image:url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
  background-size:cover;background-position:center;
}
[data-testid="stHeader"]{background:rgba(0,0,0,0);}
.mission-card{
  background:rgba(255,255,255,.85);padding:20px;border-radius:16px;margin-bottom:20px;color:#111;
}
.stButton button{
  background:#111 !important;color:#fff !important;font-weight:700;border-radius:10px;padding:8px 16px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.title("🌊 기후 데이터 탐험 미션")

# -----------------------
# 데이터 로드 (GitHub URL만)
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
    with st.container():
        st.markdown('<div class="mission-card">', unsafe_allow_html=True)
        st.subheader("팀 이름을 입력하세요")
        t = st.text_input("팀 이름")
        if st.button("시작하기"):
            if t.strip():
                st.session_state.team_name = t.strip()
                st.session_state.start_time = time.time()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
else:
    st.caption(f"현재 팀: **{st.session_state.team_name}**")

# -----------------------
# 미션 1
# -----------------------
if st.session_state.mission == 1:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 1️⃣ : 데이터 탐색하기")
    st.dataframe(df_display[["날짜", "지수"]])

    yr = st.slider("연도 범위(탐색용)", min_year, max_year, (min_year, max_year))
    _ = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    st.write(f"선택 범위 데이터 수: {len(_)}")

    st.write("질문: 이 데이터에서 **가장 첫 번째 연도**는 무엇입니까?")
    a1 = st.text_input("정답 입력 (예: 1950)")
    if st.button("제출 (미션 1)"):
        if a1.strip() == str(min_year):
            st.success("정답입니다! 다음 미션으로 이동합니다.")
            st.session_state.mission = 2
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 미션 2
# -----------------------
elif st.session_state.mission == 2:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 2️⃣ : 연도 구간 평균 지수")
    yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    filt = df_display[(df_display["Year"] >= yr[0]) & (df_display["Year"] <= yr[1])]
    avg_val = round(filt["지수"].dropna().mean(), 2)

    fig = px.line(filt, x="date", y="지수", title="월별 지수 변화")
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

# -----------------------
# 미션 3
# -----------------------
elif st.session_state.mission == 3:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 3️⃣ : 월별 최대 지수의 연도 찾기")
    sel_month = st.selectbox("월 선택", options=sorted(df_display["Month"].unique()))
    md = df_display[df_display["Month"] == sel_month].dropna(subset=["지수"])
    if len(md) > 0:
        max_idx = md["지수"].idxmax()
        max_year_for_month = int(df_display.loc[max_idx, "Year"])
        a3 = st.text_input(f"{sel_month}월의 최대 지수가 기록된 연도는?")
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
# 미션 4
# -----------------------
elif st.session_state.mission == 4:
    st.markdown('<div class="mission-card">', unsafe_allow_html=True)
    st.subheader("미션 4️⃣ : 최종 암호 입력")
    final_code = st.text_input("최종 암호")
    if st.button("제출 (미션 4)"):
        if final_code.strip().upper() == "ENSO":
            st.success("축하합니다! 모든 미션을 완료했습니다.")
            st.balloons()
            st.session_state.finished = True
            st.session_state.end_time = time.time()
            st.rerun()
        else:
            st.error("틀렸습니다. 다시 시도하세요.")
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
