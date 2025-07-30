from dataclasses import dataclass
from typing import List, Optional
from ecmind_blue_client.result_file import ResultFile


@dataclass
class Result:
    """Result dataclass.

    values -- Dictionary of output parameters.
    files -- List of ResultFile() output file parameters.
    return_code -- Integer representation of the job result.
    error_message -- String containing error responses from the server on None if return_code is 0.
    client_infos -- List of optional data returned by the individual client implementation.
    """

    values: dict
    files: List[ResultFile]
    return_code: int
    error_message: Optional[str] = None
    client_infos: Optional[dict] = None

    def __repr__(self):
        if self.return_code == 0:
            return f"Result (success, {len(self.files)} files): {self.values}"
        else:
            return f"Result (failed, code {self.return_code}): {self.error_message}"

    def __bool__(self):
        return self.return_code == 0 and self.error_message is None
