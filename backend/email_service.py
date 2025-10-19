"""
Service d'envoi d'emails pour GMAO Iris
Utilise Postfix local (SMTP)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuration depuis .env
SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '25'))
SMTP_FROM = os.environ.get('SMTP_FROM', 'noreply@gmao-iris.local')
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'GMAO Iris')
APP_URL = os.environ.get('APP_URL', 'http://localhost')


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Envoie un email via Postfix local
    
    Args:
        to_email: Email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML de l'email
        text_content: Contenu texte alternatif (optionnel)
    
    Returns:
        bool: True si envoi réussi, False sinon
    """
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
        msg['To'] = to_email
        
        # Ajouter version texte si fournie
        if text_content:
            part_text = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part_text)
        
        # Ajouter version HTML
        part_html = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part_html)
        
        # Envoyer via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        
        logger.info(f"Email envoyé avec succès à {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {e}")
        return False


def send_invitation_email(to_email: str, token: str, role: str) -> bool:
    """
    Envoie un email d'invitation à rejoindre GMAO Iris
    
    Args:
        to_email: Email du destinataire
        token: Token d'invitation JWT
        role: Rôle attribué (ADMIN, TECHNICIEN, VISUALISEUR)
    
    Returns:
        bool: True si envoi réussi
    """
    invitation_link = f"{APP_URL}/inscription?token={token}"
    
    role_labels = {
        "ADMIN": "Administrateur",
        "TECHNICIEN": "Technicien",
        "VISUALISEUR": "Visualiseur"
    }
    role_label = role_labels.get(role, role)
    
    subject = "Invitation à rejoindre GMAO Iris"
    
    # Version HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #2563eb;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 GMAO Iris</h1>
            </div>
            <div class="content">
                <h2>Bonjour,</h2>
                <p>Vous avez été invité(e) à rejoindre <strong>GMAO Iris</strong> en tant que <strong>{role_label}</strong>.</p>
                
                <p>Pour compléter votre inscription, cliquez sur le bouton ci-dessous :</p>
                
                <div style="text-align: center;">
                    <a href="{invitation_link}" class="button">Compléter mon inscription</a>
                </div>
                
                <p style="font-size: 12px; color: #666;">
                    Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :<br>
                    <a href="{invitation_link}">{invitation_link}</a>
                </p>
                
                <p><strong>⚠️ Important :</strong> Ce lien expire dans 7 jours.</p>
                
                <p>Cordialement,<br>L'équipe GMAO Iris</p>
            </div>
            <div class="footer">
                <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
                <p>© 2025 GMAO Iris - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Version texte
    text_content = f"""
Bonjour,

Vous avez été invité(e) à rejoindre GMAO Iris en tant que {role_label}.

Pour compléter votre inscription, cliquez sur le lien ci-dessous :
{invitation_link}

Ce lien expire dans 7 jours.

Cordialement,
L'équipe GMAO Iris

---
Ceci est un email automatique, merci de ne pas y répondre.
© 2025 GMAO Iris - Tous droits réservés
    """
    
    return send_email(to_email, subject, html_content, text_content)


def send_account_created_email(to_email: str, temp_password: str, prenom: str) -> bool:
    """
    Envoie un email avec les identifiants temporaires
    
    Args:
        to_email: Email du destinataire
        temp_password: Mot de passe temporaire
        prenom: Prénom de l'utilisateur
    
    Returns:
        bool: True si envoi réussi
    """
    subject = "Votre compte GMAO Iris a été créé"
    
    # Version HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #2563eb;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .credentials {{
                background-color: white;
                padding: 15px;
                border-left: 4px solid #2563eb;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 GMAO Iris</h1>
            </div>
            <div class="content">
                <h2>Bonjour {prenom},</h2>
                <p>Votre compte GMAO Iris a été créé avec succès !</p>
                
                <div class="credentials">
                    <p><strong>Vos identifiants de connexion :</strong></p>
                    <p>Email : <strong>{to_email}</strong></p>
                    <p>Mot de passe temporaire : <strong>{temp_password}</strong></p>
                </div>
                
                <p><strong>⚠️ Important :</strong> Vous devrez changer votre mot de passe lors de votre première connexion.</p>
                
                <div style="text-align: center;">
                    <a href="{APP_URL}" class="button">Se connecter</a>
                </div>
                
                <p>Cordialement,<br>L'équipe GMAO Iris</p>
            </div>
            <div class="footer">
                <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
                <p>© 2025 GMAO Iris - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Version texte
    text_content = f"""
Bonjour {prenom},

Votre compte GMAO Iris a été créé avec succès !

Vos identifiants de connexion :
Email : {to_email}
Mot de passe temporaire : {temp_password}

⚠️ Important : Vous devrez changer votre mot de passe lors de votre première connexion.

Connectez-vous sur : {APP_URL}

Cordialement,
L'équipe GMAO Iris

---
Ceci est un email automatique, merci de ne pas y répondre.
© 2025 GMAO Iris - Tous droits réservés
    """
    
    return send_email(to_email, subject, html_content, text_content)
