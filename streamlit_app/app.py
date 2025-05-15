import streamlit as st
import page.skin_disease_prediction as sdp
import page.find_dermatology_hospital as fdh

# 페이지 기본 설정
st.set_page_config(page_title="피부 질환 진단 대시보드", layout="wide")

# 사이드바 글자 크기 조정
st.markdown("""
    <style>
    /* 사이드바 전체 영역 안의 라디오 항목 label 글자 크기 변경 */
    section[data-testid="stSidebar"] label {
        font-size: 25px !important;
    }

    /* 사이드바 제목의 글자 크기 변경 */
    section[data-testid="stSidebar"] h1 {
        font-size: 33px !important;
    }
    </style>
""", unsafe_allow_html=True)


# 사이드바 메뉴
st.sidebar.markdown(" ")  # 빈 줄을 위한 공백
st.sidebar.markdown(" ")  # 빈 줄을 위한 공백
st.sidebar.title("📋 메뉴")
st.sidebar.markdown(" ")  # 빈 줄을 위한 공백
page = st.sidebar.radio("원하는 기능을 선택하세요:", ["피부 질환 예측", "피부과 전문의 병원 찾기"])

# 각 기능 조건문으로 분기
if page == "피부 질환 예측":
    sdp.render()  # 예측 페이지 렌더링
elif page == "피부과 전문의 병원 찾기":
    fdh.render()  # 병원 찾기 페이지 렌더링
