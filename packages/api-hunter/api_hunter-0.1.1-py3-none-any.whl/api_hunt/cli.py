from api_hunt.core import run_scan_git,run_scan_local
from api_hunt.add_delete import display,delete_data_from_custom,add_data_to_custom
from api_hunt.get_repattern_ai import set_google_api_key,anonymize_digits,get_pattern_gemini
from api_hunt.patterns import API_KEY_PATTERNS, SCAN_EXTENSIONS, IGNORE_PATTERNS

import asyncio

import argparse

def main():
    parser = argparse.ArgumentParser(description='Helps to find API keys in the git staged files i.e (when you git add files) or can search a single local file.')
    parser.add_argument('-d', '--display',action='store_true', help="Display's the custom patterns stored")
    parser.add_argument('-r','--remove',action="store",nargs=1,type=str,help="Remove a stored pattern takes 'key_name' as argument e.g -> hunt -r 'key_name'")
    parser.add_argument('-a','--add',action="store",nargs=2,type=str,help="adds a key and pattern to custom patterns file takes 'key_name' and 'pattern' as arguments e.g -> hunt -a 'key_name' 'pattern'")
    parser.add_argument('-n','--name',action="store",nargs=1,type=str,help="Scans a single file for API key's takes filepath as argument e.g -> hunt -n 'file_path'")
    parser.add_argument('-c','--config',action="store",nargs=1,type=str,help="Takes an API key as argument to configure gemini to be used to get custom regex pattern for your API key e.g -> hunt -c 'API_KEY'")
    parser.add_argument('-re','--regex',action="store",nargs=2,type=str,help="Takes a key_name and API key as arguments to give regex of it which will be added automatically to custom patterns folder to be used to search for API key's  e.g -> hunt -re 'key_name' 'API_key' ")
    parser.add_argument('-v','--verbose',action="store_true",help="Gives verbose result i.e also includes the Matched Pattern in the Output")
    args = parser.parse_args()

    if args.display:
        main_display()
    
    elif args.remove:
        print(f"removing key {args.remove[0]}")
        remove(args.remove[0])
    
    elif args.add:
        print(f"adding key and pattern")
        add_data_to_custom(args.add[0],args.add[1])
    
    elif args.name:
        print(f"Scanning file {args.name[0]}")
        if args.verbose:
            hunt_local(args.name[0],verbose=True)
        else:
            hunt_local(args.name[0],verbose=False)

    elif args.config:
        print("setting api key")
        set_google_api_key(args.config[0])
    
    elif args.regex:
        print("getting the regex pattern")
        get_regex_add(args.regex[0],args.regex[1])
    
    elif args.verbose:
        hunt(verbose=True)

    else:
        hunt(verbose=False)


def hunt(verbose):
    print("Scanning for secrets...")
    asyncio.run(run_scan_git(verbose))


def main_display():
    display()

def remove(key_name):
    delete_data_from_custom(key_name)

def hunt_local(file_path,verbose):
    asyncio.run(run_scan_local(file_path,verbose))


def get_regex_add(key_name,api_key):
    anon_api_key = anonymize_digits(api_key)
    res = get_pattern_gemini(key_name,anon_api_key)
    if res:
        add_data_to_custom(res["key_name"],res["pattern"])
    else:
        print("error getting regex pattern and adding to custom json")