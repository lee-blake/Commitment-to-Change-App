import tempfile
from abc import ABC, abstractmethod

from django.http import FileResponse
from django.views.generic.base import View


class GeneratedTemporaryFileDownloadView(View, ABC):
    """A generic view for dynamically generating & downloading a small file. The file will 
    automatically be cleaned up when the download has completed as it leverages `tempfile`.
    This also has the advantage of keeping the file in memory on Linux systemd distros.
    
    This view is generally not suitable for large (>1MB) file generation due to reserving a 
    worker during execution.

    This view only supports binary writes. For text writes, use
    GeneratedTemporaryTextFileDownloadView instead."""

    filename = ""
    as_attachment = True

    def get(self, *args, **kwargs):
        # We use NamedTemporaryFile over TemporaryFile to enable testing that the cleanup
        # actually occurs.
        temp_file = tempfile.NamedTemporaryFile(mode="w+b", delete=True)
        self.write_bytes_to_file(temp_file)
        # Reset the head so the written content can be read
        temp_file.seek(0)
        return FileResponse(
            temp_file,
            filename=self.filename,
            as_attachment=self.as_attachment
        )

    @abstractmethod
    def write_bytes_to_file(self, temporary_file):
        return NotImplemented
