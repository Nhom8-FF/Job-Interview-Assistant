import streamlit as st
import time
import random
import re
from prompts import SYSTEM_PROMPT
from gemini_helper import generate_response

def create_interview_system_prompt(interview_type, job_role=None, resume=None, num_questions=5, language="vi"):
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
2. Luôn đánh số câu hỏi rõ ràng (Câu hỏi 1, Câu hỏi 2...)
3. Hỏi các câu hỏi liên quan trực tiếp đến vị trí công việc và kỹ năng cần thiết.
4. Lắng nghe câu trả lời của ứng viên và đưa ra phản hồi chi tiết.
5. Phân tích độ chính xác và chất lượng của câu trả lời sau mỗi lần ứng viên trả lời.
6. Sẽ có tổng cộng {num_questions} câu hỏi trong buổi phỏng vấn này.
7. Sau khi hoàn thành {num_questions} câu hỏi, hãy kết thúc buổi phỏng vấn và đưa ra đánh giá tổng thể.
8. Đánh giá tổng thể cần có điểm số (thang điểm 1-10) và phân tích ưu điểm, nhược điểm của ứng viên.

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
2. Always number your questions clearly (Question 1, Question 2...)
3. Ask questions directly related to the job position and required skills.
4. Listen to the candidate's response and provide detailed feedback.
5. Analyze the accuracy and quality of each response after the candidate answers.
6. There will be a total of {num_questions} questions in this interview.
7. After completing {num_questions} questions, conclude the interview and provide an overall assessment.
8. The overall assessment should include a score (on a scale of 1-10) and analyze the candidate's strengths and weaknesses.

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

def count_questions(messages):
    """
    Đếm số câu hỏi đã được hỏi trong buổi phỏng vấn
    """
    question_count = 0
    for msg in messages:
        if msg["role"] == "assistant":
            # Tìm các dòng bắt đầu bằng "Câu hỏi X" hoặc "Question X"
            if re.search(r"(Câu hỏi|Question)\s+\d+", msg["content"]):
                question_count += 1
    return question_count

def check_interview_complete(messages, total_questions):
    """
    Kiểm tra xem buổi phỏng vấn đã hoàn thành chưa
    """
    question_count = count_questions(messages)
    last_message = messages[-1]["content"] if messages else ""
    
    # Kiểm tra xem có phải đánh giá cuối cùng không
    contains_score = re.search(r"(\d+)/10|(\d+)\s*/\s*10", last_message)
    contains_final_assessment = re.search(r"(đánh giá tổng thể|overall assessment|final score|điểm số cuối cùng)", 
                                         last_message.lower())
    
    return question_count >= total_questions or (contains_score and contains_final_assessment)

def start_interview_session(interview_type, job_role=None, resume=None, num_questions=5, gemini_model=None, language="vi"):
    """
    Bắt đầu phiên phỏng vấn
    """
    # Khởi tạo lịch sử tin nhắn nếu chưa có
    if "interview_messages" not in st.session_state:
        system_prompt = create_interview_system_prompt(interview_type, job_role, resume, num_questions, language)
        
        # Lưu số lượng câu hỏi
        st.session_state.total_interview_questions = num_questions
        
        # Tạo prompt bắt đầu phỏng vấn
        if language == "vi":
            start_prompt = f"Tôi muốn bắt đầu buổi phỏng vấn {interview_type} với {num_questions} câu hỏi"
            if job_role:
                start_prompt += f" cho vị trí {job_role}"
        else:
            start_prompt = f"I want to start a {interview_type} interview with {num_questions} questions"
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
        questions_label = "Số lượng câu hỏi"
        start_btn = "Bắt đầu phỏng vấn mới"
        your_answer = "Câu trả lời của bạn"
        end_btn = "Kết thúc phỏng vấn"
        reset_btn = "Bắt đầu lại"
        
        interview_options = {
            "technical": "Phỏng vấn kỹ thuật",
            "behavioral": "Phỏng vấn hành vi",
            "hr": "Phỏng vấn HR",
            "case": "Phỏng vấn tình huống"
        }
        
        progress_msg = "Tiến độ phỏng vấn"
        feedback_btn = "Xem đánh giá chi tiết"
        end_interview_msg = "Phỏng vấn đã kết thúc. Bạn có thể xem đánh giá chi tiết hoặc bắt đầu lại."
    else:
        st.title("Interview Simulator")
        st.markdown("Practice interviewing with AI - respond to questions as you would in a real interview")
        
        interview_type_label = "Select interview type"
        job_role_label = "Enter job position (optional)"
        resume_label = "Paste your resume (optional)"
        questions_label = "Number of questions"
        start_btn = "Start new interview"
        your_answer = "Your answer"
        end_btn = "End interview"
        reset_btn = "Restart"
        
        interview_options = {
            "technical": "Technical Interview",
            "behavioral": "Behavioral Interview",
            "hr": "HR Interview",
            "case": "Case Interview"
        }
        
        progress_msg = "Interview progress"
        feedback_btn = "View detailed feedback"
        end_interview_msg = "The interview has ended. You can view detailed feedback or start over."
    
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
        
        # Thêm lựa chọn số lượng câu hỏi
        num_questions = st.slider(
            questions_label, 
            min_value=3, 
            max_value=10, 
            value=5,
            step=1,
            key="num_interview_questions"
        )
        
        if st.button(start_btn, type="primary"):
            # Reset session state
            if "interview_messages" in st.session_state:
                del st.session_state.interview_messages
            if "interview_feedback" in st.session_state:
                del st.session_state.interview_feedback
            if "interview_completed" in st.session_state:
                del st.session_state.interview_completed
            
            # Bắt đầu phiên phỏng vấn mới
            start_interview_session(interview_type, job_role, resume, num_questions, gemini_model, language)
            st.rerun()
    
    # Hiển thị lịch sử tin nhắn và phần tương tác
    if "interview_messages" in st.session_state:
        messages = st.session_state.interview_messages
        total_questions = st.session_state.total_interview_questions
        
        # Hiển thị thanh tiến độ phỏng vấn
        current_questions = count_questions(messages)
        interview_complete = check_interview_complete(messages, total_questions)
        
        if interview_complete and "interview_completed" not in st.session_state:
            st.session_state.interview_completed = True
        
        # Hiển thị thanh tiến độ
        st.write(f"**{progress_msg}:** {current_questions}/{total_questions}")
        progress_percent = min(current_questions / total_questions, 1.0)
        st.progress(progress_percent)
        
        # Hiển thị tin nhắn
        for message in messages:
            if message["role"] == "system":
                continue  # Không hiển thị system prompt
                
            if message["role"] == "assistant":
                st.chat_message("assistant", avatar="👨‍💼").write(message["content"])
            else:
                st.chat_message("user", avatar="👤").write(message["content"])
        
        # Nếu phỏng vấn đã kết thúc, hiển thị nút để xem đánh giá chi tiết
        if "interview_completed" in st.session_state:
            st.info(end_interview_msg)
            
            if "interview_feedback" not in st.session_state:
                if st.button(feedback_btn, type="primary"):
                    with st.spinner("Đang tạo phản hồi chi tiết..."):
                        feedback = get_feedback_on_interview(messages, gemini_model, language)
                        st.session_state.interview_feedback = feedback
                    st.rerun()
            else:
                # Hiển thị phản hồi chi tiết
                st.subheader("📊 Đánh giá chi tiết")
                st.markdown(st.session_state.interview_feedback)
        else:
            # Nếu phỏng vấn chưa kết thúc, cho phép người dùng tiếp tục trả lời
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
                
                # Kiểm tra xem phỏng vấn đã kết thúc chưa sau khi nhận được phản hồi mới
                if check_interview_complete(st.session_state.interview_messages, total_questions):
                    st.session_state.interview_completed = True
                
                st.rerun()
            
            # Tùy chọn kết thúc sớm phỏng vấn
            if st.button(end_btn):
                # Thông báo cho AI kết thúc phỏng vấn
                end_message = "Tôi muốn kết thúc phỏng vấn và nhận đánh giá tổng thể." if language == "vi" else "I want to end the interview and get an overall assessment."
                st.session_state.interview_messages.append({"role": "user", "content": end_message})
                
                with st.spinner("Đang chuẩn bị đánh giá tổng thể..."):
                    final_assessment = generate_response(gemini_model, st.session_state.interview_messages)
                    st.session_state.interview_messages.append({"role": "assistant", "content": final_assessment})
                    st.session_state.interview_completed = True
                
                st.rerun()
    else:
        # Hướng dẫn khi chưa bắt đầu phỏng vấn
        if language == "vi":
            st.info("👈 Chọn loại phỏng vấn, số lượng câu hỏi và nhấn 'Bắt đầu phỏng vấn mới' để bắt đầu.")
        else:
            st.info("👈 Select an interview type, number of questions and click 'Start new interview' to begin.")
    
    # Nút reset
    if "interview_messages" in st.session_state:
        if st.button(reset_btn):
            if "interview_messages" in st.session_state:
                del st.session_state.interview_messages
            if "interview_feedback" in st.session_state:
                del st.session_state.interview_feedback
            if "interview_completed" in st.session_state:
                del st.session_state.interview_completed
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