import subprocess
from ..utils import get_local_ip

html="""
<!DOCTYPE html>
<html>
    <head>
        <title>
            PWNED
        </title>
    </head>
    <body>
        <h1>
            You have been spoofed by SYNapse.
        </h1>
        <a href="https://www.github.com/kalandjl/SYNapse">
            How'd we do it?
        </a>
    </body>
</html>
"""

def start_dns_server(port=80):
    """
    This function locally serves an html route as a 
    redirect endpoint for a successfull DNS spoofing attack.
    """

    spoofed_ip = get_local_ip()

    if not spoofed_ip:
        print("[ERROR] Could not determine own IP address")
        return None
    
    print(f"[DNS] Starting HTTP server on {spoofed_ip}:{port}")

    with open('index.html', 'w') as f:
        f.write(html)
    
    try:
        # Start HTTP server on port 80 (requires root)
        subprocess.run(["python3", "-m", "http.server", str(port)], check=True)
    except Exception as e:
        print(f"[DNS] Server error: {e}")
    

    