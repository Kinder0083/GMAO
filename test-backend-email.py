#!/usr/bin/env python3
"""
Script de test d'envoi d'email via le backend GMAO IRIS
À exécuter sur le container : cd /opt/gmao-iris && python3 test-backend-email.py
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/opt/gmao-iris/backend/.env')

# Couleurs pour l'affichage
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{BLUE}{title}{NC}")
    print('='*60)

def print_success(message):
    print(f"{GREEN}✅ {message}{NC}")

def print_error(message):
    print(f"{RED}❌ {message}{NC}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{NC}")

def print_info(message):
    print(f"   {message}")

def check_env_variables():
    """Vérifier les variables d'environnement SMTP"""
    print_section("1. VÉRIFICATION VARIABLES D'ENVIRONNEMENT")
    
    required_vars = {
        'SMTP_HOST': os.getenv('SMTP_HOST'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_FROM': os.getenv('SMTP_FROM'),
        'SMTP_FROM_NAME': os.getenv('SMTP_FROM_NAME'),
        'APP_URL': os.getenv('APP_URL')
    }
    
    all_present = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print_success(f"{var_name} = {var_value}")
        else:
            print_error(f"{var_name} est MANQUANT")
            all_present = False
    
    return all_present, required_vars

def test_smtp_connection(host, port):
    """Tester la connexion au serveur SMTP"""
    print_section("2. TEST CONNEXION SERVEUR SMTP")
    
    try:
        print_info(f"Connexion à {host}:{port}...")
        server = smtplib.SMTP(host, int(port), timeout=10)
        server.ehlo()
        print_success(f"Connexion établie avec {host}:{port}")
        
        # Afficher les capacités du serveur
        print_info("Capacités du serveur :")
        for line in str(server.ehlo_resp).split('\\n'):
            print_info(f"  {line}")
        
        server.quit()
        return True
    except ConnectionRefusedError:
        print_error(f"Connexion refusée - Le serveur SMTP n'est peut-être pas démarré")
        return False
    except TimeoutError:
        print_error(f"Timeout - Le serveur SMTP ne répond pas")
        return False
    except Exception as e:
        print_error(f"Erreur de connexion : {type(e).__name__}: {str(e)}")
        return False

def send_test_email(smtp_host, smtp_port, from_email, from_name, to_email):
    """Envoyer un email de test"""
    print_section("3. ENVOI EMAIL DE TEST")
    
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Test GMAO IRIS - Email de diagnostic"
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Corps de l'email
        text_content = f"""
Test d'envoi d'email depuis GMAO IRIS

Cet email a été envoyé automatiquement par le script de test.
Si vous recevez cet email, le service d'envoi fonctionne correctement.

Configuration utilisée :
- Serveur SMTP : {smtp_host}:{smtp_port}
- Expéditeur : {from_email}
- Nom expéditeur : {from_name}

Date : {os.popen('date').read().strip()}
        """
        
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2563eb;">Test GMAO IRIS - Email de diagnostic</h2>
            <p>Cet email a été envoyé automatiquement par le script de test.</p>
            <p><strong>Si vous recevez cet email, le service d'envoi fonctionne correctement. ✅</strong></p>
            
            <h3>Configuration utilisée :</h3>
            <ul>
              <li>Serveur SMTP : {smtp_host}:{smtp_port}</li>
              <li>Expéditeur : {from_email}</li>
              <li>Nom expéditeur : {from_name}</li>
            </ul>
            
            <p style="color: #666; font-size: 12px;">Date : {os.popen('date').read().strip()}</p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Envoyer l'email
        print_info(f"Envoi à {to_email}...")
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        server.ehlo()
        server.send_message(msg)
        server.quit()
        
        print_success(f"Email envoyé avec succès à {to_email}")
        print_info("Vérifiez la boîte de réception (et les spams)")
        return True
        
    except Exception as e:
        print_error(f"Erreur lors de l'envoi : {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """Tester l'API backend d'invitation"""
    print_section("4. TEST API BACKEND (OPTIONNEL)")
    
    print_info("Pour tester l'API backend complète, exécuter :")
    print_info("  curl -X POST http://localhost:8001/api/users/invite-member \\")
    print_info("    -H 'Content-Type: application/json' \\")
    print_info("    -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print_info("    -d '{\"nom\":\"Test\",\"prenom\":\"User\",\"email\":\"test@example.com\",\"role\":\"VISUALISEUR\"}'")

def main():
    print(f"\n{BLUE}{'='*60}")
    print("TEST SERVICE EMAIL - GMAO IRIS")
    print(f"{'='*60}{NC}\n")
    
    # 1. Vérifier les variables d'environnement
    env_ok, env_vars = check_env_variables()
    if not env_ok:
        print_error("\nVariables d'environnement manquantes !")
        print_info("Vérifier le fichier : /opt/gmao-iris/backend/.env")
        sys.exit(1)
    
    smtp_host = env_vars['SMTP_HOST']
    smtp_port = env_vars['SMTP_PORT']
    smtp_from = env_vars['SMTP_FROM']
    smtp_from_name = env_vars['SMTP_FROM_NAME']
    
    # 2. Tester la connexion SMTP
    if not test_smtp_connection(smtp_host, smtp_port):
        print_error("\nImpossible de se connecter au serveur SMTP !")
        print_info("Vérifier que Postfix est démarré : systemctl status postfix")
        sys.exit(1)
    
    # 3. Demander l'email de test
    print(f"\n{YELLOW}Entrez l'adresse email pour le test (ou Enter pour test@example.com) :{NC}")
    test_email = input("Email: ").strip() or "test@example.com"
    
    # 4. Envoyer l'email de test
    if send_test_email(smtp_host, smtp_port, smtp_from, smtp_from_name, test_email):
        print_section("RÉSULTAT")
        print_success("Test d'envoi d'email RÉUSSI !")
        print_info("Si l'email n'arrive pas :")
        print_info("  1. Vérifier les spams")
        print_info("  2. Vérifier les logs : tail -f /var/log/mail.log")
        print_info("  3. Vérifier la file d'attente : mailq")
    else:
        print_section("RÉSULTAT")
        print_error("Test d'envoi d'email ÉCHOUÉ !")
        print_info("Vérifier les logs pour plus de détails")
    
    # 5. Info API backend
    test_backend_api()
    
    print(f"\n{BLUE}{'='*60}")
    print("FIN DU TEST")
    print(f"{'='*60}{NC}\n")

if __name__ == "__main__":
    main()
