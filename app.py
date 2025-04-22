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
    # Initialize Gemini API
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDuz8BD10IzNM3qTfy9WCIXo2fZ1C7K2M8")
    st.session_state.gemini_model = initialize_gemini(api_key)

# Sidebar
with st.sidebar:
    st.title("Job Interview Assistant")
    
    # Theme toggle
    theme = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
    st.session_state.theme = "dark" if theme else "light"
    
    # Professional image
    st.image("https://images.unsplash.com/photo-1559523182-a284c3fb7cff", 
             caption="Professional Job Interview")
    
    # File uploader
    st.subheader("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload your resume, job description, or any relevant document",
        type=["txt", "pdf", "docx", "xlsx", "jpg", "jpeg", "png"]
    )
    
    if uploaded_file and st.button("Process Document"):
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
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.file_content = None
        st.success("Chat history cleared!")
    
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("• Resume analysis")
    st.markdown("• Mock interview preparation")
    st.markdown("• Job description analysis")
    st.markdown("• Personalized interview tips")

# Main area
st.title("3D Job Interview Assistant")

# Modern 3D interface image
cols = st.columns(3)
with cols[0]:
    st.image("https://images.unsplash.com/photo-1680536555364-9dd4a1ab313e", 
             caption="Modern 3D Interface")
with cols[1]:
    st.image("https://images.unsplash.com/photo-1507679799987-c73779587ccf", 
             caption="Interview Preparation")
with cols[2]:
    st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", 
             caption="Document Analysis")

st.markdown("---")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Chat", "Document Analysis", "Interview Tips"])

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
    st.header("Document Analysis")
    
    if st.session_state.file_content:
        st.success("Document loaded successfully!")
        
        # Display the processed content
        with st.expander("View Document Content", expanded=True):
            st.write(st.session_state.file_content)
        
        # Document analysis section
        st.subheader("Get Insights")
        analysis_type = st.selectbox(
            "What would you like to analyze?",
            ["Resume Improvements", "Job Description Keywords", "Skills Gap Analysis", "Custom Analysis"]
        )
        
        if st.button("Generate Analysis"):
            analysis_prompt = f"Based on the following document: {st.session_state.file_content}, provide {analysis_type}."
            
            with st.spinner("Analyzing document..."):
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": analysis_prompt}
                ]
                
                analysis_response = generate_response(st.session_state.gemini_model, messages)
                
                st.markdown("### Analysis Results")
                st.markdown(analysis_response)
    else:
        st.info("Please upload a document in the sidebar to analyze.")
        st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", 
                 caption="Upload a document to get started")

with tab3:
    st.header("Interview Tips & Practice")
    
    interview_type = st.selectbox(
        "Select Interview Type",
        ["Technical Interview", "Behavioral Interview", "HR Interview", "Case Interview"]
    )
    
    job_role = st.text_input("Enter Job Role (optional)")
    
    if st.button("Get Interview Tips"):
        tips_prompt = f"Provide comprehensive tips for a {interview_type}"
        if job_role:
            tips_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating interview tips..."):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": tips_prompt}
            ]
            
            tips_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown("### Interview Tips")
            st.markdown(tips_response)
    
    st.subheader("Practice Questions")
    if st.button("Generate Practice Questions"):
        questions_prompt = f"Generate 5 common {interview_type} questions"
        if job_role:
            questions_prompt += f" for a {job_role} position"
            
        with st.spinner("Generating practice questions..."):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": questions_prompt}
            ]
            
            questions_response = generate_response(st.session_state.gemini_model, messages)
            
            st.markdown("### Practice Questions")
            st.markdown(questions_response)

# Footer
st.markdown("---")
st.markdown("### Job Interview Assistant powered by Gemini API")
st.markdown("Upload your resume or job description for personalized assistance!")
