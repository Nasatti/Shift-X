import urllib.request
import json
import ssl

def test_endpoint(url, method='POST', body=None):
    print(f"Testing {url} ({method}) with body {body}...")
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    # Ignore SSL verification errors if any
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        data = json.dumps(body).encode('utf-8') if body else None
        with urllib.request.urlopen(req, data=data, context=ctx, timeout=5) as response:
            status = response.getcode()
            res_body = response.read().decode('utf-8')
            print(f"  -> SUCCESS ({status}): {res_body[:300]}")
            return True, status, res_body
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return False, None, str(e)

def main():
    base_url = "https://mg839u1xy1.execute-api.us-east-1.amazonaws.com/default"
    
    # We know this one works, let's check it first
    test_endpoint(f"{base_url}/Get_Talks_By_Tag", 'POST', {"tag": "technology", "page": 1, "doc_per_page": 2})
    
    endpoints = [
        "Carrer-Path-master",
        "Career-Path-master",
        "Get_Career_Path",
        "GetCareerPath",
        "Carrer_Path",
        "CareerPath",
        "carrer-path",
        "career-path",
        "Career-Path",
        "Carrer-Path",
        "get_career_path",
        "get-career-path",
        "GetWatchNext",
        "Get_Watch_Next"
    ]
    
    test_payloads = [
        {"position": "Data Scientist"},
        {"job": "Data Scientist"},
        {"role": "Data Scientist"},
        {"job_position": "Data Scientist"},
        {"career_path": "Data Scientist"},
        {"jobTitle": "Data Scientist"},
        {"title": "Data Scientist"}
    ]
    
    for ep in endpoints:
        url = f"{base_url}/{ep}"
        # Try POST with payload
        success, status, body = test_endpoint(url, 'POST', {"job": "Data Scientist"})
        if not success:
            # Try GET
            test_endpoint(url, 'GET')
        else:
            # Let's try different payloads to see which one works
            for payload in test_payloads:
                print(f"Trying payload {payload} for {ep}:")
                test_endpoint(url, 'POST', payload)

if __name__ == '__main__':
    main()
