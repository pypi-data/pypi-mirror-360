import subprocess
import asyncio
import os
from pathlib import Path
import re
import json
from api_hunt.patterns import API_KEY_PATTERNS, SCAN_EXTENSIONS, IGNORE_PATTERNS

def is_git_directory(path='.'):
    try:
        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', '--is-inside-work-tree'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip() == 'true'
    except subprocess.CalledProcessError:
        return False

def get_staged_files():
    try:
        result = subprocess.run(["git","diff","--cached","--name-only"],
                                text=True,capture_output=True)
        
        if result.returncode != 0:
            print(f"error running subprocess {result.stderr}")
            return []
        else:
            return [f.strip() for f in result.stdout.splitlines() if f.strip()]
        
    except subprocess.CalledProcessError as e:
            print(f"Error running git diff: {e.stderr}")
            return []
    except subprocess.SubprocessError as e:
            print(f"Subprocess error: {e}")
            return []





def should_ignore(file_path):
    for pattern in IGNORE_PATTERNS:    
        if re.search(pattern,file_path):
            return True
    return False


def should_search(file_path):
    if should_ignore(file_path):
        return False
    _,ext = os.path.splitext(file_path)
    if ext.lower() in SCAN_EXTENSIONS:
        return True
    else:
        return False

async def get_file_content(file_path):

    try:
        proc = await asyncio.create_subprocess_exec("git","show",f":{file_path}",
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE)
        
        stdout,stderr = await proc.communicate()
        
        if proc.returncode != 0:
            print(f"Error running git show: {stderr.decode()}")
            return ""        
        
        content = stdout.decode()
        return content
    
    except Exception as e:
        print(f"error getting file contents {e}")
        return ""
    



async def scan_content(content:str,file_path:str):

    try:
        custom_pattern_path = Path.home() / "api_hunt_envs" / "custom_pattern.json"

        if custom_pattern_path.exists() and os.stat(custom_pattern_path).st_size !=0:
            with open(custom_pattern_path,"r") as f:
                data = json.load(f)

            API_KEY_PATTERNS_COMBINED = API_KEY_PATTERNS + [d["pattern"] for d in data]
        else:
            API_KEY_PATTERNS_COMBINED = API_KEY_PATTERNS

        findings = []

        for i,line in enumerate(content.splitlines(),1):
            for pattern in API_KEY_PATTERNS_COMBINED:
                matches = re.finditer(pattern,line,re.IGNORECASE)
                if not matches:
                    continue
                for match in matches:
                    findings.append({
                            "file_name":file_path,
                            "match":match.group(0),
                            "line":i,
                            "context": line.strip()
                        
                        })
        return findings
    
    except Exception as e:
        return f"error scanning files error {e}"
    


async def process(file):
    content = await get_file_content(file)
    return await scan_content(content,file)


async def run_scan_local(file_path,verbose=False):
    
    try:
        YELLOW_BG = "\033[30;43m"
        GREEN_BG  = "\033[30;42m"
        RED_BG    = "\033[30;41m"
        RESET     = "\033[0m"

        with open(file_path,"r") as file:
            content = file.read()
        findings = await scan_content(content,file_path)
   
        unique_logs = []
        seen = set()
        for res in findings:
            key = (res.get("file_name",''),res.get("line",''),res.get("match",''))
            check = (key[0],key[1])
            if check not in seen:
                seen.add(check)
                unique_logs.append(key)

        if not unique_logs:
            print("No Possible key found.")
        else:
            for logs in unique_logs:
                    if verbose:
                        print(
                            f"found possible API key in file {YELLOW_BG}{logs[0]}{RESET}, "
                            f"{GREEN_BG} line : {logs[1]}{RESET}, "
                            f"matched pattern : {RED_BG}{logs[2]}{RESET}"
                        )
                    else:
                        print(
                            f"found possible API key in file {YELLOW_BG}{logs[0]}{RESET}, "
                            f"{GREEN_BG} line : {logs[1]}{RESET}, "
                        )
      

    except FileNotFoundError as e:
        print(f"File not found error {e}")
        return
    except Exception as e:
        print(f"Error scanning local file {file_path}, error {e}")
        return




async def run_scan_git(verbose=False):
    if is_git_directory():
        files = get_staged_files()

        YELLOW_BG = "\033[30;43m"
        GREEN_BG  = "\033[30;42m"
        RED_BG    = "\033[30;41m"
        RESET     = "\033[0m"

        if isinstance(files,list) and len(files)>0:
            tasks = [process(file) for file in files
                    if should_search(file)]
            
            results = await asyncio.gather(*tasks)

            flat_results = [log for r in results for log in r]

            unique_logs = []
            seen = set()
            for res in flat_results:
                key = (res.get("file_name",''),res.get("line",''),res.get("match",''))
                check = (key[0],key[1])
                if check not in seen:
                    seen.add(check)
                    unique_logs.append(key)

            if not unique_logs:
                print("No Possible key found.")
            else:
                for logs in unique_logs:
                    if verbose:
                        print(
                            f"found possible API key in file {YELLOW_BG}{logs[0]}{RESET}, "
                            f"{GREEN_BG} line : {logs[1]}{RESET}, "
                            f"matched pattern : {RED_BG}{logs[2]}{RESET}"
                        )
                    else:
                        print(
                            f"found possible API key in file {YELLOW_BG}{logs[0]}{RESET}, "
                            f"{GREEN_BG} line : {logs[1]}{RESET}, "
                        )

        elif len(files)==0:
            print("no files found in index please git add to add files")
   
    else:
        print("No git found please intialize a git Repo")

