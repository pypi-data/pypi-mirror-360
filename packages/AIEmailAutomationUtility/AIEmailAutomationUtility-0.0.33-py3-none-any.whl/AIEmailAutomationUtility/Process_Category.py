from .Email_DocumentUploader import Email_DocumentUploader
from .EmailReplyAssistant import EmailReplyAssistant
from http.cookies import SimpleCookie
from .Email_Draft import Email_Draft
import google.generativeai as genai
from email.utils import parseaddr
import loggerutility as logger
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
import mimetypes
import sqlite3
import openai
import json
import csv
import os
from email import message_from_string
import re

class Process_Category:

    def process_cat(self, category, dataValues):

        Model_Name = dataValues.get('Model_Name')
        file_JsonArray = dataValues.get('file_JsonArray')
        openai_api_key = dataValues.get('openai_api_key')
        openai_Process_Input = dataValues.get('openai_Process_Input')
        subject = dataValues.get('subject')
        sender_email_addr = dataValues.get('sender_email_addr')
        cc_email_addr = dataValues.get('cc_email_addr')
        email_body = dataValues.get('email_body')
        email_config = dataValues.get('email_config')
        msg = dataValues.get('msg')
        geminiAI_APIKey = dataValues.get('geminiAI_APIKey')
        localAIURL = dataValues.get('localAIURL')
        signature = dataValues.get('signature')
        LABEL = dataValues.get('LABEL')
        mail = dataValues.get('mail')
        email_id = dataValues.get('email_id')
        uid = dataValues.get('uid')
        to_email_addr =dataValues.get('to_email_addr')
        user_id =dataValues.get('user_id')
        date = msg.get('Date', '')
        is_html = dataValues.get('is_html')
        import_file = dataValues.get('import_file')

        customer_determination = None
        product_determination = None

        if category == "Product Enquiry":
            if Model_Name == "OpenAI":
                action_taken = "Reply email drafted using Open_AI Model"
                responseMethod, parameters = self.get_JsonArray_values(category, file_JsonArray)
                logger.log(f"the repsonse method is ::: {responseMethod}")
                if responseMethod == "Reply_Email_Ai_Assistant":
                    emailreplyassistant = EmailReplyAssistant()
                    openai_Response = emailreplyassistant.Reply_Email_Ai_Assistant(openai_api_key, parameters["Assistant_Id"], openai_Process_Input, subject)
                    logger.log(f"Process openai_Response ::: {openai_Response['message']}\n")
                    email_details = {"sender": sender_email_addr, "cc": cc_email_addr, "subject": subject, "body": email_body}
                    logger.log(f"response generated")
                    email_draft = Email_Draft()
                    status, response = email_draft.draft_email(email_config, email_details, openai_Response['message'])
                    logger.log(f"status ::: {status}")
                    logger.log(f"Email draft called")
                    csv_data_status = status
                    csv_data_response = response
                else:
                    message = f"Invalid response method received '{responseMethod}' for category : '{category}'"
                    raise ValueError(message)
            elif Model_Name == "LocalAI":
                action_taken = "Reply email drafted using Local_AI Model"
                logger.log("localAI")
                Detect_Email_category = False
                LocalAI_Response = category
                logger.log(f"Process LocalAI_Response ::: {LocalAI_Response}\n")
                email_details = {"sender": sender_email_addr, "cc": cc_email_addr, "subject": subject, "body": email_body}

                email_draft = Email_Draft()
                status, response = email_draft.draft_email(email_config, email_details, LocalAI_Response)
                logger.log(f"status ::: {status}")
                csv_data_status = status
                csv_data_response = response
            elif Model_Name == "GeminiAI":
                action_taken = "Reply email drafted using Gemini Model"
                logger.log("GeminiAI")
                Detect_Email_category = False
                GeminiAI_Response = category
                logger.log(f"Process GeminiAI_Response ::: {GeminiAI_Response}\n")
                email_details = {"sender": sender_email_addr, "cc": cc_email_addr, "subject": subject, "body": email_body}

                email_draft = Email_Draft()
                status, response = email_draft.draft_email(email_config, email_details, GeminiAI_Response)
                logger.log(f"status ::: {status}")
                csv_data_status = status
                csv_data_response = response
            else:
                raise ValueError(f"Invalid Model Name provided : '{Model_Name}'")

        elif category == "Purchase Order":
            action_taken = "Document uploaded"
            responseMethod, parameters = self.get_JsonArray_values(category, file_JsonArray)
            logger.log(f"responseMethod ::: {responseMethod}")
            logger.log(f"parameters ::: {parameters}")

            # Download the attachment
            fileName, document_type = self.download_attachment(msg)
            logger.log(f"fileName 107::: {fileName}")
            logger.log(f"document_type 108::: {document_type}")

            if responseMethod == "Upload_Document":

                email_upload_document = Email_DocumentUploader()
                if len(fileName) != 0 and document_type != '':
                    # Get today's date folder path
                    today_date = datetime.today().strftime('%Y-%m-%d')
                    order_folder = os.path.join(document_type, today_date)
                    
                    file_path = os.path.join(order_folder, fileName)  # Correct file path

                    with open(file_path, "rb") as file:
                        parameters["DOCUMENT_TYPE"] = document_type
                        
                        logger.log(f"Updated Parameters ::: {parameters}")
                        response_status, restAPI_Result = email_upload_document.email_document_upload(file, parameters)
                        logger.log(f"email_upload_document_response ::: {restAPI_Result}")
                else:
                    document_type = "Order Email"
                    # Get today's date folder path
                    today_date = datetime.today().strftime('%Y-%m-%d')
                    order_folder = os.path.join(document_type, today_date)

                    parameters["DOCUMENT_TYPE"] = document_type
                    logger.log(f"Updated Parameters ::: {parameters}")

                    email_parts = []
                    if sender_email_addr:
                        email_parts.append(f"From: {sender_email_addr}")
                    if to_email_addr:
                        email_parts.append(f"To: {to_email_addr}")
                    if cc_email_addr:
                        email_parts.append(f"CC: {cc_email_addr}")
                    if subject:
                        email_parts.append(f"Subject: {subject}")

                    email_parts.append(email_body)
                    email_body_with_details = "\n".join(email_parts)

                    logger.log(f"email_body ::: {email_body}")
                    new_fileName = self.create_file_from_emailBody(email_body_with_details, sender_email_addr, parameters)
                    new_file_path = os.path.join(order_folder, new_fileName)
                    
                    with open(new_file_path, "rb") as file:
                        response_status, restAPI_Result = email_upload_document.email_document_upload(file, parameters)
                        logger.log(f"email_upload_document_response ::: {restAPI_Result}")

                if response_status == "200":
                    logger.log(f"Attachment uploaded successfully against Document ID: '{restAPI_Result}'.")
                    csv_data_status="Success",
                    csv_data_response=f"Attachment uploaded successfully against Document ID: '{restAPI_Result}'"
                else:
                    logger.log(restAPI_Result)
                    csv_data_status="Fail",
                    csv_data_response=f"Attachment uploaded Failed against Document ID: '{restAPI_Result}'"
            else:
                message = f"Invalid response method received '{responseMethod}' for category : '{category}'"
                raise ValueError(message)

        elif category == "Quotation":
            action_taken = f"Mail drafted for products rate"
            responseMethod, parameters = self.get_JsonArray_values(category, file_JsonArray)
            logger.log(f"Inside Quotation")

            # Step 4: Identify customer from email using AI
            customer_data = self.identify_customer(email_body, subject, Model_Name, openai_api_key, geminiAI_APIKey, localAIURL, parameters["Customer_Assistant_Id"])
            logger.log(f"Identified customer is ::: {customer_data}")

            customer_determination=customer_data

            # Extract customer code once
            customer_code = customer_data.get("customer_code", "")

            # Step 5: Identify product from email using AI            
            #If there is attachment then append the content in the body.
            extracted_content = dataValues.get('extracted_content')
            logger.log(f"extracted_content is ::: {extracted_content}")
            if extracted_content != "NA" and extracted_content != None:
                attachment_email_body =email_body + " \n\n" + extracted_content
                products = self.identify_products(attachment_email_body, subject, Model_Name, openai_api_key, geminiAI_APIKey, localAIURL, parameters["Product_Assistant_Id"])
            else:
                products = self.identify_products(email_body, subject, Model_Name, openai_api_key, geminiAI_APIKey, localAIURL, parameters["Product_Assistant_Id"])
            
            logger.log(f'Identified Products are ::: {products}')

            product_determination=products

            db_connection = sqlite3.connect('database/fetchprice.db')
            for product in products:
                item_no = product.get("item_no", "").strip()
                make = product.get("make", "").strip()
                rate = None
                found_rate = False

                logger.log(f"item no is ::: {item_no}")
                logger.log(f"make is ::: {make}")

                # Step 1: Get base price from PRICE_LIST
                query_price = '''
                    SELECT PRICE 
                    FROM PRICE_LIST 
                    WHERE ITEM_NO = ?;
                '''
                cursor = db_connection.cursor()
                cursor.execute(query_price, (item_no,))
                price_result = cursor.fetchone()
                cursor.close()

                if price_result:
                    price_raw = price_result[0]
                    
                    if isinstance(price_raw, str):
                        # Clean the string: remove INR and commas
                        price_cleaned = price_raw.replace('INR', '').replace(',', '').strip()
                    else:
                        price_cleaned = price_raw  # already numeric

                    try:
                        raw_price = float(price_cleaned)
                        logger.log(f"Process_Category - Quotation [0] Base price for item '{item_no}' is {raw_price}")
                    except (TypeError, ValueError):
                        logger.log(f"Process_Category - Quotation [0] Invalid raw price for item '{item_no}': {price_result[0]}")
                        product["rate"] = None
                        continue
                else:
                    logger.log(f"Process_Category - Quotation [0] No base price found for item '{item_no}' .")
                    product["rate"] = "NA"
                    product["Price Pickup Source"]="NA" 
                    product["Discount"]="NA" 
                    continue

                # Condition 1: Exact match in special_rate_customer_wise
                query1 = '''
                    SELECT RATE 
                    FROM SPECIAL_RATE_CUSTOMER_WISE 
                    WHERE ITEM_CODE = ?
                    AND CUSTOMER_CODE = ?;
                '''
                cursor = db_connection.cursor()
                cursor.execute(query1, (item_no, customer_code))
                result = cursor.fetchone()
                cursor.close()

                if result:
                    rate = result[0]
                    found_rate = True
                    logger.log(f"Process_Category - Quotation [1] Special Rate for item '{item_no}' and customer '{customer_code}' is {rate}")
                    price_pickup_source="SPECIAL_RATE_CUSTOMER_WISE"
                    Discount="NA"

                # Condition 2: Customer + Manufacturer discount
                if not found_rate:
                    query2 = '''
                        SELECT DISCOUNT 
                        FROM CUSTOMER_WISE_DISCOUNT 
                        WHERE CUSTOMER_CODE = ? AND MAKE = ?;
                    '''
                    cursor = db_connection.cursor()
                    cursor.execute(query2, (customer_code, make))
                    discount_result = cursor.fetchone()
                    cursor.close()

                    if discount_result:
                        discount_percent = discount_result[0]
                        Discount= discount_percent
                        rate = raw_price * (1 - int(discount_percent) / 100)
                        rate = round(rate, 2)
                        found_rate = True
                        logger.log(f"Process_Category - Quotation [2] Discounted rate for '{make}' ({discount_percent}%) on price {raw_price}: {rate}")
                        price_pickup_source="CUSTOMER_WISE_DISCOUNT"

                # Condition 3: Past Sales most used make
                if not found_rate:
                    query3 = '''
                        SELECT MAKE, MAX(DISCOUNT)
                        FROM PAST_SALES
                        WHERE CUSTOMER_CODE = ?
                        AND ITEM_CODE = ?
                        GROUP BY MAKE
                        ORDER BY COUNT(*) DESC
                        LIMIT 1;
                    '''
                    cursor = db_connection.cursor()
                    cursor.execute(query3, (customer_code, item_no))
                    past_sales_result = cursor.fetchone()
                    cursor.close()

                    if past_sales_result:
                        most_common_make, past_discount = past_sales_result
                        Discount=past_discount
                        if isinstance(raw_price, (int, float)):
                            rate = raw_price * (1 - int(past_discount) / 100)
                            rate = round(rate, 2)
                            found_rate = True
                            logger.log(f"Process_Category - Quotation [3] Fallback: Most used make '{most_common_make}' for customer '{customer_code}' got {past_discount}% discount. Rate: {rate}")
                            price_pickup_source="PAST_SALES"
                        else:
                            logger.log(f"Process_Category - Quotation [3] Fallback: Invalid price for item '{item_no}'")
                   
                # Condition 4: Manufacturer General Discount
                if not found_rate:
                    query4 = '''
                        SELECT GENERAL_DISCOUNT 
                        FROM MANUFACTURE_WISE_GENERAL_DISCOUNT 
                        WHERE MAKE = ?;
                    '''
                    cursor = db_connection.cursor()
                    cursor.execute(query4, (make,))
                    general_discount_result = cursor.fetchone()
                    cursor.close()

                    if general_discount_result:
                        general_discount_percent = general_discount_result[0]
                        Discount=general_discount_percent
                        rate = raw_price * (1 - int(general_discount_percent) / 100)
                        rate = round(rate, 2)
                        found_rate = True
                        logger.log(f"Process_Category - Quotation [4] General Discount for '{make}' ({general_discount_percent}%) on price {raw_price}: {rate}")
                        price_pickup_source="MANUFACTURE_WISE_GENERAL_DISCOUNT"
                                   
                #Condition 5: Fallback to raw_price if no discount applied
                if not found_rate:
                    rate = raw_price
                    logger.log(f"Process_Category - Quotation [5] No discounts applied. Using base price for item '{item_no}': {rate}")
                    price_pickup_source="PRICE_LIST"
                    Discount = "NA"

                product["rate"] = rate
                product["Price Pickup Source"]=price_pickup_source 
                product["Discount"]=Discount 

            db_connection.close()

            logger.log(f"Identified products: {products}")
            logger.log(f"Identified products length: {len(products)}")
            quotation_draft = self.generate_quotation_draft(
                customer_data, 
                products,
                Model_Name, 
                openai_api_key, 
                geminiAI_APIKey, 
                localAIURL,
                parameters["Customer_Assistant_Id"],
                email_body, 
                subject,
                signature
            )
            logger.log(f"quotation_draft ::: {quotation_draft}")

            # Step 8: Send draft quotation email
            email_details = {"sender": sender_email_addr, "cc": cc_email_addr, "subject": subject, "body": email_body}
            email_draft = Email_Draft()
            status, response = email_draft.quotation_draft_email(email_config, email_details, quotation_draft)
            logger.log(f"status ::: {status}")

            csv_data_status = status
            csv_data_response = response
            logger.log(f"Quotation email sent to {sender_email_addr}")

        elif category == "Others" and import_file == True:
            action_taken = "-"
            csv_data_status = "Fail"
            csv_data_response = f"-"
        else:
            action_taken = f"Saved the mail to the label: {LABEL}"
            csv_data_status = "Success"
            csv_data_response = f""

            logger.log(f"Marking email as UNREAD. ")
            # print(f"email_id: {email_id}, type: {type(email_id)}")
            mail.store(email_id, '-FLAGS', '\\Seen')
            mail.create(LABEL)
            mail.copy(email_id, LABEL)
            mail.store(email_id, '+FLAGS', '\\Deleted')  # Mark for deletion
            mail.expunge()   
            logger.log(f"Mail removed from inbox and added to '{LABEL}' label.")

        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'{uid}{current_timestamp}'
        logger.log(f"The file name for csv and eml is ::: {filename}")
        self.store_email_details_to_csv(
            email_id=f'{uid}{current_timestamp}',
            to_email=parseaddr(to_email_addr)[1],
            from_email=parseaddr(sender_email_addr)[1],
            cc_email=parseaddr(cc_email_addr)[1] if cc_email_addr else '',
            subject=subject,
            body=email_body,
            email_type=category,
            action_performed=action_taken,
            filename=filename,
            user_id=user_id,
            status=csv_data_status,
            response=csv_data_response,
            current_timestamp=current_timestamp,
            customer_determination=customer_determination,
            product_determination=product_determination,
        )
        self.store_email_as_eml(
            uid=f'{uid}{current_timestamp}',
            from_email=sender_email_addr,
            to_email=to_email_addr,
            cc_email=cc_email_addr,
            subject=subject,
            date=date,
            body_content=email_body,
            is_html=is_html,
            filename=filename,
            user_id=user_id
        )    

    def get_JsonArray_values(self, category, jsonArray):
        responseMethod  = ""
        parameters      = ""
        
        for eachJson in jsonArray :
            for key, value in eachJson.items():
                if value == category:
                    responseMethod  = eachJson["Response_Method"]  
                    parameters      = eachJson["Parameters"]
        
        return responseMethod, parameters
    
    def download_attachment(self, msg):

        filename = ""
        mime_type = ""
        document_type = ""

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            mime_type = part.get_content_type().lower()

            if "pdf" in mime_type or filename.lower().endswith(".pdf"):
                document_type = "Orders"
            elif "msword" in mime_type or "wordprocessingml" in mime_type or filename.lower().endswith(".docx"):
                document_type = "Order Excel"
            elif "excel" in mime_type or "spreadsheetml" in mime_type or filename.lower().endswith((".xls", ".xlsx")):
                document_type = "Order Excel"
            elif "csv" in mime_type or filename.lower().endswith(".csv"):
                document_type = "Order Excel"
            elif "plain" in mime_type or filename.lower().endswith(".txt"):
                document_type = "Order Email"
            elif "rtf" in mime_type or filename.lower().endswith(".rtf"):
                document_type = "Order Excel"

            if filename:
                today_date = datetime.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
                date_folder = os.path.join(document_type, today_date)  # Path: ORDERS/YYYY-MM-DD
                os.makedirs(date_folder, exist_ok=True)

                filepath = os.path.join(date_folder, filename)  # Save inside date-wise folder

                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                logger.log(f"\nAttachment saved: '{filepath}'")
            else:
                logger.log("\nNo Attachment found.")
        return filename, document_type
    
    def create_file_from_emailBody(self, text, sender_email_addr, parameters):
        base_folder = parameters.get('DOCUMENT_TYPE', '')
        today_date = datetime.today().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
        order_folder = os.path.join(base_folder, today_date)

        # Ensure the date-wise folder exists
        os.makedirs(order_folder, exist_ok=True)

        # Generate filename from sender's email
        fileName = sender_email_addr[sender_email_addr.find("<")+1:sender_email_addr.find("@")].strip().replace(".","_")
        
        if parameters["FILE_TYPE"] == "pdf":
            fileName = fileName + ".pdf"
            filePath = os.path.join(order_folder, fileName)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
            pdf.output(filePath)
            logger.log(f"New PDF file created from email body and stored in '{filePath}'")

        elif parameters["FILE_TYPE"] == "txt":
            fileName = fileName + ".txt"
            filePath = os.path.join(order_folder, fileName)

            with open(filePath, "w", encoding="utf-8") as file:
                file.write(text)
                logger.log(f"New TXT file created from email body and stored in '{filePath}'")
        else:
            message = f"Invalid File Type received."
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        return fileName
    
    def identify_customer(self, email_body, subject, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id):
        logger.log("Inside identify_customer")        
        
        if model_type == "OpenAI":
            prompt = f"""/* Identify the most likely customer code, customer name from the following email using the file attached in assistant. Use various key information's such as sender name, organisation, address, email id to determine the customer. If customer not available in the data return the name and NA as code. Return the data in json format. Always return 1 row. Do not include any instruction as the output will be directly in a program. */ /n {email_body}"""
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.identify_customer_product_reply_assitant(openai_api_key, assistant_id, email_body, subject, prompt)
         
        elif model_type == "GeminiAI": 
            prompt = f"""Identify the customer code, customer name in json format from the following email {email_body} and received from {subject}. Do not include any instruction as the output will be directly in a program."""
            ai_result = self.identify_customer_product_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""Identify the customer code and customer name in JSON format from the following email: {email_body}, received from {subject}. 
            If no customer details are found, return:{{"customer_name": "","customer_code": ""}}Only return the JSON object. No explanations, no additional text."""
            ai_result = self.identify_customer_product_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "{}"
        
        customer_data = {}
        if ai_result["status"] == "Success":
            customer_data = json.loads(ai_result["message"])
        else:            
            customer_data = {
                "customer_name": "",
                "customer_code": ""
            }
        return customer_data
    
    def identify_products(self, email_body, subject, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id):
        logger.log("Inside identify_products")    
        
        if model_type == "OpenAI":
            prompt = f"""/* Extract complete item pricing information from the following mixed-format email content. The email may contain a combination of:- descriptive product listings- tabular structured price info- semi-structured lines with HSN, quantity, material, etc. Give me price in INR and information of all items in following format requested_description, item_no, make, description, price, Quantity, price unit, inventory unit strictly in JSON format. If the item is not available in the assistant files return requested description from email data and rest of the columns as NA. Do not include any instruction as the output will be directly in a program. */ /n {email_body}. """
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.identify_customer_product_reply_assitant(openai_api_key, assistant_id, email_body, subject, prompt)

        elif model_type == "GeminiAI":
            prompt = f"""
                Can you give me price information of all products in following format requested_description, item_no, make, description, price, price unit, inventory unit for following items in strictly in JSON String format {email_body}. 
                If there is one product or multiple should return in list. 
                Do not include any instruction as the output will be directly in a program.
                """
            ai_result = self.identify_customer_product_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""Can you give me price information in following format requested_description, item_no, make, description, price, price unit, inventory unit for following items it strictly in json format which loads directly in json {email_body}. If there is one product or multiple should return in list. 
            If no product details are found, return:[] Only return the JSON object. No explanations, no additional text."""
            ai_result = self.identify_customer_product_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "{}"
        
        product_data = {}
        if ai_result["status"] == "Success":
            logger.log(f"ai_result ::: {ai_result}")   
            product_data = json.loads(ai_result["message"])
        else:            
            product_data = []
        return product_data
    
    def generate_quotation_draft(self, customer_data, products, model_type, openai_api_key, gemini_api_key, local_ai_url, assistant_id, email_body, subject, signature):
        
        customer = customer_data
        
        product_table = "Products:\n"
        for product in products:
            rate = product.get("rate", "NA")
            quantity = product.get("Quantity", "NA")
            try:
                total = float(rate) * float(quantity)
            except:
                total = rate if rate != "NA" and rate not in ("", None) else "-"
            product_table += (
                f'- Requested Description: {product.get("requested_description", "-")}, '
                f'Item Code: {product.get("item_no", "-")}, '
                f'Item Description: {product.get("description", "-")}, '
                f'Manufacturer: {product.get("make", "-")}, '
                f'Price: {product.get("price", "-")}, '
                f'Inventory Unit: {product.get("inventory unit", "-")}, '
                f'Discount: {product.get("Discount", "-")}, '
                f'Rate: {rate}, '
                f'Quantity: {quantity}, '
                f'Total: {total}, '
                f'Price Pickup Source: {product.get("Price Pickup Source", "-")}, '
                f'Availability: ""\n'
            )
        
        if model_type == "OpenAI":
            prompt = f"""
                Generate product information in HTML tabular format with line separators for rows and columns in a draft reply based on the following information:

                Customer: {customer.get('customer_name', '')}  
                Customer Code: {customer.get('customer_code', '')}  

                {product_table}  
                Ensure the table has the following columns in this exact order:
                Sr. No., Requested Description, Item Code, Item Description, Manufacturer,  Price, Inventory Unit, Discount, Rate, Quantity, Total, Price Pickup Source, Availability

                - If any value is missing, use a dash ("-") instead.
                - "Total" is calculated as Rate × Quantity.
                - "Availability" should be a blank column.
                Original Email Subject: {subject}  

                Return only the following JSON String format:
                {{
                    "email_body": {{
                        "body": "Draft email body proper response, It should not be same like mail content and does not having any signature part like Best regards.",
                        "table_html": "Table Details with Sr. No. in HTML",
                        "signature": "{signature}"
                    }}
                }}

                Do not include signature in body and any instructions, explanations, or additional text—only the JSON object.
            """
            logger.log(f"Quotation draft ::: {prompt}")
            emailreplyassistant = EmailReplyAssistant()
            ai_result = emailreplyassistant.create_quotation_draft(openai_api_key, assistant_id, email_body, subject, prompt)   

        elif model_type == "GeminiAI":
            prompt = f"""
                Create an HTML product information email draft with the following details:

                Customer Name: {customer.get('customer_name', '')}
                Customer Code: {customer.get('customer_code', '')}

                Product Information:
                {product_table}
                Note: Include price column with a value of "-" if price is not available.

                Email Subject Reference: {subject}

                Please format the response as a valid JSON string with these fields:
                {{
                    "email_body": {{
                        "body": "Professional email content that summarizes the product information without being identical to the input data. Do not include signature here.",
                        "table_": "HTML table with SR. No. column and product details",
                        "signature": "{signature}"
                    }}
                }}

                Ensure the JSON is properly formatted with escaped newlines (\\n) and no trailing commas. Return only the valid JSON string without additional explanations or instructions.
            """
            logger.log(f"Quotation draft ::: {prompt}")
            ai_result = self.create_quotation_draft_GeminiAI(gemini_api_key, email_body, prompt)

        elif model_type == "LocalAI":
            prompt = f"""
                Generate product information in HTML tabular format with line separators for rows and columns in a draft reply based on the following information:

                Customer: {customer.get('customer_name', '')}  
                Customer Code: {customer.get('customer_code', '')}  

                {product_table}  
                - The table must contain the **Price** column, even if it is empty (set it as `-` if None).  
                - The table should include **Sr. No.** as the first column.  
                - Format the table with `<table>`, `<tr>`, `<th>`, and `<td>` tags with some border to table.

                Original Email Subject: {subject}  

                Return **strictly** in the following JSON String format:
                - All keys must be: `body`, `table_`, and `signature` inside the `email_body` JSON.  
                - **Do not include** `\n`, `\`, `\\`, or any unnecessary escape characters.  
                - Do not include instructions, explanations, or additional text—only the JSON object.  

                Format:
                {{
                    "email_body": {{
                        "body": "Draft email body proper response, It should not contain the table or signature.",
                        "table_": "Table Details with Sr. No. in HTML only",
                        "signature": "{signature}"
                    }}
                }}
            """
            logger.log(f"Quotation draft ::: {prompt}")
            ai_result = self.create_quotation_draft_LocalAI(openai_api_key, email_body, local_ai_url, prompt)

        else:
            ai_result = "Error: Unable to generate quotation draft. Please check the configuration."
        
        logger.log(f"Quotation draft ai_result::: {ai_result}")
        quotation_draft_data = None
        if ai_result != None:
            quotation_draft_data = json.loads(ai_result)["email_body"]
        return quotation_draft_data

    def identify_customer_product_LocalAI(self, openai_api_key, email_body, local_ai_url, prompt):
        logger.log("Inside identify_customer_product_LocalAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Local AI message for detecting category::: {message}")
            openai.api_key = openai_api_key
            client = OpenAI(base_url=local_ai_url, api_key="lm-studio")
            completion = client.chat.completions.create(
                model="mistral",
                messages=message,
                temperature=0,
                stream=False,
                max_tokens=4096
            )

            final_result = str(completion.choices[0].message.content)
            final_result = final_result.replace("\n```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","").replace("html","")
            logger.log(f"finalResult:520  {final_result}")
            return {"status": "Success", "message": final_result}

        except Exception as e:
            logger.log(f"Error with LocalAI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with LocalAI detection/generation: {str(e)}"}
        
    def create_quotation_draft_LocalAI(self, openai_api_key, email_body, local_ai_url, prompt):
        logger.log("Inside create_quotation_draft_LocalAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Local AI message for detecting category::: {message}")
            openai.api_key = openai_api_key
            client = OpenAI(base_url=local_ai_url, api_key="lm-studio")
            completion = client.chat.completions.create(
                model="mistral",
                messages=message,
                temperature=0,
                stream=False,
                max_tokens=4096
            )

            final_result = str(completion.choices[0].message.content)
            final_result = final_result.replace("\n```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","").replace("html","")
            logger.log(f"finalResult:520  {final_result}")
            return final_result

        except Exception as e:
            logger.log(f"Error with LocalAI detection/generation: {str(e)}")
            return str(e)
        
    def identify_customer_product_GeminiAI(self, gemini_api_key, email_body, prompt):
        logger.log("Inside identify_customer_product_GeminiAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Gemini AI message for detecting category::: {message}")
            message_list = str(message)

            genai.configure(api_key=gemini_api_key)
            # model = genai.GenerativeModel('gemini-1.0-pro')
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(message_list)
            
            final_result = ""
            for part in response:
                final_result = part.text
                logger.log(f"response:::  {final_result}")
                if final_result:
                    try:
                        final_result = final_result.replace("\\", "").replace('```', '').replace('json', '')
                        if final_result.startswith("{{") and final_result.endswith("}}"):
                            final_result = final_result[1:-1]
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {final_result} {type(final_result)}")

            logger.log(f"finalResult:::  {final_result}")
            return {"status": "Success", "message": final_result}

        except Exception as e:
            logger.log(f"Error with Gemini AI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with Gemini AI detection/generation: {str(e)}"}
        
    def create_quotation_draft_GeminiAI(self, gemini_api_key, email_body, prompt):
        logger.log("Inside identify_customer_product_GeminiAI")   
        try:
            message = [{
                "role": "user",
                "content": f"{prompt}"
            }]

            logger.log(f"Final Gemini AI message for detecting category::: {message}")
            message_list = str(message)

            genai.configure(api_key=gemini_api_key)
            # model = genai.GenerativeModel('gemini-1.0-pro')
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(message_list)
            
            final_result = ""
            for part in response:
                final_result = part.text
                logger.log(f"response:::  {final_result}")
                if final_result:
                    try:
                        final_result = final_result.replace('```', '').replace('json', '')
                        if final_result.startswith("{{") and final_result.endswith("}}"):
                            final_result = final_result[1:-1]
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {final_result} {type(final_result)}")

            logger.log(f"finalResult:::  {final_result}")
            return final_result

        except Exception as e:
            logger.log(f"Error with Gemini AI detection/generation: {str(e)}")
            return {"success": "Failed", "message": f"Error with Gemini AI detection/generation: {str(e)}"}
        
    def store_email_details_to_csv(self, email_id, to_email, from_email, cc_email, subject, body, email_type, action_performed, filename, user_id,status,response,current_timestamp,customer_determination,product_determination):
        """
        Stores the extracted email details to a CSV file inside 'Mail_log/mail_log_user_id' folder
        with the name user_id.csv.
        """

        logger.log(f"The response am getting in csv is : {response}")
        match = re.search(
            r'Content-Transfer-Encoding:\s*base64\s+([\s\S]+?)\n--',
            response,
            re.IGNORECASE
        )
        if match:
            response = self.extract_html_from_mime(response)
                
        logger.log(f"The response after am getting in csv is : {response}")

        # Ensure the Mail_log folder exists
        log_folder = "Mail_log"
        os.makedirs(log_folder, exist_ok=True)

        # Create the mail_log_user_id folder inside 'Mail_log' if it doesn't exist
        user_folder = os.path.join(log_folder, f"{user_id}")
        os.makedirs(user_folder, exist_ok=True)

        filename = filename.lstrip()
        full_csv_path = os.path.join(user_folder, f"{filename}.csv")

        if email_type=="Quotation":
            csv_data = [{
            'to': to_email,
            'from': from_email,
            'cc': cc_email,
            'subject': subject,
            'body': body.replace('\n', ' ').replace('\r', ''),
            'Category': email_type,
            'Action Performed': action_performed,
            'unique_id': email_id,
            'timestamp': current_timestamp,
            'status of mail draft': status,
            'Response Generated':response,
            'Customer Determination':customer_determination,
            'Product Determination':product_determination,
        }]
        else:
            csv_data = [{
                'to': to_email,
                'from': from_email,
                'cc': cc_email,
                'subject': subject,
                'body': body.replace('\n', ' ').replace('\r', ''),
                'Category': email_type,
                'Action Performed': action_performed,
                'unique_id': email_id,
                'timestamp': current_timestamp,
                'status of mail draft': status,
                'Response Generated':response
            }]
        
        # Write to CSV file (user_id.csv)
        with open(full_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            if email_type == "Quotation":
                fieldnames = [
                    'to', 'from', 'cc', 'timestamp', 'subject', 'body',
                    'Category', 'Action Performed', 'unique_id',
                    'status of mail draft', 'Response Generated',
                    'Customer Determination', 'Product Determination'
                ]
            else:
                fieldnames = [
                    'to', 'from', 'cc', 'timestamp', 'subject', 'body',
                    'Category', 'Action Performed', 'unique_id',
                    'status of mail draft', 'Response Generated'
                ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # If the file is empty, write the header
            if os.stat(full_csv_path).st_size == 0:
                writer.writeheader()
            
            # Write the email data
            writer.writerows(csv_data)

        # Log the action
        logger.log(f"Email with ID '{email_id}' details appended to {full_csv_path}")

    def store_email_as_eml(self, uid, from_email, to_email, cc_email, subject, date, body_content,filename,user_id,is_html=False,):
        """
        Stores a simplified EML-style email as a .eml file inside 'Mail_Formats' folder.

        Args:
            uid (str): Unique ID of the email.
            from_email (str): Sender email.
            to_email (str): Recipient email.
            cc_email (str): CC email.
            subject (str): Subject of the email.
            date (str): Date of the email.
            body_content (str): Email body content.
            is_html (bool): Whether the body_content is in HTML format.
        """
        archive_folder = "Mail_Formats"
        user_folder = os.path.join(archive_folder, f"{user_id}")
        os.makedirs(user_folder, exist_ok=True)

        filename = filename.lstrip()
        # Define the full path for the CSV file (csv_filename.csv inside the mail_log_user_id folder)
        eml_file_path = os.path.join(user_folder, f"{filename}.eml")

        try:
            with open(eml_file_path, 'w', encoding='utf-8') as eml_file:
                eml_file.write(f"From: {from_email}\n")
                eml_file.write(f"To: {to_email}\n")
                if cc_email:
                    eml_file.write(f"Cc: {cc_email}\n")
                eml_file.write(f"Subject: {subject}\n")
                eml_file.write(f"Date: {date}\n")
                eml_file.write(f"MIME-Version: 1.0\n")
                
                if is_html:
                    eml_file.write(f"Content-Type: text/html; charset=utf-8\n\n")
                    eml_file.write(body_content)
                else:
                    eml_file.write(f"Content-Type: text/plain; charset=utf-8\n\n")
                    eml_file.write(body_content)

            logger.log(f"Stored simplified EML file for UID '{uid}' at {eml_file_path}")

        except Exception as e:
            logger.log(f"Failed to save EML for UID '{uid}': {str(e)}")


            """Retrieves the user ID from the session or cookies."""
            # For simplicity, let's assume we get the user_id from cookies
            if "Cookie" in self.headers:
                cookie = SimpleCookie(self.headers["Cookie"])
                user_id = cookie.get("user_id")  # Assuming user_id is stored in a cookie
                if user_id:
                    return user_id.value
            return None

    def extract_html_from_mime(self, raw_data):
        msg = message_from_string(raw_data)

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_encoding = part.get("Content-Transfer-Encoding", "").lower()

                # Look for text/html part with base64 encoding
                if content_type == "text/html" and content_encoding == "base64":
                    payload = part.get_payload(decode=True)
                    return payload.decode(part.get_content_charset() or 'utf-8')
        return "No HTML content found."
   
