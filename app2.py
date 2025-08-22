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
# 스타일
# -----------------------
#st.markdown("""
#<style>
#[data-testid="stAppViewContainer"] {
#  background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
#  background-size: cover;
#  background-position: center;
#}
#[data-testid="stHeader"] { background: rgba(0,0,0,0); }
#.mission-card { background: rgba(255,255,255,0.85); padding:20px; border-radius:16px; margin-bottom:20px; }
#</style>
#""", unsafe_allow_html=True)

# -----------------------
# 페이지 흐름
# -----------------------

# 인트로 페이지
if st.session_state.mission == 0:
    st.title("🕵️‍♀️ 엘니뇨 사건 파일: 기후의 흔적을 찾아라")
    st.markdown("""
    **세계 기후를 흔드는 정체불명의 힘**이 있다는 보고가 있었습니다.   
    최근 지구 곳곳에서 이상 기후 현상이 보고되고 있습니다.   
     **2023년**    
    아시아, 아프리카, 남미지역에서 농업 생산량이 감소하고 물이 부족해지는 현상이 나타났습니다.   
    이때문에 '기후플레이션'이라 불리는 식량가격 상승이 일어났어요.   
    **2020년**   
    아시아 지역에서 한파와 폭우가 나타났습니다.   
    중국과 인동서는 기록적인 폭설과 홍수로 인해 수천명이 피해를 입었습니다.   
    **한국에서**   
    2024년 한국은 겨울철 매우 가물어서, 농사를 지을 물이 부족하여 농작물에 피해를 입었습니다.   
    2022년에는 여름에 폭우와 집중호우로 홍수 피해가 발생했습니다.   
    **기후 수사국**은 당신에게 중요한 임무를 맡겼습니다.  

    🌊 **미션:**  
    태평양 바다 속에서 숨겨진 기후의 단서를 찾고,  
    기후 코드의 암호를 해독하여 전세계에 이상기후를 일으키는 원인을 찾아라!

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
    st.subheader("미션 1️⃣ : Nino3.4 해역과 수온 데이터 탐색")
    months = list(range(1, 13))
    selected_month = st.selectbox("📅 분석할 월을 선택하세요", months, index=7)
    year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
    
    filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    filtered = filtered[filtered["Month"] == selected_month]

    if "nino3.4 수온 평균" in filtered.columns:
        fig_avg = px.line(filtered, x="date", y="nino3.4 수온 평균",
                          labels={"nino3.4 수온 평균": "수온 평균(°C)", "date": "날짜"},
                          title=f"{selected_month}월 Nino3.4 해역 수온 평균 변화")
        st.plotly_chart(fig_avg, use_container_width=True)
    else:
        st.error("컬럼 'nino3.4 수온 평균'이 없습니다.")
        st.stop()

    correct_answer = str(filtered.loc[filtered["nino3.4 수온 평균"].idxmax(), "Year"]) if not filtered.empty else None
    q1_answer = st.text_input("질문: 언제 가장 높았나요? (예: 2024년)")
    if st.button("제출 (미션 1)", key="submit_m1"):
        if q1_answer.strip() and q1_answer.strip() == correct_answer:
            st.session_state.q1_correct = True
            st.info("암호 코드: **E**")
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

    if st.session_state.get("q1_correct"):
        if st.button("다음 미션으로 이동", key="next_m1"):
            st.session_state.codes.append("E")
            st.session_state.mission = 2
            st.rerun()

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

    correct_answer = str(filt.loc[filt["지수"].idxmax(), "Year"]) if not filt.empty else None
    a2 = st.text_input("질문: 지수가 가장 높은 해는?")
    if st.button("제출 (미션 2)", key="submit_m2"):
        if a2.strip() and a2.strip() == correct_answer:
            st.session_state.q2_correct = True
            st.info("암호 코드: **N**")
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

    if st.session_state.get("q2_correct"):
        if st.button("다음 미션으로 이동", key="next_m2"):
            st.session_state.codes.append("N")
            st.session_state.mission = 3
            st.rerun()

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

    correct_answer = str(filt.loc[filt["지수"].idxmin(), "Year"]) if not filt.empty else None
    a3 = st.text_input("질문: 가장 강한 라니냐는 몇 년?")
    if st.button("제출 (미션 3)", key="submit_m3"):
        if a3.strip() and a3.strip() == correct_answer:
            st.session_state.q3_correct = True
            st.info("암호 코드: **S**")
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

    if st.session_state.get("q3_correct"):
        if st.button("다음 미션으로 이동", key="next_m3"):
            st.session_state.codes.append("S")
            st.session_state.mission = 4
            st.rerun()

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

    correct_answer = str(yearly_min.loc[yearly_min["지수"].idxmin(), "Year"]) if not yearly_min.empty else None
    a4 = st.text_input("질문: 가장 강한 라니냐 연도는?")
    if st.button("제출 (미션 4)", key="submit_m4"):
        if a4.strip() and a4.strip() == correct_answer:
            st.session_state.q4_correct = True
            st.info("암호 코드: **O**")
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

    if st.session_state.get("q4_correct"):
        if st.button("미션 완료", key="finish_btn"):
            st.session_state.codes.append("O")
            st.session_state.mission = 5
            st.session_state.end_time = time.time()
            st.rerun()

# -----------------------
# 완료 화면
# -----------------------
elif st.session_state.mission == 5:
    st.subheader("🎉 미션 완료")
    dur_sec = (st.session_state.end_time - st.session_state.start_time) if st.session_state.start_time else 0
    m = int(dur_sec // 60)
    s = int(dur_sec % 60)
    st.write(f"✅ **총 소요 시간: {m}분 {s}초**")

    st.write("모은 암호 조각을 조합해 암호를 입력하세요.")
    code = st.text_input("최종 암호 입력")
    if st.button("암호 해독"):
        if code.strip().upper() == "ENSO":
            st.success("🎯 암호 해독 성공! 사건의 진실이 밝혀졌습니다! 전세계 기후를 바꾼것은 바로 ENSO였습니다!")
            st.balloons()
            st.write("🌍 **축하합니다! 당신은 기후의 비밀을 밝혀낸 최고의 수사관입니다.**")
            st.markdown("""
    **ENSO**   
    🌊 **주요 의미:**  
- **엘니뇨(El Niño):** 태평양 적도 해수면 온도가 평소보다 높아지는 현상  
- **라니냐(La Niña):** 태평양 적도 해수면 온도가 평소보다 낮아지는 현상  

**인간과 사회에 미치는 영향:**  
- 이상 기후로 인한 가뭄, 폭우, 산불, 농작물 피해  
- 홍수나 가뭄으로 식량 생산과 물 공급에 영향  
- 열대 지역과 해양 생태계 변화  

**세계 기후에 미치는 영향:**  
- 북미, 남미, 아시아, 호주 등 지역별 강수량과 기온 패턴 변화  
- 허리케인, 태풍 등 극한 기상현상 발생 빈도 변화  
- 해양 생태계 및 어업 자원에 장기적 영향
    """)
        else:
            st.error("❌ 암호가 틀렸습니다. 다시 시도하세요.")
