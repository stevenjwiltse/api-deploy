from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema
from core.config import settings

class EmailOperations:
    def __init__(self):
        try:
            # Initialize the email configuration
            email_config = settings.get_mail_config()
            self.fast_mail = FastMail(email_config)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize email configuration: {str(e)}"
            ) 

    async def send_email(self, email: str, subject: str, body: str):
        try:
            # Create the email message schema
            message = MessageSchema(
                subject=subject,
                recipients=[email],  # List of recipients
                body=body,
                subtype="html"
            )
            # Send the email
            await self.fast_mail.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while sending the email: {str(e)}"
            )

email_operations = EmailOperations()