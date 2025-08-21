import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ✅ matplotlib 폰트 설정 (한글 깨짐 방지)
rcParams['font.family'] = 'DejaVu Sans'

# ✅ 페이지 기본 설정
st.set_page_config(page_title="기후 미션 챌린지", page_icon="🌊", layout="wide")

# ✅ CSS 디자인 (배경 이미지 + 글자색)
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
}
[data-testid="stHeader"], [data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.8);
}
h1, h2, h3, p, label {
    color: black !important;
    font-family: 'Nanum Gothic', sans-serif;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['날짜'] = df['날짜'].str.replace("﻿", "")
    df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월')
    return df

df = load_data()

# ✅ 미션 진행 단계
if "mission" not in st.session_state:
    st.session_state["mission"] = 1

mission = st.session_state["mission"]

# ✅ 미션 1: 데이터 탐색
if mission == 1:
    st.title("미션 1️⃣: 데이터 탐험가 되기")
    st.write("다음 표는 해양의 특정 지역에서 측정된 기후 지표입니다. 최근 6개월 데이터를 살펴보고, **가장 낮은 지표값**을 입력하세요.")

    st.dataframe(df.head(12))

    min_val = df["nino3.4 index"].min().round(3)
    answer = st.text_input("가장 낮은 지표값은 무엇일까요? (소수점 3자리까지)")

    if st.button("정답 확인"):
        if answer.strip() == str(min_val):
            st.success("정답입니다! 🎉 다음 미션으로 이동하세요.")
            st.session_state["mission"] = 2
            st.experimental_rerun()
        else:
            st.error("다시 시도해보세요!")

# ✅ 미션 2: 그래프 분석
elif mission == 2:
    st.title("미션 2️⃣: 그래프에서 패턴 찾기")
    st.write("아래 그래프에서 **특정 월**을 선택하여 변화 패턴을 분석하세요.")

    start_date = st.date_input("시작 날짜", df['date'].min())
    end_date = st.date_input("종료 날짜", df['date'].max())

    filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    st.write(f"선택된 기간 데이터 ({len(filtered)} 개):")
    st.dataframe(filtered)

    # ✅ 그래프
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(filtered['date'], filtered['nino3.4 index'], marker='o', label="지표 변화")
    ax.axhline(0.5, color='red', linestyle='--', label="상한선")
    ax.axhline(-0.5, color='blue', linestyle='--', label="하한선")
    ax.set_title("기후 지표 변화")
    ax.legend()
    st.pyplot(fig)

    # ✅ 문제
    st.write("질문: **그래프에서 0.5 이상으로 올라간 첫 번째 월의 연도를 입력하세요.**")
    answer2 = st.text_input("연도를 입력하세요 (예: 2024)")

    correct_year = str(df[df['nino3.4 index'] > 0.5].iloc[0]['date'].year)

    if st.button("정답 확인"):
        if answer2.strip() == correct_year:
            st.success("정답입니다! 🎉 마지막 미션으로 이동하세요.")
            st.session_state["mission"] = 3
            st.experimental_rerun()
        else:
            st.error("다시 시도해보세요!")

# ✅ 미션 3: 최종 암호 찾기
elif mission == 3:
    st.title("미션 3️⃣: 최종 암호 해독")
    st.write("축하합니다! 마지막 단계입니다. 아래 글자 조각을 조합해 최종 암호를 완성하세요.")
    st.write("🔑 조각: **E**, **N**, **S**, **O**")

    answer3 = st.text_input("최종 암호는?")

    if st.button("제출"):
        if answer3.strip().upper() == "ENSO":
            st.balloons()
            st.success("정답! 모든 미션을 완료했습니다! 🎉")
        else:
            st.error("틀렸습니다. 다시 시도하세요!")
