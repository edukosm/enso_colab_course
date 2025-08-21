import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ✅ 폰트 설정 (한글 깨짐 방지)
rcParams['font.family'] = 'DejaVu Sans'

# ✅ 페이지 설정
st.set_page_config(page_title="기후 미션 챌린지", layout="wide")

# ✅ CSS 스타일: 배경 + 카드 UI + 버튼 색상
page_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
    background-size: cover;
}

.fixed-title {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.9);
    text-align: center;
    padding: 15px;
    font-size: 32px;
    font-weight: bold;
    z-index: 1000;
    color: black;
}

.card {
    background: rgba(255, 255, 255, 0.85);
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
}

div.stButton > button {
    background-color: black !important;
    color: white !important;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    padding: 10px 20px;
}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

# ✅ 상단 고정 타이틀
st.markdown('<div class="fixed-title">🌍 기후 미션 챌린지</div>', unsafe_allow_html=True)
st.write("\n\n\n")

# ✅ 데이터 로드
df = pd.read_csv("oni_month_20250821.csv")
df.columns = df.columns.str.strip()
df['날짜'] = df['날짜'].str.replace("﻿","").str.strip()
df['date'] = pd.to_datetime(df['날짜'], format='%Y년 %m월', errors='coerce')
df = df.dropna(subset=['date'])

# ✅ 세션 상태 초기화
if 'mission' not in st.session_state:
    st.session_state['mission'] = 1
if 'hints' not in st.session_state:
    st.session_state['hints'] = []

# ✅ 미션 1 (슬라이더로 값 선택)
if st.session_state['mission'] == 1:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📌 Mission 1: 바다의 온도 비밀")
        st.write("질문: 2025년 06월의 **지수 값**을 선택하세요.")
        
        correct_value = 0.030
        value = st.slider("값을 선택하세요:", -2.0, 2.0, 0.0, 0.001)
        
        if st.button("제출"):
            if abs(value - correct_value) < 0.0005:
                st.success("정답입니다! 암호 힌트: **E**")
                st.session_state['hints'].append("E")
                st.session_state['mission'] = 2
                st.experimental_rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
        st.markdown('</div>', unsafe_allow_html=True)

# ✅ 미션 2 (기간 선택 + 자동 평균/최댓값 업데이트)
elif st.session_state['mission'] == 2:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📌 Mission 2: 그래프 탐험")
        st.write("질문: 선택한 기간 중 가장 높은 값은 어느 달인가요?")
        
        min_date = df['date'].min()
        max_date = df['date'].max()
        start_date, end_date = st.slider(
            "기간을 선택하세요:",
            min_value=min_date,
            max_value=max_date,
            value=(max_date - pd.DateOffset(months=6), max_date),
            format="YYYY-MM"
        )
        
        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        st.line_chart(filtered_df.set_index('date')['nino3.4 index'])
        
        st.write(f"📊 선택한 기간 평균: {filtered_df['nino3.4 index'].mean():.3f}")
        st.write(f"📈 선택한 기간 최대: {filtered_df['nino3.4 index'].max():.3f}")
        
        answer = st.text_input("정답 입력 (예: 2025년 03월):")
        if st.button("제출"):
            if "2025년 03월" in answer:
                st.success("정답입니다! 암호 힌트: **N**")
                st.session_state['hints'].append("N")
                st.session_state['mission'] = 3
                st.experimental_rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
        st.markdown('</div>', unsafe_allow_html=True)

# ✅ 미션 3 (최근 3개월 평균값 슬라이더 → 자동 업데이트)
elif st.session_state['mission'] == 3:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📌 Mission 3: 평균을 계산하라")
        st.write("질문: 최근 **n개월 평균 값**이 0을 넘습니까?")
        
        months = st.slider("개월 수 선택:", 3, 12, 3)
        avg = df['nino3.4 index'].tail(months).mean()
        st.write(f"최근 {months}개월 평균 값: {avg:.3f}")
        
        answer = st.radio("정답:", ["예", "아니오"])
        if st.button("제출"):
            if (avg > 0 and answer == "예") or (avg <= 0 and answer == "아니오"):
                st.success("정답입니다! 암호 힌트: **S**")
                st.session_state['hints'].append("S")
                st.session_state['mission'] = 4
                st.experimental_rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
        st.markdown('</div>', unsafe_allow_html=True)

# ✅ 미션 4 (아이콘 선택형)
elif st.session_state['mission'] == 4:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📌 Mission 4: 기후의 영향")
        st.write("질문: 이런 해양 상태가 우리나라 겨울에 주는 영향은?")
        st.write("🟢 ① 겨울이 매우 따뜻해진다\n🔵 ② 겨울이 평년보다 추워진다\n🟠 ③ 겨울 강수량이 줄어든다\n⚪ ④ 큰 영향이 없다")
        
        answer = st.selectbox("정답 선택:", ["①", "②", "③", "④"])
        if st.button("제출"):
            if answer == "②":
                st.success("정답입니다! 암호 힌트: **O**")
                st.session_state['hints'].append("O")
                st.session_state['mission'] = 5
                st.experimental_rerun()
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
        st.markdown('</div>', unsafe_allow_html=True)

# ✅ 최종 미션
elif st.session_state['mission'] == 5:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("🎯 최종 미션: 암호 해독")
        st.write(f"지금까지 모은 힌트: {''.join(st.session_state['hints'])}")
        final_answer = st.text_input("최종 암호 입력:")
        if st.button("제출"):
            if final_answer.strip().upper() == "ENSO":
                st.balloons()
                st.success("축하합니다! 모든 미션을 완료했습니다!")
            else:
                st.error("틀렸습니다. 다시 시도하세요.")
        st.markdown('</div>', unsafe_allow_html=True)
