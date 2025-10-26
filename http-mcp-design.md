# Components (EKS + CloudFront/WAF + NLB + ingress-nginx)

```mermaid
flowchart LR
  subgraph Client["MCP Client"]
    C["Client"]
  end

  subgraph Edge["Edge"]
    CF["CloudFront + AWS WAF"]
    NLB["AWS NLB"]
    INX["ingress nginx"]
  end

  subgraph Cluster["EKS Cluster"]
    ADP["MCP Adapter\nstateless\nJSON RPC over WS or HTTP\nzod validation\npolicy caps anti scrape\nresult shaping\npseudonymous cookie"]
    RDS["Redis cache\nTTL 60-120s"]
    AUTH["Auth Service optional\nwell known\nauthorize\ntoken"]
    SRCH["Search API\nread only"]
  end

  C -->|WSS HTTPS| CF --> NLB --> INX
  INX -->|mcp endpoint| ADP
  INX -->|oauth endpoints| AUTH
  ADP <-->|cache| RDS
  ADP --> SRCH
```