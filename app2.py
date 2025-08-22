import streamlit as st
import pandas as pd
import plotly.express as px
import time

# -----------------------
# 초기 설정
# -----------------------
st.set_page_config(page_title="엘니뇨 사건 파일", layout="wide")

# 세션 초기화
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "mission" not in st.session_state:
    st.session_state.mission = 1
if "codes" not in st.session_state:
    st.session_state.codes = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "finished" not in st.session_state:
    st.session_state.finished = False

# 예시 데이터 (실제 CSV로 교체)
# df = pd.read_csv("data.csv")
# 여기서는 임시 데이터 생성
data = {
    "Year": list(range(1980, 2025)) * 12,
    "Month": [m for m in range(1, 13)] * (2025 - 1980),
    "nino3.4 수온 평균": [25 + (i % 5) for i in range((2025 - 1980) * 12)],
    "지수": [round((i % 10) * 0.3 - 1.5, 2) for i in range((2025 - 1980) * 12)]
}
df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df[["Year", "Month"]].assign(DAY=1))

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

# -----------------------
# 인트로 페이지
# -----------------------
if st.session_state.page == "intro":
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
        st.session_state.page = "missions"
        st.session_state.start_time = time.time()
        st.rerun()

# -----------------------
# 미션 페이지
# -----------------------
elif st.session_state.page == "missions":
    st.title(f"🔍 미션 {st.session_state.mission}")

    # -----------------------
    # 미션 1
    # -----------------------
    if st.session_state.mission == 1:
        st.subheader("미션 1️⃣ : 바다의 온도 파일을 열어라")

        months = list(range(1, 13))
        selected_month = st.selectbox("📅 분석할 월을 선택하세요", months, index=0)

        year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))

        filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
        filtered = filtered[filtered["Month"] == selected_month]

        y_min_avg = filtered["nino3.4 수온 평균"].min() - 1
        y_max_avg = filtered["nino3.4 수온 평균"].max() + 1

        fig_avg = px.line(filtered, x="date", y="nino3.4 수온 평균",
                          labels={"nino3.4 수온 평균": "수온 평균(°C)", "date": "날짜"},
                          title=f"{selected_month}월 Nino3.4 해역 수온 평균 변화")
        fig_avg.update_traces(mode="lines+markers")
        fig_avg.update_layout(yaxis=dict(range=[y_min_avg, y_max_avg]))
        st.plotly_chart(fig_avg, use_container_width=True)

        st.write(f"**질문:** 언제 {selected_month}월의 수온 평균값이 가장 높았나요? (예: 2024년)")
        q1_answer = st.text_input("정답 입력", key="mission1_q1")

        if st.button("제출 (미션 1)"):
            if q1_answer.strip():
                st.success("정답이 제출되었습니다! 암호 조각을 획득했습니다: **E**")
                st.session_state.codes.append("E")
                st.session_state.mission = 2
                st.rerun()
            else:
                st.error("정답을 입력하세요.")

    # -----------------------
    # 미션 2
    # -----------------------
    elif st.session_state.mission == 2:
        st.subheader("미션 2️⃣ : 지수의 흔적을 추적하라")

        year_range = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year), key="m2_slider")
        filt = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
        fig = px.line(filt, x="date", y="지수", title="Nino3.4 지수 변화", markers=True)
        fig.update_yaxes(range=[-3, 3])
        st.plotly_chart(fig, use_container_width=True)

        st.write("**질문:** 선택한 기간 중 지수가 2 이상인 해는?")
        a2 = st.text_input("정답 입력", key="mission2_q2")

        if st.button("제출 (미션 2)"):
            if a2.strip():
                st.success("정답입니다! 암호 조각을 획득했습니다: **N**")
                st.session_state.codes.append("N")
                st.session_state.mission = 3
                st.rerun()
            else:
                st.error("정답을 입력하세요.")

    # -----------------------
    # 미션 3
    # -----------------------
    elif st.session_state.mission == 3:
        st.subheader("미션 3️⃣ : 강력한 흔적을 비교하라")
        st.write("엘니뇨와 라니냐 강도를 비교하세요.")

        # 데이터 요약
        summary = df.groupby("Year")["지수"].mean().reset_index()
        fig3 = px.bar(summary, x="Year", y="지수", title="연도별 평균 지수")
        st.plotly_chart(fig3, use_container_width=True)

        st.write("**질문:** 평균 지수가 가장 높은 해는?")
        a3 = st.text_input("정답 입력", key="mission3_q3")

        if st.button("제출 (미션 3)"):
            if a3.strip():
                st.success("정답입니다! 암호 조각을 획득했습니다: **S**")
                st.session_state.codes.append("S")
                st.session_state.mission = 4
                st.rerun()
            else:
                st.error("정답을 입력하세요.")

    # -----------------------
    # 미션 4
    # -----------------------
    elif st.session_state.mission == 4:
        st.subheader("미션 4️⃣ : 가장 거대한 흔적을 찾아라")

        yr = st.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
        filt = df[(df["Year"] >= yr[0]) & (df["Year"] <= yr[1])]
        if len(filt) > 0:
            yearly_min = filt.groupby("Year")["지수"].min().reset_index()

            fig4 = px.line(yearly_min, x="Year", y="지수", title="연도별 최소 지수 (가장 강한 라니냐 후보)", markers=True)
            fig4.add_hline(y=-0.5, line_dash="dash", line_color="blue", annotation_text="라니냐 기준 (-0.5)")
            fig4.update_yaxes(range=[-3, 3])
            st.plotly_chart(fig4, use_container_width=True)

            strongest_year = int(yearly_min.loc[yearly_min["지수"].idxmin(), "Year"])

            st.write("**질문:** 이 기간 동안 가장 강한 라니냐(지수가 가장 낮은) 연도는?")
            a4 = st.text_input("정답 입력", key="mission4_q4")
            if st.button("제출 (미션 4)"):
                if a4.strip() == str(strongest_year):
                    st.success("정답입니다! 암호 조각을 획득했습니다: **O**")
                    st.session_state.codes.append("O")
                    st.session_state.finished = True
                    st.session_state.end_time = time.time()
                    st.session_state.page = "finish"
                    st.rerun()
                else:
                    st.error("틀렸습니다. 다시 시도하세요.")
        else:
            st.warning("선택한 기간에 데이터가 없습니다.")

# -----------------------
# 완료 화면
# -----------------------
elif st.session_state.page == "finish":
    st.subheader("🎉 미션 완료")
    dur_sec = (st.session_state.end_time - st.session_state.start_time) if st.session_state.start_time else 0
    m = int(dur_sec // 60)
    s = int(dur_sec % 60)
    st.write(f"✅ **총 소요 시간: {m}분 {s}초**")

    st.write("모은 암호 조각을 조합해 암호를 입력하세요.")
    code = st.text_input("최종 암호 입력")
    if st.button("암호 해독"):
        if code.strip().upper() == "ENSO":
            st.success("🎯 암호 해독 성공! 사건의 진실이 밝혀졌습니다!")
            st.balloons()
        else:
            st.error("❌ 암호가 틀렸습니다. 다시 시도하세요.")
