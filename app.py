import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ----------------------------
# ✅ 1. 스타일 & 한글 폰트 적용
# ----------------------------
st.set_page_config(page_title="기후 미션 챌린지", layout="wide")

# ✅ 웹 폰트 적용 (UI)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');
html, body, [class*="css"] {
    font-family: 'Nanum Gothic', sans-serif;
    color: black !important;
}
h1, h2, h3, h4 {
    color: black !important;
}
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e"); /* 바다 배경 (Unsplash 무료 이미지) */
    background-size: cover;
}
[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.8);
}
</style>
""", unsafe_allow_html=True)

# ✅ matplotlib 한글 폰트 설정
if not os.path.exists("NanumGothic.ttf"):
    os.system('wget -O NanumGothic.ttf "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"')

fm.fontManager.addfont("NanumGothic.ttf")
plt.rcParams['font.family'] = 'NanumGothic'

# ----------------------------
# ✅ 2. 데이터 불러오기
# ----------------------------
DATA_URL = "https://raw.githubusercontent.com/edukosm/enso_colab_course/main/oni_month_20250821.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = [col.strip() for col in df.columns]
    df['날짜'] = df['날짜'].str.replace("﻿", "", regex=True)
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월', errors='coerce')
    return df

enso = load_data()

# ----------------------------
# ✅ 3. 세션 상태 (페이지 네비게이션)
# ----------------------------
if "mission" not in st.session_state:
    st.session_state["mission"] = 1

def next_mission():
    st.session_state["mission"] += 1

# ----------------------------
# ✅ 4. 미션 페이지 구현
# ----------------------------
st.title("🌊 기후 미션 챌린지")

# ----------------------------
# ✅ 미션 1: 데이터 탐험
# ----------------------------
if st.session_state["mission"] == 1:
    st.header("📊 미션 1: 데이터 탐험하기")
    st.write("아래 데이터는 특정 해양 지수의 월별 값입니다. 최근 12개월 데이터를 확인하세요.")

    # 최근 12개월 데이터 필터
    recent = enso.sort_values('date', ascending=False).head(12)
    st.dataframe(recent[['날짜', 'nino3.4 index', 'ONI index']])

    st.write("질문: **가장 최근 월의 nino3.4 index 값은 무엇인가요?**")
    user_answer = st.text_input("정답 입력")

    correct_answer = str(round(recent.iloc[0]['nino3.4 index'], 3))

    if user_answer == correct_answer:
        st.success("정답입니다! 다음 미션으로 이동하세요.")
        st.button("다음 미션으로", on_click=next_mission)
    else:
        st.info("힌트: 위 데이터 표에서 가장 최근 행을 확인하세요.")

# ----------------------------
# ✅ 미션 2: 그래프 분석
# ----------------------------
elif st.session_state["mission"] == 2:
    st.header("📈 미션 2: 변화 추세를 시각화하기")

    st.write("아래 슬라이더로 기간을 조정하여 지수 변화를 확인하세요.")
    start_year, end_year = st.slider("연도 범위 선택", 2000, 2025, (2015, 2025))

    filtered = enso[(enso['date'].dt.year >= start_year) & (enso['date'].dt.year <= end_year)]

    # 그래프
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(filtered['date'], filtered['nino3.4 index'], label='지수 변화')
    ax.axhline(0.5, color='r', linestyle='--', label='양의 기준선')
    ax.axhline(-0.5, color='b', linestyle='--', label='음의 기준선')
    ax.set_title(f"{start_year}년 ~ {end_year}년 지수 변화")
    ax.legend()
    st.pyplot(fig)

    st.write("질문: **그래프에서 양의 기준선(0.5) 이상인 구간이 몇 개월인가요?**")
    user_answer = st.number_input("정답 입력", step=1)

    correct_count = (filtered['nino3.4 index'] >= 0.5).sum()

    if user_answer == correct_count:
        st.success("정답입니다! 마지막 미션으로 이동하세요.")
        st.button("마지막 미션으로", on_click=next_mission)
    else:
        st.info("힌트: 그래프에서 빨간 점선을 기준으로 확인하세요.")

# ----------------------------
# ✅ 미션 3: 최종 암호 해독
# ----------------------------
elif st.session_state["mission"] == 3:
    st.header("🔐 미션 3: 암호 해독")

    st.write("""
    축하합니다! 이제 마지막 단계입니다.  
    아래 버튼을 눌러 최종 암호를 확인하세요.
    """)

    if st.button("최종 암호 보기"):
        st.success("🎯 최종 암호는: **OCEAN** 🌊")

    st.balloons()
