import streamlit as st
import os
import re

st.set_page_config(page_title="Email Setup", page_icon="✉️")

st.title("Cấu hình Email")
st.markdown("""
Cấu hình thông tin email để gửi báo cáo tiến trình phỏng vấn.

**Lưu ý:**
- Nếu sử dụng Gmail, bạn cần tạo "App Password" thay vì sử dụng mật khẩu chính của tài khoản
- [Xem hướng dẫn tạo App Password tại đây](https://support.google.com/accounts/answer/185833)
- Thông tin email sẽ được lưu vào file `config.py` trong thư mục gốc của ứng dụng
""")

# Đọc cấu hình hiện tại
config_file = "config.py"
config_content = ""
email_host = "smtp.gmail.com"
email_port = 587
email_user = ""
email_password = ""
email_from = ""

try:
    with open(config_file, "r") as f:
        config_content = f.read()
    
    # Trích xuất các giá trị từ file cấu hình
    host_match = re.search(r'EMAIL_HOST\s*=\s*[\'"](.+?)[\'"]', config_content)
    if host_match:
        email_host = host_match.group(1)
        
    port_match = re.search(r'EMAIL_PORT\s*=\s*(\d+)', config_content)
    if port_match:
        email_port = int(port_match.group(1))
        
    user_match = re.search(r'EMAIL_USER\s*=\s*[\'"](.+?)[\'"]', config_content)
    if user_match:
        email_user = user_match.group(1)
        
    from_match = re.search(r'EMAIL_FROM\s*=\s*[\'"](.+?)[\'"]', config_content)
    if from_match:
        email_from = from_match.group(1)
except Exception as e:
    st.warning(f"Không thể đọc file cấu hình: {e}")

# Form nhập thông tin
with st.form("email_config"):
    col1, col2 = st.columns(2)
    
    with col1:
        new_email_host = st.text_input("SMTP Server", value=email_host, 
                                      help="Ví dụ: smtp.gmail.com cho Gmail")
        new_email_port = st.number_input("Port", value=email_port, min_value=1, max_value=65535,
                                       help="587 cho TLS, 465 cho SSL")
    
    with col2:
        new_email_user = st.text_input("Email", value=email_user, 
                                      help="Địa chỉ email dùng để đăng nhập")
        new_email_password = st.text_input("Mật khẩu ứng dụng", type="password",
                                         help="App Password nếu sử dụng Gmail")
    
    new_email_from = st.text_input("Email người gửi (tùy chọn)", value=email_from,
                                 help="Để trống sẽ sử dụng địa chỉ email đăng nhập")
    
    submit = st.form_submit_button("Lưu cấu hình")
    
    if submit:
        # Kiểm tra thông tin nhập
        if not new_email_host or not new_email_user or not new_email_password:
            st.error("Vui lòng điền đầy đủ thông tin SMTP Server, Email và Mật khẩu")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", new_email_user):
            st.error("Địa chỉ email không hợp lệ")
        else:
            try:
                # Đọc toàn bộ file config
                with open(config_file, "r") as f:
                    config_content = f.read()
                
                # Cập nhật các giá trị
                config_content = re.sub(r'EMAIL_HOST\s*=\s*.*', f'EMAIL_HOST = "{new_email_host}"', config_content)
                config_content = re.sub(r'EMAIL_PORT\s*=\s*.*', f'EMAIL_PORT = {new_email_port}', config_content)
                config_content = re.sub(r'EMAIL_USER\s*=\s*.*', f'EMAIL_USER = "{new_email_user}"', config_content)
                config_content = re.sub(r'EMAIL_PASSWORD\s*=\s*.*', f'EMAIL_PASSWORD = "{new_email_password}"', config_content)
                config_content = re.sub(r'EMAIL_FROM\s*=\s*.*', f'EMAIL_FROM = "{new_email_from}"', config_content)
                
                # Ghi lại file
                with open(config_file, "w") as f:
                    f.write(config_content)
                
                st.success("Đã lưu cấu hình email thành công!")
                
                # Hiển thị button kiểm tra
                st.session_state.config_saved = True
            except Exception as e:
                st.error(f"Lỗi khi lưu cấu hình: {e}")

# Phần kiểm tra kết nối
if st.session_state.get("config_saved", False) or (email_user and email_password):
    st.subheader("Kiểm tra kết nối")
    
    test_email = st.text_input("Nhập email để kiểm tra", 
                               help="Nhập email mà bạn muốn gửi thử nghiệm")
    
    if st.button("Kiểm tra kết nối") and test_email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", test_email):
            st.error("Địa chỉ email không hợp lệ")
        else:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                
                # Lấy thông tin từ config mới nhất
                try:
                    from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM
                except ImportError:
                    # Sử dụng giá trị từ form
                    EMAIL_HOST = new_email_host
                    EMAIL_PORT = new_email_port
                    EMAIL_USER = new_email_user
                    EMAIL_PASSWORD = new_email_password
                    EMAIL_FROM = new_email_from or new_email_user
                
                with st.spinner("Đang kết nối và gửi email thử nghiệm..."):
                    # Tạo email
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_FROM or EMAIL_USER
                    msg['To'] = test_email
                    msg['Subject'] = 'Kiểm tra kết nối email từ InterviewAI'
                    
                    body = '''
                    Đây là email kiểm tra từ ứng dụng InterviewAI.
                    
                    Nếu bạn nhận được email này, cấu hình email của bạn đã hoạt động!
                    
                    Cảm ơn bạn đã sử dụng ứng dụng của chúng tôi.
                    '''
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Kết nối và gửi
                    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                    server.starttls()
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    server.quit()
                
                st.success(f"✅ Đã gửi email thử nghiệm thành công đến {test_email}!")
            except Exception as e:
                st.error(f"❌ Lỗi khi gửi email: {str(e)}")
                
                # Hiển thị gợi ý nếu là Gmail
                if "gmail" in email_host.lower():
                    st.error("""
                    **Nếu bạn đang sử dụng Gmail:**
                    1. Hãy chắc chắn bạn đã tạo [App Password](https://support.google.com/accounts/answer/185833)
                    2. Kiểm tra xem đã bật "Less secure app access" nếu không dùng 2FA
                    3. Đảm bảo không có captcha hoặc xác minh bảo mật nào đang chặn đăng nhập
                    """)
                    
# Thêm hướng dẫn sử dụng
st.markdown("""
---
### Hướng dẫn cấu hình email cho các nhà cung cấp phổ biến

**Gmail:**
- SMTP Server: smtp.gmail.com
- Port: 587
- Bắt buộc phải sử dụng App Password nếu bạn đã bật xác thực 2 yếu tố
- [Hướng dẫn tạo App Password](https://support.google.com/accounts/answer/185833)

**Outlook/Hotmail:**
- SMTP Server: smtp-mail.outlook.com
- Port: 587

**Yahoo Mail:**
- SMTP Server: smtp.mail.yahoo.com
- Port: 587
- Bạn cần tạo App Password
- [Hướng dẫn tạo App Password Yahoo](https://help.yahoo.com/kb/account/SLN15241.html)
""")

if __name__ == "__main__":
    # Hiển thị thông tin bổ sung khi chạy trực tiếp
    st.sidebar.title("Giới thiệu")
    st.sidebar.info("""
    Công cụ này giúp bạn cấu hình thông tin email để có thể gửi báo cáo tiến trình phỏng vấn từ ứng dụng InterviewAI.
    
    Sau khi cấu hình, bạn có thể quay lại ứng dụng chính và sử dụng tính năng chia sẻ qua email.
    """) 