import streamlit as st
import os
import time
import json
from file_processor import process_file
from gemini_helper import initialize_gemini, generate_response
from prompts import SYSTEM_PROMPT, get_interview_context_prompt

# Page configuration
st.set_page_config(
    page_title="3D Job Interview Assistant",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        "upload_tip": "Tải lên CV, mô tả công việc, hoặc tài liệu liên quan để được phân tích cá nhân hoá",
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
        "assistant_desc": "Hướng dẫn AI giúp thành công trong phỏng vấn việc làm",
        "chat": "Trò Chuyện",
        "doc_analysis": "Phân Tích Tài Liệu",
        "interview_tips": "Lời Khuyên Phỏng Vấn",
        "ask_anything": "Hỏi bất kỳ điều gì về phỏng vấn việc làm...",
        "doc_loaded": "Tài liệu đã được tải thành công!",
        "view_content": "Xem Nội Dung Tài Liệu",
        "get_insights": "Nhận Phân Tích AI",
        "insights_desc": "Chọn loại phân tích và tạo thông tin chi tiết dựa trên tài liệu của bạn",
        "select_analysis": "Chọn loại phân tích",
        "resume_improvements": "Cải Thiện CV",
        "job_keywords": "Từ Khoá Mô Tả Công Việc",
        "skills_gap": "Phân Tích Khoảng Cách Kỹ Năng",
        "custom_analysis": "Phân Tích Tuỳ Chỉnh",
        "analyze_document": "Phân Tích Tài Liệu",
        "no_document": "Chưa Có Tài Liệu Nào Được Tải Lên",
        "no_doc_text": "Tải lên CV, mô tả công việc, hoặc tài liệu liên quan bằng thanh bên để nhận phân tích và thông tin chi tiết",
        "upload_tip_2": "Thử tải lên các loại tài liệu khác nhau bao gồm văn bản, PDF, DOCX, hoặc thậm chí hình ảnh",
        "tips_practice": "Lời Khuyên & Luyện Tập Phỏng Vấn",
        "tips_desc_2": "Nhận hướng dẫn chuẩn bị phỏng vấn cá nhân hoá cho các loại phỏng vấn khác nhau. Chọn loại phỏng vấn bên dưới và tùy chọn nhập vai trò công việc mục tiêu để nhận lời khuyên phù hợp hơn.",
        "select_interview": "Chọn Loại Phỏng Vấn",
        "technical": "Phỏng Vấn Kỹ Thuật",
        "behavioral": "Phỏng Vấn Hành Vi",
        "hr_interview": "Phỏng Vấn HR",
        "case_interview": "Phỏng Vấn Tình Huống",
        "job_role": "Nhập Vai Trò Công Việc (tuỳ chọn)",
        "get_tips": "Nhận Lời Khuyên",
        "practice_questions": "Câu Hỏi Luyện Tập",
        "practice_tip": "Luyện tập với câu hỏi phỏng vấn thực tế cho loại phỏng vấn và vai trò cụ thể của bạn.",
        "generate_questions": "Tạo Câu Hỏi",
        "footer_tip": "Tải lên CV của bạn để được chuẩn bị phỏng vấn cá nhân hoá",
        "powered_by": "Huấn luyện viên phỏng vấn cá nhân của bạn"
    },
    "en": {
        "app_title": "Job Interview Assistant",
        "interview_coach": "Interview Coach AI",
        "dark_mode": "Dark Mode",
        "appearance": "Appearance",
        "prepare_job": "Prepare for your dream job",
        "upload_documents": "Upload Documents",
        "upload_tip": "Upload your resume, job description, or any relevant document for personalized analysis",
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
        "assistant_desc": "Your personal AI-powered guide to job interview success",
        "chat": "Chat",
        "doc_analysis": "Document Analysis",
        "interview_tips": "Interview Tips",
        "ask_anything": "Ask me anything about job interviews...",
        "doc_loaded": "Document loaded successfully!",
        "view_content": "View Document Content",
        "get_insights": "Get AI-Powered Insights",
        "insights_desc": "Select analysis type and generate personalized insights based on your document",
        "select_analysis": "Select analysis type",
        "resume_improvements": "Resume Improvements",
        "job_keywords": "Job Description Keywords",
        "skills_gap": "Skills Gap Analysis",
        "custom_analysis": "Custom Analysis",
        "analyze_document": "Analyze Document",
        "no_document": "No Document Uploaded Yet",
        "no_doc_text": "Upload a resume, job description, or any relevant document using the sidebar to get personalized analysis and insights",
        "upload_tip_2": "Try uploading different document types including text, PDF, DOCX, or even images",
        "tips_practice": "Interview Tips & Practice",
        "tips_desc_2": "Get personalized interview preparation guidance for different interview types. Select your interview type below and optionally enter your target job role for more tailored advice.",
        "select_interview": "Select Interview Type",
        "technical": "Technical Interview",
        "behavioral": "Behavioral Interview",
        "hr_interview": "HR Interview",
        "case_interview": "Case Interview",
        "job_role": "Enter Job Role (optional)",
        "get_tips": "Get Tips",
        "practice_questions": "Practice Questions",
        "practice_tip": "Practice with real interview questions for your specific role and interview type.",
        "generate_questions": "Generate Questions",
        "footer_tip": "Upload your resume for personalized interview preparation",
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
    # Initialize Gemini API with provided key
    api_key = os.getenv("GEMINI_API_KEY")
    st.session_state.gemini_model = initialize_gemini(api_key)
    
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
}
body {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}
.stApp {
    background-color: var(--background-color) !important;
}
.dark-theme {
    color: var(--text-color);
}
.dark-theme .card {
    background: var(--card-bg) !important;
    box-shadow: var(--card-shadow) !important;
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
}
.dark-theme .stButton > button {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
}
.dark-theme .stTextArea > div > div {
    background-color: #313244 !important;
    color: #CDD6F4 !important;
}
.dark-theme .stSelectbox > div > div {
    background-color: #313244 !important;
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
}
body {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}
.stApp {
    background-color: var(--background-color) !important;
}
.light-theme {
    color: var(--text-color);
}
.light-theme .card {
    background: var(--card-bg) !important;
    box-shadow: var(--card-shadow) !important;
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
    """, unsafe_allow_html=True)
    
    # Language selector
    lang_col1, lang_col2 = st.columns([1, 4])
    with lang_col1:
        st.markdown("🌐")
    with lang_col2:
        selected_language = st.selectbox(
            "Language / Ngôn ngữ",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
    
    # Theme toggle with better styling
    st.markdown(f"""<div class="{theme_class}"><h3 style='margin: 15px 0 10px 0; font-size: 1.2rem;'>{get_text("appearance")}</h3></div>""", unsafe_allow_html=True)
    theme_col1, theme_col2 = st.columns([1, 4])
    with theme_col1:
        st.markdown("🌓")
    with theme_col2:
        theme = st.toggle(get_text("dark_mode"), value=(st.session_state.theme == "dark"), key="theme_toggle")
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
    """, unsafe_allow_html=True)
    
    # File uploader with enhanced styling
    st.markdown(f"""<div class="{theme_class}"><h3 style='margin: 20px 0 10px 0; font-size: 1.2rem;'>{get_text("upload_documents")}</h3></div>""", unsafe_allow_html=True)
    
    # Custom hint box
    st.markdown(f"""
    <div class="{theme_class}">
        <div style="background: rgba(108, 99, 255, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            <p style="font-size: 0.85rem; margin: 0;">
                <strong>💡 Tip:</strong> {get_text("upload_tip")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        get_text("select_file"),
        type=["txt", "pdf", "docx", "xlsx", "jpg", "jpeg", "png"]
    )
    
    if uploaded_file and st.button(f"📄 {get_text('process_document')}", use_container_width=True):
        with st.spinner("Processing your document..."):
            file_content = process_file(uploaded_file)
            if file_content:
                st.session_state.file_content = file_content
                st.success(get_text("doc_loaded"))
                
                # Add file content to chat context
                file_context_prompt = get_interview_context_prompt(file_content)
                system_message = {"role": "system", "content": file_context_prompt}
                
                # Add system message if it's a new conversation
                if len(st.session_state.messages) == 0:
                    st.session_state.messages.append(system_message)
                # Update system message if conversation already exists
                else:
                    st.session_state.messages[0] = system_message
            else:
                st.error("Failed to process the document. Please try again.")
    
    # Clear chat button with enhanced styling
    if st.button(f"🧹 {get_text('clear_chat')}", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.file_content = None
        st.success("Chat history cleared!")
    
    st.markdown("---")
    
    # Features section with enhanced icons and styling
    st.markdown(f"""<div class="{theme_class}"><h3 style='margin-bottom: 15px; font-size: 1.2rem;'>{get_text("features")}</h3></div>""", unsafe_allow_html=True)
    
    features = [
        ("📝", get_text("resume_analysis"), get_text("resume_desc")),
        ("🎯", get_text("mock_interview"), get_text("mock_desc")),
        ("🔍", get_text("job_analysis"), get_text("job_desc")),
        ("💡", get_text("tips"), get_text("tips_desc"))
    ]
    
    for icon, feature, description in features:
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="margin-bottom: 12px;">
                <div style="font-weight: 500; margin-bottom: 3px;">{icon} {feature}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">{description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
""", unsafe_allow_html=True)

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
""", unsafe_allow_html=True)

cols = st.columns(3)
with cols[0]:
    st.markdown("""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="Modern 3D Interface">
        <div class="card-title">Modern 3D Interface</div>
        <div class="card-text">Engaging with a sleek, intuitive design optimized for all devices</div>
    </div>
    """, unsafe_allow_html=True)
    
with cols[1]:
    st.markdown("""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="Interview Preparation">
        <div class="card-title">Expert Interview Coaching</div>
        <div class="card-text">Personalized preparation with industry-specific guidance and feedback</div>
    </div>
    """, unsafe_allow_html=True)
    
with cols[2]:
    st.markdown("""
    <div class="card">
        <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71" style="width: 100%; border-radius: 10px; margin-bottom: 15px;" alt="Document Analysis">
        <div class="card-title">Smart Document Analysis</div>
        <div class="card-text">Advanced AI analysis of your resume and job descriptions for better matching</div>
    </div>
    """, unsafe_allow_html=True)

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
</style>
""", unsafe_allow_html=True)

# Create tabs for different functionalities with icons
tab1, tab2, tab3 = st.tabs([
    f"💬 {get_text('chat')}", 
    f"📊 {get_text('doc_analysis')}", 
    f"🎯 {get_text('interview_tips')}"
])

with tab1:
    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't show system messages to the user
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
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
            st.session_state.messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
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
                    messages_copy[0]["content"] += f"\n\n{language_instruction}"
                else:
                    # Insert system message with language instruction at the beginning
                    messages_copy.insert(0, {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"})
                
                assistant_response = generate_response(
                    st.session_state.gemini_model, 
                    messages_copy
                )
                
                # Simulate typing
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.02)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

with tab2:
    st.markdown(f"""
    <div class="{theme_class}">
        <h2 class="gradient-text" style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px;">
            {get_text("doc_analysis")}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
        """, unsafe_allow_html=True)
        
        # Display the processed content in a modern card
        with st.expander(f"📄 {get_text('view_content')}", expanded=True):
            st.markdown(f"""
            <div class="{theme_class}">
                <div style="background: var(--card-bg); padding: 15px; border-radius: 10px; border-left: 4px solid #6C63FF; max-height: 300px; overflow-y: auto; font-size: 0.9rem; line-height: 1.5;">
                </div>
            </div>
            """, unsafe_allow_html=True)
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
        """, unsafe_allow_html=True)
        
        # Create a card for analysis options
        st.markdown(f"""
        <div class="{theme_class}">
            <div style="background: var(--card-bg); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: var(--card-shadow);">
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        analysis_options = {
            "vi": [
                (get_text("resume_improvements"), "✏️", "Nhận gợi ý cải thiện CV của bạn hiệu quả hơn"),
                (get_text("job_keywords"), "🔍", "Trích xuất các kỹ năng và yêu cầu chính từ mô tả công việc"),
                (get_text("skills_gap"), "📊", "So sánh kỹ năng của bạn với yêu cầu công việc"),
                (get_text("custom_analysis"), "🧩", "Chỉ định tiêu chí phân tích riêng của bạn")
            ],
            "en": [
                (get_text("resume_improvements"), "✏️", "Get suggestions to enhance your resume's impact"),
                (get_text("job_keywords"), "🔍", "Extract key skills and requirements from job postings"),
                (get_text("skills_gap"), "📊", "Compare your skills with job requirements"),
                (get_text("custom_analysis"), "🧩", "Specify your own analysis criteria")
            ]
        }
        
        analysis_cols = st.columns(4)
        for i, (option, icon, desc) in enumerate(analysis_options[st.session_state.language]):
            with analysis_cols[i]:
                st.markdown(f"""
                <div class="{theme_class}">
                    <div style="text-align: center; cursor: pointer; padding: 10px 5px;">
                        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                        <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 5px;">{option}</div>
                        <div style="font-size: 0.75rem; opacity: 0.7; line-height: 1.2;">{desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        analysis_choices = [
            get_text("resume_improvements"), 
            get_text("job_keywords"), 
            get_text("skills_gap"), 
            get_text("custom_analysis")
        ]
        
        analysis_type = st.selectbox(
            get_text("select_analysis"),
            analysis_choices
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            generate_analysis = st.button(f"🔍 {get_text('analyze_document')}", use_container_width=True)
        
        if generate_analysis:
            # Set language for prompt
            language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
            analysis_prompt = f"Based on the following document: {st.session_state.file_content}, provide {analysis_type} {language_prompt}. Be detailed and specific."
            
            with st.spinner("Analyzing document..."):
                # Add language-specific system prompt
                language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
                messages = [
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"},
                    {"role": "user", "content": analysis_prompt}
                ]
                
                analysis_response = generate_response(st.session_state.gemini_model, messages)
                
                st.markdown(f"""
                <div class="{theme_class}">
                    <div style="background: var(--card-bg); padding: 25px; border-radius: 15px; margin-top: 25px; box-shadow: var(--card-shadow);">
                        <h3 style="color: var(--primary-color); margin-bottom: 20px; font-weight: 700; font-size: 1.3rem;">
                            {get_text("analyze_document")} - {analysis_type}
                        </h3>
                        <div style="line-height: 1.6;">
                """, unsafe_allow_html=True)
                st.markdown(analysis_response)
                st.markdown("</div></div></div>", unsafe_allow_html=True)
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
        """, unsafe_allow_html=True)

with tab3:
    st.markdown(f"""
    <div class="{theme_class}">
        <h2 class="gradient-text" style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px;">
            {get_text("tips_practice")}
        </h2>
        <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 20px; max-width: 650px;">
            {get_text("tips_desc_2")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    interview_options = {
        "vi": ["Phỏng Vấn Kỹ Thuật", "Phỏng Vấn Hành Vi", "Phỏng Vấn HR", "Phỏng Vấn Tình Huống"],
        "en": ["Technical Interview", "Behavioral Interview", "HR Interview", "Case Interview"]
    }
    
    interview_type = st.selectbox(
        get_text("select_interview"),
        interview_options[st.session_state.language]
    )
    
    job_role = st.text_input(get_text("job_role"))
    
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
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        get_tips = st.button(f"💡 {get_text('get_tips')}", use_container_width=True)
    
    if get_tips:
        # Set language for prompt
        language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
        tips_prompt = f"Provide comprehensive tips for a {interview_type} {language_prompt}"
        if job_role:
            tips_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating interview tips..."):
            # Add language-specific system prompt
            language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
            messages = [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"},
                {"role": "user", "content": tips_prompt}
            ]
            
            tips_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown(f"""
            <div class="{theme_class}">
                <div style="background: var(--card-bg); padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: var(--card-shadow);">
                    <h3 style="color: var(--primary-color); margin-bottom: 15px; font-weight: 700;">{get_text("get_tips")}</h3>
                    <div style="line-height: 1.6;">
            """, unsafe_allow_html=True)
            st.markdown(tips_response)
            st.markdown("</div></div></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="{theme_class}">
        <h3 style='margin: 30px 0 15px 0; font-size: 1.4rem;'>{get_text("practice_questions")}</h3>
        
        <div style="background: rgba(108, 99, 255, 0.05); padding: 10px 15px; border-radius: 8px; margin-bottom: 15px;">
            <p style="margin: 0; font-size: 0.9rem;">
                <strong>💡 Tip:</strong> {get_text("practice_tip")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        get_questions = st.button(f"🎯 {get_text('generate_questions')}", use_container_width=True)
    
    if get_questions:
        # Set language for prompt
        language_prompt = "in Vietnamese" if st.session_state.language == "vi" else "in English"
        questions_prompt = f"Generate 5 common {interview_type} questions {language_prompt}"
        if job_role:
            questions_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating practice questions..."):
            # Add language-specific system prompt
            language_instruction = "Trả lời bằng tiếng Việt." if st.session_state.language == "vi" else "Answer in English."
            messages = [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"},
                {"role": "user", "content": questions_prompt}
            ]
            
            questions_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown(f"""
            <div class="{theme_class}">
                <div style="background: var(--card-bg); padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: var(--card-shadow);">
                    <h3 style="color: var(--primary-color); margin-bottom: 15px; font-weight: 700;">{get_text("practice_questions")}</h3>
                    <div style="line-height: 1.6;">
            """, unsafe_allow_html=True)
            st.markdown(questions_response)
            st.markdown("</div></div></div>", unsafe_allow_html=True)

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
""", unsafe_allow_html=True)
