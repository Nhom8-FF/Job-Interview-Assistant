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
    
    # Đảm bảo phỏng vấn không kết thúc nếu câu hỏi cuối cùng chưa được trả lời
    if question_count >= total_questions:
        # Kiểm tra xem câu hỏi cuối cùng đã có câu trả lời chưa
        # Nếu tin nhắn cuối cùng là từ assistant và chứa câu hỏi cuối, 
        # và không có câu trả lời của user sau đó, thì phỏng vấn chưa hoàn thành
        if len(messages) >= 2:
            last_msg = messages[-1]
            if last_msg["role"] == "assistant" and re.search(f"(Câu hỏi|Question)\\s+{total_questions}", last_msg["content"]):
                return False  # Chưa có câu trả lời cho câu hỏi cuối
    
    # For an interview to be complete:
    # 1. We must have asked all questions
    # 2. The last question must have been asked, answered, and received feedback
    # 3. OR the interview has ended with a final assessment
    
    # For each question X (where X is from 1 to total_questions):
    # - There should be an assistant message containing "Question X" or "Câu hỏi X"
    # - Followed by a user response
    # - Followed by assistant feedback
    
    # Check if the last question has been fully processed
    if question_count == total_questions:
        # Find the last question in the message history
        last_question_index = -1
        for i, msg in enumerate(messages):
            if msg["role"] == "assistant" and re.search(f"(Câu hỏi|Question)\\s+{total_questions}", msg["content"]):
                last_question_index = i
        
        # If we found the last question
        if last_question_index >= 0:
            # Check if there's a user response after the last question
            if last_question_index + 1 < len(messages) and messages[last_question_index + 1]["role"] == "user":
                # Check if there's assistant feedback after user's response
                if last_question_index + 2 < len(messages) and messages[last_question_index + 2]["role"] == "assistant":
                    # The interview has completed the full cycle for the last question
                    return True
                else:
                    # Missing assistant feedback for the last question
                    return False
            else:
                # Missing user response for the last question
                return False
    
    # If we have a final assessment with score, consider the interview complete
    return (contains_score and contains_final_assessment)

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
    
    # Hiển thị phần cài đặt phỏng vấn trong tab chính thay vì sidebar
    if "interview_messages" not in st.session_state:
        # Hiển thị tùy chọn cấu hình trong một container có viền
        with st.expander("👉 Chọn loại phỏng vấn, số lượng câu hỏi và nhấn 'Bắt đầu phỏng vấn mới' để bắt đầu.", expanded=True):
            # Sử dụng cột để bố trí giao diện
            col1, col2 = st.columns([1, 1])
            
            with col1:
                interview_type = st.selectbox(
                    interview_type_label,
                    options=list(interview_options.keys()),
                    format_func=lambda x: interview_options[x],
                    key="interview_type"
                )
                
                job_role = st.text_input(job_role_label, key="interview_job_role")
            
            with col2:
                # Thêm lựa chọn số lượng câu hỏi
                num_questions = st.slider(
                    questions_label, 
                    min_value=3, 
                    max_value=10, 
                    value=5,
                    step=1,
                    key="num_interview_questions"
                )
                
                resume = st.text_area(resume_label, height=100, key="interview_resume")
            
            # Nút bắt đầu phỏng vấn
            start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
            with start_col2:
                if st.button(start_btn, type="primary", use_container_width=True):
                    # Reset session state
                    if "interview_messages" in st.session_state:
                        del st.session_state.interview_messages
                    if "interview_feedback" in st.session_state:
                        del st.session_state.interview_feedback
                    if "interview_completed" in st.session_state:
                        del st.session_state.interview_completed
                    
                    # Lưu thông tin về loại phỏng vấn và vai trò công việc
                    selected_interview_type = interview_type
                    # Sử dụng tên có ý nghĩa nếu không có vai trò công việc
                    if not job_role or job_role.strip() == "":
                        if language == "vi":
                            selected_job_role = "Vị trí chung"
                        else:
                            selected_job_role = "General Position"
                    else:
                        selected_job_role = job_role
                    
                    # Lưu vào session state
                    st.session_state.current_interview_type = selected_interview_type
                    st.session_state.current_job_role = selected_job_role
                    
                    # Chuyển đổi tên hiển thị loại phỏng vấn cho đẹp hơn
                    if language == "vi":
                        st.session_state.current_interview_type_display = interview_options[selected_interview_type]
                    else:
                        st.session_state.current_interview_type_display = interview_options[selected_interview_type]
                    
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
    if language == "vi":
        prompt = """Vui lòng phân tích buổi phỏng vấn dựa trên các câu hỏi và câu trả lời được cung cấp. 
Đánh giá điểm mạnh và điểm yếu của ứng viên và đưa ra điểm số tổng thể trên thang điểm 10.
Hãy đánh giá từng kỹ năng riêng biệt (kỹ thuật, giao tiếp, giải quyết vấn đề, lãnh đạo) trên thang điểm 10.
Đưa ra đánh giá theo định dạng:

Điểm tổng thể: X/10

Kỹ năng kỹ thuật: X/10
Kỹ năng giao tiếp: X/10
Kỹ năng giải quyết vấn đề: X/10
Kỹ năng lãnh đạo: X/10

Điểm mạnh:
- Điểm mạnh 1
- Điểm mạnh 2
...

Điểm yếu:
- Điểm yếu 1
- Điểm yếu 2
...

Gợi ý cải thiện:
1. Gợi ý 1
2. Gợi ý 2
...
"""
    else:
        prompt = """Please analyze the interview based on the questions and answers provided.
Evaluate the candidate's strengths and weaknesses and provide an overall score on a scale of 1-10.
Evaluate each skill separately (technical, communication, problem-solving, leadership) on a scale of 1-10.
Format your assessment as follows:

Overall Score: X/10

Technical skills: X/10
Communication skills: X/10
Problem-solving skills: X/10
Leadership skills: X/10

Strengths:
- Strength 1
- Strength 2
...

Weaknesses:
- Weakness 1
- Weakness 2
...

Improvement suggestions:
1. Suggestion 1
2. Suggestion 2
...
"""

    # Tạo prompt cuối cùng
    final_prompt = prompt + "\n\nĐây là nội dung cuộc phỏng vấn:" if language == "vi" else prompt + "\n\nHere is the interview content:"
    
    # Thêm nội dung cuộc phỏng vấn (bỏ qua system message)
    for msg in messages:
        if msg["role"] != "system":
            role_display = "Người phỏng vấn" if msg["role"] == "assistant" else "Ứng viên"
            role_display_en = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            
            final_prompt += f"\n\n{role_display if language == 'vi' else role_display_en}: {msg['content']}"
    
    # Tạo message mới để lấy phản hồi
    feedback_messages = [
        {"role": "system", "content": "You are an experienced interview coach providing detailed feedback and assessment."},
        {"role": "user", "content": final_prompt}
    ]
    
    # Lấy phản hồi từ AI
    feedback = generate_response(gemini_model, feedback_messages)
    
    # Lưu phản hồi vào session state để sử dụng ở nơi khác
    st.session_state.interview_feedback = feedback
    
    # Cập nhật điểm số vào hệ thống theo dõi tiến trình
    try:
        from progress_tracker import extract_scores_from_feedback, save_interview_results
        
        # Trích xuất điểm số từ phản hồi
        scores = extract_scores_from_feedback(feedback, language)
        
        # Lấy thông tin về buổi phỏng vấn từ session state
        interview_type = st.session_state.get("current_interview_type", None)
        job_role = st.session_state.get("current_job_role", None)
        
        # Sử dụng tên hiển thị của loại phỏng vấn nếu có
        if st.session_state.get("current_interview_type_display", None):
            interview_type_display = st.session_state.current_interview_type_display
        else:
            # Chuyển đổi loại phỏng vấn sang định dạng hiển thị
            if language == "vi":
                interview_type_mapping = {
                    "technical": "Phỏng vấn kỹ thuật",
                    "behavioral": "Phỏng vấn hành vi",
                    "hr": "Phỏng vấn HR",
                    "case": "Phỏng vấn tình huống"
                }
            else:
                interview_type_mapping = {
                    "technical": "Technical Interview",
                    "behavioral": "Behavioral Interview",
                    "hr": "HR Interview",
                    "case": "Case Interview"
                }
            interview_type_display = interview_type_mapping.get(interview_type, interview_type)
        
        # Lưu kết quả vào hệ thống theo dõi tiến trình
        save_interview_results(scores, job_role, interview_type_display)
    except Exception as e:
        print(f"Error saving interview results: {e}")
    
    return feedback