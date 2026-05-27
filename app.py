import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# 페이지 설정
st.set_page_config(page_title="핑크빛 연애 상담소", page_icon="💖")
st.title("💖 핑크빛 연애 상담소")
st.subheader("당신의 고민, 제미나이가 들어드릴게요.")

# 1. API 키 설정 (Streamlit Secrets)
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
        st.stop()
    
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 모델 설정 (Gemini 2.5 Flash-Lite)
    # 시스템 프롬프트로 연애 상담가 페르소나 부여
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction="당신은 따뜻하고 공감 능력이 뛰어난 전문 연애 상담가입니다. 사용자의 고민을 경청하고, 때로는 다정하게, 때로는 현실적인 조언을 제공하세요. 답변은 항상 친절한 말투(~해요, ~보세요)를 사용하세요."
    )
except Exception as e:
    st.error(f"모델 초기화 중 오류 발생: {e}")

# 2. 채팅 기록 초기화 (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 이전 대화 내역 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 사용자 입력 및 로직
if prompt := st.chat_input("오늘 어떤 고민이 있으신가요?"):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 대화 맥락 포함을 위해 기록 전달
            chat_session = model.start_chat(
                history=[
                    {"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
            )
            
            response = chat_session.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 기록 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except exceptions.InvalidArgument as e:
            st.error("API 키가 올바르지 않거나 설정이 잘못되었습니다.")
        except exceptions.ResourceExhausted:
            st.error("API 할당량을 초과했습니다. 잠시 후 다시 시도해주세요.")
        except Exception as e:
            st.error(f"예기치 못한 오류가 발생했습니다: {e}")
