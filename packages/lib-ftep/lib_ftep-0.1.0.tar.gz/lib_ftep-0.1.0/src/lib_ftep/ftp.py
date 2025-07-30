import os
import logging
from ftplib import FTP
from io import BytesIO
from lib_invoice import Invoice
from lib_idoc import IDOC

logger = logging.getLogger(__name__)

class FTP_:
    def __init__(self):
        self.ftp_hostname = os.getenv('FTP_HOSTNAME')
        self.ftp_username = os.getenv('FTP_USERNAME')
        self.ftp_password = os.getenv('FTP_PASSWORD')
        self.ftp_location_idoc = os.getenv('FTP_LOCATION_IDOC')
        self.ftp_location_pdf = os.getenv('FTP_LOCATION_PDF')
        self.ftp = None

    def connect(self):
        """Connects to the FTP server."""
        self.ftp = FTP(self.ftp_hostname)
        self.ftp.login(self.ftp_username, self.ftp_password)

    def upload_idoc(self, idoc: IDOC):
        """Uploads a file to the FTP server."""
        self.ftp.cwd(self.ftp_location_idoc)
        stream = BytesIO(idoc.xml.encode('utf-8'))
        self.ftp.storbinary(f"STOR {idoc.xml_filename}", stream)
        logger.info(f"Uploaded idoc: {idoc.xml_filename}")

    def upload_pdf(self, invoice: Invoice):
        """Uploads a file to the FTP server."""
        self.ftp.cwd(self.ftp_location_pdf)
        stream = BytesIO(invoice.pdf)
        self.ftp.storbinary(f"STOR {invoice.pdf_filename}", stream)
        logger.info(f"Uploaded pdf: {invoice.pdf_filename}")