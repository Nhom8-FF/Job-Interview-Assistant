import streamlit as st
import time
import random
from prompts import SYSTEM_PROMPT
from gemini_helper import generate_response

def create_interview_system_prompt(interview_type, job_role=None, resume=None, language="vi"):
    """
    Tạo system prompt cho mô phỏng phỏng vấn
    """
    if language == "vi":
        interviewer_role = {
            "technical": "người phỏng vấn kỹ thuật",
            "behavioral": "người phỏng vấn hành vi",
            "hr": "người phỏng vấn từ bộ phận nhân sự",
            "case": "người phỏng vấn tình huống"
        }
        
        system_prompt = f"""Bạn là một {interviewer_role.get(interview_type, "người phỏng vấn")} chuyên nghiệp và có kinh nghiệm.
Hãy tiến hành một buổi phỏng vấn thực tế và chân thực với ứng viên.

Quy tắc của cuộc phỏng vấn:
1. Mỗi lần bạn chỉ hỏi một câu hỏi.
2. Lắng nghe câu trả lời của ứng viên và đưa ra phản hồi ngắn gọn.
3. Phản hồi nên có tính xây dựng và chuyên nghiệp.
4. Sau khi đã hỏi ít nhất 5 câu hỏi, hãy hỏi ứng viên có muốn kết thúc không.
5. Nếu ứng viên muốn kết thúc, hãy đưa ra đánh giá tổng thể về buổi phỏng vấn.

Hãy bắt đầu bằng cách giới thiệu bản thân và giải thích quy trình phỏng vấn.
Trả lời bằng tiếng Việt.
"""
    else:
        interviewer_role = {
            "technical": "technical interviewer",
            "behavioral": "behavioral interviewer",
            "hr": "HR interviewer",
            "case": "case interviewer"
        }
        
        system_prompt = f"""You are an experienced {interviewer_role.get(interview_type, "interviewer")} conducting a professional interview.
Conduct a realistic and authentic interview with the candidate.

Interview rules:
1. Ask only one question at a time.
2. Listen to the candidate's response and provide brief feedback.
3. Feedback should be constructive and professional.
4. After asking at least 5 questions, ask if the candidate wants to end the interview.
5. If the candidate wants to end, provide an overall assessment of the interview.

Start by introducing yourself and explaining the interview process.
Answer in English.
"""

    # Thêm thông tin về vị trí công việc nếu có
    if job_role:
        if language == "vi":
            system_prompt += f"\n\nVị trí ứng tuyển: {job_role}"
        else:
            system_prompt += f"\n\nJob position: {job_role}"
    
    # Thêm thông tin từ CV nếu có
    if resume:
        if language == "vi":
            system_prompt += f"\n\nThông tin từ CV của ứng viên:\n{resume}"
        else:
            system_prompt += f"\n\nInformation from candidate's resume:\n{resume}"
    
    return system_prompt

def start_interview_session(interview_type, job_role=None, resume=None, gemini_model=None, language="vi"):
    """
    Bắt đầu phiên phỏng vấn
    """
    # Khởi tạo lịch sử tin nhắn nếu chưa có
    if "interview_messages" not in st.session_state:
        system_prompt = create_interview_system_prompt(interview_type, job_role, resume, language)
        
        # Tạo prompt bắt đầu phỏng vấn
        if language == "vi":
            start_prompt = f"Tôi muốn bắt đầu buổi phỏng vấn {interview_type}"
            if job_role:
                start_prompt += f" cho vị trí {job_role}"
        else:
            start_prompt = f"I want to start a {interview_type} interview"
            if job_role:
                start_prompt += f" for the {job_role} position"
        
        st.session_state.interview_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": start_prompt}
        ]
        
        # Lấy câu trả lời đầu tiên từ người phỏng vấn
        with st.spinner("Người phỏng vấn đang chuẩn bị..."):
            interviewer_response = generate_response(gemini_model, st.session_state.interview_messages)
            st.session_state.interview_messages.append({"role": "assistant", "content": interviewer_response})

def interview_simulator_page(gemini_model):
    """
    Trang mô phỏng phỏng vấn
    """
    language = st.session_state.language
    
    if language == "vi":
        st.title("Mô phỏng phỏng vấn")
        st.markdown("Luyện tập phỏng vấn với AI - hãy trả lời các câu hỏi như trong một cuộc phỏng vấn thực")
        
        interview_type_label = "Chọn loại phỏng vấn"
        job_role_label = "Nhập vị trí công việc (tùy chọn)"
        resume_label = "Dán CV của bạn (tùy chọn)"
        start_btn = "Bắt đầu phỏng vấn mới"
        your_answer = "Câu trả lời của bạn"
        send_btn = "Gửi câu trả lời"
        reset_btn = "Kết thúc và bắt đầu lại"
        
        interview_options = {
            "technical": "Phỏng vấn kỹ thuật",
            "behavioral": "Phỏng vấn hành vi",
            "hr": "Phỏng vấn HR",
            "case": "Phỏng vấn tình huống"
        }
    else:
        st.title("Interview Simulator")
        st.markdown("Practice interviewing with AI - respond to questions as you would in a real interview")
        
        interview_type_label = "Select interview type"
        job_role_label = "Enter job position (optional)"
        resume_label = "Paste your resume (optional)"
        start_btn = "Start new interview"
        your_answer = "Your answer"
        send_btn = "Send response"
        reset_btn = "End and restart"
        
        interview_options = {
            "technical": "Technical Interview",
            "behavioral": "Behavioral Interview",
            "hr": "HR Interview",
            "case": "Case Interview"
        }
    
    # Sidebar cho cài đặt phỏng vấn
    with st.sidebar:
        st.subheader(interview_type_label)
        interview_type = st.selectbox(
            "Type",
            options=list(interview_options.keys()),
            format_func=lambda x: interview_options[x],
            key="interview_type"
        )
        
        job_role = st.text_input(job_role_label, key="interview_job_role")
        resume = st.text_area(resume_label, height=150, key="interview_resume")
        
        if st.button(start_btn, type="primary"):
            # Reset session state
            if "interview_messages" in st.session_state:
                del st.session_state.interview_messages
            
            # Bắt đầu phiên phỏng vấn mới
            start_interview_session(interview_type, job_role, resume, gemini_model, language)
            st.rerun()
    
    # Hiển thị lịch sử tin nhắn
    if "interview_messages" in st.session_state:
        messages = st.session_state.interview_messages
        
        for message in messages:
            if message["role"] == "system":
                continue  # Không hiển thị system prompt
                
            if message["role"] == "assistant":
                st.chat_message("assistant", avatar="👨‍💼").write(message["content"])
            else:
                st.chat_message("user", avatar="👤").write(message["content"])
        
        # Thêm phần nhập câu trả lời
        user_response = st.chat_input(your_answer)
        
        if user_response:
            # Hiển thị câu trả lời của người dùng
            st.chat_message("user", avatar="👤").write(user_response)
            
            # Thêm vào lịch sử tin nhắn
            st.session_state.interview_messages.append({"role": "user", "content": user_response})
            
            # Lấy phản hồi từ người phỏng vấn
            with st.spinner("Người phỏng vấn đang suy nghĩ..."):
                interviewer_response = generate_response(gemini_model, st.session_state.interview_messages)
                st.session_state.interview_messages.append({"role": "assistant", "content": interviewer_response})
            
            # Hiển thị phản hồi của người phỏng vấn
            st.chat_message("assistant", avatar="👨‍💼").write(interviewer_response)
    else:
        # Hướng dẫn khi chưa bắt đầu phỏng vấn
        if language == "vi":
            st.info("👈 Chọn loại phỏng vấn và nhấn 'Bắt đầu phỏng vấn mới' để bắt đầu.")
        else:
            st.info("👈 Select an interview type and click 'Start new interview' to begin.")
    
    # Nút reset
    if "interview_messages" in st.session_state:
        if st.button(reset_btn):
            del st.session_state.interview_messages
            st.rerun()

def get_feedback_on_interview(messages, gemini_model, language="vi"):
    """
    Lấy phản hồi chi tiết về buổi phỏng vấn
    """
    # Chỉ lấy nội dung phỏng vấn, bỏ qua system prompt
    interview_content = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages[1:]])
    
    if language == "vi":
        feedback_prompt = f"""Hãy phân tích buổi phỏng vấn sau đây và đưa ra phản hồi chi tiết:

{interview_content}

Phản hồi nên bao gồm:
1. Điểm mạnh trong câu trả lời của ứng viên
2. Lĩnh vực cần cải thiện
3. Các câu trả lời cụ thể mà ứng viên trả lời tốt và lý do
4. Đề xuất cách trả lời hiệu quả hơn cho các câu hỏi khó
5. Đánh giá tổng thể và chấm điểm buổi phỏng vấn (thang điểm 1-10)

Đưa ra phản hồi chân thành, chi tiết và hữu ích để giúp ứng viên cải thiện kỹ năng phỏng vấn.
"""
    else:
        feedback_prompt = f"""Analyze the following interview and provide detailed feedback:

{interview_content}

Feedback should include:
1. Strengths in the candidate's responses
2. Areas for improvement
3. Specific answers that the candidate handled well and why
4. Suggestions for more effectively answering challenging questions
5. Overall assessment and score for the interview (scale of 1-10)

Provide honest, detailed, and helpful feedback to help the candidate improve their interviewing skills.
"""
    
    # Tạo system prompt cho phản hồi
    language_instruction = "Trả lời bằng tiếng Việt." if language == "vi" else "Answer in English."
    system_prompt = f"{SYSTEM_PROMPT}\n\nBạn là một chuyên gia huấn luyện phỏng vấn với nhiều năm kinh nghiệm.\n\n{language_instruction}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": feedback_prompt}
    ]
    
    # Gọi API Gemini để lấy phản hồi
    feedback = generate_response(gemini_model, messages)
    
    return feedback