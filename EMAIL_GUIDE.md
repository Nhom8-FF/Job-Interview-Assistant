# Hướng dẫn cài đặt và sử dụng chức năng gửi email

## 1. Giới thiệu

Chức năng gửi email cho phép bạn chia sẻ báo cáo tiến trình phỏng vấn qua email. Để sử dụng chức năng này, bạn cần cấu hình thông tin SMTP để ứng dụng có thể gửi email thay bạn.

## 2. Cài đặt

### 2.1 Chạy công cụ cấu hình email

Mở terminal và chạy lệnh sau để mở công cụ cấu hình email:

```bash
streamlit run email_setup.py
```

### 2.2 Nhập thông tin email

Trong công cụ cấu hình email, bạn cần nhập các thông tin sau:

- **SMTP Server**: Server email của nhà cung cấp email của bạn
- **Port**: Cổng kết nối (thường là 587 cho TLS)
- **Email**: Địa chỉ email dùng để đăng nhập
- **Mật khẩu ứng dụng**: Mật khẩu hoặc App Password của tài khoản email
- **Email người gửi** (tùy chọn): Để trống sẽ sử dụng email đăng nhập

### 2.3 Lưu và kiểm tra kết nối

- Nhấn nút **Lưu cấu hình** để lưu thông tin
- Nhập một địa chỉ email để kiểm tra và nhấn **Kiểm tra kết nối**

## 3. Sử dụng với các nhà cung cấp email phổ biến

### 3.1 Gmail

- **SMTP Server**: smtp.gmail.com
- **Port**: 587
- **Email**: Địa chỉ Gmail của bạn
- **Mật khẩu ứng dụng**: 
  1. Bạn cần bật xác thực 2 yếu tố cho tài khoản Google
  2. Tạo App Password tại https://myaccount.google.com/apppasswords
  3. Sử dụng mật khẩu ứng dụng này thay vì mật khẩu thông thường

### 3.2 Outlook/Hotmail

- **SMTP Server**: smtp-mail.outlook.com
- **Port**: 587
- **Email**: Địa chỉ Outlook/Hotmail của bạn
- **Mật khẩu**: Mật khẩu tài khoản Outlook

### 3.3 Yahoo Mail

- **SMTP Server**: smtp.mail.yahoo.com
- **Port**: 587
- **Email**: Địa chỉ Yahoo Mail của bạn
- **Mật khẩu ứng dụng**: Bạn cần tạo App Password trong tài khoản Yahoo

## 4. Xử lý sự cố

### 4.1 Lỗi khi gửi email

Nếu gặp lỗi khi gửi email, hãy kiểm tra:

1. Thông tin đăng nhập email đã chính xác chưa
2. Đã bật chế độ cho phép ứng dụng kém an toàn (đối với Gmail) hoặc tạo App Password
3. Không có captcha hoặc xác minh bảo mật nào đang chặn đăng nhập

### 4.2 Cài đặt lại cấu hình

Nếu cần cài đặt lại cấu hình email, hãy chạy lại công cụ `email_setup.py` và nhập thông tin mới.

## 5. Bảo mật

- Mật khẩu email của bạn được lưu trong file `config.py` trong thư mục ứng dụng
- Trong môi trường sản xuất, nên lưu thông tin nhạy cảm này trong biến môi trường thay vì file config
- Không chia sẻ file config với người khác 