# from protlib import
import base64
import hashlib
import os
import socket
import ssl
from datetime import datetime
from struct import unpack
from tempfile import gettempdir
from typing import List, Optional
from uuid import uuid4

from ecmind_blue_client.blue_exception import BlueException

from ecmind_blue_client.job import Job
from ecmind_blue_client.const import ParamTypes
from ecmind_blue_client.param import Param
from ecmind_blue_client.result import Result
from ecmind_blue_client.result_file import ResultFile, ResultFileType
from ecmind_blue_client.tcp_client_classes.call_job_parameters import CallJobParameters
from ecmind_blue_client.tcp_client_classes.file_footer import FileFooter
from ecmind_blue_client.tcp_client_classes.file_header import FileHeader
from ecmind_blue_client.tcp_client_classes.job_header import JobHeader
from ecmind_blue_client.tcp_client_classes.job_parameter_data import JobParameterData
from ecmind_blue_client.tcp_client_classes.job_parameter_description import JobParameterDescription
from ecmind_blue_client.tcp_client_classes.job_parameters import JobParameters


class JobCaller:
    CERT = """-----BEGIN CERTIFICATE-----
MIIF/TCCA+WgAwIBAgIBFzANBgkqhkiG9w0BAQsFADCBgzELMAkGA1UEBhMCREUx
DzANBgNVBAgMBkJlcmxpbjEPMA0GA1UEBwwGQmVybGluMRgwFgYDVQQKDA9PUFRJ
TUFMIFNZU1RFTVMxFTATBgNVBAsMDEJsdWUgQ2VudHJhbDEhMB8GA1UEAwwYQmx1
ZSBDZW50cmFsIGltZXJtZWRpYXRlMB4XDTE5MDEyODE3NDIwNFoXDTI3MDQxNjE3
NDIwNFowdDELMAkGA1UEBhMCREUxDzANBgNVBAgMBkJlcmxpbjEPMA0GA1UEBwwG
QmVybGluMRgwFgYDVQQKDA9PUFRJTUFMIFNZU1RFTVMxFTATBgNVBAsMDEJsdWUg
Q2VudHJhbDESMBAGA1UEAwwJQXBwU2VydmVyMIICIjANBgkqhkiG9w0BAQEFAAOC
Ag8AMIICCgKCAgEAxXSPc72aZr1wuLfpZ6Lpu7XQuS4EPImNQccJg+JUxRFhBQa1
Dme+dYLpdA7t5L2f5o00AOMVu5sCncIQ66yxtQe/ZlCUPhL9bBWfj/Yfs89PFQKQ
wCISfdBmtqsY6pEK89qelbnEtCWIjBEzAm5z9p6AOk9iBZvzKSQb9ehNzP2AMtP5
k53b8dXhjKTNM92MNzvO92ETqKUMdauzopSklRVLk6T3DRgJs+wpoKUCVvtXyoF/
feilzPabku0+Tomui8hjrXnlcHo94Gp7dVxMPsxwyzKbYLRAM6pQ4vhzv+QmAOwS
qgP79MupckGf70DMenHDjntrSw4l10if4q19xo+FJU+lfbGdPOSEMM0M3ttaAZUl
+5HltzmTxhg6djhZV+myLKHMTlPaW76MWlzj2nKSJ63mOb4NF22NSuWSE8X2RRvO
PNOZ3qaIV9a+2ljjPu8Sqmbo/ut7wcrty5ETCp3qZppM2vg8R4JfseTk5Nupfktf
/lthfDMlX79VCou229yaLxAGqJv/WvXiy/zrGPLIrIsiiYv8aeAbxWK+hF3ea90B
byHwKBAKT55RJ8fEqYWkxUdVEO5429UWKiZ0QhWas8NaZ2IokH2wjHfAKjHgVCBX
mXU37lc6g3gNEL1NDPq5x9IxC+pWEx/H094xZ5AgyH4KF8h14uuczYrA8uECAwEA
AaOBiTCBhjAdBgNVHQ4EFgQURyhC1GDxZgQGq+aT8dU15rVmZSYwHwYDVR0jBBgw
FoAUPfCYO8wLyAv/Zl3XOrmZhx9cniswCQYDVR0TBAIwADALBgNVHQ8EBAMCBaAw
LAYJYIZIAYb4QgENBB8WHU9wZW5TU0wgR2VuZXJhdGVkIENlcnRpZmljYXRlMA0G
CSqGSIb3DQEBCwUAA4ICAQBwYbo4QKNwzV8Wy3mj9iUMHPp+fb/b1YTU7+wmqCmv
ymyr83pQiuth2nu3y+7QEqHwDX+KJBm3XO1ej7GPZ5tZ6ssOsYQVGA5l7ujrsm/r
aBr3n5cghiuggX2K9lbP8/I9HwvWPOqdtSHqy5ILQgQGR4mnh8zc1zPwIeYSLkeJ
FjTChyx6ZX1p+gKYg+QQ4OzfLDbueTW/4oQrrH+DjvfD9yZnh0DRiL700NpQZxb4
mnSqVS0rjMyLcNxc9M6IcivOqDy490CLcAj1KYjFP7B/Ehf4Po96p+geqDZRRs0v
GfcRG4qaPi6mJ0p5Yf4PWeLN8ZBydg08pf3F4EDKcV+zzWoMq6ywwkUVPe5x+czJ
cwKMIvCogaQRqzEBAuDGEMPkfz/Nl0wEy3zhx8gtVRvv/sjfCyyVm5rAS+ROkVAi
w5njrOhKAGBYnVOfBEiCukCQYXNOP+/Rdi+J4QK81olPFnVpb07ltFhw68Gc+MXZ
QKmed6+PTJak8/Wgqe/7SZtXq8NPElaLax7rfIQIrEgB01ow2PqhHdkQ8w0VKL2Z
wSHyqIw00O/27DxxV1KWZkkNoen9RzY5YzzIknJ+4IaP18hyOfHm4bjrzUGvYumG
WumfghHwh0F3EQEqH/T8vlGOALteuzG8aSNs9CWqtOK5qvQn+B9eUmjldwrVI0hR
NA==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
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
sBAN
-----END CERTIFICATE-----
"""

    def __init__(self, hostname, port, use_ssl: Optional[bool] = True, file_cache_byte_limit: Optional[int] = 33554432, connect_timeout=10):
        self.hostname = hostname
        self.port = port
        self.file_cache_byte_limit = file_cache_byte_limit
        plain_text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plain_text_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if use_ssl:
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cadata=self.CERT)
            ssl_context.check_hostname = False
            self.socket = ssl_context.wrap_socket(plain_text_socket)
        else:
            self.socket = plain_text_socket
        self.socket.settimeout(connect_timeout)
        self.socket.connect((hostname, port))
        self.socket.settimeout(None)

    def close(self):
        self.socket.close()

    def execute(self, job: Job):
        # Create internal parameter
        intern_params: List[Param] = []
        intern_params.append(Param("streams", ParamTypes.INTEGER, len(job.files)))
        internal_parameters = self.build_parameters(intern_params)

        # create parameter
        parameters = self.build_parameters(job.params)

        # create request parameters
        request_parameters = CallJobParameters(
            method=job.name,
            internal_parameters=internal_parameters,
            parameters=parameters,
        )
        request_parameters_binary = request_parameters.serialize()

        # calculate digest of request parameters
        request_digest = hashlib.sha1()
        request_digest.update(request_parameters_binary)

        # create request headers
        request_headers = JobHeader()
        request_headers.set_parameter_length(len(request_parameters_binary) + 20)
        request_header_binary = request_headers.serialize()

        # send request
        self.socket.send(request_header_binary)
        self.socket.send(request_parameters_binary)

        # for each file
        for file in job.files:
            # write file header
            request_file_header = FileHeader()
            request_file_header.set_file_length(file.size)
            request_file_header.extension = file.extension
            request_file_header_binary = request_file_header.serialize()

            self.socket.send(request_file_header_binary)
            request_digest.update(request_file_header_binary)

            # stream file
            with file.open() as file_stream:
                data = file_stream.read(1024)
                while data:
                    self.socket.send(data)
                    request_digest.update(data)
                    data = file_stream.read(1024)
                file_stream.close()

            # write fix file footer @0000000000@MAERTSSA
            request_file_footer = FileFooter()
            request_file_footer_binary = request_file_footer.serialize()
            self.socket.send(request_file_footer_binary)

            request_digest.update(request_file_footer_binary)

        # send request digest
        self.socket.send(request_digest.digest())

        # ----------------------------------------------------------------------
        # Start read response
        # ----------------------------------------------------------------------

        # read header
        response_header = JobHeader.parse(self.socket.recv(20))

        # read body
        response_digest = hashlib.sha1()

        parameter_length = response_header.get_parameter_length() - 20
        body_raw = b""
        while len(body_raw) < parameter_length:
            body_raw += self.socket.recv(parameter_length - len(body_raw))

        response_digest.update(body_raw)

        response = self.parse_response_body(body_raw)

        return_code = response["internal_parameters"]["return"]
        error_message = None
        if return_code != 0:
            error_message = ""
            errors = response["errors"]
            for error in errors:
                error_message += error["message"] + "\n"

        result_values = response["parameters"]

        # parse file streams

        result_files: List[ResultFile] = []

        if "streams" in response["internal_parameters"]:
            streams = response["internal_parameters"]["streams"]
            for _ in range(0, int(streams)):
                header_raw = self.socket.recv(32)
                header = FileHeader.parse(header_raw)
                response_digest.update(header_raw)

                file_length = header.get_file_length()
                to_file = file_length >= self.file_cache_byte_limit
                remainder = file_length
                file_pointer = None
                byte_array = bytearray()
                file_path = None
                file_name = f"ecmind_{str(uuid4())}.{header.get_file_extension()}"
                if to_file:
                    file_path = os.path.join(gettempdir(), file_name)
                    file_pointer = open(file_path, "wb")

                buffer_size = 4096
                while remainder > 0:
                    file_part: bytes = self.socket.recv(min(remainder, buffer_size))
                    response_digest.update(file_part)
                    remainder -= len(file_part)
                    if to_file and file_pointer is not None:
                        file_pointer.write(file_part)
                    else:
                        byte_array += bytearray(file_part)

                if to_file and file_pointer is not None:
                    file_pointer.close()
                    result_file = ResultFile(
                        result_file_type=ResultFileType.FILE_PATH,
                        file_name=file_name,
                        file_path=file_path,
                    )
                else:
                    result_file = ResultFile(
                        result_file_type=ResultFileType.BYTE_ARRAY,
                        file_name=file_name,
                        byte_array=bytes(byte_array),
                    )

                result_files.append(result_file)

                footer_raw = self.socket.recv(20)
                response_digest.update(footer_raw)
                # footer = FileFooter.parse(footer_raw)

        response_digest_received = response_digest.digest()
        response_digest_expected = self.socket.recv(20)

        if response_digest_received != response_digest_expected:
            raise BlueException(1, "Digest for response does not match.")

        return Result(result_values, result_files, return_code, error_message)

    def build_parameters(self, params: List[Param]):

        data_offset = 4 + (len(params) * 12)
        data_length = 0

        parameter_description_list = []
        parameter_description_size = 0

        parameter_data_list = []
        parameter_data_size = 0

        for param in params:
            parameter_description = JobParameterDescription(
                name_offset=data_offset + data_length,
                type=param.type.value,
                value_offset=data_offset + data_length + len(param.name) + 1,
            )

            parameter_data = None
            if param.type == ParamTypes.STRING:
                parameter_data = JobParameterData(name=param.name, value=param.value)
            elif param.type == ParamTypes.INTEGER:
                parameter_data = JobParameterData(name=param.name, value=str(param.value))
            elif param.type == ParamTypes.BOOLEAN:
                parameter_data = JobParameterData(name=param.name, value="1" if param.value else "0")
            elif param.type == ParamTypes.DOUBLE:
                parameter_data = JobParameterData(name=param.name, value=str(param.value))
            elif param.type == ParamTypes.DATE_TIME:
                if isinstance(param.value, datetime):
                    JobParameterData(
                        name=param.name,
                        value=str(param.value.strftime("%d.%m.%y %H:%M:%S")),
                    )
                else:
                    JobParameterData(name=param.name, value=str(param.value))
            elif param.type == ParamTypes.BASE64:
                if isinstance(param.value, (bytearray, bytes)):
                    parameter_data = JobParameterData(name=param.name, value=base64.b64encode(param.value))
                else:
                    parameter_data = JobParameterData(
                        name=param.name,
                        value=base64.b64encode(param.value.encode("UTF-8")),
                    )
            if parameter_data is None:
                raise BlueException(1, "Unsupported parameter type")

            data_length += parameter_data.sizeof()

            parameter_description_list.append(parameter_description)
            parameter_description_size += parameter_description.sizeof()

            parameter_data_list.append(parameter_data)
            parameter_data_size += parameter_data.sizeof()

        params_length = 4 + parameter_description_size + parameter_data_size

        return JobParameters(
            length=params_length,
            count=len(params),
            description=parameter_description_list,
            data=parameter_data_list,
        )

    def parse_response_body(self, body_raw):
        result = {}

        # Read Mode
        _mode = unpack("s", body_raw[0:1])[0]  # Always R

        body_raw = body_raw[1:]  # drop bytes

        # Read Internal Parameters
        internal_length = unpack(">i", body_raw[0:4])[0]  # read byte length of internal parameters
        body_raw = body_raw[4:]  # drop bytes

        internal_raw = body_raw[:internal_length]  # slice internal parameters
        body_raw = body_raw[internal_length:]  # drop bytes

        result["internal_parameters"] = self.parse_parameters(internal_raw)

        # Read Parameters
        params_length = unpack(">i", body_raw[0:4])[0]  # read byte length of parameters
        body_raw = body_raw[4:]  # drop bytes

        params_raw = body_raw[:params_length]  # slice parameters
        body_raw = body_raw[params_length:]  # drop bytes

        result["parameters"] = self.parse_parameters(params_raw)

        # Read Errors
        _error_length = unpack(">i", body_raw[0:4])[0]  # read byte length of errors
        error_raw = body_raw[4:]  # drop bytes

        result["errors"] = self.parse_errors(error_raw)

        return result

    def parse_parameters(self, params_raw):
        parameters = {}
        # Read Parameter Count
        params_count = unpack(">i", params_raw[0:4])[0]

        for i in range(0, params_count):
            description_offset = 4 + (12 * i)
            name_offset = unpack(">i", params_raw[description_offset : description_offset + 4])[0]
            param_type = unpack(">i", params_raw[description_offset + 4 : description_offset + 8])[0]
            value_offset = unpack(">i", params_raw[description_offset + 8 : description_offset + 12])[0]

            value_offset_end = -1
            if i == params_count - 1:
                value_offset_end = len(params_raw) - 1
            else:
                value_offset_end = (
                    unpack(
                        ">i",
                        params_raw[description_offset + 12 : description_offset + 16],
                    )[0]
                    - 1
                )

            name = str(params_raw[name_offset : value_offset - 1], "ascii")
            value = params_raw[value_offset:value_offset_end]

            infered_value = None
            if param_type == ParamTypes.STRING.value:
                infered_value = str(value, "UTF-8")
            elif param_type == ParamTypes.INTEGER.value:
                infered_value = int(value)
            elif param_type == ParamTypes.BOOLEAN.value:
                infered_value = bool(value)
            elif param_type == ParamTypes.DOUBLE.value:
                infered_value = float(value)
            # elif param_type == ParamTypes.DATE_TIME.value:
            #     infered_value = datetime(value)
            elif param_type == ParamTypes.BASE64.value:
                infered_value = base64.b64decode(value).decode("UTF-8")
            else:
                raise ValueError("Unknown parameter type")
            parameters[name] = infered_value

        return parameters

    def parse_errors(self, errors_raw):
        errors = []
        # Read Parameter Count
        error_count = unpack(">i", errors_raw[0:4])[0]
        errors_raw = errors_raw[4:]  # drop bytes

        # dummy
        dummy = unpack(">i", errors_raw[0:4])[0]
        errors_raw = errors_raw[4:]  # drop bytes

        descriptions = []

        for _ in range(0, error_count):
            (
                message_length,
                source_code,
                source_name_length,
                error_code,
                info_elements_length,
            ) = unpack(">iiiii", errors_raw[0:20])
            errors_raw = errors_raw[20:]  # drop bytes

            info_elements = []
            for _ in range(0, info_elements_length):
                info_elements.append(unpack(">i", errors_raw[0:4])[0])
                errors_raw = errors_raw[4:]  # drop bytes

            descriptions.append(
                {
                    "message_length": message_length,
                    "source_code": source_code,
                    "source_name_length": source_name_length,
                    "error_code": error_code,
                    "info_elements_length": info_elements_length,
                    "info_elements": info_elements,
                }
            )

        for description in descriptions:
            message = str(errors_raw[: description["message_length"]], "utf-8")
            errors_raw = errors_raw[description["message_length"] :]  # drop bytes

            source = str(errors_raw[: description["source_name_length"]], "utf-8")
            errors_raw = errors_raw[description["source_name_length"] :]  # drop bytes

            infos = []
            for info_element in description["info_elements"]:
                info = str(errors_raw[:info_element], "utf-8")
                infos.append(info)
                errors_raw = errors_raw[info_element:]

            errors.append(
                {
                    "message": message,
                    "source_code": description["source_code"],
                    "source": source,
                    "error_code": description["error_code"],
                    "infos": infos,
                }
            )

        return errors
