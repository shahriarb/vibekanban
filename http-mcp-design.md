# Components (EKS + CloudFront/WAF + NLB + ingress-nginx)

```mermaid
flowchart LR
  subgraph Client["MCP Client (ChatGPT)"]
    C[Client]
  end

  subgraph Edge["Edge"]
    CF[CloudFront + AWS WAF]
    NLB[AWS NLB]
    INX[ingress-nginx]
  end

  subgraph Cluster["EKS Cluster"]
    ADP[MCP Adapter (stateless)\nJSON-RPC over WS/HTTP\nzod validation\npolicy (caps/anti-scrape)\nresult shaping\npseudonymous cookie]
    RDS[(Redis cache\nTTL 60-120s)]
    AUTH[Auth Service (optional)\n/.well-known, /authorize, /token]
    SRCH[Search API (read-only)]
  end

  C -->|WSS/HTTPS| CF --> NLB --> INX
  INX -->|/mcp| ADP
  INX -->|/.well-known /authorize /token| AUTH
  ADP <-->|cache| RDS
  ADP --> SRCH
```