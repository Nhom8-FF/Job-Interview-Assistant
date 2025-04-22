import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from gemini_helper import generate_response
from prompts import SYSTEM_PROMPT

def extract_skills(text):
    """
    Trích xuất danh sách kỹ năng từ văn bản sử dụng cả xử lý regex và AI
    """
    # Loại bỏ các ký tự đặc biệt và chuyển về chữ thường
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Danh sách từ khóa kỹ năng phổ biến
    common_skills = [
        "python", "java", "javascript", "react", "angular", "vue", "node.js", "html", "css",
        "sql", "nosql", "mongodb", "mysql", "postgresql", "oracle", "aws", "azure", "gcp",
        "docker", "kubernetes", "ci/cd", "git", "agile", "scrum", "leadership", "management",
        "communication", "teamwork", "problem solving", "critical thinking", "creativity",
        "data analysis", "machine learning", "ai", "deep learning", "nlp", "computer vision",
        "excel", "word", "powerpoint", "presentation", "project management", "marketing",
        "sales", "customer service", "accounting", "finance", "human resources", "recruiting"
    ]
    
    # Tìm kiếm các kỹ năng trong văn bản
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.append(skill)
    
    return found_skills

def analyze_skills_gap(resume_text, job_description, gemini_model, language="vi"):
    """
    Phân tích khoảng cách kỹ năng giữa sơ yếu lý lịch và mô tả công việc
    """
    # Trích xuất kỹ năng từ cả hai văn bản
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))
    
    # Phân tích khoảng cách
    matching_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills
    extra_skills = resume_skills - job_skills
    
    # Tính toán chỉ số phù hợp
    if len(job_skills) > 0:
        match_percentage = (len(matching_skills) / len(job_skills)) * 100
    else:
        match_percentage = 0
    
    # Phần AI phân tích sâu hơn
    language_instruction = "Trả lời bằng tiếng Việt." if language == "vi" else "Answer in English."
    
    analysis_prompt = f"""
Phân tích chi tiết khoảng cách kỹ năng giữa sơ yếu lý lịch và mô tả công việc sau:

Sơ yếu lý lịch:
{resume_text}

Mô tả công việc:
{job_description}

Hãy cung cấp:
1. Đánh giá phần trăm kỹ năng phù hợp
2. Danh sách kỹ năng thiếu quan trọng nhất
3. Đề xuất cách thu hẹp khoảng cách kỹ năng
4. Xếp hạng mức độ phù hợp tổng thể (1-10)
5. Điểm mạnh độc đáo từ sơ yếu lý lịch
"""
    
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nBạn là chuyên gia phân tích khoảng cách kỹ năng. {language_instruction}"},
        {"role": "user", "content": analysis_prompt}
    ]
    
    ai_analysis = generate_response(gemini_model, messages)
    
    return {
        "matching_skills": list(matching_skills),
        "missing_skills": list(missing_skills),
        "extra_skills": list(extra_skills),
        "match_percentage": match_percentage,
        "ai_analysis": ai_analysis
    }

def display_skills_gap_analysis(analysis, language="vi"):
    """
    Hiển thị phân tích khoảng cách kỹ năng dưới dạng trực quan
    """
    if language == "vi":
        labels = ["Kỹ năng phù hợp", "Kỹ năng còn thiếu"]
        title = "Phân tích khoảng cách kỹ năng"
        match_text = "Phù hợp"
        missing_text = "Còn thiếu"
        extra_text = "Kỹ năng bổ sung"
        ai_text = "Phân tích AI"
    else:
        labels = ["Matching Skills", "Missing Skills"]
        title = "Skills Gap Analysis"
        match_text = "Matching"
        missing_text = "Missing"
        extra_text = "Additional Skills"
        ai_text = "AI Analysis"
    
    # Tạo dữ liệu cho biểu đồ
    values = [analysis['match_percentage'], 100 - analysis['match_percentage']]
    
    # Tạo biểu đồ tròn với Plotly
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#4CAF50', '#F44336']
    )])
    
    fig.update_layout(
        title_text=title,
        annotations=[dict(text=f"{analysis['match_percentage']:.1f}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    # Hiển thị biểu đồ
    st.plotly_chart(fig, use_container_width=True)
    
    # Hiển thị danh sách kỹ năng
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {match_text} ({len(analysis['matching_skills'])})")
        if analysis['matching_skills']:
            for skill in analysis['matching_skills']:
                st.markdown(f"✅ {skill}")
        else:
            st.markdown("*Không tìm thấy kỹ năng phù hợp*")
    
    with col2:
        st.markdown(f"### {missing_text} ({len(analysis['missing_skills'])})")
        if analysis['missing_skills']:
            for skill in analysis['missing_skills']:
                st.markdown(f"❌ {skill}")
        else:
            st.markdown("*Không có kỹ năng còn thiếu*")
    
    st.markdown(f"### {extra_text} ({len(analysis['extra_skills'])})")
    if analysis['extra_skills']:
        extra_skills_cols = st.columns(3)
        for i, skill in enumerate(analysis['extra_skills']):
            with extra_skills_cols[i % 3]:
                st.markdown(f"➕ {skill}")
    else:
        st.markdown("*Không có kỹ năng bổ sung*")
    
    # Hiển thị phân tích AI
    st.markdown(f"## {ai_text}")
    st.markdown(analysis['ai_analysis'])

def skills_gap_analysis_page(gemini_model):
    """
    Trang phân tích khoảng cách kỹ năng
    """
    language = st.session_state.language
    
    if language == "vi":
        st.title("Phân tích khoảng cách kỹ năng")
        st.markdown("Phân tích sự phù hợp giữa CV của bạn và mô tả công việc")
        
        resume_label = "Nhập nội dung CV của bạn"
        job_label = "Nhập mô tả công việc"
        analyze_btn = "Phân tích khoảng cách kỹ năng"
        upload_cv = "Tải lên CV"
        upload_jd = "Tải lên mô tả công việc"
    else:
        st.title("Skills Gap Analysis")
        st.markdown("Analyze the match between your resume and job description")
        
        resume_label = "Enter your resume content"
        job_label = "Enter job description"
        analyze_btn = "Analyze Skills Gap"
        upload_cv = "Upload Resume"
        upload_jd = "Upload Job Description"
    
    # Thêm tùy chọn tải lên CV
    upload_resume = st.file_uploader(upload_cv, type=["pdf", "docx", "txt"], key="resume_upload")
    resume_text = st.text_area(resume_label, height=200, key="resume_text")
    
    # Thêm tùy chọn tải lên mô tả công việc
    upload_job = st.file_uploader(upload_jd, type=["pdf", "docx", "txt"], key="job_upload")
    job_description = st.text_area(job_label, height=200, key="job_description")
    
    if st.button(analyze_btn, type="primary"):
        if resume_text and job_description:
            with st.spinner("Đang phân tích..."):
                analysis = analyze_skills_gap(resume_text, job_description, gemini_model, language)
                display_skills_gap_analysis(analysis, language)
        else:
            if language == "vi":
                st.error("Vui lòng cung cấp cả CV và mô tả công việc để phân tích")
            else:
                st.error("Please provide both resume and job description for analysis")