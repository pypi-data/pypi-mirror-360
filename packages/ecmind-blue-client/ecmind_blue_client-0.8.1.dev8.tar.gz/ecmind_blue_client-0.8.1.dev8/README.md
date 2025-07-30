# ECMind blue client

A client wrapper for blue.

## Deprecation warning

- From Mai 2024, `ecmind_blue_client.com_client` is no longer supported nor tested.
- From Mai 2024, `ecmind_blue_client.soap_client` is no longer supported nor tested.

## Installation

`pip install ecmind_blue_client`

## Usage

The workflow consists roughly of the following:

- Create a new Client() connection using a client implementation. There are four implementations:
    - `SoapClient()` in the module `ecmind_blue_client.soap_client`: Connect with a SOAP connection string
    - `ComClient()` in the module `ecmind_blue_client.com_client`: Connect by using the COM class on Windows
    - `TcpClient()` in the module `ecmind_blue_client.tcp_client`: Directly talk to a server via protlib.
       - Use `TcpClient.Connection()` in a with block/context.
    - `TcpPoolClient()` in the module `ecmind_blue_client.tcp_pool_client`
- Create a new Job() with a job name and provide/add job input parameters and optional job input file parameters
- Execute the Job() with the Client() instance and consume the result 
   - `result.result_code` returns the blue result code
   - `result.values` is a dict of output parameters
   - `result.files` is a list of output file parameters
   - `result.error_messages` is a string of the servers error response or None if `result_code` == 0

```
>>> from ecmind_blue_client.soap_client import SoapClient
>>> client = SoapClient(self.endpoint, 'TestApp', 'root', 'optimal')
>>> test_job = Job('krn.GetServerInfo', Flags=0, Info=6)
>>> result = client.execute(test_job)
>>> print(result.values['Value'])
oxtrodbc.dll
```

## Example

```python
from ecmind_blue_client import SystemFields
from ecmind_blue_client.tcp_pool_client import TcpPoolClient as Client

# Connect with DMS
client = Client(
    connection_string="localhost:4000:100", # Balancing setup for the used Client class `TcpPoolClient`
    appname="Test-Script",                  # Instance name, visible in the enterprise manager
    username="root",
    password="optimal"
)

# Query a folder
query = client.lol_query(
    object_name="Dossier",
    result_fields=[
        SystemFields.OBJECT_CRDATE, 
        "LastName", 
        "FirstName"
    ]
)

# Iterate over folder results
for dossier in query:
    print(                                                 # Output some infos
        dossier["OBJECT_ID"],                              # OBJECT_ID is added per defaults
        dossier['OBJECT_CRDATE'].strftime("%Y-%m-%d"),     # Manually added system field from line 16
        (f"{dossier['FirstName']} {dossier['LastName']}"), # Manually added objdef fields from line 17 & 18
    )

# Check that we have found a least one folder
assert dossier and "OBJECT_ID" in dossier

# Import a test document into the last found folder
import_result = client.xml_import(
    object_name="Dokument", 
    folder_id=dossier["OBJECT_ID"], 
    search_fields={
        "Type": "Invoice"
    },
    import_fields={
        "Type": "Invoice"
    },
    files = ["invoice.pdf"]
)

# Check if the import was successful and output OSID
assert import_result, import_result.error_message
print(import_result.import_action, import_result.object_id)
```