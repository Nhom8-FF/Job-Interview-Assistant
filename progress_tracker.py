import streamlit as st
import pandas as pd
import numpy as np
import time
import re
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("progress_tracker")

# Try to import the font utils
try:
    from fonts.font_utils import find_font
except ImportError:
    # Fallback function if module can't be imported
    def find_font(font_name):
        """Simple fallback function for font finding"""
        # Try local directory first
        local_path = os.path.join(os.path.dirname(__file__), "fonts", font_name)
        if os.path.exists(local_path):
            return local_path
            
        # Try matplotlib fonts
        try:
            import matplotlib
            mpl_font_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
            mpl_font_path = os.path.join(mpl_font_dir, font_name)
            if os.path.exists(mpl_font_path):
                return mpl_font_path
        except:
            pass
            
        return None

def extract_scores_from_feedback(feedback, language="vi"):
    """
    Trích xuất điểm số từ phản hồi phỏng vấn
    """
    # Ghi nhật ký để debug
    print("=== DEBUG: FEEDBACK CONTENT ===")
    print(feedback)
    print("=== END FEEDBACK CONTENT ===")
    
    overall_score = 0
    technical_score = 0
    communication_score = 0
    problem_solving_score = 0
    leadership_score = 0
    
    # Tìm điểm tổng thể
    if language == "vi":
        overall_pattern = r"(?:điểm\s*(?:số|đánh giá|tổng)(?:\s*(?:tổng thể|chung|cuối cùng))?|đánh giá tổng thể|tổng\s*(?:điểm|số)|điểm\s*tổng\s*kết)[:\s]*(\d+)[\s/]*10"
    else:
        overall_pattern = r"(?:overall\s*(?:score|assessment|rating|evaluation|grade|mark|result)|final\s*(?:score|assessment|rating|evaluation|grade|mark|result)|total\s*(?:score|assessment|rating)|assessment\s*(?:score|result)|evaluation\s*(?:score|result)|score\s*overall)[:\s]*(\d+)[\s/]*10"
    
    overall_match = re.search(overall_pattern, feedback.lower())
    if overall_match:
        overall_score = int(overall_match.group(1))
        print(f"Found overall score: {overall_score}")
    else:
        # Thử thêm một biểu thức chính quy đơn giản hơn nếu không tìm thấy kết quả
        simple_pattern = r"(\d+)\s*/\s*10"
        simple_matches = re.findall(simple_pattern, feedback.lower())
        if simple_matches and len(simple_matches) > 0:
            # Lấy số đầu tiên tìm thấy
            overall_score = int(simple_matches[0])
            print(f"Found overall score using simple pattern: {overall_score}")
        else:
            print("Overall score not found")
    
    # Tìm điểm kỹ thuật
    if language == "vi":
        technical_pattern = r"(?:kỹ\s*thuật|technical)[:\s]*(\d+)[\s/]*10"
    else:
        technical_pattern = r"(?:technical\s*(?:skills?|knowledge|competency))[:\s]*(\d+)[\s/]*10"
    
    technical_match = re.search(technical_pattern, feedback.lower())
    if technical_match:
        technical_score = int(technical_match.group(1))
        print(f"Found technical score: {technical_score}")
    elif overall_score > 0:  # Nếu không tìm thấy, ước tính dựa trên điểm tổng thể
        technical_score = overall_score
    
    # Tìm điểm giao tiếp
    if language == "vi":
        communication_pattern = r"(?:giao\s*tiếp|communication|trình\s*bày)[:\s]*(\d+)[\s/]*10"
    else:
        communication_pattern = r"(?:communication\s*(?:skills?|ability))[:\s]*(\d+)[\s/]*10"
    
    communication_match = re.search(communication_pattern, feedback.lower())
    if communication_match:
        communication_score = int(communication_match.group(1))
        print(f"Found communication score: {communication_score}")
    elif overall_score > 0:  # Nếu không tìm thấy, ước tính dựa trên điểm tổng thể
        communication_score = overall_score
    
    # Tìm điểm giải quyết vấn đề
    if language == "vi":
        problem_solving_pattern = r"(?:giải\s*quyết\s*vấn\s*đề|problem\s*solving|khả\s*năng\s*xử\s*lý)[:\s]*(\d+)[\s/]*10"
    else:
        problem_solving_pattern = r"(?:problem[\s-]*solving\s*(?:skills?|ability))[:\s]*(\d+)[\s/]*10"
    
    problem_solving_match = re.search(problem_solving_pattern, feedback.lower())
    if problem_solving_match:
        problem_solving_score = int(problem_solving_match.group(1))
        print(f"Found problem solving score: {problem_solving_score}")
    elif overall_score > 0:  # Nếu không tìm thấy, ước tính dựa trên điểm tổng thể
        problem_solving_score = overall_score
    
    # Tìm điểm lãnh đạo
    if language == "vi":
        leadership_pattern = r"(?:lãnh\s*đạo|leadership|quản\s*lý)[:\s]*(\d+)[\s/]*10"
    else:
        leadership_pattern = r"(?:leadership\s*(?:skills?|ability|quality))[:\s]*(\d+)[\s/]*10"
    
    leadership_match = re.search(leadership_pattern, feedback.lower())
    if leadership_match:
        leadership_score = int(leadership_match.group(1))
        print(f"Found leadership score: {leadership_score}")
    elif overall_score > 0:  # Nếu không tìm thấy, ước tính dựa trên điểm tổng thể
        leadership_score = max(1, int(overall_score * 0.8))  # Giả định điểm lãnh đạo thấp hơn tổng thể
    
    # Nếu điểm tổng thể không được tìm thấy nhưng các điểm thành phần có, hãy tính trung bình
    if overall_score == 0 and (technical_score > 0 or communication_score > 0 or problem_solving_score > 0 or leadership_score > 0):
        valid_scores = []
        if technical_score > 0:
            valid_scores.append(technical_score)
        if communication_score > 0:
            valid_scores.append(communication_score)
        if problem_solving_score > 0:
            valid_scores.append(problem_solving_score)
        if leadership_score > 0:
            valid_scores.append(leadership_score)
        
        if valid_scores:
            overall_score = sum(valid_scores) // len(valid_scores)
            print(f"Calculated overall score from component scores: {overall_score}")
    
    return {
        "overall": overall_score,
        "technical": technical_score,
        "communication": communication_score,
        "problem_solving": problem_solving_score,
        "leadership": leadership_score,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": time.time()
    }

def save_interview_results(scores, job_role=None, interview_type=None):
    """
    Lưu kết quả phỏng vấn vào lịch sử
    """
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []
    
    # Thêm thông tin về phỏng vấn
    interview_data = scores.copy()
    interview_data["job_role"] = job_role if job_role else "Unknown"
    interview_data["interview_type"] = interview_type if interview_type else "Unknown"
    
    # Lưu vào lịch sử
    st.session_state.interview_history.append(interview_data)
    
    # Cập nhật tiến trình kỹ năng
    for skill in ["technical", "communication", "problem_solving", "leadership", "overall"]:
        if skill in scores and scores[skill] > 0:
            st.session_state.skills_progress[skill].append({
                "score": scores[skill],
                "date": scores["date"],
                "timestamp": scores["timestamp"]
            })

def create_progress_chart():
    """
    Tạo biểu đồ tiến trình kỹ năng theo thời gian
    """
    if not st.session_state.skills_progress["overall"]:
        return None
    
    # Tạo DataFrame từ dữ liệu tiến trình
    data = {
        "Date": [],
        "Technical": [],
        "Communication": [],
        "Problem Solving": [],
        "Leadership": [],
        "Overall": []
    }
    
    # Lấy thời gian từ điểm overall
    timestamps = [entry["timestamp"] for entry in st.session_state.skills_progress["overall"]]
    dates = [entry["date"] for entry in st.session_state.skills_progress["overall"]]
    
    for i, (timestamp, date) in enumerate(zip(timestamps, dates)):
        data["Date"].append(date)
        
        for skill, display_name in [
            ("technical", "Technical"),
            ("communication", "Communication"),
            ("problem_solving", "Problem Solving"),
            ("leadership", "Leadership"),
            ("overall", "Overall")
        ]:
            # Tìm điểm gần nhất với timestamp
            closest_entry = None
            min_diff = float('inf')
            
            for entry in st.session_state.skills_progress[skill]:
                diff = abs(entry["timestamp"] - timestamp)
                if diff < min_diff:
                    min_diff = diff
                    closest_entry = entry
            
            if closest_entry:
                data[display_name].append(closest_entry["score"])
            else:
                data[display_name].append(0)
    
    # Tạo DataFrame
    df = pd.DataFrame(data)
    
    # Tạo biểu đồ
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Technical"], marker='o', label="Technical")
    plt.plot(df["Date"], df["Communication"], marker='s', label="Communication")
    plt.plot(df["Date"], df["Problem Solving"], marker='^', label="Problem Solving")
    plt.plot(df["Date"], df["Leadership"], marker='D', label="Leadership")
    plt.plot(df["Date"], df["Overall"], marker='*', linewidth=2, label="Overall")
    
    plt.title("Interview Performance Progress", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Score (out of 10)", fontsize=12)
    plt.ylim(0, 10.5)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Lưu biểu đồ vào buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    return buf

def get_pdf_download_link(content, filename="interview_progress_report.pdf"):
    """
    Tạo link tải xuống file PDF
    """
    b64 = base64.b64encode(content).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 Tải báo cáo PDF</a>'
    return href

def generate_pdf_report(gemini_model, language="vi"):
    """
    Tạo báo cáo PDF về tiến trình phỏng vấn
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Dictionary to store fonts
    fonts = {
        'regular': 'Helvetica', 
        'bold': 'Helvetica-Bold'
    }
    
    # Try to register Unicode-compatible fonts
    try:
        # Try to find DejaVuSans fonts
        dejavu_regular = find_font('DejaVuSans.ttf')
        dejavu_bold = find_font('DejaVuSans-Bold.ttf')
        
        logger.info(f"Found DejaVu fonts: {dejavu_regular} and {dejavu_bold}")
        
        if dejavu_regular and os.path.exists(dejavu_regular):
            pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_regular))
            fonts['regular'] = 'DejaVuSans'
            logger.info("Successfully registered DejaVuSans font")
        
        if dejavu_bold and os.path.exists(dejavu_bold):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold))
            fonts['bold'] = 'DejaVuSans-Bold'
            logger.info("Successfully registered DejaVuSans-Bold font")
            
    except Exception as e:
        logger.warning(f"Error registering DejaVu fonts: {e}")
        logger.warning("Using default Helvetica fonts")
    
    # Tạo buffer để lưu PDF
    buffer = io.BytesIO()
    
    # Tạo document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Tạo style với font Unicode
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontName=fonts['bold'],
        fontSize=18
    )
    
    heading1_style = ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontName=fonts['bold'],
        fontSize=14
    )
    
    normal_style = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontName=fonts['regular'],
        fontSize=10
    )
    
    # Tạo tiêu đề báo cáo
    title = "Interview Progress Report" if language == "en" else "Báo Cáo Tiến Trình Phỏng Vấn"
    
    # Các phần tử trong báo cáo
    elements = []
    
    # Thêm tiêu đề
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Thêm ngày tạo báo cáo
    date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}" if language == "en" else f"Ngày tạo: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    elements.append(Paragraph(date_text, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Thêm tóm tắt tiến trình
    if st.session_state.interview_history:
        summary_title = "Progress Summary" if language == "en" else "Tóm Tắt Tiến Trình"
        elements.append(Paragraph(summary_title, heading1_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Tính điểm trung bình và tiến bộ
        first_scores = st.session_state.interview_history[0]
        last_scores = st.session_state.interview_history[-1]
        
        # Bảng tiến trình
        progress_data = [
            ["Skill", "First Score", "Current Score", "Improvement"] if language == "en" else ["Kỹ năng", "Điểm ban đầu", "Điểm hiện tại", "Tiến bộ"]
        ]
        
        skills = {
            "overall": "Overall" if language == "en" else "Tổng thể",
            "technical": "Technical" if language == "en" else "Kỹ thuật",
            "communication": "Communication" if language == "en" else "Giao tiếp",
            "problem_solving": "Problem Solving" if language == "en" else "Giải quyết vấn đề",
            "leadership": "Leadership" if language == "en" else "Lãnh đạo"
        }
        
        for skill_key, skill_name in skills.items():
            first = first_scores.get(skill_key, 0)
            last = last_scores.get(skill_key, 0)
            improvement = last - first
            
            # Định dạng chuỗi tiến bộ
            if improvement > 0:
                improvement_str = f"+{improvement}"
            else:
                improvement_str = str(improvement)
                
            progress_data.append([skill_name, str(first), str(last), improvement_str])
        
        # Tạo bảng
        table = Table(progress_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), fonts['bold']),
            ('FONTNAME', (0, 1), (-1, -1), fonts['regular']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Thêm biểu đồ tiến trình
        chart_buffer = create_progress_chart()
        if chart_buffer:
            chart_title = "Progress Chart" if language == "en" else "Biểu Đồ Tiến Trình"
            elements.append(Paragraph(chart_title, heading1_style))
            elements.append(Spacer(1, 0.15*inch))
            
            img = Image(chart_buffer, width=6*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Thêm gợi ý cải thiện từ AI
        if len(st.session_state.interview_history) >= 2:
            suggestion_title = "AI Improvement Suggestions" if language == "en" else "Gợi Ý Cải Thiện Từ AI"
            elements.append(Paragraph(suggestion_title, heading1_style))
            elements.append(Spacer(1, 0.15*inch))
            
            # Tạo prompt cho AI để phân tích tiến trình
            if language == "en":
                prompt = f"""Analyze the candidate's interview progress:
- First interview scores: {first_scores}
- Current scores: {last_scores}

Provide specific suggestions for improvement in each skill area.
Keep your response concise and actionable.
"""
            else:
                prompt = f"""Phân tích tiến trình phỏng vấn của ứng viên:
- Điểm phỏng vấn đầu tiên: {first_scores}
- Điểm hiện tại: {last_scores}

Đưa ra những gợi ý cụ thể để cải thiện từng lĩnh vực kỹ năng.
Giữ phản hồi của bạn ngắn gọn và có thể thực hiện được.
"""
            
            # Lấy gợi ý từ AI
            messages = [
                {"role": "system", "content": "You are an interview coach analyzing progress"},
                {"role": "user", "content": prompt}
            ]
            
            from gemini_helper import generate_response
            ai_suggestions = generate_response(gemini_model, messages)
            
            # Thêm gợi ý vào báo cáo
            elements.append(Paragraph(ai_suggestions, normal_style))
            elements.append(Spacer(1, 0.25*inch))
    else:
        no_data = "No interview data available yet" if language == "en" else "Chưa có dữ liệu phỏng vấn"
        elements.append(Paragraph(no_data, normal_style))
    
    # Xây dựng PDF
    doc.build(elements)
    
    # Lấy nội dung PDF
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def send_email_report(email, pdf_content, language="vi"):
    """
    Gửi báo cáo qua email
    """
    try:
        import smtplib
        import os
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        # Kiểm tra email hợp lệ
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email address" if language == "en" else "Địa chỉ email không hợp lệ"
        
        # Lấy thông tin đăng nhập email từ biến môi trường hoặc config
        # Trong môi trường thực tế, bạn nên lưu thông tin này trong biến môi trường bảo mật
        try:
            # Thử lấy thông tin từ config
            from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM
        except ImportError:
            # Nếu không có file config, sử dụng giá trị mặc định cho demo
            EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
            EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
            EMAIL_USER = os.environ.get("EMAIL_USER", "")
            EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
            EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
        
        # Kiểm tra nếu chưa cấu hình thông tin email
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logger.error("Email credentials not configured. Please set up EMAIL_USER and EMAIL_PASSWORD.")
            return False, "Email not configured" if language == "en" else "Chưa cấu hình email"
        
        # Tạo message
        msg = MIMEMultipart()
        
        # Thiết lập thông tin email
        msg['From'] = EMAIL_FROM or EMAIL_USER
        msg['To'] = email
        
        if language == "en":
            msg['Subject'] = 'Your Interview Progress Report'
            body = 'Please find attached your interview progress report.\n\nThank you for using our Interview Assistant.'
        else:
            msg['Subject'] = 'Báo Cáo Tiến Trình Phỏng Vấn Của Bạn'
            body = 'Vui lòng xem báo cáo tiến trình phỏng vấn đính kèm.\n\nCảm ơn bạn đã sử dụng Trợ Lý Phỏng Vấn của chúng tôi.'
        
        # Thêm body
        msg.attach(MIMEText(body, 'plain'))
        
        # Thêm file PDF đính kèm
        attachment = MIMEApplication(pdf_content)
        attachment.add_header('Content-Disposition', 'attachment', 
                             filename="interview_progress_report.pdf")
        msg.attach(attachment)
        
        # Kết nối đến server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Bảo mật kết nối
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Gửi email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        
        # Đóng kết nối
        server.quit()
        
        logger.info(f"Email sent successfully to {email}")
        return True, "Email sent successfully" if language == "en" else "Đã gửi email thành công"
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False, f"Error sending email: {str(e)}" if language == "en" else f"Lỗi khi gửi email: {str(e)}"

def display_progress_tracker(gemini_model):
    """
    Hiển thị trang theo dõi tiến trình
    """
    language = st.session_state.language
    theme_class = "dark-theme" if st.session_state.theme == "dark" else "light-theme"
    
    # CSS tùy chỉnh cho trang progress tracker
    progress_tracker_css = """
    <style>
    .progress-section {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-color);
        transition: transform 0.3s ease;
    }
    .progress-section:hover {
        transform: translateY(-5px);
    }
    .progress-title {
        color: var(--primary-color);
        font-size: 1.4rem;
        margin-bottom: 15px;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 10px;
    }
    .progress-description {
        margin-bottom: 20px;
        opacity: 0.8;
    }
    .data-card {
        background-color: var(--secondary-bg);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .export-options {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-top: 15px;
    }
    .download-button {
        display: inline-block;
        background-color: var(--primary-color);
        color: white !important;
        padding: 10px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(108, 99, 255, 0.3);
    }
    .chart-container {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-color);
    }
    </style>
    """
    st.markdown(progress_tracker_css, unsafe_allow_html=True)
    
    # Tiêu đề
    if language == "vi":
        title_text = "Theo Dõi Tiến Trình"
        description = "Phân tích sự tiến bộ của bạn qua các buổi phỏng vấn mô phỏng"
        no_data_text = "Bạn chưa có dữ liệu phỏng vấn nào. Hãy hoàn thành ít nhất một cuộc phỏng vấn mô phỏng để xem tiến trình của bạn."
        chart_title = "Biểu Đồ Tiến Trình"
        history_title = "Lịch Sử Phỏng Vấn"
        export_title = "Xuất Báo Cáo"
        pdf_button_text = "Tạo báo cáo PDF"
        pdf_generating = "Đang tạo PDF..."
        pdf_success = "Đã tạo PDF thành công!"
        email_title = "Chia Sẻ Qua Email"
        email_placeholder = "Nhập địa chỉ email của bạn"
        email_button = "Gửi báo cáo qua email"
        setup_email_text = "Cấu hình email"
        email_note = "Chưa cấu hình email? Hãy thiết lập thông tin email trước khi gửi báo cáo."
        email_sending = "Đang gửi email..."
        email_error = "Email chưa được cấu hình. Vui lòng thiết lập thông tin email trước."
        setup_command_note = "Sao chép và chạy lệnh trên trong terminal để mở trang cấu hình email"
    else:
        title_text = "Progress Tracker"
        description = "Analyze your progress across multiple mock interviews"
        no_data_text = "You don't have any interview data yet. Complete at least one mock interview to see your progress."
        chart_title = "Progress Chart"
        history_title = "Interview History"
        export_title = "Export Report"
        pdf_button_text = "Generate PDF Report"
        pdf_generating = "Generating PDF..."
        pdf_success = "PDF generated successfully!"
        email_title = "Share via Email"
        email_placeholder = "Enter your email address"
        email_button = "Send report via email"
        setup_email_text = "Setup Email"
        email_note = "Email not configured? Set up your email settings before sending reports."
        email_sending = "Sending email..."
        email_error = "Email not configured. Please set up your email settings first."
        setup_command_note = "Copy and run the command above in terminal to open email setup page"
    
    # Hiển thị tiêu đề và mô tả chính
    st.markdown(f"<h1>{title_text}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='progress-description {theme_class}'>{description}</p>", unsafe_allow_html=True)
    
    # Kiểm tra xem có dữ liệu phỏng vấn hay không
    if not st.session_state.interview_history:
        st.info(no_data_text)
        return
    
    # Hiển thị biểu đồ tiến trình
    st.markdown(f"<div class='progress-section {theme_class}'><h2 class='progress-title'>{chart_title}</h2>", unsafe_allow_html=True)
    
    chart_buffer = create_progress_chart()
    if chart_buffer:
        # Tùy chỉnh màu sắc biểu đồ dựa trên theme
        if st.session_state.theme == "dark":
            plt.style.use('dark_background')
            plt.rcParams['axes.facecolor'] = '#313244'
            plt.rcParams['figure.facecolor'] = '#313244'
            
        st.image(chart_buffer, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Hiển thị bảng tiến trình
    st.markdown(f"<div class='progress-section {theme_class}'><h2 class='progress-title'>{history_title}</h2>", unsafe_allow_html=True)
    
    # Tạo DataFrame từ lịch sử phỏng vấn
    history_data = []
    
    for interview in st.session_state.interview_history:
        history_data.append({
            "Date": interview.get("date", "Unknown"),
            "Job Role": interview.get("job_role", "Unknown"),
            "Interview Type": interview.get("interview_type", "Unknown"),
            "Overall": interview.get("overall", 0),
            "Technical": interview.get("technical", 0),
            "Communication": interview.get("communication", 0),
            "Problem Solving": interview.get("problem_solving", 0),
            "Leadership": interview.get("leadership", 0)
        })
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tạo báo cáo PDF
    st.markdown(f"<div class='progress-section {theme_class}'><h2 class='progress-title'>{export_title}</h2>", unsafe_allow_html=True)
    
    if st.button(pdf_button_text, key="generate_pdf_btn", use_container_width=False):
        with st.spinner(pdf_generating):
            pdf_content = generate_pdf_report(gemini_model, language)
            st.success(pdf_success)
            
            # Hiển thị link tải xuống
            st.markdown(f"<div class='export-options'>{get_pdf_download_link(pdf_content)}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chia sẻ qua email
    st.markdown(f"<div class='progress-section {theme_class}'><h2 class='progress-title'>{email_title}</h2>", unsafe_allow_html=True)
    
    # Kiểm tra xem đã cấu hình email chưa
    try:
        from config import EMAIL_USER, EMAIL_PASSWORD
        has_email_config = bool(EMAIL_USER and EMAIL_PASSWORD)
    except (ImportError, AttributeError):
        has_email_config = False
    
    # Hiển thị thông báo nếu chưa cấu hình
    if not has_email_config:
        st.warning(email_note)
        if st.button(setup_email_text, key="setup_email_btn"):
            # Mở trang cấu hình email trong tab mới
            js = f"""
            <script>
            window.open('http://localhost:8501/email_setup.py', '_blank');
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
            
            # Hiển thị hướng dẫn chạy
            setup_command = "streamlit run email_setup.py"
            st.code(setup_command, language="bash")
            st.info(setup_command_note)
    
    email = st.text_input(email_placeholder, key="email_input")
    
    if email and st.button(email_button, key="send_email_btn"):
        if not has_email_config:
            st.error(email_error)
        else:
            with st.spinner(email_sending):
                pdf_content = generate_pdf_report(gemini_model, language)
                success, message = send_email_report(email, pdf_content, language)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                    
                    # Hiển thị nút cấu hình email nếu gặp lỗi
                    if st.button(setup_email_text + " ⚙️", key="setup_email_error_btn"):
                        setup_command = "streamlit run email_setup.py"
                        st.code(setup_command, language="bash")
                        st.info(setup_command_note)
                        
    st.markdown("</div>", unsafe_allow_html=True) 