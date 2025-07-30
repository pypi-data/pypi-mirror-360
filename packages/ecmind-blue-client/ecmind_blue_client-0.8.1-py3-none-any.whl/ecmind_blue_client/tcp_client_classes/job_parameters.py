from protlib import CArray, CInt, CStruct

from ecmind_blue_client.tcp_client_classes.job_parameter_data import JobParameterData
from ecmind_blue_client.tcp_client_classes.job_parameter_description import JobParameterDescription


class JobParameters(CStruct):
    length = CInt()
    count = CInt()
    description = CArray(length="count", ctype=JobParameterDescription)
    data = CArray(length="count", ctype=JobParameterData)

    def get(self, name):
        for data in list(self.data):
            d_name = data.name.decode("ascii")
            if d_name == name:
                return data.value

        return None
