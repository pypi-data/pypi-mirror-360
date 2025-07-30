import os
import unittest
import urllib.request
from uuid import uuid4
from pathlib import Path

from XmlElement import XmlElement as X
from XmlElement.xml_element import XmlElement

from ecmind_blue_client import (
    FieldGroupOperators,
    ImportActions,
    Job,
    Jobs,
    QueryConditionField,
    QueryConditionGroup,
    QueryResultField,
    ResultFile,
    SortOrder,
    SystemFields,
)
from ecmind_blue_client.blue_exception import BlueException
from ecmind_blue_client.const import FieldSchema, MainTypeId, QueryOperators, StoreInCacheByIdConversion
from ecmind_blue_client.options import Options
from ecmind_blue_client.request_file import RequestFileFromReader, RequestFileFromBytes
from ecmind_blue_client.tcp_pool_client import TcpPoolClient


class TestTcpPoolClient(unittest.TestCase):
    connection_string = "localhost:4000:1"
    use_ssl = True
    folder_id = 44
    doc_id = 83
    doc_type_id = 262144
    multifile_docs = [
        {"id": 87, "count": 3},
        {"id": 86, "count": 2},
        {"id": 88, "count": 2},
    ]

    def test_simple_job(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "!;`|K!llEF!llE6!;k", self.use_ssl)
        test_job = Job(Jobs.KRN_GETSERVERINFO, Flags=0, Info=6)
        result = client.execute(test_job)
        self.assertEqual(result.values["Value"], "oxtrodbc.dll")

    def test_unicode_error(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={"StringField": "Test Unittest", "DateField": "03.11.2020"},
            import_fields={
                "StringField": "Test Unittest",
                "DateField": "03.11.2020",
                "InvalüdField": "123.456",
            },
            folder_id=self.folder_id,
            action1=ImportActions.UPDATE,
        )
        self.assertEqual(result.return_code, -24)
        if result.error_message is not None:
            self.assertRegex(result.error_message, ".*The DMS field >InvalüdField< could not be found.*")
        else:
            self.assertIsNotNone(result.error_message, "The error message should not be None")

    def test_permission_error(self):
        def test_function():
            client = TcpPoolClient(self.connection_string, "TestApp", "unknown", "user", self.use_ssl)
            test_job = Job("krn.GetServerInfo", Flags=0, Info=6)
            result = client.execute(test_job)
            self.assertEqual(result.values["Value"], "oxtrodbc.dll")

        self.assertRaises(PermissionError, test_function)

    def test_get_object_type_by_id(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        type_id = client.get_object_type_by_id(self.doc_id)
        self.assertEqual(type_id, self.doc_type_id)

    def test_store_in_cache(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        files = client.store_in_cache(self.doc_id)
        for file in files:
            self.assertIsInstance(file, ResultFile)
            self.assertGreater(file.size(), 0)
            file_path = file.store()
            self.assertTrue(file_path is not None and os.path.exists(file_path))

    def test_xml_import(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={"StringField": "Test Unittest", "DateField": "03.11.2020"},
            import_fields={
                "StringField": "Test Unittest",
                "DateField": "03.11.2020",
                "DoubleField": "123.456",
            },
            table_fields={
                "TableField": [
                    {
                        "TableCol1": "TestTableValue1",
                        "TableCol2": "17",
                        "TableCol3": "17.02.2020",
                        "TableCol4": "17.18",
                    },
                    {
                        "TableCol1": "TestTableValue2",
                        "TableCol2": "27",
                        "TableCol3": "27.03.2020",
                        "TableCol4": "18.19",
                    },
                ]
            },
            folder_id=self.folder_id,
            action1=ImportActions.UPDATE,
            files=["README.md"],
            options=Options(REPLACETABLEFIELDS=True),
        )
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.values["Action"], ImportActions.UPDATE.value)
        self.assertEqual(result.import_action, ImportActions.UPDATE)
        self.assertEqual(result.values["ObjectID"], result.object_id)
        self.assertEqual(result.values["ObjectType"], result.object_type)

    def test_xml_import_context_user(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        context_user = "USER_WITH_RIGHTS"
        result = client.xml_import(
            object_name="Unittest",
            search_fields={"StringField": "Test Context User", "DateField": "08.10.2024"},
            import_fields={"StringField": "Test Context User", "DateField": "08.10.2024"},
            context_user=context_user,
        )
        self.assertEqual(result.return_code, 0)
        data = client.execute_sql(f"SELECT modifyuser FROM stamm1 WHERE id = {result.object_id}")

        if data is not None:
            self.assertEqual(data[0]["modifyuser"], context_user)
        else:
            self.fail("Data is None")

    def test_xml_import_main_type(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={"StringField": "Test Unittest", "DateField": "03.11.2020"},
            import_fields={
                "StringField": "Test Unittest",
                "DateField": "03.11.2020",
                "DoubleField": "123.456",
            },
            table_fields={
                "TableField": [
                    {
                        "TableCol1": "TestTableValue1",
                        "TableCol2": "17",
                        "TableCol3": "17.02.2020",
                        "TableCol4": "17.18",
                    },
                    {
                        "TableCol1": "TestTableValue2",
                        "TableCol2": "27",
                        "TableCol3": "27.03.2020",
                        "TableCol4": "18.19",
                    },
                ]
            },
            folder_id=self.folder_id,
            action1=ImportActions.UPDATE,
            files=["README.md"],
            main_type=MainTypeId.DOC_MULTIMEDIA,
            options="REPLACEFILES=1",
        )
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.values["Action"], ImportActions.UPDATE.value)

    def test_xml_import_parent_variant_id(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={"StringField": "Test Variant"},
            import_fields={"StringField": "Test Variant"},
            folder_id=self.folder_id,
            action1=ImportActions.NONE,
            main_type=MainTypeId.DOC_WINDOWS,
            files=["README.md"],
        )
        parent_id = result.values["ObjectID"]
        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={},
            import_fields={"StringField": "Test Variant"},
            folder_id=self.folder_id,
            files=["README.md"],
            main_type=MainTypeId.DOC_WINDOWS,
            variant_parent_id=parent_id,
        )
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.values["Action"], ImportActions.INSERT.value)

    def test_xml_import_from_reader(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        with open("README.md", "rb") as reader:
            path = Path("README.md")
            result = client.xml_import(
                object_name="UnittestDoc",
                search_fields={"StringField": "Test Unittest MD", "DateField": "30.05.2024"},
                import_fields={"StringField": "Test Unittest MD", "DateField": "30.05.2024"},
                folder_id=self.folder_id,
                action1=ImportActions.UPDATE,
                files=[RequestFileFromReader(reader, path.stat().st_size, path.suffix[1:])],
                options=Options(REPLACETABLEFIELDS=True),
            )
        self.assertEqual(result.return_code, 0)

        with urllib.request.urlopen("https://ecmind.ch/index.html") as web_response:
            web_size = len(web_response.read())

        with urllib.request.urlopen("https://ecmind.ch/index.html") as web_response:
            result = client.xml_import(
                object_name="UnittestDoc",
                search_fields={"StringField": "Test Unittest HTML", "DateField": "30.05.2024"},
                import_fields={"StringField": "Test Unittest HTML", "DateField": "30.05.2024"},
                folder_id=self.folder_id,
                action1=ImportActions.UPDATE,
                files=[RequestFileFromReader(web_response, web_size, "html")],
                options=Options(REPLACETABLEFIELDS=True),
            )
        self.assertEqual(result.return_code, 0)

    def test_xml_import_from_bytes(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        with open("README.md", "rb") as file:
            file_bytes = file.read()

        result = client.xml_import(
            object_name="UnittestDoc",
            search_fields={"StringField": "Test Unittest MD", "DateField": "30.05.2024"},
            import_fields={"StringField": "Test Unittest MD", "DateField": "30.05.2024"},
            folder_id=self.folder_id,
            action1=ImportActions.UPDATE,
            files=[RequestFileFromBytes(file_bytes, "md")],
            options=Options(REPLACETABLEFIELDS=True),
        )
        self.assertEqual(result.return_code, 0)

    def test_get_result_list(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        query_xml = X(
            "DMSQuery",
            {},
            [
                X(
                    "Archive",
                    {"internal_name": "Unittest"},
                    [
                        X(
                            "ObjectType",
                            {"internal_name": "UnittestDoc"},
                            [
                                X(
                                    "Fields",
                                    {"field_schema": "DEF"},
                                    [
                                        X("Field", {"internal_name": "StringField"}),
                                        X(
                                            "Field",
                                            {
                                                "internal_name": "DateTimeField",
                                                "sortpos": "1",
                                                "sortorder": "ASC",
                                            },
                                        ),
                                        X("Field", {"internal_name": "DoubleField"}),
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        job = Job(
            "dms.GetResultList",
            Flags=0,
            Encoding="UTF-8",
            RequestType="LOL",
            XML=query_xml,
        )
        result = client.execute(job)
        self.assertEqual(result.return_code, 0)
        self.assertGreater(result.values["TotalHits"], 0)
        result_xml = X.from_string(result.values["XML"])
        result_rows = result_xml["Archive"][0]["ObjectType"][0]["Rowset"][0]["Rows"][0]["Row"]
        self.assertEqual(len(result_rows), result.values["Count"])

    def test_get_result_list2(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        query_xml = X(
            "DMSQuery",
            {},
            [
                X(
                    "Archive",
                    {},
                    [
                        X(
                            "ObjectType",
                            {"internal_name": "Unittest"},
                            [X("Fields", {"field_schema": "All"}, [])],
                        )
                    ],
                )
            ],
        )

        job = Job(
            "dms.GetResultList",
            Flags=0,
            Encoding="UTF-8",
            RequestType="LOL",
            XML=query_xml,
        )
        result = client.execute(job)
        self.assertEqual(result.return_code, 0)
        self.assertGreater(result.values["TotalHits"], 0)
        result_xml = X.from_string(result.values["XML"])
        result_rows = result_xml["Archive"][0]["ObjectType"][0]["Rowset"][0]["Rows"][0]["Row"]
        self.assertEqual(len(result_rows), result.values["Count"])

    def test_get_object_details(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        obj_details_document = client.get_object_details(
            "UnittestDoc",
            self.doc_id,
            [
                SystemFields.SDSTA_ID,
                SystemFields.OBJECT_ID,
                SystemFields.OBJECT_FOREIGNID,
                SystemFields.OBJECT_TIME,
                SystemFields.OBJECT_MAIN,
                SystemFields.OBJECT_COUNT,
                SystemFields.OBJECT_FILESIZE,
            ],
        )
        print(obj_details_document)
        self.assertEqual(int(obj_details_document[SystemFields.OBJECT_ID.name]), self.doc_id)
        self.assertEqual(obj_details_document[SystemFields.OBJECT_MAIN.name], "MULTIMEDIA")
        self.assertGreater(len(obj_details_document["TableField"]), 1)

        obj_details_folder = client.get_object_details("Unittest", obj_details_document[SystemFields.SDSTA_ID.name])
        self.assertGreater(len(obj_details_folder), 0)

    def test_execute_sql(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        test_data = str(uuid4())
        data = client.execute_sql(f"UPDATE benutzer SET bemerkung = '{test_data}' WHERE benutzer = 'ROOT'")
        data = client.execute_sql("SELECT * FROM benutzer")

        if data is not None:
            self.assertEqual(data[0]["bemerkung"], test_data)
        else:
            self.fail("Data is None")

        def test_function():
            client.execute_sql("DEFECT_STATEMENT")

        self.assertRaises(Exception, test_function)

    def test_basic_lol_query(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=[
                    "StringField",
                    "DateField",
                    "OSID",
                    QueryResultField("DateTimeField", sort_pos=1),
                    "DoubleField",
                    QueryResultField(
                        SystemFields.OBJECT_USERGUID,
                        sort_pos=2,
                        sort_order=SortOrder.DESC,
                    ),
                    SystemFields.OBJECT_RETENTION,
                    "OBJECT_MIMETYPEID",
                ],
                page_size=2,
                max_hits=10,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
            )
        )
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["OBJECT_INTERNAL_NAME"], "UnittestDoc")
        self.assertEqual(result[0]["OBJECT_ID"], result[0]["OSID"])

    def test_paging_with_multi_location_lol_query(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=[SystemFields.SDSTA_ID, SystemFields.SDREG_ID],
                page_size=2,
                max_hits=6,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
            )
        )
        ids = list()
        duplicates = 0
        for row in result:
            object_id = row["OBJECT_ID"]
            if object_id in ids:
                duplicates += 1
            else:
                ids.append(object_id)

        self.assertGreater(duplicates, 0)
        self.assertTrue(len(result) == 6)

    def test_lol_query_or_and(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        object_name = "UnittestDoc"
        field_conditions = [
            QueryConditionField(field=SystemFields.OBJECT_COUNT, values=1),
            QueryConditionField(
                field=SystemFields.OBJECT_ID,
                operator=QueryOperators.BETWEEN,
                values=[5, 500],
            ),
        ]
        result_and = list(
            client.lol_query(
                object_name=object_name,
                conditions=QueryConditionGroup(object_name=object_name, field_conditions=field_conditions),
            )
        )
        result_or = list(
            client.lol_query(
                object_name=object_name,
                conditions=QueryConditionGroup(
                    object_name=object_name,
                    field_conditions=field_conditions,
                    group_operator=FieldGroupOperators.OR,
                ),
            )
        )
        self.assertGreater(len(result_or), len(result_and))

    def test_basic_lol_query_user_context(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=[
                    "StringField",
                    "DateField",
                    "OSID",
                    QueryResultField("DateTimeField", sort_pos=1),
                    "DoubleField",
                    QueryResultField(
                        SystemFields.OBJECT_USERGUID,
                        sort_pos=2,
                        sort_order=SortOrder.DESC,
                    ),
                    SystemFields.OBJECT_RETENTION,
                    "OBJECT_MIMETYPEID",
                ],
                page_size=2,
                max_hits=10,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
                context_user="USER_WITHOUT_RIGHTS",
            )
        )
        self.assertEqual(len(result), 0)

    def test_sub_group_lol_query(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                conditions=[
                    QueryConditionGroup(
                        object_name="UnittestDoc",
                        field_conditions=[QueryConditionField("DateField", "10.05.2021")],
                        group_operator=FieldGroupOperators.AND,
                        field_groups=[
                            QueryConditionGroup(
                                object_name="UnittestDoc",
                                field_conditions=[
                                    QueryConditionField("StringField", "Multifile Gray"),
                                    QueryConditionField("StringField", "Multifile Color"),
                                ],
                                group_operator=FieldGroupOperators.OR,
                            )
                        ],
                    ),
                    QueryConditionGroup(object_name="Unittest", field_conditions=[QueryConditionField("StringField", "Unittest Folder")]),
                ],
                result_fields=["StringField", "DateField", SystemFields.OBJECT_ID],
                page_size=2,
                max_hits=10,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
            )
        )

        self.assertEqual(len(result), 3)

    def test_custom_field_schema_query(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=["DateField", SystemFields.OBJECT_ID, SystemFields.SDSTA_ID],
                page_size=1,
                max_hits=1,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
            )
        )

        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertEqual("StringField" not in first.keys(), True)
        self.assertEqual("DateField" in first.keys(), True)
        self.assertEqual("SDSTA_ID" in first.keys(), True)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=["DateField", SystemFields.OBJECT_ID, SystemFields.SDSTA_ID],
                page_size=1,
                max_hits=1,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
                field_schema=FieldSchema.ALL,
            )
        )

        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertEqual("StringField" in first.keys(), True)
        self.assertEqual("DateField" in first.keys(), True)
        self.assertEqual("SDSTA_ID" in first.keys(), True)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=["DateField", SystemFields.OBJECT_ID, SystemFields.SDSTA_ID],
                page_size=1,
                max_hits=1,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
                field_schema=FieldSchema.DEF,
            )
        )

        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertEqual("StringField" not in first.keys(), True)
        self.assertEqual("DateField" in first.keys(), True)
        self.assertEqual("SDSTA_ID" in first.keys(), True)

        result = list(
            client.lol_query(
                object_name="UnittestDoc",
                result_fields=["DateField", SystemFields.OBJECT_ID, SystemFields.SDSTA_ID],
                page_size=1,
                max_hits=1,
                include_file_info=True,
                include_status=True,
                garbage_mode=False,
                field_schema="DEF",
            )
        )

        self.assertGreaterEqual(len(result), 1)
        first = result[0]
        self.assertEqual("StringField" not in first.keys(), True)
        self.assertEqual("DateField" in first.keys(), True)
        self.assertEqual("SDSTA_ID" in first.keys(), True)

    def test_store_in_cache_by_id_multifile(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        for doc_info in self.multifile_docs:
            files = client.store_in_cache_by_id(doc_info["id"])
            self.assertEqual(len(files), doc_info["count"])
            for file in files:
                self.assertIsInstance(file, ResultFile)
                self.assertGreater(file.size(), 0)
                file_path = file.store()
                self.assertTrue(file_path is not None and os.path.exists(file_path))

    def test_store_in_cache_by_id_convert(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        for doc_info in self.multifile_docs:
            files = client.store_in_cache_by_id(doc_info["id"], convert=StoreInCacheByIdConversion.PDF)
            self.assertEqual(len(files), 1)
            for file in files:
                self.assertGreater(file.size(), 0)
                file_bytes = file.bytes()
                if file_bytes is not None:
                    self.assertEqual(file_bytes[0:4].decode("ascii"), "%PDF")
                else:
                    self.fail("File bytes are None")

    def test_get_group_list_encoding(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        result = client.execute(Job(jobname="mng.GetGroupList", Flags=0))
        groups = XmlElement.from_string(result.values["GroupList"])
        self.assertGreater(len(groups), 0)

    def test_result_boolness(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)
        test_result_true = client.execute(Job(Jobs.KRN_GETSERVERINFO, Flags=0, Info=6))
        self.assertTrue(test_result_true)
        test_result_false = client.execute(Job(Jobs.KRN_GETSERVERINFO, Flags=0, Info=666))
        self.assertFalse(test_result_false)

    def test_raise_exception(self):
        client = TcpPoolClient(self.connection_string, "TestApp", "root", "optimal", self.use_ssl)

        def test_function():
            client.execute(Job(Jobs.KRN_GETSERVERINFO, raise_exception=True, Flags=0, Info=666))

        self.assertRaises(BlueException, test_function)

    def test_partially_defect_pool(self):
        client = TcpPoolClient(
            self.connection_string + "#" + "localhost:4001:5", "TestApp", "root", "!;`|K!llEF!llE6!;k", self.use_ssl, connect_timeout=3
        )
        test_job = Job(Jobs.KRN_GETSERVERINFO, Flags=0, Info=6)
        result = client.execute(test_job)
        self.assertEqual(result.values["Value"], "oxtrodbc.dll")


if __name__ == "__main__":
    unittest.main()
