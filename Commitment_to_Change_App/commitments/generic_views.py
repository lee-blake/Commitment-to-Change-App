import io
import tempfile
from abc import ABC, abstractmethod

from django.http import FileResponse
from django.views.generic.base import View


class GeneratedTemporaryFileDownloadView(View, ABC):
    filename = ""
    as_attachment = False

    def get(self, *args, **kwargs):
        # We use NamedTemporaryFile over TemporaryFile to enable testing that the cleanup
        # actually occurs.
        temp_file = tempfile.NamedTemporaryFile(mode="w+b", delete=True)
        self._write_content_to_file(temp_file)
        # Reset the head so the written content can be read
        print(temp_file)
        temp_file.seek(0)
        return FileResponse(
            temp_file,
            filename=self.filename,
            as_attachment=self.as_attachment
        )

    @abstractmethod
    def _write_content_to_file(self, temporary_file):
        return NotImplemented


class GeneratedTemporaryBinaryFileDownloadView(GeneratedTemporaryFileDownloadView):
    """A generic view for dynamically generating & downloading a small file. The file will 
    automatically be cleaned up when the download has completed as it leverages `tempfile`.
    This also has the advantage of keeping the file in memory on Linux systemd distros.
    
    This view is generally not suitable for large (>1MB) file generation due to reserving a 
    worker during execution.

    This view only supports binary writes. For text writes, use
    GeneratedTemporaryTextFileDownloadView instead."""

    def _write_content_to_file(self, temporary_file):
        self.write_bytes_to_file(temporary_file)

    @abstractmethod
    def write_bytes_to_file(self, temporary_file):
        return NotImplemented


class GeneratedTemporaryTextFileDownloadView(GeneratedTemporaryFileDownloadView):
    """A generic view for dynamically generating & downloading a small file. The file will 
    automatically be cleaned up when the download has completed as it leverages `tempfile`.
    This also has the advantage of keeping the file in memory on Linux systemd distros.
    
    This view is generally not suitable for large (>1MB) file generation due to reserving a 
    worker during execution.

    This view only supports text writes. For binary writes, use
    GeneratedTemporaryBinaryFileDownloadView instead."""

    def _write_content_to_file(self, temporary_file):
        write_text_wrapped_temporary_file = io.TextIOWrapper(temporary_file)
        try:
            self.write_text_to_file(write_text_wrapped_temporary_file)
        finally:
            # This must be detached or else it will close the temporary_file on cleanup,
            # preventing it form being read & delivered in the response
            write_text_wrapped_temporary_file.detach()

    @abstractmethod
    def write_text_to_file(self, temporary_file):
        return NotImplemented
