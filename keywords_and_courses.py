import streamlit as st
from gemini_helper import generate_response

def suggest_keywords(interview_type, job_role, language="vi", gemini_model=None):
    """
    Gợi ý từ khóa và cụm từ quan trọng cho buổi phỏng vấn dựa trên loại phỏng vấn và vị trí công việc
    """
    if language == "vi":
        system_prompt = """Bạn là một chuyên gia tuyển dụng và phỏng vấn với nhiều năm kinh nghiệm.
Nhiệm vụ của bạn là đưa ra các từ khóa và cụm từ quan trọng mà ứng viên nên sử dụng trong buổi phỏng vấn.
Hãy phân loại từ khóa theo các nhóm như: kỹ năng chuyên môn, kỹ năng mềm, thành tích, và thuật ngữ ngành.
Với mỗi từ khóa, hãy giải thích ngắn gọn tại sao nó quan trọng và cách sử dụng hiệu quả.
Đưa ra 10-15 từ khóa/cụm từ phù hợp nhất.
Trả lời bằng tiếng Việt."""
        
        prompt = f"""Tôi sắp tham gia một buổi phỏng vấn {interview_type}"""
        if job_role:
            prompt += f" cho vị trí {job_role}"
        prompt += """.
Vui lòng đề xuất các từ khóa và cụm từ quan trọng mà tôi nên sử dụng trong buổi phỏng vấn này.
Phân loại theo nhóm và giải thích cách sử dụng hiệu quả."""
    else:
        system_prompt = """You are an expert recruiter and interviewer with many years of experience.
Your task is to provide important keywords and phrases that candidates should use during interviews.
Categorize the keywords into groups such as: technical skills, soft skills, achievements, and industry terminology.
For each keyword, briefly explain why it's important and how to use it effectively.
Provide 10-15 most relevant keywords/phrases.
Answer in English."""
        
        prompt = f"""I'm about to participate in a {interview_type} interview"""
        if job_role:
            prompt += f" for a {job_role} position"
        prompt += """.
Please suggest important keywords and phrases I should use during this interview.
Categorize them and explain how to use them effectively."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    return response

def suggest_courses(weaknesses, language="vi", gemini_model=None):
    """
    Gợi ý khóa học và tài liệu dựa trên điểm yếu phát hiện được
    """
    if language == "vi":
        system_prompt = """Bạn là một cố vấn nghề nghiệp và chuyên gia đào tạo kỹ năng.
Nhiệm vụ của bạn là đề xuất các khóa học, tài liệu và nguồn học tập để giúp ứng viên cải thiện điểm yếu.
Đối với mỗi khuyến nghị, hãy cung cấp:
1. Tên khóa học/tài liệu cụ thể
2. Mô tả ngắn gọn về nội dung
3. Lý do tại sao nó sẽ giúp cải thiện điểm yếu
4. Liên kết đến khóa học/tài liệu (nếu có)
5. Thời gian dự kiến để hoàn thành

Đưa ra tối đa 3 khuyến nghị cho mỗi điểm yếu.
Tập trung vào các nguồn uy tín và nổi tiếng bao gồm cả nguồn miễn phí và trả phí.
Ưu tiên các nguồn tiếng Việt và quốc tế.
Trả lời bằng tiếng Việt."""
        
        prompt = f"""Dựa trên đánh giá phỏng vấn, tôi cần cải thiện các điểm yếu sau:

{weaknesses}

Vui lòng đề xuất các khóa học, tài liệu và nguồn học tập để giúp tôi cải thiện những điểm yếu này."""
    else:
        system_prompt = """You are a career advisor and skills training expert.
Your task is to recommend courses, materials, and learning resources to help candidates improve their weaknesses.
For each recommendation, provide:
1. Specific course/resource name
2. Brief description of content
3. Why it will help address the weakness
4. Link to the course/resource (if available)
5. Estimated time to complete

Provide maximum 3 recommendations for each weakness.
Focus on reputable and well-known sources including both free and paid options.
Prioritize both English and international resources.
Answer in English."""
        
        prompt = f"""Based on my interview assessment, I need to improve the following weaknesses:

{weaknesses}

Please suggest courses, materials, and learning resources to help me improve these weaknesses."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    return response

def display_keywords_suggestions(interview_type=None, job_role=None, gemini_model=None):
    """
    Hiển thị gợi ý từ khóa trong giao diện
    """
    language = st.session_state.language
    
    if language == "vi":
        st.subheader("💡 Từ khóa quan trọng cho buổi phỏng vấn")
        type_label = "Loại phỏng vấn"
        role_label = "Vị trí công việc (tùy chọn)"
        generate_btn = "Gợi ý từ khóa"
        interview_options = {
            "technical": "Phỏng vấn kỹ thuật",
            "behavioral": "Phỏng vấn hành vi",
            "hr": "Phỏng vấn HR",
            "case": "Phỏng vấn tình huống"
        }
    else:
        st.subheader("💡 Important Keywords for Your Interview")
        type_label = "Interview Type"
        role_label = "Job Position (optional)"
        generate_btn = "Suggest Keywords"
        interview_options = {
            "technical": "Technical Interview",
            "behavioral": "Behavioral Interview",
            "hr": "HR Interview",
            "case": "Case Interview"
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sử dụng giá trị mặc định từ tham số nếu có
        default_interview_type = interview_type if interview_type else list(interview_options.keys())[0]
        selected_type = st.selectbox(
            type_label,
            options=list(interview_options.keys()),
            format_func=lambda x: interview_options[x],
            key="keywords_interview_type",
            index=list(interview_options.keys()).index(default_interview_type) if default_interview_type in interview_options else 0
        )
        
        # Sử dụng giá trị mặc định từ tham số nếu có
        default_job_role = job_role if job_role else ""
        selected_job = st.text_input(role_label, value=default_job_role, key="keywords_job_role")
    
    with col2:
        st.write("")
        st.write("")
        generate_keywords = st.button(generate_btn, type="primary", use_container_width=True)
    
    if generate_keywords or (interview_type and job_role):
        with st.spinner("Đang tạo gợi ý từ khóa..."):
            keywords = suggest_keywords(selected_type, selected_job, language, gemini_model)
        
        # Hiển thị kết quả với tiêu đề rõ ràng và định dạng tốt
        if language == "vi":
            st.success("✅ Đã tạo danh sách từ khóa quan trọng!")
            st.info("💡 Hãy sử dụng những từ khóa này trong câu trả lời của bạn để tạo ấn tượng tốt với người phỏng vấn.")
        else:
            st.success("✅ Keywords list generated!")
            st.info("💡 Use these keywords in your answers to make a good impression with the interviewer.")
        
        # Hiển thị kết quả
        st.markdown("### Từ khóa quan trọng")
        st.markdown(keywords)

def display_courses_recommendations(weaknesses=None, gemini_model=None):
    """
    Hiển thị đề xuất khóa học trong giao diện
    """
    language = st.session_state.language
    
    if language == "vi":
        st.subheader("🎓 Khóa học và tài liệu đề xuất")
        weaknesses_label = "Điểm yếu cần cải thiện"
        example_weaknesses = """1. Kỹ năng trình bày ý tưởng chưa mạch lạc
2. Thiếu kinh nghiệm giải quyết xung đột trong nhóm
3. Kiến thức về React.js còn hạn chế"""
        generate_btn = "Đề xuất khóa học"
    else:
        st.subheader("🎓 Recommended Courses & Resources")
        weaknesses_label = "Weaknesses to improve"
        example_weaknesses = """1. Presentation skills need improvement
2. Lacking experience in resolving team conflicts
3. Limited knowledge of React.js"""
        generate_btn = "Suggest Courses"
    
    # Sử dụng giá trị mặc định từ tham số nếu có
    default_weaknesses = weaknesses if weaknesses else ""
    
    weaknesses_input = st.text_area(
        weaknesses_label,
        value=default_weaknesses,
        height=150,
        placeholder=example_weaknesses,
        key="weaknesses_input"
    )
    
    generate_courses = st.button(generate_btn, type="primary")
    
    if generate_courses or weaknesses:
        if not weaknesses_input:
            if language == "vi":
                st.warning("Vui lòng nhập ít nhất một điểm yếu cần cải thiện")
            else:
                st.warning("Please enter at least one weakness to improve")
        else:
            with st.spinner("Đang tìm kiếm khóa học phù hợp..."):
                courses = suggest_courses(weaknesses_input, language, gemini_model)
            
            # Hiển thị kết quả với tiêu đề rõ ràng và định dạng tốt
            if language == "vi":
                st.success("✅ Đã tìm thấy các khóa học phù hợp!")
                st.info("💡 Những khóa học này sẽ giúp bạn cải thiện các điểm yếu và chuẩn bị tốt hơn cho các cuộc phỏng vấn trong tương lai.")
            else:
                st.success("✅ Suitable courses found!")
                st.info("💡 These courses will help you improve your weaknesses and better prepare for future interviews.")
            
            # Hiển thị kết quả
            st.markdown("### Khóa học và tài liệu đề xuất")
            st.markdown(courses) 