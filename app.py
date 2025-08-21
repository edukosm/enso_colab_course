import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 페이지 기본 설정
st.set_page_config(page_title="ENSO Mission", page_icon="🌊", layout="wide")

# ✅ CSS 스타일 추가 (배경 이미지, 글꼴)
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ 제목
st.title("🌊 ENSO 미션: 데이터로 기후의 비밀을 풀어라!")
st.markdown("**팀별 미션**: 데이터를 분석하고 퀴즈를 풀어 최종 암호를 완성하세요!")

# ✅ 데이터 로드
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
    df = pd.read_csv(url)
    df['날짜'] = df['날짜'].str.replace("﻿", "")
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')
    return df

enso = load_data()

# ✅ 사이드바: 사용자 필터
st.sidebar.header("🔍 데이터 필터")
year_range = st.sidebar.slider("연도 선택", 2024, 2025, (2024, 2025))
enso_filtered = enso[(enso['date'].dt.year >= year_range[0]) & (enso['date'].dt.year <= year_range[1])]

# ✅ 데이터 표 표시
st.subheader("📊 ENSO 데이터 테이블")
st.dataframe(enso_filtered[['날짜', 'nino3.4 index', 'ONI index', 'nino3.4 수온 평균']])

# ✅ 그래프 옵션
st.subheader("📈 ENSO 시각화")
show_ma = st.checkbox("이동평균(3개월) 표시", value=True)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(enso_filtered['date'], enso_filtered['ONI index'], label='ONI Index', color='blue')
if show_ma:
    ax.plot(enso_filtered['date'], enso_filtered['nino3.4 수온 평균(3개월)'], label='3개월 이동평균', color='orange')
ax.axhline(0.5, color='red', linestyle='--', label='El Niño 기준')
ax.axhline(-0.5, color='green', linestyle='--', label='La Niña 기준')
ax.set_title("ONI Index 변화")
ax.legend()
st.pyplot(fig)

# ✅ 미션 1: 데이터 탐색 퀴즈
st.subheader("🕵️ 미션 1: 데이터 퀴즈")
st.markdown("**문제:** 2025년 6월의 ONI index 값은 얼마인가요?")
answer = st.text_input("정답을 입력하세요 (소수점 둘째자리까지)")
if st.button("제출"):
    correct_value = round(float(enso[enso['날짜'] == "2025년 06월"]['ONI index'].values[0]), 2)
    if answer == str(correct_value):
        st.success("정답입니다! 🔑 첫 번째 암호: **E**")
    else:
        st.error("틀렸습니다. 다시 시도해보세요!")

# ✅ 미션 2: 시각화 분석 퀴즈
st.subheader("🕵️ 미션 2: 그래프 해석")
st.markdown("**문제:** ONI index가 0.5 이상으로 올라간 달이 있나요? (예/아니오)")
answer2 = st.radio("선택", ["예", "아니오"])
if st.button("제출 (미션 2)"):
    if (enso['ONI index'] > 0.5).any() and answer2 == "예":
        st.success("정답입니다! 🔑 두 번째 암호: **N**")
    else:
        st.error("틀렸습니다. 힌트를 다시 찾아보세요!")

# ✅ 최종 안내
st.markdown("---")
st.info("모든 미션을 완료하면 **암호를 조합해보세요! (총 4글자)**")
