import unittest

from ecmind_blue_client import Job
from ecmind_blue_client.tcp_client import Connection


class TestTcpClient(unittest.TestCase):
    hostname = "localhost"
    port = 4000
    use_ssl = True

    def test_simple_job_in_context(self):
        with Connection(self.hostname, self.port, "TestApp", "root", "optimal", self.use_ssl) as client:
            test_job = Job("krn.GetServerInfo", Flags=0, Info=6)
            result = client.execute(test_job)
        self.assertEqual(result.values["Value"], "oxtrodbc.dll")

    def test_reveal(self):
        for p in ["optimal", "!;`|K!llEF!llE6!;k"]:
            with Connection(self.hostname, self.port, "TestApp", "root", p, self.use_ssl) as client:
                test_job = Job("krn.GetServerInfo", Flags=0, Info=6)
                result = client.execute(test_job)
            self.assertEqual(result.values["Value"], "oxtrodbc.dll")


if __name__ == "__main__":
    unittest.main()
