import streamlit as st
import requests

def render():
    st.title("📷 피부 질환 진단 시스템")

    # 초기화
    if "show_chatbot_header" not in st.session_state:
        st.session_state.show_chatbot_header = False

    for key, default in {
        "questions": [],
        "answers": [],
        "disease": "",
        "predicted": False,
        "chat_history": [],
        "prediction_message": ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    def chat_bot(message, is_user=False):
        role = "user" if is_user else "assistant"
        with st.chat_message(role):
            st.write(message)

    def make_prediction(file):
        files = {"file": (file.name, file, file.type)}
        with st.spinner("🔍 이미지를 분석 중입니다..."):
            try:
                response = requests.post("http://127.0.0.1:8000/predict", files=files)
                response.raise_for_status()
                result = response.json()["predictions"][0]["class"]
                confidence = response.json()["predictions"][0]["confidence"]

                st.session_state.disease = result
                st.session_state.predicted = True
                st.session_state.prediction_message = f"✅ 예측된 질환: {result} 🔎 이미지 예측 확률: {confidence * 100:.2f}%"
            except Exception as e:
                st.session_state.predicted = False
                chat_bot(f"❌ 예측 실패: {e}")

    uploaded_file = st.file_uploader("질병 이미지를 업로드하세요.", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and st.button("진단 시작"):
        st.session_state.show_chatbot_header = True   # 이미지 업로드 시 챗봇 제목 보여주기
        make_prediction(uploaded_file)
        
    # 예측 결과 표시
    if "prediction_message" in st.session_state and st.session_state.prediction_message != "":
        st.success(st.session_state.prediction_message)

    # 챗봇 제목은 이미지 업로드 이후에만 보여줌
    if st.session_state.show_chatbot_header:
        st.subheader("🩺 피부 질환 진단 챗봇")

    # 예측 완료 후 질문 생성
    if st.session_state.predicted and st.session_state.disease:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/generate_questions",
                json={"disease_name": st.session_state.disease}
            )
            response.raise_for_status()
            data = response.json()

            st.session_state.questions = data["questions"]
            st.session_state.answers = [None] * len(data["questions"])

            chat_bot("📋 아래 질문에 답변해주세요.")
            st.session_state.predicted = False
        except Exception as e:
            chat_bot(f"⚠️ 질문 생성 실패: {e}")
            st.session_state.predicted = False

    # 질문 응답 받기 (채팅 스타일)
    if st.session_state.questions and None in st.session_state.answers:
        idx = st.session_state.answers.index(None)
        chat_bot(f"{idx + 1}. {st.session_state.questions[idx]}")

        col1, col_yes, col_no, col_spacer = st.columns([5, 1, 2, 8])
        with col_yes:
            if st.button("예", key=f"yes_{idx}"):
                st.session_state.answers[idx] = True
                chat_bot("예", is_user=True)
                st.rerun()
        with col_no:
            if st.button("아니오", key=f"no_{idx}"):
                st.session_state.answers[idx] = False
                chat_bot("아니오", is_user=True)
                st.rerun()

    # 최종 결과 출력
    elif st.session_state.questions and None not in st.session_state.answers:
        true_count = sum(st.session_state.answers)
        disease = st.session_state.disease

        if true_count == 3:
            final_msg = f"🧾 최종 진단 결과: **{disease}일 가능성이 매우 높습니다.**"
        elif true_count == 2:
            final_msg = f"🧾 최종 진단 결과: **{disease}일 것으로 예상됩니다.**"
        else:
            final_msg = f"🧾 최종 진단 결과: **{disease}가 의심됩니다.**"

        chat_bot(final_msg)

        # 질병 정보 요청
        try:
            with st.spinner("📚 질병 정보를 불러오는 중입니다..."):
                info_response = requests.post(
                    "http://127.0.0.1:8000/get_disease_info",
                    json={"disease_name": disease}
                )
                info_response.raise_for_status()
                disease_info = info_response.json()["info"]
                chat_bot(f"🧠 **{disease}에 대한 요약 정보**\n\n{disease_info}")
                chat_bot("🏥 더 정확한 진단을 위해 가까운 병원에 방문해보세요.")
        except Exception as e:
            chat_bot(f"⚠️ 질병 정보 불러오기 실패: {e}")

        st.divider()
        if st.button("🔄 진단 다시하기"):
            for key in ["questions", "answers", "disease", "predicted", "prediction_message", "chat_history", "show_chatbot_header"]:
                st.session_state.pop(key, None)
            st.rerun()

if __name__ == "__main__":
    render()
