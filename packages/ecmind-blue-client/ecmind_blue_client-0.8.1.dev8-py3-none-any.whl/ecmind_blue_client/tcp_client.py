import base64
import hashlib
import logging
import socket
import os
from random import randint

from ecmind_blue_client.blue_exception import BlueException

from ecmind_blue_client.client import Client
from ecmind_blue_client.job import Job
from ecmind_blue_client.result import Result
from ecmind_blue_client.tcp_client_classes.job_caller import JobCaller


class TcpClient(Client):
    @staticmethod
    def encrypt_password(password: str) -> str:
        if password is None or password == "":
            raise ValueError("Password must not be empty")

        def create_random_char():
            return chr(ord("0") + (randint(0, 32000) % 8))

        plen = len(password)
        nmax = 4 * plen * 2
        ioff = randint(0, 32000) % max(1, nmax - plen * 3 - 3)
        cryptid = chr(ord("A") + plen) + chr(ord("A") + ioff)
        for _ in range(0, ioff):
            cryptid += create_random_char()

        def replace_in_string(i: int, c: str):
            return cryptid[:i] + c + cryptid[i + 1 :]

        for i in range(0, plen):
            j = 2 + ioff + i * 3
            oct_part = ioff + ord(password[i])
            oct_data = f"{oct_part:03o}"
            for k in range(0, 3):
                cryptid = replace_in_string(j + k, oct_data[k])

        for i in range(2 + ioff + 3 * plen, nmax):
            cryptid = replace_in_string(i, create_random_char())

        try:
            cryptid.encode("ascii")
            return cryptid
        except ValueError as ex:
            logging.debug(ex)
            return TcpClient.encrypt_password(password)

    @staticmethod
    def reveal(s: str, k=None):
        k = hashlib.md5(os.environ.get("ECMIND_KEY", k or "").encode()).hexdigest()
        try:
            d = []
            r = base64.b85decode(s).decode()
            for i, char in enumerate(r):
                c = k[i % len(k)]
                b = chr((256 + ord(char) - ord(c)) % 256)
                d.append(b)
            return "".join(d)
        except Exception:
            return s

    def __attach__(self, username: str, password: str):
        session_attach_job = Job("krn.SessionAttach", Flags=0, SessionGUID="")
        session_attach_result = self.execute(session_attach_job)
        self.session_guid = session_attach_result.values["SessionGUID"]

        session_properties_set_job = Job(
            "krn.SessionPropertiesSet",
            Flags=0,
            Properties="instname;statname;address",
            address=f"{socket.gethostbyname(socket.gethostname())}=dummy",
            instname=self.appname,
            statname=socket.gethostname(),
        )
        _session_properties_set_result = self.execute(session_properties_set_job)

        session_login_job = Job(
            "krn.SessionLogin",
            Flags=0,
            UserName=username,
            UserPwd=TcpClient.encrypt_password(TcpClient.reveal(password)),
        )
        session_login_result = self.execute(session_login_job)

        if session_login_result.values["Description"] is not None and session_login_result.values["Description"] != "":
            raise RuntimeError(f'Login error: {session_login_result.values["Description"]}')

    def __init__(
        self,
        hostname: str,
        port: int,
        appname: str,
        username: str,
        password: str,
        use_ssl: bool = True,
        file_cache_byte_limit: int = 33554432,
        auto_reconnect: bool = True,
        connect_timeout: int = 10,
    ):
        self.session_guid = None
        self.job_caller = None
        self.hostname = hostname
        self.port = port
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.auto_reconnect = auto_reconnect
        self.connect_timeout = connect_timeout
        self._connect()

    def _connect(self):
        if hasattr(self, "job_caller") and self.job_caller is not None:
            # try to close existing job_caller
            try:
                self.job_caller.close()
            except OSError as ex:
                logging.warning(ex)
            # remove job_caller reference
            self.job_caller = None

        self.job_caller = JobCaller(self.hostname, self.port, self.use_ssl, self.file_cache_byte_limit, self.connect_timeout)
        self.__attach__(self.username, self.password)

    def __del__(self):
        if self.job_caller is not None:
            try:
                self.job_caller.socket.close()
            except OSError as ex:
                logging.error(ex)

    def execute(self, job: Job) -> Result:
        """Send a job to the blue server (via TCP), execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """

        if self.auto_reconnect:
            if self.job_caller is None:
                # try to connect if current job_caller is None
                self._connect()

            if self.job_caller is None:
                # Auto reconnect failed and no job_caller available to execute the job
                raise BlueException(return_code=-1, message=str("Auto reconnect failed and no job_caller available to execute the job"))

            try:
                return self.job_caller.execute(job)
            except ConnectionAbortedError as ex:
                # fetch connection closed exceptions and try to reconnect and execute again
                logging.warning(ex)
                self._connect()
                return self.execute(job)
        else:
            if self.job_caller is None:
                # No job_caller available to execute the job
                raise BlueException(return_code=-1, message=str("No job_caller available to execute the job"))

            result: Result = self.job_caller.execute(job)
            if not result and job.raise_exception:
                raise BlueException(return_code=result.return_code, message=str(result.error_message))
            return result


class Connection:
    def __init__(
        self,
        hostname: str,
        port: int,
        appname: str,
        username: str,
        password: str,
        use_ssl: bool = True,
        file_cache_byte_limit: int = 33554432,
        auto_reconnect: bool = True,
    ):
        self.client = None
        self.hostname = hostname
        self.port = port
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.auto_reconnect = auto_reconnect

    def __enter__(self):
        self.client = TcpClient(
            hostname=self.hostname,
            port=self.port,
            appname=self.appname,
            username=self.username,
            password=self.password,
            use_ssl=self.use_ssl,
            file_cache_byte_limit=self.file_cache_byte_limit,
            auto_reconnect=self.auto_reconnect,
        )
        return self.client

    def __exit__(self, type_name, value, traceback):
        if self.client is not None:
            self.client.__del__()
