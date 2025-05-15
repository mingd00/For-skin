import streamlit as st
import streamlit.components.v1 as components

def render():
    st.markdown("## 🏥 피부과 전문의 병원 찾기")
    st.write("대한피부과학회 인증 피부과 전문의가 운영하는 병원을 확인할 수 있습니다.")

    iframe_html = """
        <style>
            .iframe-card {
                border: 1px solid #ddd;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
        </style>
        <div class="iframe-card">
            <iframe src="https://www.akd.or.kr/dermatologist/local" width="100%" height="800px" frameborder="0"></iframe>
        </div>
    """
    components.html(iframe_html, height=800)
    
if __name__ == "__main__":
    render()
