import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from prompts import SYSTEM_PROMPT
from gemini_helper import generate_response

def extract_skills(text):
    """
    Trích xuất danh sách kỹ năng từ văn bản sử dụng cả xử lý regex và AI
    """
    # Pattern cơ bản để tìm kỹ năng
    skill_pattern = r"(?:[\•\-\★\✓\✔]\s*)?([A-Za-z0-9][\w\+\#\.\-\s]*(?:Framework|Language|API|SDK|Library|Technologies|Systems|Software|Development|Programming|Design|Analysis|Management|Marketing|Analytics|Engineering|Security|Architecture|Cloud|DevOps|Testing|UI\/UX|Database|SQL|Python|Java|JavaScript|React|Angular|Vue|Node\.js|PHP|C\+\+|Swift|Go|Rust|TypeScript|AWS|Azure|GCP|Docker|Kubernetes|Linux|Git|Machine Learning|ML|AI|NLP|Deep Learning|Data Science|Scrum|Agile|Kanban|SEO|SEM|Content Marketing|Social Media|Email Marketing|Google Analytics|Photoshop|Illustrator|Sketch|Figma|XD|HTML|CSS|SASS|LESS)(?:\s+\d+(?:\.\d+)?\s+(?:years|yrs))?)"
    
    # Tìm tất cả các kỹ năng sử dụng pattern
    skills_found = re.findall(skill_pattern, text, re.IGNORECASE)
    
    # Loại bỏ duplicates và whitespace
    cleaned_skills = list(set([skill.strip() for skill in skills_found if len(skill.strip()) > 2]))
    
    return cleaned_skills

def analyze_skills_gap(resume_text, job_description, gemini_model, language="vi"):
    """
    Phân tích khoảng cách kỹ năng giữa sơ yếu lý lịch và mô tả công việc
    """
    # Tạo prompt phân tích
    if language == "vi":
        analysis_prompt = f"""
Hãy phân tích khoảng cách kỹ năng giữa CV và mô tả công việc dưới đây:

CV:
{resume_text}

Mô tả công việc:
{job_description}

Phân tích theo các tiêu chí sau:
1. Các kỹ năng và yêu cầu chính trong mô tả công việc
2. Các kỹ năng và kinh nghiệm của ứng viên từ CV
3. Kỹ năng trùng khớp (đánh giá % trùng khớp)
4. Kỹ năng thiếu (đánh giá % thiếu hụt)
5. Kỹ năng vượt trội của ứng viên không được nhắc trong mô tả công việc (điểm mạnh)
6. Đánh giá tổng thể về sự phù hợp (thang điểm 1-10)
7. Đề xuất cải thiện cụ thể

Định dạng kết quả thành các phần rõ ràng với tiêu đề và liệt kê cụ thể từng kỹ năng.
Đảm bảo cung cấp dữ liệu phần trăm về mức độ phù hợp, khoảng cách kỹ năng, số điểm đánh giá tổng thể để sử dụng cho biểu đồ.
"""
    else:
        analysis_prompt = f"""
Analyze the skills gap between the resume and job description below:

Resume:
{resume_text}

Job Description:
{job_description}

Analyze according to these criteria:
1. Key skills and requirements in the job description
2. Candidate's skills and experience from the resume
3. Matching skills (evaluate % match)
4. Missing skills (evaluate % gap)
5. Candidate's exceptional skills not mentioned in the job description (strengths)
6. Overall assessment of fit (scale of 1-10)
7. Specific improvement suggestions

Format the results into clear sections with headers and list each skill specifically.
Make sure to provide percentage data about the level of fit, skills gap, and overall assessment score for use in charts.
"""
    
    # Tạo hướng dẫn ngôn ngữ
    language_instruction = "Trả lời bằng tiếng Việt." if language == "vi" else "Answer in English."
    
    # Tạo system prompt
    system_prompt = f"{SYSTEM_PROMPT}\n\nBạn là một chuyên gia phân tích kỹ năng và tuyển dụng với nhiều năm kinh nghiệm.\n\n{language_instruction}"
    
    # Tạo tin nhắn
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": analysis_prompt}
    ]
    
    # Gọi Gemini API
    analysis = generate_response(gemini_model, messages)
    
    return analysis

def display_skills_gap_analysis(analysis, language="vi"):
    """
    Hiển thị phân tích khoảng cách kỹ năng dưới dạng trực quan
    """
    try:
        # Trích xuất phần trăm từ nội dung phân tích
        match_pattern = r"(\d+)%\s*(?:trùng khớp|match)"
        gap_pattern = r"(\d+)%\s*(?:thiếu|gap|không phù hợp|missing)"
        score_pattern = r"(\d+(?:\.\d+)?)\s*(?:\/|trên)\s*10"
        
        match_percent = re.search(match_pattern, analysis, re.IGNORECASE)
        gap_percent = re.search(gap_pattern, analysis, re.IGNORECASE)
        score = re.search(score_pattern, analysis, re.IGNORECASE)
        
        match_value = int(match_percent.group(1)) if match_percent else 50
        gap_value = int(gap_percent.group(1)) if gap_percent else 50
        score_value = float(score.group(1)) if score else 5.0
        
        # Đảm bảo không vượt quá 100%
        if match_value + gap_value > 100:
            total = match_value + gap_value
            match_value = int((match_value / total) * 100)
            gap_value = 100 - match_value
        
        # Tạo dữ liệu cho biểu đồ
        labels = ["Kỹ năng phù hợp", "Khoảng cách kỹ năng"] if language == "vi" else ["Matching Skills", "Skills Gap"]
        values = [match_value, gap_value]
        colors = ['#4CAF50', '#FF5252']
        
        # Hiển thị biểu đồ tròn
        fig1 = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=colors
        )])
        
        fig1.update_layout(
            title_text="Phân tích khoảng cách kỹ năng" if language == "vi" else "Skills Gap Analysis",
            annotations=[dict(text=f"{match_value}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        st.plotly_chart(fig1)
        
        # Hiển thị điểm số
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Đánh giá tổng thể" if language == "vi" else "Overall Assessment"},
            gauge = {
                'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 3], 'color': '#FF5252'},
                    {'range': [3, 7], 'color': '#FFC107'},
                    {'range': [7, 10], 'color': '#4CAF50'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score_value
                }
            }
        ))
        
        fig2.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=250,
        )
        
        st.plotly_chart(fig2)
        
    except Exception as e:
        st.error(f"Lỗi khi tạo biểu đồ: {str(e)}")
        st.write("Hiển thị phân tích văn bản")
        st.write(analysis)


def skills_gap_analysis_page(gemini_model):
    """
    Trang phân tích khoảng cách kỹ năng
    """
    language = st.session_state.language
    
    if language == "vi":
        st.title("Phân tích khoảng cách kỹ năng")
        st.markdown("Tìm hiểu mức độ phù hợp của bạn với công việc mong muốn và cách cải thiện kỹ năng")
        
        resume_label = "CV của bạn"
        job_desc_label = "Mô tả công việc"
        analyze_btn = "Phân tích khoảng cách kỹ năng"
    else:
        st.title("Skills Gap Analysis")
        st.markdown("Understand your fit for a desired job and how to improve your skills")
        
        resume_label = "Your Resume"
        job_desc_label = "Job Description"
        analyze_btn = "Analyze Skills Gap"
    
    # Nhập CV và mô tả công việc
    resume_text = st.text_area(resume_label, height=200)
    job_description = st.text_area(job_desc_label, height=200)
    
    # Nút phân tích
    if st.button(analyze_btn, type="primary", disabled=(not resume_text or not job_description)):
        if not resume_text or not job_description:
            if language == "vi":
                st.warning("Vui lòng nhập cả CV và mô tả công việc")
            else:
                st.warning("Please enter both resume and job description")
        else:
            with st.spinner("Đang phân tích..."):
                # Phân tích khoảng cách kỹ năng
                analysis_result = analyze_skills_gap(resume_text, job_description, gemini_model, language)
                
                # Hiển thị kết quả
                st.subheader("Kết quả phân tích" if language == "vi" else "Analysis Results")
                
                # Hiển thị biểu đồ trực quan
                display_skills_gap_analysis(analysis_result, language)
                
                # Hiển thị phân tích chi tiết
                st.markdown("### Phân tích chi tiết" if language == "vi" else "### Detailed Analysis")
                st.markdown(analysis_result)
                
                # Nút tải xuống báo cáo
                if language == "vi":
                    st.download_button("📥 Tải xuống báo cáo", analysis_result, "skills_gap_analysis.txt")
                else:
                    st.download_button("📥 Download Report", analysis_result, "skills_gap_analysis.txt")
    else:
        # Hiển thị hướng dẫn khi chưa phân tích
        if language == "vi":
            st.info("Dán CV của bạn và mô tả công việc mong muốn để phân tích khoảng cách kỹ năng và nhận đề xuất cải thiện")
        else:
            st.info("Paste your resume and desired job description to analyze skills gap and receive improvement suggestions")