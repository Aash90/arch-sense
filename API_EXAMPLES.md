# API Usage Examples

## Base URL
```
http://localhost:3000/api
```

## Health Check

### Request
```bash
curl -X GET http://localhost:3000/api/health
```

### Response
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "timestamp": "2024-04-07T10:30:45.123Z"
  }
}
```

---

## Session Management

### 1. Create New Session

**Request**
```bash
curl -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Design a notification system for 100M users"
  }'
```

**Response**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4",
    "nodes": [],
    "edges": [],
    "phase": "PROBLEM_STATEMENT",
    "scenario": "Design a notification system for 100M users",
    "scalingChallenge": "",
    "signals": [],
    "messages": [],
    "evaluation": null,
    "stressEvents": [],
    "currentStressIndex": -1,
    "createdAt": 1712489445123,
    "updatedAt": 1712489445123
  }
}
```

---

### 2. Get All Sessions

**Request**
```bash
curl -X GET "http://localhost:3000/api/sessions?limit=10&offset=0"
```

**Response**
```json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4",
      "nodes": [...],
      "edges": [...],
      ...
    }
  ]
}
```

---

### 3. Get Specific Session

**Request**
```bash
curl -X GET http://localhost:3000/api/sessions/a1b2c3d4
```

**Response**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4",
    "nodes": [],
    "edges": [],
    ...
  }
}
```

---

### 4. Update Session

**Request**
```bash
curl -X POST http://localhost:3000/api/sessions/a1b2c3d4 \
  -H "Content-Type: application/json" \
  -d '{
    "phase": "DESIGN",
    "scalingChallenge": "Handle 100x traffic spike",
    "nodes": [
      {
        "id": "node1",
        "type": "API_GATEWAY",
        "x": 100,
        "y": 100,
        "label": "API Gateway",
        "properties": {}
      },
      {
        "id": "node2",
        "type": "LOAD_BALANCER",
        "x": 300,
        "y": 100,
        "label": "Load Balancer",
        "properties": {}
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "label": "routes to"
      }
    ]
  }'
```

**Response**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4",
    "phase": "DESIGN",
    "scalingChallenge": "Handle 100x traffic spike",
    "nodes": [...],
    "edges": [...],
    "signals": ["NO_LOAD_BALANCER"],
    "updatedAt": 1712489500000
  }
}
```

The server automatically detects design signals:
- `HAS_MESSAGE_QUEUE`
- `NO_LOAD_BALANCER`
- `DIRECT_EXTERNAL_CALL`
- `ASYNC_PROCESSING`
- `SPOF_DATABASE`

---

### 5. Get Session Summary

**Request**
```bash
curl -X GET http://localhost:3000/api/sessions/a1b2c3d4/summary
```

**Response**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4",
    "phase": "DESIGN",
    "nodesCount": 2,
    "edgesCount": 1,
    "messagesCount": 0,
    "signals": ["NO_LOAD_BALANCER"],
    "hasEvaluation": false,
    "createdAt": 1712489445123,
    "updatedAt": 1712489500000
  }
}
```

---

### 6. Delete Session

**Request**
```bash
curl -X DELETE http://localhost:3000/api/sessions/a1b2c3d4
```

**Response**
```json
{
  "success": true
}
```

---

## AI Feedback

### 1. Get Architect Feedback

**Request**
```bash
curl -X POST http://localhost:3000/api/ai/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {
        "id": "node1",
        "type": "API_GATEWAY",
        "x": 100,
        "y": 100,
        "label": "API Gateway",
        "properties": {}
      },
      {
        "id": "node2",
        "type": "MICROSERVICE",
        "x": 300,
        "y": 100,
        "label": "Auth Service",
        "properties": {}
      },
      {
        "id": "node3",
        "type": "DATABASE",
        "x": 500,
        "y": 100,
        "label": "User DB",
        "properties": {}
      }
    ],
    "edges": [
      {
        "id": "e1",
        "source": "node1",
        "target": "node2",
        "label": "calls"
      },
      {
        "id": "e2",
        "source": "node2",
        "target": "node3",
        "label": "queries"
      }
    ],
    "history": [
      {
        "id": "m1",
        "role": "architect",
        "content": "Welcome to the design review.",
        "timestamp": 1712489445000
      }
    ],
    "phase": "DESIGN",
    "scenario": "Design a notification system for 100M users",
    "scalingChallenge": "Handle 100x traffic spike"
  }'
```

**Response**
```json
{
  "success": true,
  "data": {
    "feedback": "I see you have a single database without replication or sharding. How will you handle 100x traffic on this single instance? Also, where's your caching layer? For 100M users, you need Redis or similar between your API Gateway and service."
  }
}
```

---

### 2. Get Final Evaluation

**Request**
```bash
curl -X POST http://localhost:3000/api/ai/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {
        "id": "node1",
        "type": "LOAD_BALANCER",
        "x": 100,
        "y": 100,
        "label": "Load Balancer",
        "properties": {}
      },
      {
        "id": "node2",
        "type": "MICROSERVICE",
        "x": 300,
        "y": 100,
        "label": "Notification Service",
        "properties": {}
      },
      {
        "id": "node3",
        "type": "CACHE",
        "x": 300,
        "y": 200,
        "label": "Redis Cache",
        "properties": {}
      },
      {
        "id": "node4",
        "type": "MESSAGE_QUEUE",
        "x": 500,
        "y": 100,
        "label": "RabbitMQ",
        "properties": {}
      },
      {
        "id": "node5",
        "type": "DATABASE",
        "x": 500,
        "y": 200,
        "label": "PostgreSQL",
        "properties": {}
      }
    ],
    "edges": [
      {"id": "e1", "source": "node1", "target": "node2"},
      {"id": "e2", "source": "node2", "target": "node3"},
      {"id": "e3", "source": "node2", "target": "node4"},
      {"id": "e4", "source": "node4", "target": "node5"}
    ],
    "history": [
      {
        "id": "m1",
        "role": "architect",
        "content": "Your design looks much better now.",
        "timestamp": 1712489500000
      }
    ],
    "scenario": "Design a notification system for 100M users",
    "scalingChallenge": "Handle 100x traffic spike"
  }'
```

**Response**
```json
{
  "success": true,
  "data": {
    "evaluation": {
      "scalability": 82,
      "reliability": 78,
      "clarity": 85,
      "feedback": "Your design demonstrates good understanding of distributed systems. You've included a load balancer, caching layer, and asynchronous processing with message queues. The architecture can handle significant load increases.",
      "strengths": [
        "Good separation of concerns with load balancer",
        "Message queue for async notification delivery",
        "Cache layer for frequently accessed data",
        "Reasonable component distribution"
      ],
      "weaknesses": [
        "No mention of database replication or sharding",
        "Missing monitoring and alerting systems",
        "No disaster recovery or failover strategy",
        "Single database instance is potential SPOF"
      ]
    }
  }
}
```

---

### 3. Send Message to Architect

**Request**
```bash
curl -X POST http://localhost:3000/api/ai/message \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "a1b2c3d4",
    "userMessage": "Should I use MySQL or PostgreSQL for the database?",
    "nodes": [...],
    "edges": [...],
    "history": [
      {
        "id": "m1",
        "role": "architect",
        "content": "Welcome to the design review.",
        "timestamp": 1712489445000
      },
      {
        "id": "m2",
        "role": "user",
        "content": "I've added a load balancer and cache",
        "timestamp": 1712489500000
      },
      {
        "id": "m3",
        "role": "architect",
        "content": "Good start. Now tell me how you're handling failures.",
        "timestamp": 1712489550000
      }
    ],
    "context": {
      "phase": "DESIGN",
      "scenario": "Design a notification system for 100M users",
      "scalingChallenge": "Handle 100x traffic spike"
    }
  }'
```

**Response**
```json
{
  "success": true,
  "data": {
    "message": "For 100M users with high throughput, PostgreSQL with horizontal read replicas and shared-nothing architecture is better than MySQL. You'll want to shard your user data by region or user ID. PostgreSQL handles JSON better too if you have flexible notification configurations."
  }
}
```

The session is automatically updated with the new message exchange.

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "nodes and edges are required"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Session a1b2c3d4 not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Failed to get architect feedback"
}
```

---

## Session Data Structure

### Full Session Object
```json
{
  "id": "string",
  "nodes": [
    {
      "id": "string",
      "type": "LOAD_BALANCER|API_GATEWAY|MICROSERVICE|DATABASE|CACHE|MESSAGE_QUEUE|CDN|EXTERNAL_SERVICE|COMMENT",
      "x": number,
      "y": number,
      "label": "string",
      "properties": { "key": "value" }
    }
  ],
  "edges": [
    {
      "id": "string",
      "source": "string (node id)",
      "target": "string (node id)",
      "label": "string (optional)"
    }
  ],
  "phase": "PROBLEM_STATEMENT|DESIGN|STRESS|EVALUATION",
  "scenario": "string",
  "scalingChallenge": "string",
  "signals": [
    "HAS_MESSAGE_QUEUE|DIRECT_EXTERNAL_CALL|ASYNC_PROCESSING|SPOF_DATABASE|NO_LOAD_BALANCER"
  ],
  "messages": [
    {
      "id": "string",
      "role": "architect|user",
      "content": "string",
      "timestamp": number
    }
  ],
  "evaluation": {
    "scalability": number,
    "reliability": number,
    "clarity": number,
    "feedback": "string",
    "strengths": ["string"],
    "weaknesses": ["string"]
  } | null,
  "stressEvents": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "impact": "string",
      "triggered": boolean
    }
  ],
  "currentStressIndex": number,
  "createdAt": number,
  "updatedAt": number
}
```

---

## Common Workflows

### Complete Design Review Workflow

```bash
# 1. Create session
SESSION_ID=$(curl -s -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"scenario":"..."}' | jq -r '.data.id')

# 2. Add nodes and edges
curl -X POST http://localhost:3000/api/sessions/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"nodes":[...],"edges":[...]}'

# 3. Get architect feedback
curl -X POST http://localhost:3000/api/ai/feedback \
  -H "Content-Type: application/json" \
  -d '{"nodes":[...],"edges":[...],"history":[...],"phase":"DESIGN"}'

# 4. Continue conversation
curl -X POST http://localhost:3000/api/ai/message \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"'$SESSION_ID'","userMessage":"...","nodes":[...]}'

# 5. Get final evaluation
curl -X POST http://localhost:3000/api/ai/evaluate \
  -H "Content-Type: application/json" \
  -d '{"nodes":[...],"edges":[...],"history":[...]}'

# 6. Save evaluation
curl -X POST http://localhost:3000/api/sessions/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"phase":"EVALUATION","evaluation":{...}}'
```

---

## Testing with TypeScript/JavaScript

```typescript
// Create session
const sessionResponse = await fetch('http://localhost:3000/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ scenario: 'Design a scalable API' })
});

const { data: session } = await sessionResponse.json();

// Get architect feedback
const feedbackResponse = await fetch('http://localhost:3000/api/ai/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nodes: session.nodes,
    edges: session.edges,
    history: session.messages,
    phase: session.phase,
    scenario: session.scenario,
    scalingChallenge: session.scalingChallenge
  })
});

const { data: { feedback } } = await feedbackResponse.json();
console.log(feedback);
```
