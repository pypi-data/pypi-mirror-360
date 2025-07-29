import imaplib
import email
import time
import loggerutility as logger
from datetime import datetime

import threading
import traceback
import json
import os, shutil
import csv

import io
import pandas as pd
import docx
import PyPDF2

from .Save_Transaction import Save_Transaction
from .Email_Classification import Email_Classification
from .EmailReplyAssistant import EmailReplyAssistant
from .Process_Category import Process_Category

import re
from email.utils import parseaddr
from email.header import decode_header

shared_status = True

class Email_Read:
    def read_email(self, email_config):
        try:
            logger.log("inside read_email")
            mail = imaplib.IMAP4_SSL(email_config['host'], email_config['port'])
            mail.login(email_config['email'], email_config['password'])
            logger.log("login successfully")
            mail.select('inbox')

            while True:
                status, email_ids = mail.search(None, 'UNSEEN')
                emails = []
                
                if status == 'OK':
                    email_ids = email_ids[0].split()

                    if not email_ids: 
                        logger.log("Email not found, going to check new mail")
                        logger.log("Email not found,\ngoing to check new mail \n")
                    else:
                    
                        for email_id in email_ids:
                            email_body = ""
                            attachments = []
                            status, data = mail.fetch(email_id, '(RFC822)')
                            
                            if status == 'OK':
                                raw_email = data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                sender_email = msg['From']
                                cc_email = msg['CC']
                                subject = msg['Subject']
                                to = msg['To']

                                if msg.is_multipart():
                                    for part in msg.walk():
                                        content_type = part.get_content_type()
                                        if content_type == "text/plain":
                                            email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                                else:
                                    email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              

                                email_data = {
                                    "email_id": email_id,
                                    "from": sender_email,
                                    "to": to,
                                    "cc": cc_email,
                                    "subject": subject,
                                    "body": email_body
                                }
                                emails.append(email_data)
                                logger.log(f"emails:: {emails}")
                                call_save_transaction = Save_Transaction()
                                save_transaction_response = call_save_transaction.email_save_transaction(email_data)
                                logger.log(f"save_transaction_response:: {save_transaction_response}")
                time.sleep(10)
        
        except Exception as e:
            return {"success": "Failed", "message": f"Error reading emails: {str(e)}"}
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception as close_error:
                logger.log(f"Error during mail close/logout: {str(close_error)}")

    def read_email_automation(self, email_config,user_id):
        logger.log(f"inside read_email_automation")
        LABEL                       = "Unprocessed_Email"
        file_JsonArray              = []
        templateName                = "ai_email_automation.json"
        fileName                    = ""

        Model_Name =  email_config.get('model_type', 'OpenAI') 
        reciever_email_addr = email_config.get('email', '').replace("\xa0", "").strip()
        receiver_email_pwd = email_config.get('password', '').replace("\xa0", "").strip()
        host =  email_config.get('host', '') 
        port =  email_config.get('port', '') 

        try:
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(reciever_email_addr, receiver_email_pwd)
            logger.log("login successfully")
            login_status = "Success"
            mail.select('inbox')

            file_JsonArray, categories = self.read_JSON_File(templateName, user_id)

        except Exception as e:
            login_status = "Failed"
            logger.log(f"Login failed: {e}")
            raise Exception(e)   

        # Log the result
        self.log_email_login(user_id, reciever_email_addr, Model_Name, login_status)

        while True:
            shared_status = self.read_status()

            if shared_status:
                status, email_ids = mail.search(None, 'UNSEEN')
                emails = []
                
                if status == 'OK':
                    email_ids = email_ids[0].split()
                
                    if not email_ids: 
                        logger.log("Email not found, going to check new mail")
                        logger.log("Email not found,\ngoing to check new mail \n")
                    else:
                    
                        for email_id in email_ids:
                            email_body = ""
                            attachments = []
                            # status, data = mail.fetch(email_id, '(RFC822)')
                            status, data = mail.fetch(email_id, '(RFC822 UID)') # Fetch UID as well
                            emailCategory = "Not Classified"

                            if status == 'OK':
                                raw_email = data[0][1]
                                msg = email.message_from_bytes(raw_email)

                                subject = msg['Subject']
                                sender_email_addr   = msg['From']
                                cc_email_addr       = msg['CC']
                                subject             = msg['Subject']
                                to_email_addr = msg.get('To', '')
                                

                                # Extract UID
                                logger.log(f" the data -----{data[0][0]}")
                                raw_uid = data[0][0].decode() if isinstance(data[0][0], bytes) else data[0][0]
                                logger.log(f"the raw uid is ------- {raw_uid}")
                                uid_match = re.search(r'UID (\d+)', raw_uid)
                                uid = uid_match.group(1) if uid_match else "N/A"

                                is_html = False  # Initialize is_html

                                if msg.is_multipart():
                                    for part in msg.walk():
                                        content_type = part.get_content_type()
                                        if content_type == "text/html" and not is_html:
                                            is_html = True  # Set flag if HTML part is found

                                        if content_type == "text/plain":
                                            email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')
                                        
                                else:
                                    email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              
                                    content_type = msg.get_content_type()
                                    is_html = (content_type == "text/html")  # Set is_html based on single-part type
                                
                                openai_Process_Input  = email_body 

                                logger.log(f"\nEmail Subject::: {subject}")
                                logger.log(f"\nEmail body::: {openai_Process_Input}")

                                openai_api_key = email_config.get('openai_api_key', '') 
                                geminiAI_APIKey = email_config.get('gemini_api_key', '') 
                                signature = email_config.get('signature', '') 
                                localAIURL = email_config.get('local_ai_url', '') 
                                
                                if len(str(openai_Process_Input)) > 0 :
                                    email_cat_data = {
                                        "model_type" : Model_Name,
                                        "openai_api_key" : openai_api_key,
                                        "categories" : categories,
                                        "email_body" : email_body,
                                        "gemini_api_key" : geminiAI_APIKey,
                                        "signature" : signature,
                                        "local_ai_url" : localAIURL,
                                    }
                                    # logger.log(f"\nemail_cat_data ::: {email_cat_data}")
                                    email_classification = Email_Classification()
                                    emailCategory = email_classification.detect_category(email_cat_data)
                                    emailCategory = emailCategory['message']
                                    logger.log(f"\nDetected Email category ::: {emailCategory}")

                                    dataValues = {
                                        'Model_Name': Model_Name,
                                        'file_JsonArray': file_JsonArray,
                                        'openai_api_key': openai_api_key,
                                        'openai_Process_Input': openai_Process_Input,
                                        'subject': subject,
                                        'sender_email_addr': sender_email_addr,
                                        'cc_email_addr': cc_email_addr,
                                        'email_body': email_body,
                                        'email_config': email_config,
                                        'msg': msg,
                                        'geminiAI_APIKey': geminiAI_APIKey,
                                        'localAIURL': localAIURL,
                                        'signature': signature,
                                        'LABEL': LABEL,
                                        'mail': mail,
                                        'email_id': email_id,
                                        "uid": uid,
                                        "to_email_addr": to_email_addr,
                                        "user_id": user_id,
                                        "is_html": is_html
                                    }
                                    processcategory = Process_Category()
                                    processcategory.process_cat(emailCategory, dataValues)

            time.sleep(10)

    def read_email_quotation(self, email_config,user_id):
        # try:
        LABEL                       = "Unprocessed_Email"
        file_JsonArray              = []
        templateName                = "ai_email_automation.json"
        fileName                    = ""

        Model_Name =  email_config.get('model_type', 'OpenAI') 
        reciever_email_addr = email_config.get('email', '').replace("\xa0", "").strip()
        receiver_email_pwd = email_config.get('password', '').replace("\xa0", "").strip()
        host =  email_config.get('host', '') 
        port =  email_config.get('port', '') 

        try:
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(reciever_email_addr, receiver_email_pwd)
            logger.log("login successfully")
            login_status = "Success"
            mail.select('inbox')

            file_JsonArray, categories = self.read_JSON_File(templateName, user_id)

        except Exception as e:
            logger.log(f"Login failed: {e}")
            return f"Login failed: {e}"

        # Log the result
        self.log_email_login(user_id, reciever_email_addr, Model_Name, login_status)

        while True:
            status, email_ids = mail.search(None, 'UNSEEN')
            emails = []
            
            if status == 'OK':
                email_ids = email_ids[0].split()

                if not email_ids: 
                    logger.log("Email not found, going to check new mail")
                    logger.log("Email not found,\ngoing to check new mail \n")
                else:
                
                    for email_id in email_ids:
                        email_body = ""
                        attachments = []
                        status, data = mail.fetch(email_id, '(RFC822 UID)')
                        
                        if status == 'OK':
                            raw_email = data[0][1]
                            msg = email.message_from_bytes(raw_email)

                            subject = msg['Subject']
                            sender_email_addr   = msg['From']
                            cc_email_addr       = msg['CC']
                            subject             = msg['Subject']
                            to_email_addr = msg.get('To', '')

                            # Extract UID
                            raw_uid = data[0][0].decode() if isinstance(data[0][0], bytes) else data[0][0]
                            uid_match = re.search(r'UID (\d+)', raw_uid)
                            uid = uid_match.group(1) if uid_match else "N/A"

                            is_html = False  # Initialize is_html

                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/html" and not is_html:
                                        is_html = True  # Set flag if HTML part is found

                                    if content_type == "text/plain":
                                        email_body += part.get_payload(decode=True).decode('utf-8', errors='replace')

        
                            # For attachment
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_disposition = str(part.get("Content-Disposition") or "")
                                    content_type = part.get_content_type()
                                    if "attachment" in content_disposition.lower():
                                        filename = part.get_filename() or "attachment"
                                        content_bytes = part.get_payload(decode=True)
                                        if content_bytes:
                                            extracted_content = self.Extract_attachment_content(filename, content_bytes)
                                            extracted_content =f"\n\n--- The content of the attachment '{filename}' is below ---\n{extracted_content}\n"
                                            # email_body += f"\n\n--- The content of the attachment '{filename}' is below ---\n{extracted_content}\n"
                                    else:
                                        extracted_content="NA"
                             
                            else:
                                email_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')                              
                                content_type = msg.get_content_type()
                                is_html = (content_type == "text/html")  # Set is_html based on single-part type
                            
                            openai_Process_Input  = email_body 
                            logger.log(f"\nEmail Subject::: {subject}")
                            logger.log(f"\nEmail body::: {openai_Process_Input}")

                            openai_api_key = email_config.get('openai_api_key', '') 
                            geminiAI_APIKey = email_config.get('gemini_api_key', '') 
                            signature = email_config.get('signature', '') 
                            localAIURL = email_config.get('local_ai_url', '') 
                            logger.log(f"\ngeminiAI_APIKey::: {geminiAI_APIKey}")
                            logger.log(f"\nlocalAIURL::: {localAIURL}")
                            logger.log(f"\nsignature::: {signature}")
                            
                            if len(str(openai_Process_Input)) > 0 :
                                email_cat_data = {
                                    "model_type" : Model_Name,
                                    "openai_api_key" : openai_api_key,
                                    "categories" : categories,
                                    "email_body" : email_body,
                                    "gemini_api_key" : geminiAI_APIKey,
                                    "signature" : signature,
                                    "local_ai_url" : localAIURL,
                                }
                                # logger.log(f"\nemail_cat_data ::: {email_cat_data}")
                                email_classification = Email_Classification()
                                emailCategory = email_classification.detect_category(email_cat_data)
                                emailCategory = emailCategory['message']
                                logger.log(f"\nDetected Email category ::: {emailCategory}")
                                
                                dataValues = {
                                    'Model_Name': Model_Name,
                                    'file_JsonArray': file_JsonArray,
                                    'openai_api_key': openai_api_key,
                                    'openai_Process_Input': openai_Process_Input,
                                    'subject': subject,
                                    'sender_email_addr': sender_email_addr,
                                    'cc_email_addr': cc_email_addr,
                                    'email_body': email_body,
                                    'email_config': email_config,
                                    'msg': msg,
                                    'geminiAI_APIKey': geminiAI_APIKey,
                                    'localAIURL': localAIURL,
                                    'signature': signature,
                                    'LABEL': LABEL,
                                    'mail': mail,
                                    'email_id': email_id,
                                    "uid": uid,
                                    "to_email_addr": to_email_addr,
                                    "user_id": user_id,
                                    "is_html": is_html,
                                    "extracted_content" : extracted_content
                                }
                                processcategory = Process_Category()
                                processcategory.process_cat(emailCategory, dataValues)

            time.sleep(10)

    def Read_Email(self, data):
        try:

            reciever_email_addr = data.get("reciever_email_addr")
            receiver_email_pwd = data.get("receiver_email_pwd")
            host = data.get("host")
            port = data.get("port")
            openai_api_key = data.get("openai_api_key") 
            geminiAI_APIKey = data.get("GeminiAI_APIKey")
            localAIURL = data.get("LOCAL_AI_URL")

            if not all([reciever_email_addr, receiver_email_pwd, host, port]):
                raise ValueError("Missing required email configuration fields.")

            logger.log(f"\nReceiver Email Address: {reciever_email_addr}\t{type(reciever_email_addr)}", "0")
            logger.log(f"\nReceiver Email Password: {receiver_email_pwd}\t{type(receiver_email_pwd)}", "0")
            logger.log(f"\nHost: {host}\t{type(host)}", "0")
            logger.log(f"\nPort: {port}\t{type(port)}", "0")

            email_config = {
                'email': reciever_email_addr,
                'password': receiver_email_pwd,
                'host': host,
                'port': int(port),
                'openai_api_key': openai_api_key,
                'gemini_api_key': geminiAI_APIKey,
                'local_ai_url': localAIURL
            }

            emails = self.read_email(email_config)            
            logger.log(f"Read_Email response: {emails}")

        except Exception as e:
            logger.log(f"Error in Read_Email: {str(e)}")
    
    def extract_all_email_info(self, eml_content):
        # Parse the email content
        msg = email.message_from_string(eml_content)
        extracted_info = {}

        # Extracting To, From, and CC
        extracted_info['to'] = msg.get('To')
        extracted_info['from'] = msg.get('From')
        extracted_info['cc'] = msg.get('Cc')
        logger.log(f"To: {extracted_info['to']}, From: {extracted_info['from']}, CC: {extracted_info['cc']}")

        # Extracting subject and decoding it if necessary
        subject = decode_header(msg.get('Subject', ''))[0][0]
        if decode_header(msg.get('Subject', ''))[0][1]:
            subject = subject.decode()
        extracted_info['subject'] = subject
        logger.log(f"Subject: {extracted_info['subject']}")

        # Extracting the body content (text or HTML)
        text_body = None
        html_body = None
        if msg.is_multipart():
            logger.log("Multipart email detected.")
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                logger.log(f"Part content type: {content_type}, Content-Disposition: {content_disposition}")

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    text_body = part.get_payload(decode=True).decode()
                    logger.log("Text body extracted.")
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html_body = part.get_payload(decode=True).decode()
                    logger.log("HTML body extracted.")
        else:
            if msg.get_content_type() == "text/plain":
                text_body = msg.get_payload(decode=True).decode()
                logger.log("Text body extracted (non-multipart) .")
            elif msg.get_content_type() == "text/html":
                html_body = msg.get_payload(decode=True).decode()
                logger.log("HTML body extracted (non-multipart).")

        extracted_info['email_body'] = text_body if text_body else html_body if html_body else None
        extracted_info['is_html'] = bool(html_body)

        # Extracting the date and converting it to ISO format
        date_tuple = email.utils.parsedate_tz(msg.get('Date'))
        logger.log(f"date tuple is {date_tuple}")
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            extracted_info['date'] = local_date.isoformat()
            logger.log(f"Date: {extracted_info['date']}")
        else:
            extracted_info['date'] = None
            logger.log("No date found.")

        # Extracting the unique ID (Message-ID)
        extracted_info['unique_id'] = msg.get('Message-ID')
        logger.log(f"Unique ID: {extracted_info['unique_id']}")
        logger.log(f"-------------------------------The extracted info is --------------------------{extracted_info}")

        return extracted_info,msg
    
    def process_eml_files(self, user_id, eml_content,mail,Model_Name,email_config):
        LABEL = "Unprocessed_Email"
        file_JsonArray = []
        templateName = "ai_email_automation.json"
        fileName = ""
    
        file_JsonArray, categories = self.read_JSON_File(templateName, user_id)
        # Call the `extract_all_email_info` method to extract details from the eml content
        extracted_info,msg = self.extract_all_email_info(eml_content)

        # Extract the details from `extracted_info`
        subject = extracted_info.get('subject', '')
        sender_email_addr = extracted_info.get('from', '')
        cc_email_addr = extracted_info.get('cc', '')
        to_email_addr = extracted_info.get('to', '')
        date = extracted_info.get('date', '')
        email_body = extracted_info.get('email_body', '')
        msg_id = extracted_info.get('unique_id', '')
        is_html = extracted_info.get('is_html', False)  

        uid = re.sub(r'[<>]|\@.*|\+', '', msg_id) 
        logger.log(f"\nEmail Subject::: {subject}")
        logger.log(f"\nEmail body::: {email_body}")

        openai_Process_Input = email_body

        openai_api_key = email_config.get('openai_api_key', '') 
        geminiAI_APIKey = email_config.get('gemini_api_key', '') 
        signature = email_config.get('signature', '') 
        localAIURL = email_config.get('local_ai_url', '') 

        if len(str(openai_Process_Input)) > 0:
            email_cat_data = {
                "model_type": Model_Name,
                "openai_api_key": openai_api_key,
                "categories": categories,
                "email_body": email_body,
                "gemini_api_key": geminiAI_APIKey,
                "signature": signature,
                "local_ai_url": localAIURL,
            }
            email_classification = Email_Classification()
            emailCategory = email_classification.detect_category(email_cat_data)
            emailCategory = emailCategory['message']
            logger.log(f"\nDetected Email category ::: {emailCategory}")

            dataValues = {
                'Model_Name': Model_Name,
                'file_JsonArray': file_JsonArray,
                'openai_api_key': openai_api_key,
                'openai_Process_Input': openai_Process_Input,
                'subject': subject,
                'sender_email_addr': sender_email_addr,
                'cc_email_addr': cc_email_addr,
                'email_body': email_body,
                'email_config': email_config,
                'msg': msg,
                'geminiAI_APIKey': geminiAI_APIKey,
                'localAIURL': localAIURL,
                'signature': signature,
                'LABEL': LABEL,
                'mail': mail,
                'email_id': msg_id,
                "uid": uid,
                "to_email_addr": to_email_addr,
                "user_id": user_id,
                "is_html": is_html,
                "import_file": True
            }
            processcategory = Process_Category()
            processcategory.process_cat(emailCategory, dataValues)

        return "success"

    def read_JSON_File(self, json_fileName, user_id):
        category_list               = []
        categories                  = ""
        try:
            logger.log(f"\nEmail_Read() read_JSON_File user_id ::: {user_id}")
            user_file = json_fileName
            if user_id:
                user_dir = os.path.join('user_data', user_id)
                logger.log(f"\nEmail_Read() read_JSON_File user_dir ::: {user_dir}")
                if not os.path.exists(user_dir):
                    os.makedirs(user_dir, exist_ok=True)
                user_file = os.path.join(user_dir, json_fileName)
                if not os.path.exists(user_file) and os.path.exists(json_fileName):
                    shutil.copy(json_fileName, user_file)

            logger.log(f"\nEmail_Read() read_JSON_File user_file ::: {user_file}")

            if os.path.exists(user_file):
                with open(user_file, "r") as fileObj:
                    file_JsonArray = json.load(fileObj)
                    
                    for eachJson in file_JsonArray :
                        for key, value in eachJson.items():
                            if key == "Category":
                                category_list.append(value)
                        # categories = ", ".join(category_list)
                        
                return file_JsonArray, category_list

            else:
                message = f"{user_file} file not found."
                raise Exception(message)
        except Exception as e:
            msg = f"'{json_fileName}' file is empty. Please provide JSON parameters in the filename."
            trace = traceback.format_exc()
            logger.log(f"Exception in writeJsonFile: {msg} \n {trace} \n DataType ::: {type(msg)}")
            raise Exception(msg)

    def log_email_login(self, user_id, email, model_name, login_status):
        base_dir="EMail_log"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = os.path.join(base_dir, user_id)
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"{user_id}.csv")

        log_exists = os.path.isfile(log_file_path)
        with open(log_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not log_exists:
                writer.writerow(["timestamp", "user_id", "email", "Model_Name", "login_status"])
            writer.writerow([timestamp, user_id, email, model_name, login_status])

    def update_status(self):
        global shared_status
        shared_status = False

    def read_status(self):
        global shared_status
        return shared_status
    
    def Extract_attachment_content(self,filename, content_bytes):
        extension = os.path.splitext(filename)[1].lower()

        try:
            if extension == ".pdf":
                # Extract text from PDF
                reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                return text if text.strip() else "[No text content found in PDF]"

            elif extension in [".docx", ".doc"]:
                # Extract text from Word document
                doc = docx.Document(io.BytesIO(content_bytes))
                text = "\n".join([para.text for para in doc.paragraphs])
                return text if text.strip() else "[No text content found in Word document]"

            elif extension in [".xls", ".xlsx"]:
                # Extract text from Excel sheet
                df = pd.read_excel(io.BytesIO(content_bytes), engine='openpyxl')
                return df.to_string(index=False)

            elif extension == ".csv":
                # Extract text from CSV file
                df = pd.read_csv(io.BytesIO(content_bytes))
                return df.to_string(index=False)

            elif extension in [".txt"]:
                # Decode plain text file
                return content_bytes.decode('utf-8', errors='replace')

            else:
                return "[Unsupported attachment type]"

        except Exception as e:
            return f"[Error extracting content: {str(e)}]"

   