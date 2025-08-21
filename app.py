import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ✅ 페이지 기본 설정
st.set_page_config(page_title="해양 기후 탐험", page_icon="🌊", layout="wide")

# ✅ CSS 스타일 추가 (배경 이미지)
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
st.title("🌊 해양 기후 탐험: 데이터로 미션을 완수하라!")
st.markdown("**팀별 미션**: 데이터를 분석하고 퀴즈를 풀어 최종 암호를 완성하세요!")

# ✅ 데이터 로드
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
    df = pd.read_csv(url)
    df['날짜'] = df['날짜'].str.replace("﻿", "")
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')
    return df

data = load_data()

# ✅ 사이드바: 사용자 필터
st.sidebar.header("🔍 데이터 필터")
year_range = st.sidebar.slider("연도 선택", 2024, 2025, (2024, 2025))
filtered_data = data[(data['date'].dt.year >= year_range[0]) & (data['date'].dt.year <= year_range[1])]

# ✅ 데이터 표
st.subheader("📊 기후 데이터 테이블")
st.dataframe(filtered_data[['날짜', 'nino3.4 index', 'ONI index', 'nino3.4 수온 평균']])

# ✅ 그래프 옵션
st.subheader("📈 기후 지수 변화")
show_ma = st.checkbox("이동평균(3개월) 표시", value=True)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(filtered_data['date'], filtered_data['ONI index'], label='ONI Index', color='blue')
if show_ma:
    ax.plot(filtered_data['date'], filtered_data['nino3.4 수온 평균(3개월)'], label='3개월 이동평균', color='orange')
ax.axhline(0.5, color='red', linestyle='--', label='양의 변화 기준')
ax.axhline(-0.5, color='green', linestyle='--', label='음의 변화 기준')
ax.set_title("기후 지수 변화")
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.header("🕵️ 팀별 미션: 암호 4단계")

# ✅ 미션 1
st.subheader("🔐 미션 1")
st.markdown("**문제:** 2025년 6월의 ONI index 값은 얼마인가요? (소수점 둘째자리까지)")
answer1 = st.text_input("정답 입력 (예: 0.12)", key="m1")
if st.button("제출 (미션 1)"):
    correct_value = round(float(data[data['날짜'] == "2025년 06월"]['ONI index'].values[0]), 2)
    if answer1 == str(correct_value):
        st.success("정답입니다! 🔑 첫 번째 암호: **E**")
    else:
        st.error("틀렸습니다. 다시 확인하세요!")

# ✅ 미션 2
st.subheader("🔐 미션 2")
st.markdown("**문제:** ONI index가 0.5 이상으로 올라간 달이 있나요? (예/아니오)")
answer2 = st.radio("선택", ["예", "아니오"], key="m2")
if st.button("제출 (미션 2)"):
    if (data['ONI index'] > 0.5).any() and answer2 == "예":
        st.success("정답입니다! 🔑 두 번째 암호: **N**")
    else:
        st.error("틀렸습니다. 힌트를 다시 찾아보세요!")

# ✅ 미션 3
st.subheader("🔐 미션 3")
st.markdown("**문제:** 데이터에서 nino3.4 수온 평균이 가장 높은 달은 언제인가요? (예: 2025년 05월)")
answer3 = st.text_input("정답 입력", key="m3")
if st.button("제출 (미션 3)"):
    max_month = data.loc[data['nino3.4 수온 평균'].idxmax(), '날짜']
    if answer3.strip() == max_month.strip():
        st.success("정답입니다! 🔑 세 번째 암호: **S**")
    else:
        st.error("틀렸습니다. 다시 시도하세요!")

# ✅ 미션 4
st.subheader("🔐 미션 4")
st.markdown("**문제:** nino3.4 index가 가장 낮은 값은 얼마인가요? (소수점 둘째자리까지)")
answer4 = st.text_input("정답 입력 (예: -0.87)", key="m4")
if st.button("제출 (미션 4)"):
    min_val = round(data['nino3.4 index'].min(), 2)
    if answer4 == str(min_val):
        st.success("정답입니다! 🔑 네 번째 암호: **O**")
    else:
        st.error("틀렸습니다. 다시 확인하세요!")

st.markdown("---")
st.header("🏆 최종 암호 입력")
final_code = st.text_input("암호 4글자를 입력하세요", key="final")
if st.button("제출 (최종)"):
    if final_code.upper() == "ENSO":
        st.balloons()
        st.success("🎉 축하합니다! 모든 미션을 완료했습니다!")
    else:
        st.error("❌ 암호가 틀렸습니다. 다시 조합해보세요!")
