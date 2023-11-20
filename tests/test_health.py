from gotenberg_client._client import GotenbergClient
from gotenberg_client._health import StatusOptions


class TestHealthStatus:
    def test_health_endpoint(
        self,
        client: GotenbergClient,
    ):
        status = client.health.health()
        assert status.overall == StatusOptions.Up
        assert status.chromium is not None
        assert status.chromium.status == StatusOptions.Up
        if "uno" in status.data:
            assert status.uno is not None
            assert status.uno.status == StatusOptions.Up
