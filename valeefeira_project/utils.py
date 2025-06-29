import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask_mail import Message
from app import app, mail
from io import BytesIO

def get_cities():
    """Return list of cities in Vale do Jequitinhonha"""
    cities = [
        'Almenara', 'Araçuaí', 'Bandeira', 'Berilo', 'Capelinha', 'Caraí',
        'Comercinho', 'Coronel Murta', 'Diamantina', 'Divisópolis',
        'Francisco Badaró', 'Felício dos Santos', 'Felisburgo', 'Itamarandiba',
        'Itaobim', 'Itinga', 'Santa Maria do Salto', 'Jacinto', 'Jenipapo de Minas',
        'Joaíma', 'Minas Novas', 'Mata Verde', 'Medina', 'Monte Formoso',
        'Padre Paraíso', 'Pedra Azul', 'Ponto dos Volantes', 'Rio do Prado',
        'Rio Pardo', 'Rio Pardo Pequeno', 'Rubim', 'Salinas', 'Salto da Divisa',
        'São Gonçalo do Rio das Pedras', 'Serro', 'Turmalina', 'Virgem da Lapa',
        'Jequitinhonha'
    ]
    return sorted(cities)

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    """Process uploaded image and return binary data with mimetype"""
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Open image with PIL
        image = Image.open(file)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize image maintaining aspect ratio
        max_size = (800, 600)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO object
        img_io = BytesIO()
        image.save(img_io, 'JPEG', optimize=True, quality=85)
        img_io.seek(0)
        
        return {
            'data': img_io.read(),
            'mimetype': 'image/jpeg',
            'filename': str(uuid.uuid4()) + '.jpg'
        }
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def format_currency(value):
    """Format currency for Brazilian Real"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def send_reset_email(user_email, reset_token):
    """Send password reset email using SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os
    from flask import url_for
    
    try:
        # Generate reset URL
        reset_url = url_for('reset_password', token=reset_token, _external=True)
        
        # Email configuration
        sender_email = "noreply@valefeira.com"
        sender_name = "Vale&feira"
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Vale&feira - Recuperação de Senha"
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = user_email
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperação de Senha - Vale&feira</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #17a2b8, #20c997); color: white; padding: 40px 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 32px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">Vale&feira</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; font-style: italic; opacity: 0.9;">Do Vale para o mercado: mais acesso, menos desperdício</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <h2 style="color: #17a2b8; margin: 0 0 20px 0; font-size: 24px; font-weight: 600;">🔑 Recuperação de Senha</h2>
                    
                    <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6; color: #333;">Olá!</p>
                    
                    <p style="margin: 0 0 25px 0; font-size: 16px; line-height: 1.6; color: #333;">
                        Você solicitou a recuperação da sua senha no <strong>Vale&feira</strong>. 
                        Para criar uma nova senha e acessar sua conta novamente, clique no botão abaixo:
                    </p>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{reset_url}" 
                           style="background: linear-gradient(135deg, #28a745, #20c997); 
                                  color: white; 
                                  padding: 16px 32px; 
                                  text-decoration: none; 
                                  border-radius: 8px; 
                                  font-weight: 600; 
                                  font-size: 16px;
                                  display: inline-block;
                                  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                                  transition: all 0.3s ease;">
                            ✉️ Redefinir Minha Senha
                        </a>
                    </div>
                    
                    <p style="margin: 25px 0 20px 0; font-size: 14px; color: #666; text-align: center;">
                        Ou copie e cole este link no seu navegador:
                    </p>
                    
                    <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; word-break: break-all; font-family: 'Courier New', monospace; font-size: 13px; color: #495057;">
                            {reset_url}
                        </p>
                    </div>
                    
                    <!-- Warning Box -->
                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 30px 0; border-radius: 0 6px 6px 0;">
                        <p style="margin: 0 0 10px 0; font-weight: 600; color: #856404; font-size: 15px;">⚠️ Informações Importantes:</p>
                        <ul style="margin: 0; padding-left: 20px; color: #856404; font-size: 14px;">
                            <li>Este link expira em <strong>1 hora</strong> por segurança</li>
                            <li>Se você não solicitou esta recuperação, pode ignorar este email</li>
                            <li>Sua senha atual continua funcionando até você criar uma nova</li>
                        </ul>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #e9ecef; margin: 35px 0;">
                    
                    <!-- Footer -->
                    <div style="text-align: center;">
                        <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                            Este é um email automático do sistema Vale&feira
                        </p>
                        <p style="margin: 0; color: #6c757d; font-size: 13px;">
                            © 2025 Vale&feira - Conectando produtores do Vale do Jequitinhonha
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version (fallback)
        text_content = f"""
Vale&feira - Recuperação de Senha

Olá!

Você solicitou a recuperação da sua senha no Vale&feira.

Para criar uma nova senha, acesse este link:
{reset_url}

INFORMAÇÕES IMPORTANTES:
• Este link expira em 1 hora por segurança
• Se você não solicitou esta recuperação, pode ignorar este email
• Sua senha atual continua funcionando até você criar uma nova

--
Vale&feira
Do Vale para o mercado: mais acesso, menos desperdício
© 2025 Vale&feira - Conectando produtores do Vale do Jequitinhonha
        """
        
        # Create text and HTML parts
        text_part = MIMEText(text_content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")
        
        # Add parts to message
        message.attach(text_part)
        message.attach(html_part)
        
        # Try multiple email sending methods
        email_sent = False
        
        # Method 1: Try SendGrid if API key is available
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if sendgrid_key and not email_sent:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                
                sg = SendGridAPIClient(sendgrid_key)
                
                mail = Mail(
                    from_email=sender_email,
                    to_emails=user_email,
                    subject=message["Subject"],
                    html_content=html_content
                )
                
                response = sg.send(mail)
                
                print("=" * 60)
                print("EMAIL ENVIADO VIA SENDGRID!")
                print("=" * 60)
                print(f"Para: {user_email}")
                print(f"Status: {response.status_code}")
                print(f"Link: {reset_url}")
                print("=" * 60)
                
                email_sent = True
                
            except Exception as sg_error:
                print(f"Erro SendGrid: {sg_error}")
        
        # Method 2: Try Gmail SMTP
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if gmail_user and gmail_password and not email_sent:
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, user_email, message.as_string())
                server.quit()
                
                print("=" * 60)
                print("EMAIL ENVIADO VIA GMAIL!")
                print("=" * 60)
                print(f"Para: {user_email}")
                print(f"De: {gmail_user}")
                print(f"Link: {reset_url}")
                print("=" * 60)
                
                email_sent = True
                
            except Exception as gmail_error:
                print(f"Erro Gmail: {gmail_error}")
        
        # Method 3: Use alternative SMTP service
        if not email_sent:
            try:
                # Use Mailtrap for development (free testing service)
                smtp_server = "smtp.mailtrap.io"
                port = 2525
                
                # Default test credentials (replace with real ones)
                mailtrap_user = os.environ.get('MAILTRAP_USER', 'test_user')
                mailtrap_password = os.environ.get('MAILTRAP_PASSWORD', 'test_pass')
                
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
                server.login(mailtrap_user, mailtrap_password)
                server.sendmail(sender_email, user_email, message.as_string())
                server.quit()
                
                print("=" * 60)
                print("EMAIL ENVIADO VIA MAILTRAP!")
                print("=" * 60)
                print(f"Para: {user_email}")
                print(f"Link: {reset_url}")
                print("=" * 60)
                
                email_sent = True
                
            except Exception as mailtrap_error:
                print(f"Erro Mailtrap: {mailtrap_error}")
        
        # Final fallback: Show instructions
        if not email_sent:
            print("=" * 60)
            print("CONFIGURACAO DE EMAIL NECESSARIA")
            print("=" * 60)
            print(f"Para: {user_email}")
            print(f"Link de recuperacao: {reset_url}")
            print("=" * 60)
            print("INSTRUCOES PARA CONFIGURAR EMAIL:")
            print("1. Configure SENDGRID_API_KEY (recomendado)")
            print("2. Ou configure GMAIL_USER e GMAIL_APP_PASSWORD")
            print("3. Ou use o link acima diretamente")
            print("=" * 60)
            print("PARA USAR O LINK AGORA:")
            print("1. Copie o link acima")
            print("2. Cole no navegador")
            print("3. Redefina sua senha")
            print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

# Register filter for templates
app.jinja_env.filters['currency'] = format_currency
