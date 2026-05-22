from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/support", tags=["Support"])

class ContactRequest(BaseModel):
    title: str
    content: str
    sender_email: EmailStr

@router.post("/contact")
async def send_contact_email(data: ContactRequest):
    """
    고객지원 문의 메일을 관리자에게 발송합니다.
    """
    admin_email = "admin@dearzit.com" # 관리자 메일 주소
    
    # ---------------------------------------------------------
    # 실제 메일 발송 로직 (SMTP 설정이 준비된 경우 동작)
    # 현재는 SMTP 서버 정보가 없으므로 터미널에 로그로 출력하고 성공 처리합니다.
    # ---------------------------------------------------------
    print("=" * 50)
    print(f"[문의 메일 발송 시뮬레이션]")
    print(f"발송인: {data.sender_email}")
    print(f"수신인(관리자): {admin_email}")
    print(f"제목: {data.title}")
    print(f"내용:\n{data.content}")
    print("=" * 50)
    
    # 실제 메일 발송을 원하신다면 아래 코드를 활성화하고 환경변수를 설정하세요.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = data.sender_email
        msg['To'] = admin_email
        msg['Subject'] = f"[DearZit 문의] {data.title}"
        
        msg.attach(MIMEText(data.content, 'plain'))
        
        # SMTP 서버 설정 (예: Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email Send Error: {e}")
        raise HTTPException(status_code=500, detail="메일 발송에 실패했습니다.")
    """
    
    return {"status": "success", "message": "성공적으로 관리자에게 문의 메일이 발송되었습니다."}
