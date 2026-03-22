import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço responsável apenas por envio de e-mails.
    """

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    EMAIL_REMETENTE = "seuapp@gmail.com"
    SENHA_APP = "SENHA_DE_APP_AQUI"

    @staticmethod
    def enviar_email(destinatario, assunto, corpo):
        try:
            msg = EmailMessage()
            msg["From"] = EmailService.EMAIL_REMETENTE
            msg["To"] = destinatario
            msg["Subject"] = assunto
            msg.set_content(corpo)

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(
                    EmailService.EMAIL_REMETENTE,
                    EmailService.SENHA_APP
                )
                server.send_message(msg)

            return True

        except Exception:
            logger.exception("Erro ao enviar e-mail")
            return False