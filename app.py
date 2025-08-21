import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 앱 제목
st.set_page_config(page_title="ENSO 암호 해독 챌린지", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edukosm/enso_colab_course/refs/heads/main/oni_month_20250821.csv"
    df = pd.read_csv(url)
    df['날짜'] = df['날짜'].str.replace('﻿', '')  # BOM 제거
    return df

enso = load_data()

# 단계 관리
if "step" not in st.session_state:
    st.session_state.step = 0
if "hints" not in st.session_state:
    st.session_state.hints = []

# UI
st.title("🌊 ENSO 암호 해독 챌린지")
st.write("해양 기후의 비밀 코드를 해독하고, 숨겨진 단어를 완성하세요!")

# 진행률 표시
progress = st.session_state.step / 5
st.progress(progress)

# 인트로
if st.session_state.step == 0:
    st.header("시작하기 전에")
    st.write("""
    **미션 구조**:
    1. ONI 데이터를 분석해 퀴즈를 풀어야 합니다.
    2. 각 미션 정답을 맞히면 **알파벳 힌트**를 얻습니다.
    3. 마지막 단계에서 힌트를 조합해 **최종 암호**를 입력하세요.
    """)
    if st.button("챌린지 시작"):
        st.session_state.step = 1

# ✅ 미션 1: 최근 연도 찾기
elif st.session_state.step == 1:
    st.header("🔍 Mission 1: 최근 데이터 연도는?")
    if st.button("데이터 보기"):
        st.dataframe(enso.head())

    answer = st.text_input("가장 최근 연도는?", key="m1")
    recent_year = enso['날짜'].iloc[0][:4]  # 예: "2025"
    if st.button("정답 확인", key="b1"):
        if answer.strip() == recent_year:
            st.success("정답입니다! 알파벳 힌트: E")
            st.session_state.hints.append("E")
            st.session_state.step = 2
        else:
            st.error("틀렸습니다. 다시 시도하세요.")

# ✅ 미션 2: El Niño 개수
elif st.session_state.step == 2:
    st.header("🔍 Mission 2: El Niño 개수")
    if st.button("그래프 보기"):
        st.line_chart(enso['ONI index'])

    answer = st.text_input("ONI index ≥ 0.5인 개월 수는?", key="m2")
    el_nino_count = (enso['ONI index'] >= 0.5).sum()
    if st.button("정답 확인", key="b2"):
        if answer.strip() == str(el_nino_count):
            st.success("정답입니다! 알파벳 힌트: N")
            st.session_state.hints.append("N")
            st.session_state.step = 3
        else:
            st.error("틀렸습니다. 다시 확인하세요.")

# ✅ 미션 3: La Niña 개수
elif st.session_state.step == 3:
    st.header("🔍 Mission 3: La Niña 개수")
    answer = st.text_input("ONI index ≤ -0.5인 개월 수는?", key="m3")
    la_nina_count = (enso['ONI index'] <= -0.5).sum()
    if st.button("정답 확인", key="b3"):
        if answer.strip() == str(la_nina_count):
            st.success("정답입니다! 알파벳 힌트: S")
            st.session_state.hints.append("S")
            st.session_state.step = 4
        else:
            st.error("틀렸습니다. 다시 확인하세요.")

# ✅ 미션 4: 평균 ONI 값
elif st.session_state.step == 4:
    st.header("🔍 Mission 4: 평균 ONI 값")
    answer = st.text_input("ONI index의 평균을 소수 둘째 자리까지 입력하세요 (예: -0.12)", key="m4")
    mean_oni = round(enso['ONI index'].mean(), 2)
    if st.button("정답 확인", key="b4"):
        if answer.strip() == str(mean_oni):
            st.success("정답입니다! 알파벳 힌트: O")
            st.session_state.hints.append("O")
            st.session_state.step = 5
        else:
            st.error("틀렸습니다. 다시 확인하세요.")

# ✅ 최종 단계
elif st.session_state.step == 5:
    st.header("🎯 최종 단계: 암호 입력")
    st.write("힌트:", " ".join(st.session_state.hints))
    final = st.text_input("최종 암호는?", key="final")
    if st.button("제출"):
        if final.upper() == "".join(st.session_state.hints):
            st.balloons()
            st.success("축하합니다! 모든 미션을 완료했습니다!")
        else:
            st.error("틀렸습니다. 다시 확인하세요.")
