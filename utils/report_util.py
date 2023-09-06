import xlsxwriter
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import smtplib

class RepotUtil:
    def __init__(self, list_data, email):
        self.data = list_data
        self.email = email
        self._losttoexe(self.data)
        self.sendmail(self.email)
        
    def _losttoexe(self, new_list):
        #print(len(self.data.keys()), self.data.rowcount)
        #new_list.insert(0, tuple(new_list.keys()))

        with xlsxwriter.Workbook('report_exise.xlsx') as workbook:
            worksheet = workbook.add_worksheet()
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            time_format = workbook.add_format({'num_format': 'hh:mm:ss'})
            worksheet.set_column('G:G', None, date_format)
            worksheet.set_column('H:H', None, time_format)
            worksheet.write_row(0, 0, new_list.keys())
            for row_num, data in enumerate(new_list,1):
                worksheet.write_row(row_num, 0, data)
            worksheet.autofit()

            worksheet.autofilter(0, 0, new_list.rowcount - 1, len(new_list.keys()) - 1)  
    def sendmail(self, to):
        host = "smtp2.lvivcold.com.ua"
        server = smtplib.SMTP(host,port='25')
        FROM = "lkhadmin@lvivkholod.com"
        msg = MIMEMultipart()
        msg['Subject'] = f"Інформація про сканування акцизних марок за {(datetime.today() - timedelta(days=1)).strftime('%d.%m.%Y')}"
        #msg.attach(MIMEText("Інформація про сканування акцизних марок за..."))
        filename = "report_exise.xlsx"
        attachment = open(filename, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename}")
        msg.attach(part)
        msg['To'] = ", ".join(to)
        server.sendmail(FROM, to, msg.as_string())
        server.quit()