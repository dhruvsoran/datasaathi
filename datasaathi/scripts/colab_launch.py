"""Start DataSaathi inside Google Colab and print a public link (Cloudflare quick tunnel).
Usage in a Colab cell:  !python scripts/colab_launch.py
Add --no-tunnel to only start the app (used for local testing)."""
import os, re, stat, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
CF_BIN = Path("/tmp/cloudflared")


def wait_for(url: str, seconds: int) -> bool:
    for _ in range(seconds):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def main() -> int:
    # restart cleanly if an older copy of the app (or tunnel) is still running from a previous run of this cell
    for pattern in ("streamlit run app.py", "cloudflared tunnel"):
        subprocess.run(["pkill", "-f", pattern], capture_output=True)       # list form: pkill never matches itself
    time.sleep(2)
    log = open("/tmp/streamlit.log", "w")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
                     cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "DATASAATHI_DB": "/tmp/datasaathi.duckdb"})
    if not wait_for("http://localhost:8501/_stcore/health", 60):
        print("Streamlit did not start. Last log lines:\n" + "".join(open("/tmp/streamlit.log").readlines()[-15:]))
        return 1
    print("App is running on port 8501.")
    if "--no-tunnel" in sys.argv:
        return 0
    if not CF_BIN.exists():
        urllib.request.urlretrieve(CF_URL, CF_BIN)
        CF_BIN.chmod(CF_BIN.stat().st_mode | stat.S_IEXEC)
    subprocess.Popen([str(CF_BIN), "tunnel", "--url", "http://localhost:8501"], stdout=subprocess.DEVNULL, stderr=open("/tmp/cf.log", "w"))
    for _ in range(45):
        time.sleep(1)
        found = re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", open("/tmp/cf.log").read())
        if found:
            print("\nOPEN THIS LINK:", found[0], "\n(keep this Colab tab open; the link stops working when the runtime stops)")
            return 0
    print("No link yet. Run `!tail -5 /tmp/cf.log` and re-run this cell.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
