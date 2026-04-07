# Quick Start Guide - arch-sense Server

## 5-Minute Setup

### Step 1: Navigate to Server Directory
```bash
cd /workspaces/arch-sense/server
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment
```bash
# Create environment file from template
cp .env.example .env

# Edit .env and add your Gemini API key
# Get one from: https://aistudio.google.com/app/apikey
nano .env  # or use your preferred editor
```

### Step 4: Start Development Server
```bash
npm run dev
```

You should see:
```
✓ Database initialized at ./data/arch-sense.db
🚀 Server running on http://localhost:3000
📝 Environment: development
📊 Database: ./data/arch-sense.db
```

### Step 5: Test It
```bash
# In a new terminal
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "timestamp": "2024-04-07T10:30:45.123Z"
  }
}
```

## What You Have Now

✅ **Express Server** running on port 3000
✅ **SQLite Database** with session persistence
✅ **Gemini AI Integration** for architect feedback
✅ **REST API** with full crud operations
✅ **Error Handling** and logging
✅ **Type Safety** with TypeScript

## Key Files

| File | Purpose |
|------|---------|
| `src/index.ts` | Server entry point |
| `src/config/index.ts` | Configuration |
| `src/db/index.ts` | Database setup |
| `.env` | API keys & settings |
| `README.md` | Full documentation |

## Available NPM Commands

```bash
npm run dev          # Development with auto-reload (← use this)
npm run build        # Compile TypeScript
npm run start        # Run compiled code
npm run lint         # Type check
npm run type-check   # Type check only
```

## API Endpoints (Ready to Use)

### Session Management
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/:id` - Get session
- `POST /api/sessions/:id` - Update session
- `DELETE /api/sessions/:id` - Delete session

### AI Feedback
- `POST /api/ai/feedback` - Get architect review
- `POST /api/ai/evaluate` - Get scoring
- `POST /api/ai/message` - Chat with AI

### Health
- `GET /api/health` - Server status

## Create Your First Session

```bash
curl -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Design a notification system for 100M users"
  }'
```

Response includes your new session ID (e.g., `"a1b2c3d4"`)

## Next Steps

1. **Connect Frontend**: Update webapp to point to `http://localhost:3000/api`
2. **Add Designs**: POST architecture nodes and edges to `/api/sessions/:id`
3. **Get Feedback**: POST to `/api/ai/feedback` with your design
4. **Review Results**: Check `/api/ai/evaluate` for scores

## Documentation Files in Root

- **SCAFFOLD_SUMMARY.md** - Complete overview
- **SERVER_STRUCTURE.md** - File structure & patterns
- **API_EXAMPLES.md** - All API examples with cURL
- **server/README.md** - Detailed server docs

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
PORT=3001
npm run dev
```

### Missing Gemini API Key
```
⚠️  Missing environment variables: GEMINI_API_KEY
```
→ Add to `.env` from https://aistudio.google.com/app/apikey

### Database Error
```bash
# Reset database
rm -rf data/
npm run dev  # Will recreate
```

### TypeScript Errors
```bash
npm run type-check  # See exact errors
```

## Development Tips

### Watch Mode
Server auto-reloads when you save files:
```bash
npm run dev  # Already watching
```

### View Logs
Check terminal where you ran `npm run dev`

### Database Inspection
```bash
# View raw database (requires sqlite3)
sqlite3 data/arch-sense.db "SELECT DISTINCT id FROM sessions;"
```

### Test with Frontend
Update webapp fetch calls to use:
```typescript
const API = 'http://localhost:3000/api';

// Instead of
fetch('/api/sessions')

// Use
fetch(`${API}/sessions`)
```

## Useful Resources

- **Google Gemini API**: https://ai.google.dev/
- **Express.js Docs**: https://expressjs.com/
- **SQLite Docs**: https://www.sqlite.org/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/

## Production Deployment

```bash
# Build
npm run build

# Run
npm start
```

Set environment variables:
```bash
NODE_ENV=production
GEMINI_API_KEY=your_key
CORS_ORIGIN=https://yourdomain.com
```

## Getting Help

- See `server/README.md` for full documentation
- See `API_EXAMPLES.md` for cURL examples
- See `SERVER_STRUCTURE.md` for code organization
- Check logs in terminal for error details

---

**You're all set! Happy architecture designing! 🎉**
