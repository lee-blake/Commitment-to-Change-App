import os
import pytest

from django.test import RequestFactory

from commitments.generic_views import GeneratedTemporaryBinaryFileDownloadView, \
    GeneratedTemporaryTextFileDownloadView, GeneratedTemporaryFileDownloadView


@pytest.fixture(name="trivial_request")
def fixture_trivial_request():
    return RequestFactory().get("/")

class TestGeneratedTemporaryFileDownloadView:
    """Tests for GeneratedTemporaryBinaryFileDownloadView"""

    class TestClassParameters:
        """Tests that class fields of GeneratedTemporaryFileDownloadView are correctly used"""

        @pytest.mark.parametrize("file_name", ["first filename", "second filename"])
        def test_filename_is_respected_in_response(self, file_name, trivial_request):
            class ChildClass(GeneratedTemporaryFileDownloadView):
                filename = file_name

                def _write_content_to_file(self, temporary_file):
                    pass

            request = ChildClass.as_view()(trivial_request)
            assert request.filename == file_name

        def test_as_attachment_defaults_to_false(self, trivial_request):
            class ChildClass(GeneratedTemporaryFileDownloadView):
                def _write_content_to_file(self, temporary_file):
                    pass

            request = ChildClass.as_view()(trivial_request)
            assert request.as_attachment is False

        def test_as_attachment_respects_true(self, trivial_request):
            class ChildClass(GeneratedTemporaryFileDownloadView):
                as_attachment = True

                def _write_content_to_file(self, temporary_file):
                    pass

            request = ChildClass.as_view()(trivial_request)
            assert request.as_attachment is True


    class TestGet:
        """Tests for GeneratedTemporaryFileDownloadView.get"""

        def test_file_gets_cleaned_up(self, trivial_request):
            class ChildClass(GeneratedTemporaryFileDownloadView):
                def _write_content_to_file(self, temporary_file):
                    temporary_file.write(b"x")
            response = ChildClass.as_view()(trivial_request)
            underlying_file_name = response.file_to_stream.name
            # Make sure the file actually can be found by the OS (ensure this test could fail)
            assert os.path.exists(underlying_file_name)
            # Stream the file and then dereference the response to simulate user download process
            b"".join(response.streaming_content)
            del response
            assert not os.path.exists(underlying_file_name)


class TestGeneratedTemporaryBinaryFileDownloadView:
    """Tests for GeneratedTemporaryBinaryFileDownloadView"""

    class TestGet:
        """Tests for GeneratedTemporaryBinaryFileDownloadView.get"""

        @pytest.mark.parametrize("content", [b"x", b"y"])
        def test_file_contains_correct_content(self, content, trivial_request):
            class ChildClass(GeneratedTemporaryBinaryFileDownloadView):
                def write_bytes_to_file(self, temporary_file):
                    temporary_file.write(content)
            response = ChildClass.as_view()(trivial_request)
            response_content = b"".join(response.streaming_content)
            assert response_content == content


class TestGeneratedTemporaryTextFileDownloadView:
    """Tests for GeneratedTemporaryTextFileDownloadView"""

    class TestGet:
        """Tests for GeneratedTemporaryTextFileDownloadView.get"""

        @pytest.mark.parametrize("content", ["x", "y"])
        def test_file_contains_correct_content(self, content, trivial_request):
            class ChildClass(GeneratedTemporaryTextFileDownloadView):
                def write_text_to_file(self, temporary_file):
                    temporary_file.write(content)
            response = ChildClass.as_view()(trivial_request)
            response_content = b"".join(response.streaming_content)
            assert response_content.decode() == content
