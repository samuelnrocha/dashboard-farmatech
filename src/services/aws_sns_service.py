import boto3
from moto import mock_aws
from datetime import datetime

class AWSService:
    _mock = mock_aws()
    
    def __init__(self):
        # Iniciar o mock da AWS para interceptar boto3 no processo local
        self._mock.start()
        
        self.region = "us-east-1"
        self.sender_email = "alertas@farmtech.com"
        self.recipient_email = "operador@farmtech.com"
        self.topic_arn = None
        self.alert_logs = []
        
        try:
            # Cliente SNS para SMS
            self.sns = boto3.client(
                "sns",
                region_name=self.region,
                aws_access_key_id="mock_key",
                aws_secret_access_key="mock_secret"
            )
            
            # Cliente SES para E-mail
            self.ses = boto3.client(
                "ses",
                region_name=self.region,
                aws_access_key_id="mock_key",
                aws_secret_access_key="mock_secret"
            )
            
            self._setup_mock_resources()
        except Exception as e:
            print(f"[AWS Mock] Erro ao instanciar clientes boto3: {e}")

    def _setup_mock_resources(self):
        try:
            # 1. Setup SNS
            sns_resp = self.sns.create_topic(Name="farmtech-alertas-criticos")
            self.topic_arn = sns_resp["TopicArn"]
            
            # Registrar assinaturas de teste no SNS
            self.sns.subscribe(
                TopicArn=self.topic_arn,
                Protocol="sms",
                Endpoint="+5511999998888"
            )
            
            # 2. Setup SES (precisa verificar a identidade do remetente no mock)
            self.ses.verify_email_identity(EmailAddress=self.sender_email)
            self.ses.verify_email_identity(EmailAddress=self.recipient_email)
            print("[AWS Mock] Recursos do SNS e SES mockados criados e configurados com sucesso.")
        except Exception as e:
            print(f"[AWS Mock] Erro no setup dos recursos: {e}")

    def enviar_sms(self, mensagem, telefone="+5511999998888"):
        try:
            resp = self.sns.publish(
                PhoneNumber=telefone,
                Message=mensagem,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'FarmTech'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            msg_id = resp.get("MessageId", "N/A")
            log_entry = {
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "tipo": "SMS (AWS SNS)",
                "destinatario": telefone,
                "mensagem": mensagem,
                "message_id": msg_id,
                "status": "Sucesso (Mockado)"
            }
            self.alert_logs.append(log_entry)
            return True, msg_id
        except Exception as e:
            print(f"[AWS SNS Mock] Erro ao enviar SMS: {e}")
            return False, str(e)

    def enviar_email(self, assunto, mensagem_html, destinatario="operador@farmtech.com"):
        try:
            resp = self.ses.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [destinatario]
                },
                Message={
                    'Subject': {
                        'Data': assunto,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': mensagem_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            msg_id = resp.get("MessageId", "N/A")
            log_entry = {
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "tipo": "E-mail (AWS SES)",
                "destinatario": destinatario,
                "mensagem": assunto,
                "message_id": msg_id,
                "status": "Sucesso (Mockado)"
            }
            self.alert_logs.append(log_entry)
            return True, msg_id
        except Exception as e:
            print(f"[AWS SES Mock] Erro ao enviar E-mail: {e}")
            return False, str(e)

    def get_logs(self):
        return list(self.alert_logs)
        
    def clear_logs(self):
        self.alert_logs.clear()
