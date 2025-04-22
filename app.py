import streamlit as st
import os
import time
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

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "file_content" not in st.session_state:
    st.session_state.file_content = None

if "gemini_model" not in st.session_state:
    # Initialize Gemini API with provided key
    api_key = os.getenv("GEMINI_API_KEY")
    st.session_state.gemini_model = initialize_gemini(api_key)

# Enhanced sidebar with modern styling
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-weight: 800; font-size: 1.8rem; background: linear-gradient(90deg, #6C63FF, #FF6584); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Interview Coach AI
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme toggle with better styling
    st.markdown("<h3 style='margin-bottom: 10px; font-size: 1.2rem;'>Appearance</h3>", unsafe_allow_html=True)
    theme_col1, theme_col2 = st.columns([1, 4])
    with theme_col1:
        st.markdown("🌓")
    with theme_col2:
        theme = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
        st.session_state.theme = "dark" if theme else "light"
    
    # Professional image with rounded corners
    st.markdown("""
    <div style="margin: 15px 0; text-align: center;">
        <img src="https://images.unsplash.com/photo-1573497620053-ea5300f94f21" 
             style="border-radius: 12px; width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" 
             alt="Professional Job Interview">
        <p style="font-size: 0.8rem; margin-top: 8px; opacity: 0.7; text-align: center;">
            Prepare for your dream job
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader with enhanced styling
    st.markdown("<h3 style='margin: 20px 0 10px 0; font-size: 1.2rem;'>Upload Documents</h3>", unsafe_allow_html=True)
    
    # Custom hint box
    st.markdown("""
    <div style="background: rgba(108, 99, 255, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <p style="font-size: 0.85rem; margin: 0;">
            <strong>💡 Tip:</strong> Upload your resume, job description, or any related documents for personalized analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Select file to upload",
        type=["txt", "pdf", "docx", "xlsx", "jpg", "jpeg", "png"]
    )
    
    if uploaded_file and st.button("📄 Process Document", use_container_width=True):
        with st.spinner("Processing your document..."):
            file_content = process_file(uploaded_file)
            if file_content:
                st.session_state.file_content = file_content
                st.success("Document processed successfully!")
                
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
    if st.button("🧹 Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.file_content = None
        st.success("Chat history cleared!")
    
    st.markdown("---")
    
    # Features section with enhanced icons and styling
    st.markdown("<h3 style='margin-bottom: 15px; font-size: 1.2rem;'>Features</h3>", unsafe_allow_html=True)
    
    features = [
        ("📝 Resume analysis", "Get feedback on your resume"),
        ("🎯 Mock interview preparation", "Practice with realistic questions"),
        ("🔍 Job description analysis", "Understand key requirements"),
        ("💡 Personalized interview tips", "Tailored advice for your situation")
    ]
    
    for icon_feature, description in features:
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div style="font-weight: 500; margin-bottom: 3px;">{icon_feature}</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">{description}</div>
        </div>
        """, unsafe_allow_html=True)

# Main area with modern 3D design
st.markdown("""
<div style="text-align: center; padding: 20px; margin-bottom: 30px;">
    <h1 style="font-size: 3.2rem; font-weight: 800; margin-bottom: 10px; background: linear-gradient(90deg, #6C63FF, #FF6584); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        3D Job Interview Assistant
    </h1>
    <p style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 20px;">
        Your personal AI-powered guide to job interview success
    </p>
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
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Document Analysis", "🎯 Interview Tips"])

with tab1:
    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't show system messages to the user
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Ask me anything about job interviews..."):
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
                assistant_response = generate_response(
                    st.session_state.gemini_model, 
                    st.session_state.messages
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
    st.markdown("""
    <h2 style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px; background: linear-gradient(90deg, #6C63FF, #FF6584); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Document Analysis
    </h2>
    """, unsafe_allow_html=True)
    
    if st.session_state.file_content:
        st.markdown("""
        <div style="background-color: #E8F5E9; padding: 10px 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin: 0; display: flex; align-items: center;">
                <span style="background-color: #4CAF50; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; color: white;">✓</span>
                <span style="font-weight: 500;">Document loaded successfully!</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display the processed content in a modern card
        with st.expander("📄 View Document Content", expanded=True):
            st.markdown("""
            <div style="background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #6C63FF; max-height: 300px; overflow-y: auto; font-size: 0.9rem; line-height: 1.5;">
            """, unsafe_allow_html=True)
            st.markdown(f"```\n{st.session_state.file_content}\n```")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Document analysis section with enhanced UI
        st.markdown("""
        <div style="margin: 25px 0 15px 0;">
            <h3 style="font-weight: 600; font-size: 1.4rem; color: #1E2A3A;">
                💡 Get AI-Powered Insights
            </h3>
            <p style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 15px;">
                Select analysis type and generate personalized insights based on your document
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a card for analysis options
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
        """, unsafe_allow_html=True)
        
        analysis_options = [
            ("Resume Improvements", "✏️", "Get suggestions to enhance your resume's impact"),
            ("Job Description Keywords", "🔍", "Extract key skills and requirements from job postings"),
            ("Skills Gap Analysis", "📊", "Compare your skills with job requirements"),
            ("Custom Analysis", "🧩", "Specify your own analysis criteria")
        ]
        
        analysis_cols = st.columns(4)
        for i, (option, icon, desc) in enumerate(analysis_options):
            with analysis_cols[i]:
                st.markdown(f"""
                <div style="text-align: center; cursor: pointer; padding: 10px 5px;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                    <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 5px;">{option}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; line-height: 1.2;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        analysis_type = st.selectbox(
            "Select analysis type",
            ["Resume Improvements", "Job Description Keywords", "Skills Gap Analysis", "Custom Analysis"]
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            generate_analysis = st.button("🔍 Analyze Document", use_container_width=True)
        
        if generate_analysis:
            analysis_prompt = f"Based on the following document: {st.session_state.file_content}, provide {analysis_type}."
            
            with st.spinner("Analyzing document..."):
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": analysis_prompt}
                ]
                
                analysis_response = generate_response(st.session_state.gemini_model, messages)
                
                st.markdown("""
                <div style="background: white; padding: 25px; border-radius: 15px; margin-top: 25px; box-shadow: 0 8px 25px rgba(0,0,0,0.08);">
                    <h3 style="color: #6C63FF; margin-bottom: 20px; font-weight: 700; font-size: 1.3rem;">Analysis Results</h3>
                    <div style="line-height: 1.6;">
                """, unsafe_allow_html=True)
                st.markdown(analysis_response)
                st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        # Empty state with 3D-style illustration
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
            <img src="https://images.unsplash.com/photo-1586281380349-632531db7ed4" style="width: 250px; border-radius: 15px; margin-bottom: 20px;" alt="Upload a document">
            <h3 style="margin-bottom: 10px; font-weight: 600; color: #1E2A3A;">No Document Uploaded Yet</h3>
            <p style="opacity: 0.7; max-width: 450px; margin: 0 auto 15px auto; line-height: 1.5;">
                Upload a resume, job description, or any relevant document using the sidebar to get personalized analysis and insights
            </p>
            <div style="background: rgba(108, 99, 255, 0.1); padding: 10px 15px; border-radius: 8px; display: inline-block; margin-top: 10px;">
                <p style="margin: 0; font-size: 0.85rem; text-align: left;">
                    <strong>💡 Tip:</strong> Try uploading different document types including text, PDF, DOCX, or even images
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <h2 style="font-weight: 700; font-size: 1.8rem; margin-bottom: 20px; background: linear-gradient(90deg, #6C63FF, #FF6584); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Interview Tips & Practice
    </h2>
    <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 20px; max-width: 650px;">
        Get personalized interview preparation guidance for different interview types. Select your interview type below and optionally enter your target job role for more tailored advice.
    </p>
    """, unsafe_allow_html=True)
    
    interview_type = st.selectbox(
        "Select Interview Type",
        ["Technical Interview", "Behavioral Interview", "HR Interview", "Case Interview"]
    )
    
    job_role = st.text_input("Enter Job Role (optional)")
    
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
        get_tips = st.button("💡 Get Tips", use_container_width=True)
    
    if get_tips:
        tips_prompt = f"Provide comprehensive tips for a {interview_type}"
        if job_role:
            tips_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating interview tips..."):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": tips_prompt}
            ]
            
            tips_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);">
                <h3 style="color: #6C63FF; margin-bottom: 15px; font-weight: 700;">Interview Tips</h3>
                <div style="line-height: 1.6;">
            """, unsafe_allow_html=True)
            st.markdown(tips_response)
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin: 30px 0 15px 0; font-size: 1.4rem;'>Practice Questions</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(108, 99, 255, 0.05); padding: 10px 15px; border-radius: 8px; margin-bottom: 15px;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>💡 Tip:</strong> Practice with real interview questions for your specific role and interview type.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        get_questions = st.button("🎯 Generate Questions", use_container_width=True)
    
    if get_questions:
        questions_prompt = f"Generate 5 common {interview_type} questions"
        if job_role:
            questions_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating practice questions..."):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": questions_prompt}
            ]
            
            questions_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);">
                <h3 style="color: #6C63FF; margin-bottom: 15px; font-weight: 700;">Practice Questions</h3>
                <div style="line-height: 1.6;">
            """, unsafe_allow_html=True)
            st.markdown(questions_response)
            st.markdown("</div></div>", unsafe_allow_html=True)

# Enhanced 3D footer
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(to right, #f7f9fc, #eef1f8); padding: 20px; border-radius: 15px; margin-top: 30px; box-shadow: 0 -5px 20px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h3 style="margin: 0; background: linear-gradient(90deg, #6C63FF, #FF6584); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.4rem; font-weight: 700;">
                3D Job Interview Assistant
            </h3>
            <p style="margin: 8px 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                Powered by Gemini 2.0 API | Your personal interview coach
            </p>
        </div>
        <div>
            <div style="background: rgba(108, 99, 255, 0.1); padding: 10px 15px; border-radius: 8px; display: inline-block;">
                <p style="margin: 0; font-size: 0.85rem;">
                    <strong>💡 Pro Tip:</strong> Upload your resume for personalized interview preparation
                </p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
