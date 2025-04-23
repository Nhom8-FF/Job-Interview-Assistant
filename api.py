import os
import json
from fastapi import FastAPI, HTTPException, Body, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from gemini_helper import initialize_gemini, generate_response
from file_processor import process_file  # Sửa thành tên hàm đúng
from prompts import get_interview_context_prompt, SYSTEM_PROMPT

# Khởi tạo Gemini API
gemini_model = initialize_gemini()

# Định nghĩa các model dữ liệu
class DocumentRequest(BaseModel):
    content: str
    document_type: str = "resume"  # resume, job_description, other
    
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    language: str = "vi"  # vi, en
    
class AnalysisRequest(BaseModel):
    content: str
    analysis_type: str  # resume_improvements, job_keywords, skills_gap, custom
    language: str = "vi"  # vi, en
    custom_prompt: Optional[str] = None
    
class InterviewSimulationRequest(BaseModel):
    resume: Optional[str] = None
    job_role: Optional[str] = None
    interview_type: str  # technical, behavioral, hr, case
    language: str = "vi"  # vi, en
    
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# Khởi tạo FastAPI
app = FastAPI(
    title="Trợ Lý Phỏng Vấn API",
    description="API cho ứng dụng trợ lý phỏng vấn xin việc",
    version="1.0.0"
)

# Thêm CORS middleware để cho phép tích hợp với các ứng dụng web khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường thực tế, nên giới hạn các domain được phép
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chào mừng đến với API Trợ Lý Phỏng Vấn Xin Việc"}

@app.post("/api/chat", response_model=APIResponse)
async def chat(request: ChatRequest):
    try:
        # Thêm hướng dẫn ngôn ngữ
        messages_copy = request.messages.copy()
        language_instruction = "Trả lời bằng tiếng Việt." if request.language == "vi" else "Answer in English."
        
        # Kiểm tra và thêm system prompt nếu cần
        if len(messages_copy) > 0 and messages_copy[0].get("role") == "system":
            messages_copy[0]["content"] += f"\n\n{language_instruction}"
        else:
            # Thêm system prompt mới
            messages_copy.insert(0, {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"})
        
        # Gọi API Gemini để lấy phản hồi
        response = generate_response(gemini_model, messages_copy)
        
        return APIResponse(success=True, data={"response": response})
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@app.post("/api/analyze-document", response_model=APIResponse)
async def analyze_document(request: AnalysisRequest):
    try:
        # Xác định prompt dựa trên loại phân tích
        analysis_prompt = ""
        language_prompt = "bằng tiếng Việt" if request.language == "vi" else "in English"
        
        if request.analysis_type == "resume_improvements":
            analysis_prompt = f"Phân tích CV sau đây và đưa ra các gợi ý cụ thể để cải thiện {language_prompt}: {request.content}"
            
        elif request.analysis_type == "job_keywords":
            analysis_prompt = f"Trích xuất các từ khóa và kỹ năng quan trọng từ mô tả công việc sau, phân loại theo mức độ quan trọng {language_prompt}: {request.content}"
            
        elif request.analysis_type == "skills_gap":
            analysis_prompt = f"Phân tích khoảng cách kỹ năng giữa sơ yếu lý lịch và yêu cầu công việc sau {language_prompt}. Đưa ra đề xuất cụ thể về cách thu hẹp khoảng cách này: {request.content}"
            
        elif request.analysis_type == "custom" and request.custom_prompt:
            analysis_prompt = f"{request.custom_prompt} {language_prompt}: {request.content}"
            
        else:
            return APIResponse(success=False, error="Loại phân tích không hợp lệ hoặc thiếu thông tin")
        
        # Thêm hướng dẫn ngôn ngữ
        language_instruction = "Trả lời bằng tiếng Việt." if request.language == "vi" else "Answer in English."
        
        # Tạo messages cho API Gemini
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"},
            {"role": "user", "content": analysis_prompt}
        ]
        
        # Gọi API Gemini để lấy phân tích
        response = generate_response(gemini_model, messages)
        
        return APIResponse(success=True, data={"analysis": response})
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@app.post("/api/interview-simulation", response_model=APIResponse)
async def interview_simulation(request: InterviewSimulationRequest):
    try:
        # Xây dựng yêu cầu cho mô phỏng phỏng vấn
        language_instruction = "Trả lời bằng tiếng Việt." if request.language == "vi" else "Answer in English."
        
        # Xác định loại phỏng vấn
        interview_types = {
            "technical": "kỹ thuật" if request.language == "vi" else "technical",
            "behavioral": "hành vi" if request.language == "vi" else "behavioral",
            "hr": "HR" if request.language == "vi" else "HR",
            "case": "tình huống" if request.language == "vi" else "case"
        }
        
        interview_type = interview_types.get(request.interview_type, request.interview_type)
        
        # Tạo system prompt cho mô phỏng
        system_prompt = f"""Bạn là một người phỏng vấn {interview_type} chuyên nghiệp. 
Hãy tiến hành buổi phỏng vấn thực tế bằng cách đặt câu hỏi và đánh giá câu trả lời. 
Mỗi lần chỉ đặt một câu hỏi và chờ câu trả lời từ người dùng.

{language_instruction}
"""

        job_context = ""
        if request.job_role:
            job_context = f"Vai trò công việc: {request.job_role}\n"
            
        if request.resume:
            job_context += f"Thông tin sơ yếu lý lịch: {request.resume}\n"
        
        # Tạo prompt đầu tiên để bắt đầu cuộc phỏng vấn
        user_prompt = f"Bắt đầu phỏng vấn {interview_type}" + (f" cho vị trí {request.job_role}" if request.job_role else "")
        
        # Tạo messages cho API Gemini
        messages = [
            {"role": "system", "content": system_prompt + job_context},
            {"role": "user", "content": user_prompt}
        ]
        
        # Gọi API Gemini để bắt đầu phỏng vấn
        response = generate_response(gemini_model, messages)
        
        return APIResponse(success=True, data={"interview_start": response})
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@app.post("/api/skills-gap-analysis", response_model=APIResponse)
async def skills_gap_analysis(request: Request):
    try:
        body = await request.json()
        resume = body.get("resume", "")
        job_description = body.get("job_description", "")
        language = body.get("language", "vi")
        
        if not resume or not job_description:
            return APIResponse(success=False, error="Cần cung cấp cả sơ yếu lý lịch và mô tả công việc")
        
        # Xác định ngôn ngữ
        language_prompt = "bằng tiếng Việt" if language == "vi" else "in English"
        language_instruction = "Trả lời bằng tiếng Việt." if language == "vi" else "Answer in English."
        
        # Tạo prompt phân tích khoảng cách kỹ năng thông minh
        analysis_prompt = f"""
Tiến hành phân tích khoảng cách kỹ năng chi tiết {language_prompt} theo các bước sau:

1. Trích xuất các kỹ năng và yêu cầu chính từ mô tả công việc sau:
{job_description}

2. Xác định các kỹ năng và kinh nghiệm từ sơ yếu lý lịch sau:
{resume}

3. Phân tích:
   - Kỹ năng trùng khớp mạnh mẽ (đánh giá phần trăm)
   - Kỹ năng trùng khớp một phần (đánh giá phần trăm)
   - Kỹ năng thiếu hoàn toàn (đánh giá phần trăm)
   - Điểm mạnh bổ sung từ sơ yếu lý lịch nhưng không được đề cập trong mô tả công việc

4. Đánh giá tổng thể về sự phù hợp (thang điểm 1-10 với lý do cụ thể)
5. Đề xuất ngắn gọn 3-5 hành động cụ thể để thu hẹp khoảng cách
"""
        
        # Tạo messages cho API Gemini
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nHãy làm một chuyên gia phân tích kỹ năng.\n\n{language_instruction}"},
            {"role": "user", "content": analysis_prompt}
        ]
        
        # Gọi API Gemini để lấy phân tích
        response = generate_response(gemini_model, messages)
        
        return APIResponse(success=True, data={"analysis": response})
    except Exception as e:
        return APIResponse(success=False, error=str(e))

# Hàm để chạy API độc lập
def run_api():
    uvicorn.run(app, host="localhost", port=8000)

if __name__ == "__main__":
    run_api()