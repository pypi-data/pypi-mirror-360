import requests

class Email(object):

    def __init__(self, tenant_id, client_id, client_secret, email_remetente):
       self.tenant_id = tenant_id
       self.client_id = client_id
       self.client_secret = client_secret
       self.email_remetente = email_remetente
       self.token = self.__get_token()


    def enviar_email(self, email_subject, email_message, email_recipient):
        url = f'https://graph.microsoft.com/v1.0/users/{self.email_remetente}/sendMail'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Verifica se email_recipient contém múltiplos emails separados por ";"
        if ";" in email_recipient:
            # Se contém ";", faz split e cria um recipient para cada email
            emails_list = [email.strip() for email in email_recipient.split(";") if email.strip()]
            to_recipients = [
                {
                    "emailAddress": {
                        "address": email
                    }
                }
                for email in emails_list
            ]
        else:
            # Se não contém ";", trata como email único
            to_recipients = [
                {
                    "emailAddress": {
                        "address": f"{email_recipient}"
                    }
                }
            ]
        
        email_body = {
            "message": {
                "subject": f"{email_subject}",
                "body": {
                    "contentType": "Text",
                    "content": f"{email_message}"
                },
                "toRecipients": to_recipients
            }
        }

        response = requests.post(url, headers=headers, json=email_body)
        if response.status_code == 202:
            recipients_count = len(to_recipients)
            print(f"✅ E-mail enviado com sucesso para {recipients_count} destinatário(s)!")
        else:
            print("❌ Falha ao enviar e-mail:", response.status_code, response.text)


    def __get_token(self):
        url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']


if __name__ == "__main__":
    tenantId, clientId, clientSecret, emailRemetente = 'X', 'X', 'X', 'X'
    email = Email(tenantId, clientId, clientSecret, emailRemetente)

    # Exemplo 1: Enviando para um único email
    titulo, texto, emailDestino = 'Teste', 'Teste envio de email', 'email@exemplo.com'
    email.enviar_email(titulo, texto, emailDestino)
    
    # Exemplo 2: Enviando para múltiplos emails separados por ";"
    titulo_multiplos = 'Teste Múltiplos'
    texto_multiplos = 'Teste envio para múltiplos destinatários'
    emails_destino_multiplos = 'email1@exemplo.com; email2@exemplo.com; email3@exemplo.com'
    email.enviar_email(titulo_multiplos, texto_multiplos, emails_destino_multiplos)
