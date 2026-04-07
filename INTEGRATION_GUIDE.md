# Frontend-Server Integration Guide

## Overview

The webapp currently makes API calls assuming a local backend. This guide explains how to connect the webapp to the new server scaffold.

## Current Webapp API Calls

### In App.tsx (lines ~60-70)

```typescript
// Fetch initial state
useEffect(() => {
  fetch('/api/session')
    .then(res => res.json())
    .then(data => {
      setNodes(data.nodes);
      setEdges(data.edges);
      setState(prev => ({ ...prev, phase: data.phase }));
    });
}, []);

// Sync state to backend
const syncState = useCallback(async (newNodes, newEdges, signals) => {
  await fetch('/api/session/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes: newNodes, edges: newEdges, scalingChallenge, signals })
  });
}, [scalingChallenge]);
```

### In services/geminiService.ts

```typescript
// Direct Gemini API calls
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const response = await ai.models.generateContent({...});
```

## Changes Needed

### Option 1: Keep Current Setup (No Backend)

The webapp currently handles everything including direct Gemini API calls. This works but:
- ❌ API key exposed in browser
- ❌ No persistent storage
- ❌ No session history after refresh
- ❌ Cannot scale to multiple users

### Option 2: Use New Backend (Recommended)

Migrate to use the new server for better architecture.

## Step-by-Step Integration

### Step 1: Update Environment Variables

**File: `webapp/.env`**
```bash
# Remove GEMINI_API_KEY from here
# API_KEY_REMOVED=true

# Add backend URL
VITE_API_URL=http://localhost:3000/api
```

**Note:** Vite requires `VITE_` prefix for client-side env vars

### Step 2: Create API Client

**Create: `webapp/src/lib/apiClient.ts`**

```typescript
const API_URL = import.meta.env.VITE_API_URL || '/api';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Generic API request wrapper
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  const result: ApiResponse<T> = await response.json();
  
  if (!result.success) {
    throw new Error(result.error || 'API request failed');
  }

  return result.data as T;
}

/**
 * Session API
 */
export const sessionApi = {
  create: (scenario: string) =>
    apiRequest('/sessions', {
      method: 'POST',
      body: JSON.stringify({ scenario }),
    }),

  get: (id: string) =>
    apiRequest(`/sessions/${id}`),

  list: (limit = 10, offset = 0) =>
    apiRequest(`/sessions?limit=${limit}&offset=${offset}`),

  update: (id: string, data: any) =>
    apiRequest(`/sessions/${id}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiRequest(`/sessions/${id}`, {
      method: 'DELETE',
    }),

  getSummary: (id: string) =>
    apiRequest(`/sessions/${id}/summary`),
};

/**
 * AI API
 */
export const aiApi = {
  getFeedback: (data: {
    nodes: any[];
    edges: any[];
    history: any[];
    phase: string;
    scenario: string;
    scalingChallenge: string;
  }) =>
    apiRequest('/ai/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  evaluate: (data: {
    nodes: any[];
    edges: any[];
    history: any[];
    scenario: string;
    scalingChallenge: string;
  }) =>
    apiRequest('/ai/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  sendMessage: (data: {
    sessionId?: string;
    userMessage: string;
    nodes: any[];
    edges: any[];
    history: any[];
    context: any;
  }) =>
    apiRequest('/ai/message', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

/**
 * Health check
 */
export const healthApi = {
  check: () =>
    apiRequest('/health'),
};
```

### Step 3: Update App.tsx

**Replace in `webapp/src/App.tsx`:**

```typescript
// OLD CODE (lines ~60-75)
useEffect(() => {
  fetch('/api/session')
    .then(res => res.json())
    .then(data => {
      setNodes(data.nodes);
      setEdges(data.edges);
      setState(prev => ({ ...prev, phase: data.phase }));
    });
}, []);

const syncState = useCallback(async (newNodes, newEdges, signals = []) => {
  await fetch('/api/session/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes: newNodes, edges: newEdges, scalingChallenge, signals })
  });
}, [scalingChallenge]);

// NEW CODE
import { sessionApi, aiApi } from './lib/apiClient';

// Create/load session
const [sessionId, setSessionId] = useState<string | null>(null);

useEffect(() => {
  // Create new session on mount
  if (!sessionId) {
    sessionApi
      .create(INITIAL_SCENARIO)
      .then((session: any) => {
        setSessionId(session.id);
        setNodes(session.nodes);
        setEdges(session.edges);
      })
      .catch(err => console.error('Failed to create session', err));
  }
}, []);

const syncState = useCallback(
  async (newNodes, newEdges, signals = []) => {
    if (!sessionId) return;

    try {
      await sessionApi.update(sessionId, {
        nodes: newNodes,
        edges: newEdges,
        scalingChallenge,
        signals,
        phase: state.phase,
      });
    } catch (error) {
      console.error('Failed to sync state', error);
    }
  },
  [sessionId, state.phase, scalingChallenge]
);
```

### Step 4: Update AIReviewer.tsx

**Replace AI calls in `webapp/src/components/AIReviewer.tsx`:**

```typescript
// OLD CODE - Direct Gemini API
import { getArchitectFeedback, getFinalEvaluation } from '../services/geminiService';

const handleSendMessage = async (message: string) => {
  // Direct API call
  const response = await getArchitectFeedback(...);
};

// NEW CODE - Use backend
import { aiApi } from '../lib/apiClient';

const handleSendMessage = async (message: string) => {
  try {
    const { feedback } = await aiApi.getFeedback({
      nodes,
      edges,
      history: messages,
      phase: state.phase,
      scenario: state.scenario,
      scalingChallenge,
    });

    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'architect',
      content: feedback,
      timestamp: Date.now(),
    }]);
  } catch (error) {
    console.error('Error getting feedback:', error);
  }
};
```

### Step 5: Update EvaluationView.tsx

**Replace evaluation calls in `webapp/src/components/EvaluationView.tsx`:**

```typescript
// OLD CODE
import { getFinalEvaluation } from '../services/geminiService';

const handleEvaluate = async () => {
  const evaluation = await getFinalEvaluation(...);
  setEvaluation(evaluation);
};

// NEW CODE
import { aiApi, sessionApi } from '../lib/apiClient';

const handleEvaluate = async () => {
  try {
    const { evaluation } = await aiApi.evaluate({
      nodes,
      edges,
      history: messages,
      scenario: state.scenario,
      scalingChallenge,
    });

    setEvaluation(evaluation);

    // Save evaluation to session
    if (sessionId) {
      await sessionApi.update(sessionId, {
        evaluation,
        phase: 'EVALUATION',
      });
    }
  } catch (error) {
    console.error('Error evaluating design:', error);
  }
};
```

### Step 6: Remove Direct Gemini Service

You can now remove or convert `webapp/src/services/geminiService.ts`:

```typescript
// REMOVE or comment out if Gemini API key is in client
// export async function getArchitectFeedback(...) { ... }
// export async function getFinalEvaluation(...) { ... }
```

Remove from `webapp/.env`:
```bash
# VITE_GEMINI_API_KEY=xxx  # ← Remove this
```

## File Changes Summary

| File | Changes | Type |
|------|---------|------|
| `webapp/.env` | Remove GEMINI_API_KEY, add VITE_API_URL | Config |
| `webapp/src/lib/apiClient.ts` | Create new API client | New File |
| `webapp/src/App.tsx` | Update session initialization, sync calls | Core |
| `webapp/src/components/AIReviewer.tsx` | Replace Gemini calls with API calls | Component |
| `webapp/src/components/EvaluationView.tsx` | Replace Gemini calls with API calls | Component |
| `webapp/src/services/geminiService.ts` | Remove or deprecate | Service |

## Running Both Together

### Terminal 1: Backend
```bash
cd server
npm run dev
# Runs on http://localhost:3000
```

### Terminal 2: Frontend
```bash
cd webapp
npm run dev
# Runs on http://localhost:5173
# API calls go to http://localhost:3000/api
```

## Validation Checklist

After integration:

- [ ] Backend server running (`npm run dev` in server/)
- [ ] Frontend server running (`npm run dev` in webapp/)
- [ ] Environment file has `VITE_API_URL=http://localhost:3000/api`
- [ ] No `GEMINI_API_KEY` in webapp/.env
- [ ] API client created (`webapp/src/lib/apiClient.ts`)
- [ ] App.tsx uses sessionApi instead of fetch
- [ ] AIReviewer.tsx uses aiApi instead of geminiService
- [ ] EvaluationView.tsx uses aiApi instead of geminiService
- [ ] Create new session on app load
- [ ] Update session on design changes
- [ ] Get feedback works via API
- [ ] Evaluation works via API
- [ ] No console errors in browser

## CORS Notes

The server is configured for CORS:
```typescript
res.header('Access-Control-Allow-Origin', config.corsOrigin);
// Default: http://localhost:5173
```

If you change the webapp port, update `server/.env`:
```
CORS_ORIGIN=http://localhost:5174
```

## Architecture Benefits After Integration

✅ **Security**: API key no longer in browser
✅ **Persistence**: Sessions saved to database
✅ **Scalability**: Multiple users, shared backend
✅ **Analytics**: Can log all interactions
✅ **Reliability**: Centralized error handling
✅ **Maintainability**: Clean separation of concerns

## Authentication (Optional Future Enhancement)

Once working, you can add:

```typescript
// Auth token in requests
const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});

// Server-side validation
app.use((req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  // Verify token
  next();
});
```

## Troubleshooting Integration

### CORS Error
```
Access to XMLHttpRequest blocked by CORS policy
```
→ Check `CORS_ORIGIN` in `server/.env`

### 404 API Not Found
```
POST http://localhost:3000/api/sessions 404
```
→ Verify server is running: `npm run dev` in server/

### Session Not Saving
→ Check browser console and server logs
→ Verify database is initialized: `data/arch-sense.db` exists

### API Key Still Exposed
→ Remove `VITE_GEMINI_API_KEY` from `.env`
→ Remove imports from `geminiService.ts`

## Next Steps

1. ✅ Implement the 6 steps above
2. ✅ Test both servers together
3. ✅ Verify session persistence
4. ✅ Deploy backend to cloud service
5. ✅ Add authentication if needed
6. ✅ Add monitoring and logging

---

**Integration complete!** Your app now has a proper backend architecture. 🎉
