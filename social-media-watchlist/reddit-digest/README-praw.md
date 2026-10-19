# Reddit via PRAW

Uses env `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` (secret-request).
Venv: `../reddit-venv`

Read-only (no Reddit username) works for public subreddits.
User-context needs `REDDIT_USERNAME` + `REDDIT_PASSWORD` (script app).

## Rate limit
Johnny: max **100 API calls per minute**. Pace PRAW accordingly (sleep/backoff between batches).
