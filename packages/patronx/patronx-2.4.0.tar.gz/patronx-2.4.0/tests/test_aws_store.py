from patronx.aws_store import AWSAssetStore


def test_from_env(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    store = AWSAssetStore.from_env()
    assert store.aws_access_key_id == "id"
    assert store.aws_secret_access_key == "secret"
    assert store.region_name == "us-east-1"


def test_upload_file(monkeypatch, tmp_path):
    called = {}

    class FakeClient:
        def upload_file(self, file_path, bucket, key):
            called["args"] = (file_path, bucket, key)

    monkeypatch.setattr(AWSAssetStore, "_client", lambda self: FakeClient())

    f = tmp_path / "file"
    f.write_text("data")
    store = AWSAssetStore("id", "secret", "reg")
    store.upload_file(f, "bucket", "key")

    assert called["args"] == (str(f), "bucket", "key")