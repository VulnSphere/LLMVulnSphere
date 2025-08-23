Security Analysis Report: Node.js VM Sandbox File System Access Vulnerability

##  Executive Summary

  A critical security vulnerability has been identified in the Node.js VM sandbox
   implementation of the Sim project. The vulnerability allows arbitrary file
  system access through the fetch API with the file:// protocol. This report
  details the root cause analysis, proof of concept, impact assessment, and
  recommended remediation steps.

  Affected Component: /apps/sim/app/api/function/execute/route.ts

##  Root Cause Analysis

  The vulnerability exists in the sandbox implementation found in
  /apps/sim/app/api/function/execute/route.ts. The critical flaw is in the
  context creation for the VM sandbox:

```javascript
    1 // File: /apps/sim/app/api/function/execute/route.ts (lines 379-395)
    2 const context = createContext({
    3   params: executionParams,
    4   environmentVariables: envVars,
    5   ...contextVariables,
    6   fetch: globalThis.fetch || require('node-fetch').default, // <--
      VULNERABILITY
    7   console: {
    8     log: (...args: any[]) => {
    9       const logMessage = `${args
   10         .map((arg) => (typeof arg === 'object' ? JSON.stringify(arg)
      : String(arg)))
   11         .join(' ')}\n`
   12       stdout += logMessage
   13     },
   14     error: (...args: any[]) => {
   15       const errorMessage = `${args
   16         .map((arg) => (typeof arg === 'object' ? JSON.stringify(arg)
      : String(arg)))
   17         .join(' ')}\n`
   18       logger.error(`[${requestId}] Code Console Error:
      ${errorMessage}`)
   19       stdout += `ERROR: ${errorMessage}`
   20     },
   21   },
   22 });
```

  The root cause is that the implementation directly passes the native fetch
  function to the sandbox context without any restrictions or wrappers. This
  native fetch implementation supports multiple URL schemes, including the
  file:// protocol, which allows access to the host file system.

  Technical Details

   1. The Node.js VM module creates a sandboxed context that isolates code execution
       from the global scope
   2. However, the sandbox only isolates JavaScript objects and not underlying
      system resources
   3. When the native fetch function is passed directly to the sandbox, it retains
      its full capabilities
   4. The fetch function supports the file:// protocol, which allows reading files
      from the file system
   5. No URL validation or protocol restriction is implemented before executing the
      fetch requests

##  Proof of Concept

  The following curl command demonstrates the vulnerability by reading the
  contents of /etc/passwd from the server's file system:


```bash
curl -X POST http://IP:3000/api/function/execute -H
     "Content-Type: application/json" -d '{"code":"return
     fetch(\"file:///etc/passwd\").then(r => r.text()).catch(e =>
     e.toString())", "timeout":5000}'

```
  
##  Remediation

Implement a secure wrapper around the fetch function that restricts URL
  protocols:

```js
    1 const safeFetch = async (url, options) => {
    2   // Parse the URL to validate it
    3   let parsedUrl;
    4   try {
    5     parsedUrl = new URL(url);
    6   } catch (e) {
    7     throw new Error('Invalid URL');
    8   }
    9
   10   // Only allow http and https protocols
   11   if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !==
      'https:') {
   12     throw new Error('Only HTTP and HTTPS protocols are allowed');
   13   }
   14
   15   // Block access to internal networks (optional)
   16   // This requires additional implementation to resolve hostnames and
      check IP ranges
   17
   18   // Call the original fetch with the validated URL
   19   return fetch(url, options);
   20 };
   21
   22 // Use the safe fetch in the context
   23 const context = createContext({
   24   // ...other context properties
   25   fetch: safeFetch,
   26   // ...
   27 });
```

  The vulnerability in the Node.js VM sandbox implementation represents a
  critical security risk that allows arbitrary file system access. The root cause
   is the direct inclusion of the native fetch function in the sandbox context
  without appropriate restrictions. This vulnerability can be exploited to read
  sensitive files from the host system.

  Immediate action is recommended to implement proper URL validation and protocol
   restrictions for the fetch function. Long-term, a more comprehensive security
  review of the sandbox implementation and adoption of more secure sandboxing
  technologies should be considered.

