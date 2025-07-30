from protlib import CString, CStruct

from ecmind_blue_client.tcp_client_classes.job_parameters import JobParameters
from ecmind_blue_client.tcp_client_classes.response_job_errors import ResponseJobErrors


class ResponseJobParameters(CStruct):
    mode = CString(default="R", length=1)  # always R for response
    internal_parameters = JobParameters.get_type()
    parameters = JobParameters.get_type()
    errors = ResponseJobErrors.get_type()
