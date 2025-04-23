import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gemini_helper import generate_response
import time
import matplotlib.pyplot as plt
import io
import json

def analyze_job_market_trends(industry, job_role=None, language="vi", gemini_model=None):
    """
    Phân tích xu hướng kỹ năng đang được tìm kiếm trên thị trường
    """
    if language == "vi":
        system_prompt = """Bạn là một chuyên gia phân tích thị trường việc làm và xu hướng tuyển dụng.
Nhiệm vụ của bạn là phân tích và cung cấp thông tin chi tiết về các kỹ năng đang được tìm kiếm trong ngành cụ thể.
Hãy đưa ra:
1. Top 10 kỹ năng kỹ thuật/chuyên môn đang được tìm kiếm nhiều nhất (kèm % mức độ phổ biến trong các tin tuyển dụng)
2. Top 5 kỹ năng mềm quan trọng nhất (kèm % mức độ phổ biến)
3. Các chứng chỉ/bằng cấp có giá trị cao (kèm mức tăng % giá trị so với năm trước)
4. Xu hướng công nghệ/kỹ năng mới nổi trong 6 tháng qua
5. Dự đoán xu hướng kỹ năng trong 1-2 năm tới

Hãy đảm bảo cung cấp dữ liệu định lượng cụ thể (tỷ lệ phần trăm, con số thống kê) để có thể trực quan hóa.
Trả lời bằng tiếng Việt và định dạng thông tin một cách rõ ràng, dễ đọc."""
        
        prompt = f"""Hãy phân tích xu hướng kỹ năng đang được tìm kiếm trong ngành {industry}"""
        if job_role:
            prompt += f" cho vị trí {job_role}"
        prompt += """.\n\nCung cấp dữ liệu chi tiết về:
1. Top kỹ năng kỹ thuật/chuyên môn
2. Top kỹ năng mềm 
3. Chứng chỉ/bằng cấp giá trị
4. Xu hướng kỹ năng mới nổi
5. Dự đoán xu hướng tương lai"""
    else:
        system_prompt = """You are a job market and recruitment trends expert.
Your task is to analyze and provide detailed insights on skills in demand for a specific industry.
Please provide:
1. Top 10 technical/hard skills in demand (with % prevalence in job postings)
2. Top 5 essential soft skills (with % prevalence)
3. High-value certifications/qualifications (with % value increase from previous year)
4. Emerging technology/skill trends in the past 6 months
5. Projected skill trends for the next 1-2 years

Ensure you provide specific quantitative data (percentages, statistics) that can be visualized.
Answer in English and format the information clearly and readably."""
        
        prompt = f"""Analyze the skill trends currently in demand in the {industry} industry"""
        if job_role:
            prompt += f" for {job_role} positions"
        prompt += """.\n\nProvide detailed data on:
1. Top technical/hard skills
2. Top soft skills
3. Valuable certifications
4. Emerging skill trends
5. Future trend predictions"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    return response

def compare_with_competitors(resume_text, industry, job_role=None, language="vi", gemini_model=None):
    """
    So sánh hồ sơ cá nhân với các ứng viên cạnh tranh trong cùng ngành
    """
    if language == "vi":
        system_prompt = """Bạn là một chuyên gia tuyển dụng và phân tích thị trường lao động.
Nhiệm vụ của bạn là phân tích CV của ứng viên và so sánh với hồ sơ trung bình của các ứng viên cạnh tranh trong cùng ngành.
Hãy đưa ra:
1. Phân tích điểm mạnh và điểm yếu của ứng viên so với thị trường (cho điểm từ 1-10 cho từng kỹ năng chính)
2. Các kỹ năng còn thiếu hoặc cần cải thiện để cạnh tranh tốt hơn
3. Điểm cạnh tranh độc đáo của ứng viên
4. Mức lương dự kiến dựa trên hồ sơ (so với mức trung bình ngành)
5. Tỷ lệ cạnh tranh cho vị trí (số lượng ứng viên/vị trí)

Hãy cung cấp dữ liệu định lượng cụ thể (thang điểm, tỷ lệ phần trăm, số liệu thống kê) để có thể trực quan hóa.
Trả lời bằng tiếng Việt và định dạng thông tin một cách rõ ràng, dễ đọc."""
        
        prompt = f"""Dựa trên CV của tôi, hãy so sánh với các ứng viên cạnh tranh trong ngành {industry}"""
        if job_role:
            prompt += f" cho vị trí {job_role}"
        prompt += f""".\n\nCV của tôi:\n{resume_text}\n\nCung cấp phân tích chi tiết về:
1. Điểm mạnh và điểm yếu so với thị trường
2. Kỹ năng còn thiếu/cần cải thiện
3. Điểm cạnh tranh độc đáo
4. Mức lương dự kiến dựa trên hồ sơ
5. Tỷ lệ cạnh tranh trên thị trường"""
    else:
        system_prompt = """You are a recruitment and labor market analysis expert.
Your task is to analyze a candidate's resume and compare it with the average profile of competitive candidates in the same industry.
Please provide:
1. Analysis of the candidate's strengths and weaknesses compared to the market (score 1-10 for each key skill)
2. Skills missing or needing improvement to better compete
3. The candidate's unique competitive edge
4. Expected salary based on the profile (compared to industry average)
5. Competition ratio for the position (number of candidates/position)

Provide specific quantitative data (score scales, percentages, statistics) that can be visualized.
Answer in English and format the information clearly and readably."""
        
        prompt = f"""Based on my resume, compare with competitive candidates in the {industry} industry"""
        if job_role:
            prompt += f" for {job_role} positions"
        prompt += f""".\n\nMy resume:\n{resume_text}\n\nProvide detailed analysis on:
1. Strengths and weaknesses compared to the market
2. Missing/improvable skills
3. Unique competitive edge
4. Expected salary based on profile
5. Market competition ratio"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    return response

def suggest_career_path(resume_text, industry, job_role=None, language="vi", gemini_model=None):
    """
    Gợi ý định hướng phát triển nghề nghiệp dài hạn
    """
    if language == "vi":
        system_prompt = """Bạn là một cố vấn phát triển nghề nghiệp và chuyên gia quy hoạch lộ trình sự nghiệp.
Nhiệm vụ của bạn là phân tích CV của ứng viên và đề xuất lộ trình phát triển nghề nghiệp dài hạn.
Hãy đưa ra:
1. 3 con đường phát triển nghề nghiệp khả thi trong 5-10 năm tới
2. Các kỹ năng cần phát triển theo từng bước trên lộ trình
3. Mốc thời gian cụ thể cho việc đạt được các kỹ năng và chứng chỉ
4. Dự đoán mức lương và vị trí tiềm năng theo từng giai đoạn
5. Các ngành/lĩnh vực mới phù hợp với kỹ năng hiện tại có thể chuyển đổi

Hãy vẽ ra lộ trình cụ thể theo năm với các mục tiêu rõ ràng và kỹ năng cần đạt được.
Trả lời bằng tiếng Việt và định dạng thông tin một cách rõ ràng, dễ đọc."""
        
        prompt = f"""Dựa trên CV của tôi, hãy gợi ý định hướng phát triển nghề nghiệp dài hạn trong ngành {industry}"""
        if job_role:
            prompt += f", hiện tại đang làm vị trí {job_role}"
        prompt += f""".\n\nCV của tôi:\n{resume_text}\n\nCung cấp phân tích chi tiết về:
1. 3 lộ trình phát triển nghề nghiệp khả thi
2. Kỹ năng cần phát triển theo từng giai đoạn
3. Mốc thời gian cụ thể
4. Dự đoán mức lương theo lộ trình
5. Các ngành có thể chuyển đổi"""
    else:
        system_prompt = """You are a career development advisor and career path planning expert.
Your task is to analyze a candidate's resume and suggest long-term career development paths.
Please provide:
1. 3 viable career development paths for the next 5-10 years
2. Skills to develop at each step of the pathways
3. Specific timeline for achieving skills and certifications
4. Projected salary and potential positions at each stage
5. New sectors/fields compatible with current skills for potential transition

Draw specific year-by-year roadmaps with clear goals and skills to achieve.
Answer in English and format the information clearly and readably."""
        
        prompt = f"""Based on my resume, suggest long-term career development paths in the {industry} industry"""
        if job_role:
            prompt += f", currently working as a {job_role}"
        prompt += f""".\n\nMy resume:\n{resume_text}\n\nProvide detailed analysis on:
1. 3 viable career development paths
2. Skills to develop at each stage
3. Specific timelines
4. Salary projections along paths
5. Potential transition industries"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    return response

def create_skills_radar_chart(skills_data):
    """
    Tạo biểu đồ radar cho các kỹ năng
    """
    fig = go.Figure()
    
    # Thêm dữ liệu cho ứng viên và thị trường
    fig.add_trace(go.Scatterpolar(
        r=skills_data['candidate_scores'],
        theta=skills_data['skills'],
        fill='toself',
        name='Hồ sơ của bạn',
        line_color='rgba(108, 99, 255, 0.8)',
        fillcolor='rgba(108, 99, 255, 0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=skills_data['market_scores'],
        theta=skills_data['skills'],
        fill='toself',
        name='Trung bình thị trường',
        line_color='rgba(255, 101, 132, 0.8)',
        fillcolor='rgba(255, 101, 132, 0.2)'
    ))
    
    # Cập nhật layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        height=500
    )
    
    return fig

def create_skills_trend_chart(trend_data):
    """
    Tạo biểu đồ xu hướng kỹ năng
    """
    fig = px.bar(
        trend_data, 
        x='percentage', 
        y='skill',
        color='percentage',
        color_continuous_scale=px.colors.sequential.Bluyl,
        labels={
            'percentage': 'Mức độ yêu cầu (%)',
            'skill': 'Kỹ năng'
        },
        orientation='h',
        height=500
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        title='Top kỹ năng đang được tìm kiếm'
    )
    
    return fig

def create_career_path_timeline(career_paths):
    """
    Tạo biểu đồ lộ trình nghề nghiệp
    """
    fig = go.Figure()
    
    colors = ['#6C63FF', '#FF6584', '#36D399']
    
    for i, path in enumerate(career_paths):
        fig.add_trace(go.Scatter(
            x=path['years'],
            y=path['salaries'],
            mode='lines+markers+text',
            name=path['name'],
            line=dict(color=colors[i], width=3),
            marker=dict(size=10, color=colors[i]),
            text=path['positions'],
            textposition="top center"
        ))
    
    fig.update_layout(
        title='Lộ trình phát triển nghề nghiệp và mức lương dự kiến',
        xaxis_title='Năm',
        yaxis_title='Mức lương (triệu VNĐ/tháng)',
        height=500
    )
    
    return fig

def get_job_market_insights(job_role, country, gemini_model, language):
    """
    Lấy thông tin về thị trường việc làm cho một vai trò và quốc gia cụ thể
    """
    if language == "vi":
        prompt = f"""Hãy cung cấp phân tích thị trường việc làm cho vị trí {job_role} tại {country}. 
Bao gồm những thông tin sau:
1. Mức lương trung bình (khoảng)
2. Kỹ năng quan trọng nhất được yêu cầu
3. Xu hướng tuyển dụng hiện tại
4. Các công ty hàng đầu đang tuyển dụng
5. Dự báo tăng trưởng ngành trong 3-5 năm tới

Hãy định dạng phản hồi dưới dạng JSON với các trường:
"salary_range": "...",
"top_skills": ["kỹ năng 1", "kỹ năng 2", ...],
"hiring_trends": "...",
"top_companies": ["công ty 1", "công ty 2", ...],
"growth_forecast": "..."

Đảm bảo thông tin cụ thể cho thị trường Việt Nam nếu có thể.
"""
    else:
        prompt = f"""Provide a job market analysis for {job_role} position in {country}.
Include the following information:
1. Average salary range
2. Most important required skills
3. Current hiring trends
4. Top companies that are hiring
5. Industry growth forecast for the next 3-5 years

Format your response as JSON with fields:
"salary_range": "...",
"top_skills": ["skill 1", "skill 2", ...],
"hiring_trends": "...",
"top_companies": ["company 1", "company 2", ...],
"growth_forecast": "..."

Ensure information is specific to the {country} market.
"""

    messages = [
        {"role": "system", "content": "You are a job market analysis expert with access to current labor market data."},
        {"role": "user", "content": prompt}
    ]
    
    response = generate_response(gemini_model, messages)
    
    # Xử lý phản hồi để trích xuất JSON
    try:
        # Tìm phần JSON trong phản hồi
        import re
        json_match = re.search(r'({[\s\S]*})', response)
        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)
            return data
        else:
            # Thử trích xuất từng phần riêng biệt
            salary_range = re.search(r'"salary_range":\s*"([^"]*)"', response)
            salary_range = salary_range.group(1) if salary_range else "N/A"
            
            top_skills_match = re.search(r'"top_skills":\s*\[(.*?)\]', response, re.DOTALL)
            if top_skills_match:
                top_skills_str = top_skills_match.group(1)
                top_skills = [skill.strip().strip('"\'') for skill in top_skills_str.split(',')]
            else:
                top_skills = ["N/A"]
            
            hiring_trends = re.search(r'"hiring_trends":\s*"([^"]*)"', response)
            hiring_trends = hiring_trends.group(1) if hiring_trends else "N/A"
            
            top_companies_match = re.search(r'"top_companies":\s*\[(.*?)\]', response, re.DOTALL)
            if top_companies_match:
                top_companies_str = top_companies_match.group(1)
                top_companies = [company.strip().strip('"\'') for company in top_companies_str.split(',')]
            else:
                top_companies = ["N/A"]
            
            growth_forecast = re.search(r'"growth_forecast":\s*"([^"]*)"', response)
            growth_forecast = growth_forecast.group(1) if growth_forecast else "N/A"
            
            return {
                "salary_range": salary_range,
                "top_skills": top_skills,
                "hiring_trends": hiring_trends,
                "top_companies": top_companies,
                "growth_forecast": growth_forecast
            }
    except Exception as e:
        st.error(f"Error extracting market data: {str(e)}")
        return {
            "salary_range": "N/A",
            "top_skills": ["N/A"],
            "hiring_trends": "N/A",
            "top_companies": ["N/A"],
            "growth_forecast": "N/A"
        }

def display_market_analysis(gemini_model):
    """
    Hiển thị phân tích thị trường việc làm
    """
    language = st.session_state.language
    theme_class = "dark-theme" if st.session_state.theme == "dark" else "light-theme"
    
    # CSS động cho card theo chế độ (sáng/tối)
    card_css = """
    <style>
    .market-card {
        background-color: var(--card-bg);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: var(--card-shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .market-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .market-card h3 {
        color: var(--primary-color);
        font-size: 18px;
        margin-bottom: 10px;
    }
    .market-card p, .market-card ul {
        font-size: 16px;
        line-height: 1.5;
    }
    .market-card li {
        margin-bottom: 5px;
    }
    .market-heading {
        background-color: var(--secondary-bg);
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        border-left: 4px solid var(--primary-color);
    }
    .market-heading h2 {
        color: var(--primary-color);
        margin-bottom: 0;
    }
    </style>
    """
    st.markdown(card_css, unsafe_allow_html=True)
    
    # Tiêu đề
    if language == "vi":
        st.title("Phân Tích Thị Trường Việc Làm")
        st.markdown("Tìm hiểu thông tin thị trường việc làm mới nhất để chuẩn bị tốt nhất cho cuộc phỏng vấn")
        job_role_label = "Nhập vị trí công việc"
        country_label = "Chọn quốc gia/khu vực"
        analyze_button_text = "Phân tích thị trường"
        salary_title = "Mức lương trung bình"
        skills_title = "Kỹ năng quan trọng nhất"
        trends_title = "Xu hướng tuyển dụng"
        companies_title = "Công ty hàng đầu đang tuyển dụng"
        forecast_title = "Dự báo tăng trưởng"
    else:
        st.title("Job Market Analysis")
        st.markdown("Get the latest job market information to best prepare for your interview")
        job_role_label = "Enter job position"
        country_label = "Select country/region"
        analyze_button_text = "Analyze market"
        salary_title = "Average Salary Range"
        skills_title = "Most Important Skills"
        trends_title = "Hiring Trends"
        companies_title = "Top Companies Hiring"
        forecast_title = "Growth Forecast"
    
    # Danh sách các quốc gia theo ngôn ngữ
    countries = {
        "vi": ["Việt Nam", "Hoa Kỳ", "Singapore", "Nhật Bản", "Úc", "Châu Âu", "Khác"],
        "en": ["United States", "United Kingdom", "Canada", "Australia", "Singapore", "Japan", "Europe", "Other"]
    }
    
    job_role = st.text_input(job_role_label, key="market_job_role")
    
    country_options = countries.get(language, countries["en"])
    country = st.selectbox(country_label, country_options, key="market_country")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        analyze = st.button(analyze_button_text, type="primary", use_container_width=True)
    
    if analyze and job_role:
        with st.spinner("Analyzing job market..." if language == "en" else "Đang phân tích thị trường..."):
            market_data = get_job_market_insights(job_role, country, gemini_model, language)
            
            # Sử dụng container Streamlit thay vì HTML trực tiếp
            with st.container():
                # Tạo tiêu đề với styling
                st.subheader(f"{job_role} - {country}")
                st.markdown("---")
                
                # Hiển thị kết quả trong layout cột
                col1, col2 = st.columns(2)
                
                # Cột 1 với thông tin lương, xu hướng và dự báo
                with col1:
                    with st.expander(salary_title, expanded=True):
                        st.write(market_data['salary_range'])
                    
                    with st.expander(trends_title, expanded=True):
                        st.write(market_data['hiring_trends'])
                    
                    with st.expander(forecast_title, expanded=True):
                        st.write(market_data['growth_forecast'])
                
                # Cột 2 với kỹ năng và công ty tuyển dụng
                with col2:
                    with st.expander(skills_title, expanded=True):
                        for skill in market_data['top_skills']:
                            st.markdown(f"- {skill}")
                    
                    with st.expander(companies_title, expanded=True):
                        for company in market_data['top_companies']:
                            st.markdown(f"- {company}")
            
            # Tạo biểu đồ kỹ năng
            st.subheader(skills_title)
            
            # Tạo DataFrame cho biểu đồ
            skills_value = [1] * len(market_data['top_skills'])  # Giá trị đơn giản
            skills_df = pd.DataFrame({
                'Skills': market_data['top_skills'],
                'Importance': skills_value
            })
            
            # Tạo biểu đồ cột ngang
            plt.figure(figsize=(10, 5))
            
            # Màu sắc tùy chỉnh theo theme
            chart_color = '#6C63FF' if st.session_state.theme == 'light' else '#8F8AFF'
            bg_color = 'white' if st.session_state.theme == 'light' else '#313244'
            text_color = '#1E2A3A' if st.session_state.theme == 'light' else '#CDD6F4'
            grid_color = 'lightgray' if st.session_state.theme == 'light' else '#444444'
            
            # Thiết lập style cho biểu đồ
            plt.style.use('default')
            plt.rcParams['axes.facecolor'] = bg_color
            plt.rcParams['figure.facecolor'] = bg_color
            plt.rcParams['text.color'] = text_color
            plt.rcParams['axes.labelcolor'] = text_color
            plt.rcParams['xtick.color'] = text_color
            plt.rcParams['ytick.color'] = text_color
            
            plt.barh(skills_df['Skills'], skills_df['Importance'], color=chart_color)
            plt.xlabel('Importance' if language == "en" else 'Mức độ quan trọng', color=text_color)
            plt.title(skills_title, color=text_color)
            plt.grid(axis='x', linestyle='--', alpha=0.7, color=grid_color)
            
            # Hiển thị biểu đồ
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', transparent=(st.session_state.theme == 'dark'))
            buf.seek(0)
            st.image(buf)
    else:
        if language == "vi":
            st.info("Nhập vị trí công việc và chọn quốc gia để xem phân tích thị trường việc làm.")
        else:
            st.info("Enter a job position and select a country to view job market analysis.") 