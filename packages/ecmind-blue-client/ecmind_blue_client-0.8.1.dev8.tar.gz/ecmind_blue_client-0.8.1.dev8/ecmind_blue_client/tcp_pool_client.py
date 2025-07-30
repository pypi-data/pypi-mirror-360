import logging
import queue
import random
import socket
from threading import Lock

from ecmind_blue_client.blue_exception import BlueException
from ecmind_blue_client.client import Client

from ecmind_blue_client.job import Job
from ecmind_blue_client.result import Result
from ecmind_blue_client.tcp_client import TcpClient
from ecmind_blue_client.tcp_client_classes.job_caller import JobCaller


class TcpPoolClient(Client):
    def __init__(
        self,
        connection_string: str,
        appname: str,
        username: str,
        password: str,
        use_ssl: bool = True,
        file_cache_byte_limit: int = 33554432,
        pool_size: int = 10,
        connect_timeout: int = 10,
    ):
        super()
        servers = []
        for server_string in connection_string.split("#"):
            server_parts = server_string.split(":")
            if len(server_parts) != 3:
                raise ValueError(
                    f"""Connection String invalid, server '{connection_string}' must be formatted as hostname:port:weight.
                    For example localhost:4000:1"""
                )
            servers.append(
                {
                    "hostname": server_parts[0],
                    "port": int(server_parts[1]),
                    "weight": int(server_parts[2]),
                }
            )

        self.servers = servers
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.connect_timeout = connect_timeout
        self._pool_size = pool_size
        self._pool_available = queue.Queue()
        self._pool_in_use = 0
        self.lock = Lock()

    def execute(self, job: Job) -> Result:
        job_caller = self._borrow()
        try:
            result: Result = job_caller.execute(job)
            result.client_infos = {
                "hostname": job_caller.hostname,
                "port": job_caller.port,
            }
            self._return(job_caller)

            if not result and job.raise_exception:
                raise BlueException(return_code=result.return_code, message=str(result.error_message))
            return result

        except ConnectionAbortedError as ex:
            # fetch connection closed exceptions and try to reconnect and execute again
            logging.warning(ex)
            self._invalidate(job_caller)
            return self.execute(job)

        except Exception as ex:
            self._invalidate(job_caller)
            raise ex

    def _borrow(self) -> JobCaller:
        try:
            job_caller = self._pool_available.get_nowait()
            self._pool_in_use += 1
            return job_caller
        except queue.Empty:
            if self._pool_in_use >= self._pool_size:
                job_caller = self._pool_available.get()
                self._pool_in_use += 1
                return job_caller
            else:
                job_caller = self._create()
                self._pool_in_use += 1
                return job_caller

    def _invalidate(self, job_caller: JobCaller):
        self._pool_in_use -= 1
        try:
            job_caller.close()
        except OSError as ex:
            logging.warning(ex)

    def _return(self, job_caller: JobCaller):
        self._pool_in_use -= 1
        self._pool_available.put(job_caller)

    def _create(self) -> JobCaller:

        self.lock.acquire()
        random.shuffle(rand_servers := [*self.servers])

        job_caller = None
        for server in rand_servers:
            try:
                job_caller = JobCaller(
                    server["hostname"],
                    server["port"],
                    self.use_ssl,
                    self.file_cache_byte_limit,
                    self.connect_timeout,
                )
                if job_caller:
                    logging.debug("Connected with %s:%s", server["hostname"], server["port"])
                    break
            except (ConnectionRefusedError, TimeoutError) as err:
                logging.error(err)

        if job_caller is None:
            self.lock.release()
            raise ConnectionRefusedError("No valid enaio server found")

        self.lock.release()

        session_attach_job = Job("krn.SessionAttach", Flags=0, SessionGUID="")
        job_caller.execute(session_attach_job)

        session_properties_set_job = Job(
            "krn.SessionPropertiesSet",
            Flags=0,
            Properties="instname;statname;address",
            address=f"{socket.gethostbyname(socket.gethostname())}=dummy",
            instname=self.appname,
            statname=socket.gethostname(),
        )
        job_caller.execute(session_properties_set_job)

        session_login_job = Job(
            "krn.SessionLogin",
            Flags=0,
            UserName=self.username,
            UserPwd=TcpClient.encrypt_password(TcpClient.reveal(self.password)),
        )
        session_login_result = job_caller.execute(session_login_job)

        if "Description" in session_login_result.values and session_login_result.values["Description"] != "":
            raise PermissionError(f'Login error: {session_login_result.values["Description"]}')

        return job_caller

    def __del__(self):
        for _ in range(0, self._pool_available.qsize()):
            job_caller = self._pool_available.get_nowait()
            job_caller.socket.close()
