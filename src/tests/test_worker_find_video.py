import unittest
from unittest.mock import patch, Mock
import json
from src.ui.workers.find_video_worker import FindVideoWorker


class TestWorkerFindVideo(unittest.TestCase):
    """ Tests for WorkerFindVideo with mocking subprocess. """
    def setUp(self):
        """ Create a worker instance before each test. """
        self._worker = FindVideoWorker()
        self._test_link: str = "https://www.youtube.com/"

    @patch("src.ui.workers.find_video_worker.subprocess.Popen")
    def test_search_video_success(self, mock_popen):
        """Successful search: subprocess returns valid JSON with all required fields."""
        received = []
        self._worker.video_found_signal.connect(lambda *args: received.append(args))

        mock_process = Mock()
        mock_json = {
            "title": "Test video",
            "uploader": "Denis Dennisov",
            "description": "Simple description video."
        }

        mock_process.communicate.return_value = (json.dumps(mock_json), "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        self._worker.get_info_about_video(self._test_link)

        self.assertEqual(len(received), 1)
        name_video, name_channel, description, preview = received[0]
        self.assertEqual(name_video, mock_json["title"])
        self.assertEqual(name_channel, mock_json["uploader"])
        self.assertEqual(description, mock_json["description"])

    @patch("src.ui.workers.find_video_worker.subprocess.Popen")
    def test_search_video_error(self, mock_popen):
        """Error case: subprocess returns non-zero exit code."""
        received = []
        self._worker.video_found_signal.connect(lambda *args: received.append(args))

        mock_process = Mock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        self._worker.get_info_about_video(self._test_link)

        self.assertEqual(len(received), 0)

    @patch("src.ui.workers.find_video_worker.subprocess.Popen")
    def test_search_video_invalid_json(self, mock_popen):
        """Error case: subprocess returns invalid JSON."""
        received = []
        self._worker.video_found_signal.connect(lambda *args: received.append(args))

        mock_process = Mock()
        mock_process.communicate.return_value = (b"invalid json", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        self._worker.get_info_about_video(self._test_link)

        self.assertEqual(len(received), 0)

    @patch("src.ui.workers.find_video_worker.subprocess.Popen")
    def test_search_video_missing_field(self, mock_popen):
        """Error case: JSON lacks required field."""
        received = []
        self._worker.video_found_signal.connect(lambda *args: received.append(args))

        mock_process = Mock()
        mock_process.communicate.return_value = (json.dumps({"title": "Some Video"}), b"")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        self._worker.get_info_about_video(self._test_link)

        self.assertEqual(len(received), 0)


if __name__ == "__main__":
    unittest.main()
