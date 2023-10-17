import uuid

from httpx import codes

from gotenberg_client._client import GotenbergClient
from tests.conftest import SAMPLE_DIR
from tests.utils import call_run_with_server_error_handling


class TestMiscFunctionality:
    def test_trace_id_header(
        self,
        client: GotenbergClient,
    ):
        trace_id = str(uuid.uuid4())
        with client.merge.merge() as route:
            resp = call_run_with_server_error_handling(
                route.merge([SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"]).trace(
                    trace_id,
                ),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert "Gotenberg-Trace" in resp.headers
        assert resp.headers["Gotenberg-Trace"] == trace_id

    def test_output_filename(
        self,
        client: GotenbergClient,
    ):
        filename = "my-cool-file"
        with client.merge.merge() as route:
            resp = call_run_with_server_error_handling(
                route.merge([SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"]).output_name(
                    filename,
                ),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert "Content-Disposition" in resp.headers
        assert f"{filename}.pdf" in resp.headers["Content-Disposition"]
