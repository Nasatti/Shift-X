import sys
import os

try:
    import boto3
except ImportError:
    print("boto3 is not installed. Installing it...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3

def main():
    print("Checking AWS credentials and listing Lambda functions...")
    try:
        # Check if we can load credentials
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            print("No AWS credentials found. Please configure AWS credentials.")
            return
            
        print(f"AWS Access Key ID: {credentials.access_key[:10]}...")
        print(f"AWS Default Region: {session.region_name}")
        
        # Use lambda client
        # Default to us-east-1 if none specified, as it's common for coursework
        region = session.region_name or 'us-east-1'
        client = boto3.client('lambda', region_name=region)
        
        print("Listing Lambda functions...")
        response = client.list_functions()
        functions = response.get('Functions', [])
        
        found = False
        for f in functions:
            name = f['FunctionName']
            print(f" - {name} ({f['Runtime']})")
            if 'carrer' in name.lower() or 'career' in name.lower() or 'path' in name.lower():
                print(f"   *** FOUND TARGET FUNCTION! ***")
                print(f"   Description: {f.get('Description')}")
                print(f"   ARN: {f['FunctionArn']}")
                # Get function details to see configuration (like environment variables)
                details = client.get_function(FunctionName=name)
                print(f"   Code URL: {details.get('Code', {}).get('Location')[:100]}...")
                found = True
                
        if not found:
            print("No career-path functions found in this region. Trying other common regions...")
            for reg in ['us-east-1', 'us-east-2', 'eu-west-1', 'eu-central-1']:
                if reg == region:
                    continue
                try:
                    c = boto3.client('lambda', region_name=reg)
                    res = c.list_functions()
                    funcs = res.get('Functions', [])
                    for f in funcs:
                        name = f['FunctionName']
                        print(f" - {name} ({f['Runtime']}) in {reg}")
                        if 'carrer' in name.lower() or 'career' in name.lower() or 'path' in name.lower():
                            print(f"   *** FOUND TARGET FUNCTION IN {reg}! ***")
                            details = c.get_function(FunctionName=name)
                            print(f"   ARN: {f['FunctionArn']}")
                            found = True
                except Exception as e:
                    pass
                    
    except Exception as e:
        print(f"Error checking AWS: {e}")

if __name__ == '__main__':
    main()
