import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_ftv():
    loader = importlib.machinery.SourceFileLoader("ftv_under_test", str(ROOT / "ftv"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class FtvTests(unittest.TestCase):
    def setUp(self):
        self.ftv = load_ftv()

    def test_device_serial_supports_ipv4_and_ipv6(self):
        self.assertEqual(self.ftv.device_serial("192.0.2.10"), "192.0.2.10:5555")
        self.assertEqual(self.ftv.device_serial("2001:db8::10"), "[2001:db8::10]:5555")

    def test_invalid_configuration_exits_with_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text("[]", encoding="utf-8")
            self.ftv.CONFIG_FILE = config
            with self.assertRaises(SystemExit) as error:
                self.ftv.load_cfg()
        self.assertIn("expected an object", str(error.exception))

    def test_invalid_ip_is_rejected_before_saving(self):
        with self.assertRaises(SystemExit) as error:
            self.ftv.cmd_set_ip("not-an-ip")
        self.assertIn("not a valid IP address", str(error.exception))

    def test_launch_uses_resolved_main_activity_after_monkey_fails(self):
        responses = [
            SimpleNamespace(returncode=1, stdout=""),
            SimpleNamespace(returncode=0, stdout="com.example.app/.MainActivity\n"),
            SimpleNamespace(returncode=0, stdout="Starting: Intent\n"),
        ]
        with mock.patch.object(self.ftv, "ensure_connected"), \
             mock.patch.object(self.ftv, "adb", side_effect=responses) as adb:
            self.ftv.cmd_launch("com.example.app")

        self.assertEqual(
            adb.call_args_list[1][0],
            ("shell", "cmd", "package", "resolve-activity", "--brief",
             "-a", "android.intent.action.MAIN", "-p", "com.example.app"),
        )
        self.assertEqual(
            adb.call_args_list[2][0],
            ("shell", "am", "start", "-n", "com.example.app/.MainActivity"),
        )

    def test_screenshot_always_removes_its_unique_remote_file(self):
        with mock.patch.object(self.ftv, "ensure_connected"), \
             mock.patch.object(self.ftv, "adb", side_effect=[None, SystemExit("pull failed"), None]) as adb:
            with self.assertRaises(SystemExit):
                self.ftv.cmd_screenshot("capture.png")

        remote = adb.call_args_list[0][0][-1]
        self.assertTrue(remote.startswith("/sdcard/ftv_shot_"))
        self.assertEqual(adb.call_args_list[2][0], ("shell", "rm", remote))

    def test_stream_binds_to_lan_address_and_uses_tokenized_url(self):
        socket = mock.Mock()
        socket.getsockname.return_value = ("192.0.2.20", 50000)
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "video.mkv"
            video.write_bytes(b"video")
            with mock.patch.object(self.ftv, "ensure_connected"), \
                 mock.patch.object(self.ftv, "get_ip", return_value="192.0.2.10"), \
                 mock.patch.object(self.ftv, "adb") as adb, \
                 mock.patch("socket.socket", return_value=socket), \
                 mock.patch("http.server.ThreadingHTTPServer") as server_class, \
                 mock.patch.object(self.ftv.time, "sleep"):
                server = server_class.return_value
                server.__enter__.return_value = server
                self.ftv.cmd_stream(str(video), 8766)

            self.assertEqual(server_class.call_args[0][0], ("192.0.2.20", 8766))
            launch_args = adb.call_args_list[1][0]
            url = launch_args[launch_args.index("-d") + 1]
            self.assertRegex(url, r"^http://192\.0\.2\.20:8766/stream/[A-Za-z0-9_-]+$")

            handler_class = server_class.call_args[0][1]
            handler = handler_class.__new__(handler_class)
            handler.path = "/" + url.split("/", 3)[3]
            handler.headers = {"Range": "bytes=99-"}
            handler.send_response = mock.Mock()
            handler.send_header = mock.Mock()
            handler.end_headers = mock.Mock()
            self.assertIsNone(handler.send_head())
            handler.send_response.assert_called_once_with(416)


if __name__ == "__main__":
    unittest.main()
