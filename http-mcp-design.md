# Components (EKS + CloudFront/WAF + NLB + ingress-nginx)

``` mermaid
flowchart LR
    subgraph Client["MCP Client (ChatGPT)"]
    C[C]
    end

    subgraph Edge["Edge"]
    CF[CloudFront<br/>+ AWS WAF]
    NLB[AWS NLB]
    INX[ingress-nginx<br/>(EKS Auto Mode)]
    end

    subgraph Cluster["EKS Cluster"]
    ADP[MCP Adapter (stateless)<br/>JSON-RPC over WS/HTTP<br/>• zod validation<br/>• policy (caps/anti-scrape)<br/>• result shaping<br/>• pseudonymous cookie]
    RDS[(Redis cache)<br/>TTL 60–120s]
    AUTH[Auth Service (optional)<br/>/.well-known, /authorize, /token]
    SRCH[Search API (read-only)]
    end

    C -->|WSS/HTTPS| CF --> NLB --> INX
    INX -->|/mcp| ADP
    INX -->|/.well-known /authorize /token| AUTH
    ADP <-->|cache| RDS
    ADP --> SRCH

```