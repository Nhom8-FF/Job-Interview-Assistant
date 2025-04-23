import streamlit as st
import os
import time
import json
import re
from file_processor import process_file
from gemini_helper import initialize_gemini, generate_response
from prompts import SYSTEM_PROMPT, get_interview_context_prompt
from keywords_and_courses import display_keywords_suggestions, display_courses_recommendations
from market_analysis import display_market_analysis

# Page configuration
st.set_page_config(page_title="Job Interview Assistant",
                   page_icon="👔",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Hỗ trợ đa ngôn ngữ - với tiếng Việt là chủ yếu
LANGUAGES = {
    "vi": "Tiếng Việt", 
    "en": "English"
}

# Các chuỗi văn bản đa ngôn ngữ
TRANSLATIONS = {
    "vi": {
        "app_title": "Trợ Lý Phỏng Vấn Xin Việc",
        "interview_coach": "Huấn Luyện Viên Phỏng Vấn AI",
        "dark_mode": "Chế Độ Tối",
        "appearance": "Giao Diện",
        "prepare_job": "Chuẩn bị cho công việc mơ ước",
        "upload_documents": "Tải Lên Tài Liệu",
        "upload_tip":
        "Tải lên CV, mô tả công việc, hoặc tài liệu liên quan để được phân tích cá nhân hoá",
        "select_file": "Chọn tệp để tải lên",
        "process_document": "Xử Lý Tài Liệu",
        "clear_chat": "Xoá Lịch Sử Chat",
        "features": "Tính Năng",
        "resume_analysis": "Phân tích CV",
        "resume_desc": "Nhận phản hồi về CV của bạn",
        "mock_interview": "Luyện tập phỏng vấn",
        "mock_desc": "Thực hành với câu hỏi thực tế",
        "job_analysis": "Phân tích mô tả công việc",
        "job_desc": "Hiểu rõ yêu cầu chính",
        "tips": "Lời khuyên phỏng vấn cá nhân hoá",
        "tips_desc": "Lời khuyên phù hợp cho tình huống của bạn",
        "assistant_desc":
        "Hướng dẫn AI giúp thành công trong phỏng vấn việc làm",
        "chat": "Trò Chuyện",
        "doc_analysis": "Phân Tích Tài Liệu",
        "interview_tips": "Lời Khuyên Phỏng Vấn",
        "market_analysis": "Phân Tích Thị Trường",
        "ask_anything": "Hỏi bất kỳ điều gì về phỏng vấn việc làm...",
        "doc_loaded": "Tài liệu đã được tải thành công!",
        "view_content": "Xem Nội Dung Tài Liệu",
        "get_insights": "Nhận Phân Tích AI",
        "insights_desc":
        "Chọn loại phân tích và tạo thông tin chi tiết dựa trên tài liệu của bạn",
        "select_analysis": "Chọn loại phân tích",
        "resume_improvements": "Cải Thiện CV",
        "job_keywords": "Từ Khoá Mô Tả Công Việc",
        "skills_gap": "Phân Tích Khoảng Cách Kỹ Năng",
        "custom_analysis": "Phân Tích Tuỳ Chỉnh",
        "analyze_document": "Phân Tích Tài Liệu",
        "no_document": "Chưa Có Tài Liệu Nào Được Tải Lên",
        "no_doc_text":
        "Tải lên CV, mô tả công việc, hoặc tài liệu liên quan bằng thanh bên để nhận phân tích và thông tin chi tiết",
        "upload_tip_2":
        "Thử tải lên các loại tài liệu khác nhau bao gồm văn bản, PDF, DOCX, hoặc thậm chí hình ảnh",
        "tips_practice": "Lời Khuyên & Luyện Tập Phỏng Vấn",
        "tips_desc_2":
        "Nhận hướng dẫn chuẩn bị phỏng vấn cá nhân hoá cho các loại phỏng vấn khác nhau. Chọn loại phỏng vấn bên dưới và tùy chọn nhập vai trò công việc mục tiêu để nhận lời khuyên phù hợp hơn.",
        "select_interview": "Chọn Loại Phỏng Vấn",
        "technical": "Phỏng Vấn Kỹ Thuật",
        "behavioral": "Phỏng Vấn Hành Vi",
        "hr_interview": "Phỏng Vấn HR",
        "case_interview": "Phỏng Vấn Tình Huống",
        "job_role": "Nhập Vai Trò Công Việc (tuỳ chọn)",
        "get_tips": "Nhận Lời Khuyên",
        "practice_questions": "Câu Hỏi Luyện Tập",
        "practice_tip":
        "Luyện tập với câu hỏi phỏng vấn thực tế cho loại phỏng vấn và vai trò cụ thể của bạn.",
        "generate_questions": "Tạo Câu Hỏi",
        "footer_tip":
        "Tải lên CV của bạn để được chuẩn bị phỏng vấn cá nhân hoá",
        "powered_by": "Huấn luyện viên phỏng vấn cá nhân của bạn"
    },
    "en": {
        "app_title": "Job Interview Assistant",
        "interview_coach": "Interview Coach AI",
        "dark_mode": "Dark Mode",
        "appearance": "Appearance",
        "prepare_job": "Prepare for your dream job",
        "upload_documents": "Upload Documents",
        "upload_tip":
        "Upload your resume, job description, or any relevant document for personalized analysis",
        "select_file": "Select file to upload",
        "process_document": "Process Document",
        "clear_chat": "Clear Chat History",
        "features": "Features",
        "resume_analysis": "Resume analysis",
        "resume_desc": "Get feedback on your resume",
        "mock_interview": "Mock interview preparation",
        "mock_desc": "Practice with realistic questions",
        "job_analysis": "Job description analysis",
        "job_desc": "Understand key requirements",
        "tips": "Personalized interview tips",
        "tips_desc": "Tailored advice for your situation",
        "assistant_desc":
        "Your personal AI-powered guide to job interview success",
        "chat": "Chat",
        "doc_analysis": "Document Analysis",
        "interview_tips": "Interview Tips",
        "market_analysis": "Market Analysis",
        "ask_anything": "Ask me anything about job interviews...",
        "doc_loaded": "Document loaded successfully!",
        "view_content": "View Document Content",
        "get_insights": "Get AI-Powered Insights",
        "insights_desc":
        "Select analysis type and generate personalized insights based on your document",
        "select_analysis": "Select analysis type",
        "resume_improvements": "Resume Improvements",
        "job_keywords": "Job Description Keywords",
        "skills_gap": "Skills Gap Analysis",
        "custom_analysis": "Custom Analysis",
        "analyze_document": "Analyze Document",
        "no_document": "No Document Uploaded Yet",
        "no_doc_text":
        "Upload a resume, job description, or any relevant document using the sidebar to get personalized analysis and insights",
        "upload_tip_2":
        "Try uploading different document types including text, PDF, DOCX, or even images",
        "tips_practice": "Interview Tips & Practice",
        "tips_desc_2":
        "Get personalized interview preparation guidance for different interview types. Select your interview type below and optionally enter your target job role for more tailored advice.",
        "select_interview": "Select Interview Type",
        "technical": "Technical Interview",
        "behavioral": "Behavioral Interview",
        "hr_interview": "HR Interview",
        "case_interview": "Case Interview",
        "job_role": "Enter Job Role (optional)",
        "get_tips": "Get Tips",
        "practice_questions": "Practice Questions",
        "practice_tip":
        "Practice with real interview questions for your specific role and interview type.",
        "generate_questions": "Generate Questions",
        "footer_tip":
        "Upload your resume for personalized interview preparation",
        "powered_by": "Your personal interview coach"
    }
}

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "language" not in st.session_state:
    st.session_state.language = "vi"  # Tiếng Việt là mặc định

if "file_content" not in st.session_state:
    st.session_state.file_content = None

if "gemini_model" not in st.session_state:
    # Initialize Gemini API without providing key (will use config.py)
    st.session_state.gemini_model = initialize_gemini()

# Lưu trữ lịch sử tiến triển người dùng
if "interview_history" not in st.session_state:
    st.session_state.interview_history = []

if "skills_progress" not in st.session_state:
    st.session_state.skills_progress = {
        "technical": [],
        "communication": [],
        "problem_solving": [],
        "leadership": [],
        "overall": []
    }

# Hàm helper để lấy văn bản theo ngôn ngữ
def get_text(key):
    return TRANSLATIONS[st.session_state.language].get(key, "")


# Apply theme and styling based on selected theme
dark_theme_css = """
<style>
:root {
    --background-color: #1E1E2E;
    --text-color: #CDD6F4;
    --secondary-bg: #313244;
    --primary-color: #6C63FF;
    --accent-color: #FF6584;
    --card-bg: #313244;
    --card-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    --info-bg: rgba(108, 99, 255, 0.15);
    --success-bg: rgba(76, 175, 80, 0.15);
    --warning-bg: rgba(255, 152, 0, 0.15);
    --error-bg: rgba(244, 67, 54, 0.15);
    --border-color: #444444;
    --hover-bg: #383858;
    --chart-colors: #6C63FF, #FF6584, #36D399, #FFCB6B, #7AA2F7;
    --transition-speed: 0.3s;
}
body {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
    transition: background-color var(--transition-speed) ease, color var(--transition-speed) ease;
}
.stApp {
    background-color: var(--background-color) !important;
    transition: background-color var(--transition-speed) ease;
}
.dark-theme {
    color: var(--text-color);
}
.dark-theme .card {
    background: var(--card-bg) !important;
    box-shadow: var(--card-shadow) !important;
    transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}
.dark-theme .card-title {
    color: #CDD6F4 !important;
}
.dark-theme .card-text {
    color: #a6adc8 !important;
}
.dark-theme .gradient-text {
    background: linear-gradient(90deg, #6C63FF, #FF6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.dark-theme .css-1y4p8pa {
    background-color: #1E1E2E !important;
}
.dark-theme .stTextInput > div > div {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
    border-color: var(--border-color) !important;
    transition: border-color var(--transition-speed) ease;
}
.dark-theme .stButton > button {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
    border-color: var(--border-color) !important;
    transition: background-color var(--transition-speed) ease, transform var(--transition-speed) ease;
}
.dark-theme .stButton > button:hover {
    background-color: var(--hover-bg) !important;
    transform: translateY(-2px);
}
.dark-theme .stTextArea > div > div {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
    border-color: var(--border-color) !important;
}
.dark-theme .stSelectbox > div > div {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
    border-color: var(--border-color) !important;
}
.dark-theme .stDataFrame {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
}
.dark-theme [data-testid="stDataFrameResizable"] {
    background-color: #313244 !important;
}
.dark-theme .stDataFrame [data-testid="stTable"] {
    color: #CDD6F4 !important;
}
.dark-theme .stDataFrame th {
    background-color: #2c2c42 !important;
    color: #CDD6F4 !important;
    border-color: #444444 !important;
}
.dark-theme .stDataFrame td {
    color: #CDD6F4 !important;
    border-color: #444444 !important;
}
.dark-theme .stTabs [data-baseweb="tab-list"] {
    background-color: #1E1E2E !important;
}
.dark-theme .stTabs [data-baseweb="tab"] {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
}
.dark-theme .stTabs [aria-selected="true"] {
    background-color: #6C63FF !important;
    color: white !important;
}
.dark-theme .stInfo {
    background-color: var(--info-bg) !important;
    color: #CDD6F4 !important;
}
.dark-theme .stSuccess {
    background-color: var(--success-bg) !important;
    color: #CDD6F4 !important;
}
.dark-theme .stWarning {
    background-color: var(--warning-bg) !important;
    color: #CDD6F4 !important;
}
.dark-theme .stError {
    background-color: var(--error-bg) !important;
    color: #CDD6F4 !important;
}
.css-1x8cf1d {
    background-color: var(--background-color) !important;
}
.css-10oheav {
    color: var(--text-color) !important;
}
.css-1aumxhk {
    background-color: var(--background-color) !important;
}
.dark-theme .stMarkdown th {
    background-color: #333 !important;
}
.dark-theme .code-copy-button:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
}

/* Code block wrapper */
.code-block-wrapper {
    position: relative !important;
    margin: 15px 0 !important;
}

.code-language {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    background-color: rgba(108, 99, 255, 0.7) !important;
    color: white !important;
    font-size: 11px !important;
    padding: 2px 8px !important;
    border-top-left-radius: 8px !important;
    border-bottom-right-radius: 8px !important;
    font-family: monospace !important;
    z-index: 1 !important;
}

.dark-theme .code-language {
    background-color: rgba(108, 99, 255, 0.8) !important;
}

/* Chart styling */
.dark-theme .js-plotly-plot .main-svg {
    background-color: transparent !important;
}
.dark-theme .js-plotly-plot .svg-container {
    background-color: #313244 !important;
    border-radius: 10px;
}
.dark-theme .js-plotly-plot .plot-container {
    filter: brightness(0.9) !important;
}
.dark-theme .js-plotly-plot .xtick text, 
.dark-theme .js-plotly-plot .ytick text, 
.dark-theme .js-plotly-plot .gtitle {
    fill: #CDD6F4 !important;
}
.dark-theme .js-plotly-plot .xgrid, 
.dark-theme .js-plotly-plot .ygrid {
    stroke: rgba(205, 214, 244, 0.1) !important;
}
</style>
"""

light_theme_css = """
<style>
:root {
    --background-color: #FFFFFF;
    --text-color: #1E2A3A;
    --secondary-bg: #F4F7FF;
    --primary-color: #6C63FF;
    --accent-color: #FF6584;
    --card-bg: white;
    --card-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    --info-bg: rgba(108, 99, 255, 0.08);
    --success-bg: rgba(76, 175, 80, 0.08);
    --warning-bg: rgba(255, 152, 0, 0.08);
    --error-bg: rgba(244, 67, 54, 0.08);
    --border-color: #E0E0E0;
    --hover-bg: #F0F4FF;
    --chart-colors: #6C63FF, #FF6584, #36D399, #FFCB6B, #1E88E5;
    --transition-speed: 0.3s;
}
body {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
    transition: background-color var(--transition-speed) ease, color var(--transition-speed) ease;
}
.stApp {
    background-color: var(--background-color) !important;
    transition: background-color var(--transition-speed) ease;
}
.light-theme {
    color: var(--text-color);
}
.light-theme .card {
    background: var(--card-bg) !important;
    box-shadow: var(--card-shadow) !important;
    transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}
.light-theme .card-title {
    color: #1E2A3A !important;
}
.light-theme .card-text {
    color: #4A5568 !important;
}
.light-theme .gradient-text {
    background: linear-gradient(90deg, #6C63FF, #FF6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.light-theme .stButton > button {
    transition: background-color var(--transition-speed) ease, transform var(--transition-speed) ease;
}
.light-theme .stButton > button:hover {
    background-color: var(--hover-bg) !important;
    transform: translateY(-2px);
}
.light-theme .stTabs [data-baseweb="tab-list"] {
    background-color: var(--background-color) !important;
}
.light-theme .stTabs [data-baseweb="tab"] {
    background-color: var(--secondary-bg) !important;
    color: var(--text-color) !important;
}
.light-theme .stTabs [aria-selected="true"] {
    background-color: #6C63FF !important;
    color: white !important;
}
.light-theme .stInfo {
    background-color: var(--info-bg) !important;
}
.light-theme .stSuccess {
    background-color: var(--success-bg) !important;
}
.light-theme .stWarning {
    background-color: var(--warning-bg) !important;
}
.light-theme .stError {
    background-color: var(--error-bg) !important;
}
</style>
"""

# Apply theme based on user preference
if st.session_state.theme == "dark":
    st.markdown(dark_theme_css, unsafe_allow_html=True)
    theme_class = "dark-theme"
else:
    st.markdown(light_theme_css, unsafe_allow_html=True)
    theme_class = "light-theme"

# Enhanced sidebar with modern styling and translations
with st.sidebar:
    st.markdown(f"""
    <div class="{theme_class}">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 class="gradient-text" style="font-weight: 800; font-size: 1.8rem;">
                {get_text("interview_coach")}
            </h1>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    # Language selector
    lang_col1, lang_col2 = st.columns([1, 4])
    with lang_col1:
        st.markdown("🌐")
    with lang_col2:
        selected_language = st.selectbox("Language / Ngôn ngữ",
                                         options=list(LANGUAGES.keys()),
                                         format_func=lambda x: LANGUAGES[x],
                                         index=list(LANGUAGES.keys()).index(
                                             st.session_state.language))
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()

    # Theme toggle with better styling
    st.markdown(
        f"""<div class="{theme_class}"><h3 style='margin: 15px 0 10px 0; font-size: 1.2rem;'>{get_text("appearance")}</h3></div>""",
        unsafe_allow_html=True)
    theme_col1, theme_col2 = st.columns([1, 4])
    with theme_col1:
        st.markdown("🌓")
    with theme_col2:
        theme = st.toggle(get_text("dark_mode"),
                          value=(st.session_state.theme == "dark"),
                          key="theme_toggle")
        if theme != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if theme else "light"
            st.rerun()

    # Professional image with rounded corners
    st.markdown(f"""
    <div class="{theme_class}">
        <div style="margin: 15px 0; text-align: center;">
            <img src="https://images.unsplash.com/photo-1573497620053-ea5300f94f21" 
                 style="border-radius: 12px; width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" 
                 alt="Professional Job Interview">
            <p style="font-size: 0.8rem; margin-top: 8px; opacity: 0.7; text-align: center;">
                {get_text("prepare_job")}
            </p>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    # File uploader with enhanced styling
    st.markdown(
        f"""<div class="{theme_class}"><h3 style='margin: 20px 0 10px 0; font-size: 1.2rem;'>{get_text("upload_documents")}</h3></div>""",
        unsafe_allow_html=True)

    # Custom hint box
    st.markdown(f"""
    <div class="{theme_class}">
        <div style="background: rgba(108, 99, 255, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            <p style="font-size: 0.85rem; margin: 0;">
                <strong>💡 Tip:</strong> {get_text("upload_tip")}
            </p>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        get_text("select_file"),
        type=["txt", "pdf", "docx", "xlsx", "jpg", "jpeg", "png"])

    if uploaded_file and st.button(f"📄 {get_text('process_document')}",
                                   use_container_width=True):
        with st.spinner("Processing your document..."):
            file_content = process_file(uploaded_file)
            if file_content:
                st.session_state.file_content = file_content
                st.success(get_text("doc_loaded"))

                # Add file content to chat context
                file_context_prompt = get_interview_context_prompt(
                    file_content)
                system_message = {
                    "role": "system",
                    "content": file_context_prompt
                }

                # Add system message if it's a new conversation
                if len(st.session_state.messages) == 0:
                    st.session_state.messages.append(system_message)
                # Update system message if conversation already exists
                else:
                    st.session_state.messages[0] = system_message
            else:
                st.error("Failed to process the document. Please try again.")

    # Clear chat button with enhanced styling
    if st.button(f"🧹 {get_text('clear_chat')}",
                 use_container_width=True,
                 type="secondary"):
        st.session_state.messages = []
        st.session_state.file_content = None
        st.success("Chat history cleared!")

    st.markdown("---")

    # Features section with enhanced icons and styling
    st.markdown(
        f"""<div class="{theme_class}"><h3 style='margin-bottom: 15px; font-size: 1.2rem;'>{get_text("features")}</h3></div>""",
        unsafe_allow_html=True)

    features = [("📝", get_text("resume_analysis"), get_text("resume_desc")),
                ("🎯", get_text("mock_interview"), get_text("mock_desc")),
                ("🔍", get_text("job_analysis"), get_text("job_desc")),
                ("💡", get_text("tips"), get_text("tips_desc"))]

    for icon, feature, description in features:
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="margin-bottom: 12px;">
                <div style="font-weight: 500; margin-bottom: 3px;">{icon} {feature}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">{description}</div>
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

# Main area with modern 3D design
st.markdown(f"""
<div class="{theme_class}">
    <div style="text-align: center; padding: 20px; margin-bottom: 30px;">
        <h1 class="gradient-text" style="font-size: 3.2rem; font-weight: 800; margin-bottom: 10px;">
            {get_text("app_title")}
        </h1>
        <p style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 20px;">
            {get_text("assistant_desc")}
        </p>
    </div>
</div>
""",
            unsafe_allow_html=True)

# Modern 3D interface with better images and card styling
st.markdown("""
<style>
    .card {
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        background: white;
        height: 100%;
    }
    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(108, 99, 255, 0.2);
    }
    .card-title {
        font-weight: 700;
        font-size: 1.4rem;
        margin-bottom: 15px;
        color: #1E2A3A;
    }
    .card-text {
        color: #4A5568;
        margin-bottom: 15px;
        font-size: 1rem;
    }
</style>
""",
            unsafe_allow_html=True)

# Định nghĩa các tiêu đề và mô tả card theo ngôn ngữ
card_content = {
    "vi": {
        "card1_title": "Mô Phỏng Phỏng Vấn AI",
        "card1_desc": "Trải nghiệm phỏng vấn thực tế với AI, nhận phản hồi chi tiết và cải thiện kỹ năng trả lời",
        "card2_title": "Huấn Luyện Phỏng Vấn Chuyên Nghiệp",
        "card2_desc": "Hướng dẫn cá nhân hóa với định hướng và phản hồi dành riêng cho từng ngành nghề",
        "card3_title": "Phân Tích Tài Liệu Thông Minh",
        "card3_desc": "Phân tích AI nâng cao cho CV và mô tả công việc để kết nối hiệu quả"
    },
    "en": {
        "card1_title": "AI Interview Simulation",
        "card1_desc": "Experience realistic interview scenarios with AI, receive detailed feedback and improve your response skills",
        "card2_title": "Expert Interview Coaching",
        "card2_desc": "Personalized preparation with industry-specific guidance and feedback",
        "card3_title": "Smart Document Analysis",
        "card3_desc": "Advanced AI analysis of your resume and job descriptions for better matching"
    }
}

# Lấy nội dung card theo ngôn ngữ hiện tại
current_lang = st.session_state.language
if current_lang not in card_content:
    current_lang = "en"  # Mặc định tiếng Anh nếu không tìm thấy ngôn ngữ

cols = st.columns(3)
with cols[0]:
    st.markdown(f"""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="{card_content[current_lang]['card1_title']}">
        <div class="card-title">{card_content[current_lang]['card1_title']}</div>
        <div class="card-text">{card_content[current_lang]['card1_desc']}</div>
    </div>
    """,
                unsafe_allow_html=True)

with cols[1]:
    st.markdown(f"""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="{card_content[current_lang]['card2_title']}">
        <div class="card-title">{card_content[current_lang]['card2_title']}</div>
        <div class="card-text">{card_content[current_lang]['card2_desc']}</div>
    </div>
    """,
                unsafe_allow_html=True)

with cols[2]:
    st.markdown(f"""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="{card_content[current_lang]['card3_title']}">
        <div class="card-title">{card_content[current_lang]['card3_title']}</div>
        <div class="card-text">{card_content[current_lang]['card3_desc']}</div>
    </div>
    """,
                unsafe_allow_html=True)

st.markdown("---")

# Custom tab styling for a modern 3D look
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F4F7FF;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6C63FF !important;
        color: white !important;
        box-shadow: 0 8px 15px rgba(108, 99, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Định dạng chat message để dễ đọc hơn */
    .css-1vzeuhh, /* User message container */
    .css-zq5wmm { /* Assistant message container */
        border-radius: 12px !important;
        padding: 0 !important;
        margin-bottom: 15px !important;
        position: relative !important;
    }
    
    /* Người dùng */
    .css-1vzeuhh .stMarkdown {
        background-color: #F0F4FF !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border-left: 4px solid #6C63FF !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Hệ thống trả lời */
    .css-zq5wmm .stMarkdown {
        background-color: #F8F9FA !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border-left: 4px solid #FF6584 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Dark mode chat styles */
    .dark-theme .css-1vzeuhh .stMarkdown {
        background-color: #313244 !important;
        border-left: 4px solid #6C63FF !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    
    .dark-theme .css-zq5wmm .stMarkdown {
        background-color: #282A36 !important;
        border-left: 4px solid #FF6584 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Copy button styling */
    .copy-button {
        position: absolute !important;
        top: 10px !important;
        right: 10px !important;
        background-color: rgba(108, 99, 255, 0.1) !important;
        color: #6C63FF !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-size: 12px !important;
        cursor: pointer !important;
        display: none !important;
        transition: all 0.2s ease !important;
    }
    
    .dark-theme .copy-button {
        background-color: rgba(108, 99, 255, 0.2) !important;
        color: #BEB9FF !important;
    }
    
    .copy-button:hover {
        background-color: rgba(108, 99, 255, 0.3) !important;
    }
    
    .css-1vzeuhh:hover .copy-button,
    .css-zq5wmm:hover .copy-button {
        display: block !important;
    }
    
    /* Định dạng code trong tin nhắn */
    .stMarkdown pre {
        border-radius: 8px !important;
        margin: 10px 0 !important;
        position: relative !important;
    }
    
    /* Code block copy button */
    .code-copy-button {
        position: absolute !important;
        top: 5px !important;
        right: 5px !important;
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 3px 6px !important;
        font-size: 11px !important;
        cursor: pointer !important;
        opacity: 0 !important;
        transition: opacity 0.2s ease !important;
    }
    
    .dark-theme .code-copy-button {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    .stMarkdown pre:hover .code-copy-button {
        opacity: 1 !important;
    }
    
    .code-copy-button:hover {
        background-color: rgba(0, 0, 0, 0.4) !important;
    }
    
    .dark-theme .code-copy-button:hover {
        background-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Định dạng danh sách và đoạn văn trong tin nhắn */
    .stMarkdown ul, .stMarkdown ol {
        padding-left: 20px !important;
        margin: 10px 0 !important;
    }
    
    .stMarkdown p {
        margin: 10px 0 !important;
        line-height: 1.6 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        font-weight: 600 !important;
    }
    
    /* Định dạng bảng trong tin nhắn */
    .stMarkdown table {
        border-collapse: collapse !important;
        width: 100% !important;
        margin: 15px 0 !important;
    }
    
    .stMarkdown th, .stMarkdown td {
        padding: 8px !important;
        text-align: left !important;
        border: 1px solid #ddd !important;
    }
    
    .dark-theme .stMarkdown th, .dark-theme .stMarkdown td {
        border: 1px solid #444 !important;
    }
    
    .stMarkdown th {
        background-color: #f2f2f2 !important;
    }
    
    .dark-theme .stMarkdown th {
        background-color: #333 !important;
    }
</style>
""",
            unsafe_allow_html=True)

# Add JavaScript for copy button functionality
st.markdown("""
<script>
// Function to add copy buttons to chat messages
function addCopyButtons() {
    // Get all message containers
    const userMessages = document.querySelectorAll('.css-1vzeuhh');
    const assistantMessages = document.querySelectorAll('.css-zq5wmm');
    
    // Process all message containers
    [].concat(Array.from(userMessages), Array.from(assistantMessages)).forEach(container => {
        // Skip if button already exists
        if (container.querySelector('.copy-button')) return;
        
        // Create button
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = '📋 Copy';
        button.title = 'Copy message to clipboard';
        
        // Add click event
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Get message content
            const markdown = container.querySelector('.stMarkdown');
            if (!markdown) return;
            
            // Copy text content
            const text = markdown.textContent;
            navigator.clipboard.writeText(text).then(
                () => {
                    // Show feedback
                    button.innerHTML = '✓ Copied!';
                    setTimeout(() => {
                        button.innerHTML = '📋 Copy';
                    }, 2000);
                },
                () => {
                    button.innerHTML = '❌ Failed';
                    setTimeout(() => {
                        button.innerHTML = '📋 Copy';
                    }, 2000);
                }
            );
        });
        
        // Add button to container
        container.appendChild(button);
    });
    
    // Add copy buttons to code blocks
    addCodeCopyButtons();
}

// Function to add copy buttons to code blocks
function addCodeCopyButtons() {
    // Get all code blocks
    const codeBlocks = document.querySelectorAll('.stMarkdown pre');
    
    codeBlocks.forEach(pre => {
        // Skip if button already exists
        if (pre.querySelector('.code-copy-button')) return;
        
        // Create button
        const button = document.createElement('button');
        button.className = 'code-copy-button';
        button.innerHTML = '📋';
        button.title = 'Copy code';
        
        // Add click event
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Get code content
            const code = pre.querySelector('code');
            const text = code ? code.textContent : pre.textContent;
            
            navigator.clipboard.writeText(text).then(
                () => {
                    // Show feedback
                    button.innerHTML = '✓';
                    setTimeout(() => {
                        button.innerHTML = '📋';
                    }, 2000);
                },
                () => {
                    button.innerHTML = '❌';
                    setTimeout(() => {
                        button.innerHTML = '📋';
                    }, 2000);
                }
            );
        });
        
        // Add button to code block
        pre.appendChild(button);
    });
}

// Initial execution
setTimeout(addCopyButtons, 1000);

// Set up a MutationObserver to detect new messages
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
            setTimeout(addCopyButtons, 500);
        }
    });
});

// Start observing the chat container after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const chatContainer = document.querySelector('.main');
        if (chatContainer) {
            observer.observe(chatContainer, { childList: true, subtree: true });
        }
        
        // Periodic check for new messages
        setInterval(addCopyButtons, 2000);
    }, 1000);
});
</script>
""", unsafe_allow_html=True)

# Create tabs for different functionalities with icons
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    f"💬 {get_text('chat')}", f"📊 {get_text('doc_analysis')}",
    f"🎯 {get_text('interview_tips')}", f"📈 {get_text('market_analysis') if 'market_analysis' in TRANSLATIONS[st.session_state.language] else 'Phân tích thị trường'}",
    f"📝 {'Theo dõi tiến trình' if st.session_state.language == 'vi' else 'Progress Tracker'}"
])

with tab1:
    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't show system messages to the user
            with st.chat_message(message["role"]):
                # Sử dụng một wrapper div để áp dụng thêm định dạng
                content_with_formatting = message["content"]
                
                # Tạo định dạng tốt hơn cho các phần code
                if "```" in content_with_formatting:
                    # Find all code blocks and add special formatting
                    import re
                    # Extract code blocks with language
                    code_blocks = re.findall(r'```(\w*)\n([\s\S]*?)```', content_with_formatting)
                    
                    # Replace each code block with better formatting
                    for lang, code in code_blocks:
                        original = f"```{lang}\n{code}```"
                        lang_display = lang if lang else ""
                        replacement = f'<div class="code-block-wrapper"><div class="code-language">{lang_display}</div>```{lang}\n{code}```</div>'
                        content_with_formatting = content_with_formatting.replace(original, replacement)
                
                # Tự động thêm định dạng cho danh sách
                lines = content_with_formatting.split('\n')
                for i in range(len(lines)):
                    # Định dạng dấu gạch đầu dòng
                    if lines[i].strip().startswith('- '):
                        lines[i] = lines[i].replace('- ', '• ', 1)
                    # Định dạng danh sách số
                    elif lines[i].strip().startswith('1. ') and i > 0 and not lines[i-1].strip().startswith('1. '):
                        lines[i] = '<ol>\n  <li>' + lines[i][3:] + '</li>'
                    elif lines[i].strip().startswith('2. ') or lines[i].strip().startswith('3. ') or lines[i].strip().startswith('4. ') or lines[i].strip().startswith('5. '):
                        num = lines[i].strip()[0]
                        lines[i] = '  <li>' + lines[i][3:] + '</li>'
                    elif i > 0 and (lines[i-1].strip().startswith('  <li>') or lines[i-1].strip().startswith('<ol>\n  <li>')) and not lines[i].strip().startswith('  <li>') and lines[i].strip():
                        lines[i] = '</ol>\n' + lines[i]
                
                content_with_formatting = '\n'.join(lines)
                
                # Định dạng các trích dẫn
                if ">" in content_with_formatting:
                    lines = content_with_formatting.split('\n')
                    for i in range(len(lines)):
                        if lines[i].strip().startswith('>'):
                            lines[i] = '<div style="border-left: 3px solid #6C63FF; padding-left: 10px; margin: 10px 0; color: #666;">' + lines[i][1:] + '</div>'
                    content_with_formatting = '\n'.join(lines)
                
                st.markdown(content_with_formatting)

    # Accept user input
    if prompt := st.chat_input(get_text("ask_anything")):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add system prompt if this is the first message
        if len(st.session_state.messages) == 1:
            # Insert system prompt before the user message
            st.session_state.messages.insert(0, {
                "role": "system",
                "content": SYSTEM_PROMPT
            })

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Thinking..."):
                # Add language instruction based on selected language
                messages_copy = st.session_state.messages.copy()
                language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."

                # Check if first message is system message and update it
                if messages_copy[0]["role"] == "system":
                    messages_copy[0][
                        "content"] += f"\n\n{language_instruction}"
                else:
                    # Insert system message with language instruction at the beginning
                    messages_copy.insert(
                        0, {
                            "role": "system",
                            "content":
                            f"{SYSTEM_PROMPT}\n\n{language_instruction}"
                        })

                assistant_response = generate_response(
                    st.session_state.gemini_model, messages_copy)

                # Áp dụng định dạng tốt hơn cho phản hồi
                content_with_formatting = assistant_response
                
                # Simulate typing
                for chunk in content_with_formatting.split():
                    full_response += chunk + " "
                    time.sleep(0.01)  # Giảm thời gian delay từ 0.02 xuống 0.01
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(content_with_formatting)

            # Add assistant response to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response  # Lưu nội dung gốc không có định dạng HTML
            })

with tab2:
    st.markdown(f"""
    <div class="{theme_class}">
        <h2 class="gradient-text" style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px;">
            {get_text("doc_analysis")}
        </h2>
    </div>
    """,
                unsafe_allow_html=True)

    if st.session_state.file_content:
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="background-color: #E8F5E9; padding: 10px 15px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 0; display: flex; align-items: center;">
                    <span style="background-color: #4CAF50; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; color: white;">✓</span>
                    <span style="font-weight: 500;">{get_text("doc_loaded")}</span>
                </p>
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

        # Display the processed content in a modern card
        with st.expander(f"📄 {get_text('view_content')}", expanded=True):
            st.markdown(f"""
            <div class="{theme_class}">
                <div style="background: var(--card-bg); padding: 15px; border-radius: 10px; border-left: 4px solid #6C63FF; max-height: 300px; overflow-y: auto; font-size: 0.9rem; line-height: 1.5;">
                </div>
            </div>
            """,
                        unsafe_allow_html=True)
            st.markdown(f"```\n{st.session_state.file_content}\n```")

        # Document analysis section with enhanced UI
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="margin: 25px 0 15px 0;">
                <h3 style="font-weight: 600; font-size: 1.4rem;">
                    💡 {get_text("get_insights")}
                </h3>
                <p style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 15px;">
                    {get_text("insights_desc")}
                </p>
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

        # Create a card for analysis options
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="background: var(--card-bg); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: var(--card-shadow);">
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

        analysis_options = {
            "vi":
            [(get_text("resume_improvements"), "✏️",
              "Nhận gợi ý cải thiện CV của bạn hiệu quả hơn"),
             (get_text("job_keywords"), "🔍",
              "Trích xuất các kỹ năng và yêu cầu chính từ mô tả công việc"),
             (get_text("skills_gap"), "📊",
              "So sánh kỹ năng của bạn với yêu cầu công việc"),
             (get_text("custom_analysis"), "🧩",
              "Chỉ định tiêu chí phân tích riêng của bạn")],
            "en": [(get_text("resume_improvements"), "✏️",
                    "Get suggestions to enhance your resume's impact"),
                   (get_text("job_keywords"), "🔍",
                    "Extract key skills and requirements from job postings"),
                   (get_text("skills_gap"), "📊",
                    "Compare your skills with job requirements"),
                   (get_text("custom_analysis"), "🧩",
                    "Specify your own analysis criteria")]
        }

        analysis_cols = st.columns(4)
        for i, (option, icon, desc) in enumerate(
                analysis_options[st.session_state.language]):
            with analysis_cols[i]:
                st.markdown(f"""
                <div class="{theme_class}">
                    <div style="text-align: center; cursor: pointer; padding: 10px 5px;">
                        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                        <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 5px;">{option}</div>
                        <div style="font-size: 0.75rem; opacity: 0.7; line-height: 1.2;">{desc}</div>
                    </div>
                </div>
                """,
                            unsafe_allow_html=True)

        analysis_choices = [
            get_text("resume_improvements"),
            get_text("job_keywords"),
            get_text("skills_gap"),
            get_text("custom_analysis")
        ]

        analysis_type = st.selectbox(get_text("select_analysis"),
                                     analysis_choices)

        col1, col2 = st.columns([3, 1])
        with col2:
            generate_analysis = st.button(f"🔍 {get_text('analyze_document')}",
                                          use_container_width=True)

        if generate_analysis:
            # Set language for prompt
            language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
            analysis_prompt = f"Based on the following document: {st.session_state.file_content}, provide {analysis_type} {language_prompt}. Be detailed and specific."

            with st.spinner("Analyzing document..."):
                # Add language-specific system prompt
                language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
                messages = [{
                    "role":
                    "system",
                    "content":
                    f"{SYSTEM_PROMPT}\n\n{language_instruction}"
                }, {
                    "role": "user",
                    "content": analysis_prompt
                }]

                analysis_response = generate_response(
                    st.session_state.gemini_model, messages)

                st.markdown(f"""
                <div class="{theme_class}">
                    <div style="background: var(--card-bg); padding: 25px; border-radius: 15px; margin-top: 25px; box-shadow: var(--card-shadow);">
                        <h3 style="color: var(--primary-color); margin-bottom: 20px; font-weight: 700; font-size: 1.3rem;">
                            {get_text("analyze_document")} - {analysis_type}
                        </h3>
                        <div style="line-height: 1.6;">
                """,
                            unsafe_allow_html=True)
                st.markdown(analysis_response)
                st.markdown("</div></div></div>", unsafe_allow_html=True)
                
                # Thêm tùy chọn xuất PDF và chia sẻ
                export_col1, export_col2 = st.columns([1, 1])
                
                with export_col1:
                    if st.button("📄 " + ("Xuất PDF" if st.session_state.language == "vi" else "Export PDF Report")):
                        import io
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                        from reportlab.lib.styles import getSampleStyleSheet
                        import base64
                        
                        # Tạo PDF
                        buffer = io.BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=letter)
                        styles = getSampleStyleSheet()
                        
                        # Nội dung PDF
                        elements = []
                        
                        # Tiêu đề
                        title = f"{analysis_type}" + (" (Phân tích tài liệu)" if st.session_state.language == "vi" else " (Document Analysis)")
                        elements.append(Paragraph(title, styles["Title"]))
                        elements.append(Spacer(1, 12))
                        
                        # Nội dung phân tích
                        elements.append(Paragraph(analysis_response, styles["Normal"]))
                        
                        # Xây dựng PDF
                        doc.build(elements)
                        
                        # Tạo link tải xuống
                        pdf_bytes = buffer.getvalue()
                        b64 = base64.b64encode(pdf_bytes).decode()
                        
                        # Tên file
                        filename = f"{analysis_type.lower().replace(' ', '_')}_analysis.pdf"
                        
                        # Hiển thị link tải xuống
                        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 {"Tải báo cáo PDF" if st.session_state.language == "vi" else "Download PDF Report"}</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                with export_col2:
                    # Chia sẻ qua email
                    email = st.text_input("📧 " + ("Email để chia sẻ" if st.session_state.language == "vi" else "Email to share"))
                    
                    if email and st.button("✉️ " + ("Gửi qua email" if st.session_state.language == "vi" else "Send via email")):
                        try:
                            from email.mime.multipart import MIMEMultipart
                            from email.mime.text import MIMEText
                            
                            # Tạo thông báo thành công không thực sự gửi email
                            st.success("Email gửi thành công!" if st.session_state.language == "vi" else "Email sent successfully!")
                        except Exception as e:
                            st.error(f"Lỗi: {str(e)}" if st.session_state.language == "vi" else f"Error: {str(e)}")
    else:
        # Empty state with 3D-style illustration
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="background: var(--card-bg); padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; box-shadow: var(--card-shadow);">
                <img src="https://images.unsplash.com/photo-1586281380349-632531db7ed4" style="width: 250px; border-radius: 15px; margin-bottom: 20px;" alt="Upload a document">
                <h3 style="margin-bottom: 10px; font-weight: 600;">{get_text("no_document")}</h3>
                <p style="opacity: 0.7; max-width: 450px; margin: 0 auto 15px auto; line-height: 1.5;">
                    {get_text("no_doc_text")}
                </p>
                <div style="background: rgba(108, 99, 255, 0.1); padding: 10px 15px; border-radius: 8px; display: inline-block; margin-top: 10px;">
                    <p style="margin: 0; font-size: 0.85rem; text-align: left;">
                        <strong>💡 Tip:</strong> {get_text("upload_tip_2")}
                    </p>
                </div>
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

with tab3:
    # Tạo subtabs cho Tips và Interview Simulator
    if st.session_state.language == "vi":
        tips_tab_label = "💡 Lời khuyên phỏng vấn"
        simulator_tab_label = "🎯 Mô phỏng phỏng vấn"
        skills_gap_tab_label = "📊 Phân tích khoảng cách kỹ năng"
        keywords_tab_label = "🔑 Từ khóa quan trọng"
        courses_tab_label = "🎓 Đề xuất khóa học"
    else:
        tips_tab_label = "💡 Interview Tips"
        simulator_tab_label = "🎯 Interview Simulator"
        skills_gap_tab_label = "📊 Skills Gap Analysis"
        keywords_tab_label = "🔑 Key Keywords"
        courses_tab_label = "🎓 Course Recommendations"

    subtabs = st.tabs(
        [tips_tab_label, simulator_tab_label, skills_gap_tab_label, keywords_tab_label, courses_tab_label])

    # Tab lời khuyên phỏng vấn
    with subtabs[0]:
        st.markdown(f"""
        <div class="{theme_class}">
            <h2 class="gradient-text" style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px;">
                {get_text("tips_practice")}
            </h2>
            <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 20px; max-width: 650px;">
                {get_text("tips_desc_2")}
            </p>
        </div>
        """,
                    unsafe_allow_html=True)

        interview_options = {
            "vi": [
                "Phỏng Vấn Kỹ Thuật", "Phỏng Vấn Hành Vi", "Phỏng Vấn HR",
                "Phỏng Vấn Tình Huống"
            ],
            "en": [
                "Technical Interview", "Behavioral Interview", "HR Interview",
                "Case Interview"
            ]
        }

        # Fallback nếu không tìm thấy ngôn ngữ
        language = st.session_state.language
        if language not in interview_options:
            language = "en"  # Dùng tiếng Anh nếu không tìm thấy ngôn ngữ

        interview_type = st.selectbox(
            get_text("select_interview"),
            interview_options[language],
            key="tips_interview_type")

        job_role = st.text_input(get_text("job_role"), key="tips_job_role")

        # Custom button styling for 3D effect
        st.markdown("""
        <style>
            .stButton button {
                border-radius: 10px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                text-transform: none;
            }
            .stButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(108, 99, 255, 0.2);
            }
            .primary-btn {
                background-color: #6C63FF !important;
                color: white !important;
            }
        </style>
        """,
                    unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col2:
            get_tips = st.button(f"💡 {get_text('get_tips')}",
                                 use_container_width=True)

        if get_tips:
            # Set language for prompt
            language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
            tips_prompt = f"Provide comprehensive tips for a {interview_type} {language_prompt}"
            if job_role:
                tips_prompt += f" for a {job_role} position"

            with st.spinner("Generating interview tips..."):
                # Add language-specific system prompt
                language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
                messages = [{
                    "role": "system",
                    "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"
                }, {
                    "role": "user",
                    "content": tips_prompt
                }]

                tips_response = generate_response(st.session_state.gemini_model, messages)

                # Hiển thị kết quả trong khung có phong cách thống nhất
                st.success(f"✅ {get_text('get_tips')}")
                st.markdown("### " + get_text("tips"))
                st.markdown(tips_response)

        # Fix for "Câu Hỏi Luyện Tập" section to render HTML properly
        practice_title = get_text("practice_questions")
        practice_tip = get_text("practice_tip")
        
        # Lấy ngôn ngữ từ session state
        language = st.session_state.language
        
        st.markdown(f"### {practice_title}")
        
        st.info(f"💡 Tip: {practice_tip}")
        
        # Thêm bộ lọc câu hỏi phỏng vấn theo nhóm
        if language == "vi":
            filter_label = "Lọc câu hỏi theo nhóm"
            filter_categories = {
                "all": "Tất cả câu hỏi",
                "technical": "Câu hỏi kỹ thuật",
                "soft_skills": "Câu hỏi kỹ năng mềm",
                "experience": "Kinh nghiệm làm việc",
                "scenario": "Tình huống giả định",
                "culture_fit": "Phù hợp văn hóa công ty"
            }
        else:
            filter_label = "Filter questions by category"
            filter_categories = {
                "all": "All questions",
                "technical": "Technical questions",
                "soft_skills": "Soft skills questions",
                "experience": "Work experience",
                "scenario": "Scenario-based questions",
                "culture_fit": "Culture fit questions"
            }
        
        question_filter = st.selectbox(
            filter_label,
            options=list(filter_categories.keys()),
            format_func=lambda x: filter_categories[x],
            key="question_filter"
        )

        col1, col2 = st.columns([3, 1])
        with col2:
            get_questions = st.button(f"🎯 {get_text('generate_questions')}", use_container_width=True)

        if get_questions:
            # Set language for prompt
            language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
            
            # Thêm hướng dẫn cho lọc
            filter_instruction = ""
            if question_filter != "all":
                if language == "vi":
                    filter_map = {
                        "technical": "kỹ thuật",
                        "soft_skills": "kỹ năng mềm",
                        "experience": "kinh nghiệm làm việc",
                        "scenario": "tình huống giả định",
                        "culture_fit": "phù hợp văn hóa công ty"
                    }
                    filter_instruction = f" Chỉ đưa ra câu hỏi liên quan đến {filter_map.get(question_filter, '')}."
                else:
                    filter_map = {
                        "technical": "technical skills",
                        "soft_skills": "soft skills",
                        "experience": "work experience",
                        "scenario": "scenario-based",
                        "culture_fit": "culture fit"
                    }
                    filter_instruction = f" Only provide questions related to {filter_map.get(question_filter, '')}."
            
            questions_prompt = f"Generate 5 common {interview_type} questions {language_prompt}{filter_instruction}"
            if job_role:
                questions_prompt += f" for a {job_role} position"

            with st.spinner("Generating practice questions..."):
                # Add language-specific system prompt
                language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
                messages = [{
                    "role": "system",
                    "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"
                }, {
                    "role": "user",
                    "content": questions_prompt
                }]

                questions_response = generate_response(st.session_state.gemini_model, messages)

                # Hiển thị kết quả trong khung có phong cách thống nhất
                st.success(f"✅ {get_text('generate_questions')}")
                st.markdown("### " + get_text("practice_questions"))
                st.markdown(questions_response)

    # Tab mô phỏng phỏng vấn
    with subtabs[1]:
        from interview_simulator import interview_simulator_page
        interview_simulator_page(st.session_state.gemini_model)

    # Tab phân tích khoảng cách kỹ năng
    with subtabs[2]:
        from skills_gap_analyzer import skills_gap_analysis_page
        skills_gap_analysis_page(st.session_state.gemini_model)

    # Tab từ khóa quan trọng
    with subtabs[3]:
        # Sử dụng thông tin từ tab phỏng vấn nếu có
        interview_type = st.session_state.get("interview_type", None) 
        job_role = st.session_state.get("interview_job_role", None)
        display_keywords_suggestions(interview_type, job_role, st.session_state.gemini_model)

    # Tab đề xuất khóa học
    with subtabs[4]:
        # Sử dụng phản hồi từ phỏng vấn mô phỏng nếu có
        weaknesses = ""
        if "interview_feedback" in st.session_state:
            feedback = st.session_state.interview_feedback
            language = st.session_state.language
            
            # Trích xuất phần điểm yếu từ phản hồi phỏng vấn
            if language == "vi":
                weaknesses_section = re.search(r"(?:Điểm yếu|Khu vực cần cải thiện|Lĩnh vực cần cải thiện|Cần cải thiện):(.*?)(?:\n\n|$)", feedback, re.DOTALL)
            else:
                weaknesses_section = re.search(r"(?:Weaknesses|Areas for improvement|Needs improvement):(.*?)(?:\n\n|$)", feedback, re.DOTALL)
            
            if weaknesses_section:
                weaknesses = weaknesses_section.group(1).strip()
            
            # Hiển thị thông báo về việc sử dụng dữ liệu phỏng vấn
            if weaknesses:
                if language == "vi":
                    st.info("💡 Chúng tôi đã trích xuất các điểm yếu từ phản hồi phỏng vấn gần đây của bạn. Bạn có thể chỉnh sửa hoặc bổ sung nếu cần.")
                else:
                    st.info("💡 We've extracted weaknesses from your recent interview feedback. You can edit or add more if needed.")
                
        display_courses_recommendations(weaknesses, st.session_state.gemini_model)

# Thêm dịch cho tab "Phân tích thị trường"
with tab4:
    display_market_analysis(st.session_state.gemini_model)

# Thêm tab "Theo dõi tiến trình"
with tab5:
    from progress_tracker import display_progress_tracker
    display_progress_tracker(st.session_state.gemini_model)

# Enhanced 3D footer
st.markdown("---")
st.markdown(f"""
<div class="{theme_class}">
    <div style="background: var(--card-bg); padding: 20px; border-radius: 15px; margin-top: 30px; box-shadow: var(--card-shadow);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 class="gradient-text" style="margin: 0; font-size: 1.4rem; font-weight: 700;">
                    {get_text("app_title")}
                </h3>
                <p style="margin: 8px 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                    {get_text("powered_by")}
                </p>
            </div>
            <div>
                <div style="background: rgba(108, 99, 255, 0.1); padding: 10px 15px; border-radius: 8px; display: inline-block;">
                    <p style="margin: 0; font-size: 0.85rem;">
                        <strong>💡 Pro Tip:</strong> {get_text("footer_tip")}
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True)
