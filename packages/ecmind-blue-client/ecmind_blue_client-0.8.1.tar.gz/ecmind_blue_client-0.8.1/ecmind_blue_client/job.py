from typing import List, Union

from ecmind_blue_client.const import Jobs, ParamTypes
from ecmind_blue_client.param import Param
from ecmind_blue_client.request_file import RequestFile, RequestFileFromPath


class Job:
    def __init__(
        self,
        jobname: Union[str, Jobs],
        files: Union[List[Union[RequestFile, str]], None] = None,
        context_user: Union[str, None] = None,
        raise_exception: bool = False,
        **params,
    ):
        """Create a new Job() object.

        Keyword arguments:
        jobname -- String with the a blue jobname, i. e. 'dms.GetResultList'
        files -- (Optional) List of strings with file paths to add to the job or RequestFile objects.
        context_user -- (Optional) Set the magical parameter `$$$SwitchContextUserName$$$` to a username.
        raise_exception -- (Optional) Set to true to raise BlueException() on non-zero results.
        **params -- Add arbitrary job input parameters. Uses Param.infer_type() to guess the blue parameter type.
        """
        self.name = jobname.value if isinstance(jobname, Jobs) else jobname
        self.params: List[Param] = []

        self.files: List[RequestFile] = []
        if files:
            for file in files:
                self.append_file(file)

        self.raise_exception = raise_exception
        for name, value in params.items():
            self.append(Param.infer_type(name, value))
        if context_user:
            self.append(Param("$$$SwitchContextUserName$$$", ParamTypes.STRING, context_user))

    def append(self, param: Param):
        """Appends a job input parameter.
        Keyword arguments:
        param -- Param object.
        """
        self.params.append(param)

    def update(self, param: Param):
        """Updates a job input parameters value and type. Appends the parameter if not allready present.
        Keyword arguments:
        param -- Param object.
        """
        for current_param in self.params:
            if current_param.name == param.name:
                current_param.value = param.value
                current_param.type = param.type
                return True
        self.append(param)

    def append_file(self, file: Union[str, RequestFile]):
        """Appends a job input file parameter.
        Keyword arguments:
        filepath -- String with file path to append.
        """
        if isinstance(file, RequestFile):
            self.files.append(file)
        else:
            self.files.append(RequestFileFromPath(str(file)))

    def __repr__(self) -> str:
        return f'Job "{self.name}" ({len(self.files)} files): {self.params}'
