from dnalib.log import log
from dnalib.utils import Utils
import ssl
from ftplib import FTP_TLS
from io import BytesIO


class FTP:
    def __init__(self, username, password, host, port, max_retry=10, max_seconds_retry_delay=10):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.max_retry = max_retry
        self.max_seconds_retry_delay = max_seconds_retry_delay    
        self.connection = None

    def connect(self):
        context_ssl = ssl.create_default_context()
        context_ssl.set_ciphers('DEFAULT:@SECLEVEL=1')
        context_ssl.check_hostname = False
        context_ssl.verify_mode = ssl.CERT_NONE

        current_retry = 0
        currently_error = ""
        for retry in range(0, self.max_retry):            
            try:
                self.connection = FTP_TLS(context=context_ssl)
                self.connection.connect(self.host, self.port)
                self.connection.auth()
                self.connection.prot_p()
                self.connection.login(self.username, self.password)
                self.connection.encoding = 'latin-1'
                break
            except Exception as e:
                time.sleep(self.max_seconds_retry_delay)
                currently_error = e
                current_retry = current_retry + 1
            if current_retry == self.max_retry:
                log(__name__).error(f"You reached max number of retry, you must have some problem in connection:\n {currently_error}")            
                raise Exception(f"You reached max number of retry, you must have some problem in connection:\n {currently_error}")      
        log(__name__).info(f"Sucessfully connected to {self.host} with user {self.username}.")
        return self


    def list_files(self, path):
        for files in self.connection.nlst(path):
            yield files

    def download_and_save(self, remote_dir, filenames, external_path):
        """
        Download files from FTP and save in external_path
        """
        self.connection.cwd(remote_dir)
        for filename in filenames:
            try:
                buffer = BytesIO()
                buffer.truncate(0)
                log(__name__).info(f"Downloading file: {filename}.")
                self.connection.retrbinary(f"RETR {filename}", buffer.write)
                buffer.seek(0)
                tmp_path = f"/tmp/{filename}"
                with open(f"{tmp_path}", "wb") as f:
                    f.write(buffer.read())
                Utils.dbutils().fs.cp(f"file://{tmp_path}", external_path)          
            except Exception as e:
                log(__name__).error(f"Error copying file {filename} from {self.host}:\n {e}")
                raise Exception(f"Error copying file {filename} from {self.host}:\n {e}")
            log(__name__).info(f"Sucessfully copied file {filename} at {external_path}.")
        return self
