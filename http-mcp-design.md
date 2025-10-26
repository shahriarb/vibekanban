# Http MCP

## Components (EKS + CloudFront/WAF + NLB + ingress-nginx)

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
    ADP["MCP Adapter\nstateless
         JSON RPC over WS or HTTP
         zod validation
         policy caps anti scrape
         result shaping
         pseudonymous cookie"]
    RDS["Redis cache
         TTL 60-120s"]
    AUTH["Auth Service optional
          well known
          authorize
          token"]
    SRCH["Search API
          read only"]
  end

  C -->|WSS HTTPS| CF --> NLB --> INX
  INX -->|mcp endpoint| ADP
  INX -->|oauth endpoints| AUTH
  ADP <-->|cache| RDS
  ADP --> SRCH
```


## Anonymous search flow

```mermaid
sequenceDiagram
    participant U as "MCP Client"
    participant CF as "CloudFront and WAF"
    participant N as "AWS NLB"
    participant I as "ingress nginx"
    participant A as "MCP Adapter"
    participant R as "Redis cache"
    participant S as "Search API"

    Note over U: "User calls v1.search_properties anonymous"

    U->>CF: "tools call request"
    CF->>CF: "apply WAF rules rate and bot"
    CF->>N: "forward request"
    N->>I: "forward tcp"
    I->>I: "local rate limit per ip"
    I->>A: "route to mcp endpoint"

    A->>A: "validate input and normalize"
    A->>A: "policy anonymous apply caps and anti scrape"
    A->>R: "cache lookup by normalized query"

    alt "cache hit"
        R-->>A: "cached items"
    else "cache miss"
        A->>S: "search with filters"
        S-->>A: "results public fields"
        A->>R: "cache set ttl 60 to 120 seconds"
    end

    A-->>I: "result minimal fields"
    I-->>U: "response ok set cookie mcp uid if first visit"

```

## Optional authorization flow for MCP OAuth with PKCE

```mermaid
sequenceDiagram
    participant U as "MCP Client"
    participant CF as "CloudFront and WAF"
    participant N as "AWS NLB"
    participant I as "Ingress nginx"
    participant AUTH as "Auth Service"
    participant A as "MCP Adapter"

    Note over U: "Client supports MCP authorization optional"

    U->>CF: "get metadata well known oauth server"
    CF->>N: "forward"
    N->>I: "forward"
    I->>AUTH: "serve metadata json"
    AUTH-->>U: "issuer and endpoints"

    U->>CF: "get authorize with code challenge pkce"
    CF->>N: "forward"
    N->>I: "forward"
    I->>AUTH: "authorize user interaction or stub"
    AUTH-->>U: "redirect with authorization code"

    U->>CF: "post token with code and code verifier"
    CF->>N: "forward"
    N->>I: "forward"
    I->>AUTH: "exchange code for access token"
    AUTH-->>U: "access token and scope"

    Note over U: "Now call MCP with bearer token"

    U->>CF: "tools call with authorization bearer"
    CF->>N: "forward"
    N->>I: "forward"
    I->>A: "route to mcp endpoint"
    A->>A: "validate jwt and build context"
    A-->>U: "results with policy for authenticated"

```

## WebSocket upgrade and per message policy

```mermaid
sequenceDiagram
    participant U as "MCP Client"
    participant I as "ingress nginx"
    participant A as "MCP Adapter"

    U->>I: "websocket upgrade with optional authorization header"
    I-->>U: "switching protocols"

    loop "json rpc messages over websocket"
        U->>A: "tools call v1.search_properties"
        A->>A: "if session has token then policy authenticated else policy anonymous"
        A-->>U: "result with caps applied"
    end

```

## Error and abuse control decision points

```mermaid
flowchart TB
  U["Client"] --> CF["CloudFront and WAF"]
  CF --> NLB["AWS NLB"]
  NLB --> INX["ingress nginx"]
  INX --> ADP["MCP Adapter"]

  CF -->|WAF rate and bot rules| CF
  INX -->|limit rps per ip| INX
  ADP -->|policy anonymous or authenticated
          limit max 50 radius max 10
          reject blank plus wide queries| ADP
  ADP -->|timeout and retries to search api| ADP
```