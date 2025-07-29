"""Module test_download"""
import subprocess


def test_script_runs(tmp_path):
    """ test_script_runs """
    out_file = tmp_path / "test.bin"

    # Use a known small binary resource for testing
    url = "https://httpbin.org/bytes/10"

    result = subprocess.run([
        "python", "download_retry.py",
        "--url", url,
        "--delta_t", "1",
        "--max_t", "5",
        "--out", str(out_file),
        "--insecure", "true"
    ], check=False)

    assert result.returncode == 0
    assert out_file.exists()
    assert out_file.stat().st_size == 10
