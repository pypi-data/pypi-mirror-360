import os
from inspect import getsourcefile
from os.path import dirname
from pipebio.pipebio_client import PipebioClient
from tests.test_helpers import get_project_id, get_parent_id


class TestPipeBioClientIntegration:

    def setup_method(self):
        self.api_url = os.environ.get("PIPE_API_URL")
        print('PIPE_API_URL', self.api_url)

    def test_upload_fasta_file(self):
        """Test file upload and export functionality."""

        client = PipebioClient(url=self.api_url)

        file_name = 'adimab/137_adimab_VH.fsa'
        current_dir = dirname(getsourcefile(lambda: 0))
        test_file = os.path.join(current_dir, f'../sample_data/{file_name}')

        parent_folder_id = get_parent_id(client)
        project_id = get_project_id(client)

        # Test file upload
        result = client.upload_file(
            file_name=test_file,
            absolute_file_location=test_file,
            parent_id=parent_folder_id,
            project_id=project_id,
        )
        ten_mins = 10 * 60
        job = client.jobs.poll_job(result['id'], ten_mins)

        assert job["status"] == "COMPLETE", "Upload failed"
