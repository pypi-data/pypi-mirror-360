from dnalib.log import log
from datetime import datetime
import pytz
import time
import pysftp
import pandas as pd
from io import StringIO


class Sftp:

    def __init__(self, username, password, host, port, max_retry=10, max_seconds_retry_delay=10):
        """ """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.max_retry = max_retry
        self.max_seconds_retry_delay = max_seconds_retry_delay    
        self.connection = None

    def connect(self):             
        """ """
        # Set hostkeys to None to disable host key checking   
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        # Count number of retries
        current_retry = 0
        currently_error = ""
        for retry in range(0, self.max_retry):            
            try:
                self.connection = pysftp.Connection(host=self.host, username=self.username, password=self.password, port=self.port, cnopts=cnopts)
                break
            except Exception as e:
                time.sleep(self.max_seconds_retry_delay)
                currently_error = e
                current_retry = current_retry + 1
        # If max retries is reached, raise an exception
        if current_retry == self.max_retry:
            log(__name__).error(f"You reached max number of retry, you must have some problem in connection:\n {currently_error}")            
            raise Exception(f"You reached max number of retry, you must have some problem in connection:\n {currently_error}")
        # if not happn we are sucessfully connected        
        log(__name__).info(f"Sucessfully connected to {self.host} with user {self.username}.")
        return self

    def listdir(self, remote_path):
        """ """
        for directory in self.connection.listdir(remote_path):
            yield directory

    def listdir_attr(self, remote_path):
        """ """
        for attr in self.connection.listdir_attr(remote_path):
            yield attr

    def disconnect(self):
        """ """
        self.connection.close()
        log(__name__).info(f"Disconnected from {self.host}.")    
        return self
    
    def add_watermark(self, remote_path):
        tz = pytz.timezone('America/Sao_Paulo')
        watermark = datetime.now(tz).strftime('%Y%m%d%H%M%S') 
        file_split = remote_path.rsplit(".", 1)
        return f"{file_split[0]}_{watermark}.{file_split[1]}"
    
    def remove(self, *files):
        """  """
        for file in files:
            try:
                self.connection.remove(file)
            except Exception as e:
                log(__name__).warning(f"Unable to remove file {file}:\n {e}")
        return self

    def upload(self, source_local_path, remote_path, include_watermark=True):
        """ """
        if include_watermark:
            remote_path = self.add_watermark(remote_path)
        try:
            # upload file to SFTP
            log(__name__).info(f"Uploading {source_local_path} to {remote_path}")
            self.connection.put(source_local_path, remote_path)            
        except Exception as e:
            log(__name__).error(f"Unable to upload file {source_local_path} to {remote_path}:\n {e}")
            raise Exception(f"Unable to upload file {source_local_path} to {remote_path}:\n {e}")
        log(__name__).info(f"Sucessfully uploaded {source_local_path} to {remote_path}")
        return self
    
    def read_csv(self, remote_path, sep=';', decode='utf-8', **read_csv_kwargs):
        """ """
        try:
            with self.connection.open(remote_path, mode='r') as remote_file:
                content = remote_file.read().decode(decode)
                df = pd.read_csv(StringIO(content), sep=sep, **read_csv_kwargs)
        except Exception as e:
            log(__name__).error(f"Unable to read file {remote_path}:\n {e}")
            raise Exception(f"Unable to read file {remote_path}:\n {e}")
        log(__name__).info(f"Sucessfully read file {remote_path}")
        return df
    
class MftSftp(Sftp):

    def __init__(self, username, password, **kwargs):
        super().__init__(username, password, "mft.portoseguro.brasil", 2022, **kwargs)
        