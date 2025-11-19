# Projects.co.id Scraper - Scheduler & Session Management

## 🎯 Features

- ✅ **Scheduled Scraping**: Run every 15 minutes automatically
- ✅ **Session Management**: Maintain login session across runs
- ✅ **Persistent Storage**: Save session to file
- ✅ **Error Recovery**: Automatic retry and error handling
- ✅ **JSON Output**: Save scraped data with timestamps

---

## 🚀 Quick Start

### Option 1: Python Scheduler (Playwright)

```bash
# Install dependencies
pip install -r requirements-scheduler.txt
playwright install chromium

# Run scheduler (every 15 minutes)
python scheduler.py

# Run once (no scheduling)
python scheduler.py --once
```

### Option 2: Node.js Scheduler (Crawlee) ⭐ Recommended

```bash
# Install dependencies
npm install

# Run scheduler (every 15 minutes)
npm run scrape:schedule

# Run once
npm run scrape
```

---

## 📋 Configuration

### Environment Variables (`.env`)

```bash
# Projects.co.id Credentials
PROJECTS_CO_ID_USERNAME=daddy.dev.id@icloud.com
PROJECTS_CO_ID_PASSWORD=hidzav-Tehmug-hugza7

# Scraping Configuration
SCRAPE_INTERVAL_MINUTES=15
MAX_PAGES=10
SCRAPE_DELAY_SECONDS=2
```

---

## 🔄 Session Management

### How It Works

1. **First Run**: Login and save session to `data/sessions/projects_co_id_session.json`
2. **Subsequent Runs**: Load session, validate, use if still valid
3. **Session Expiry**: Automatically re-login if session expired (>24 hours)

### Session File Structure

```json
{
  "cookies": [...],
  "last_login": "2025-11-16T23:33:00Z",
  "session_valid": true
}
```

---

## 📊 Output

Scraped data saved to: `data/scraped/projects-co-id/projects_co_id_YYYYMMDD_HHMMSS.json`

### Output Format

```json
{
  "scraped_at": "2025-11-16T23:33:00Z",
  "total_projects": 50,
  "platform": "projects.co.id",
  "projects": [
    {
      "title": "Project Title",
      "description": "...",
      "url": "https://projects.co.id/project/...",
      "budget": {
        "min": "350000",
        "max": "600000",
        "currency": "IDR"
      },
      "tags": ["React", "Node.js"],
      "scraped_at": "2025-11-16T23:33:00Z",
      "platform": "projects.co.id"
    }
  ]
}
```

---

## 🔧 GitHub Actions Integration

See `.github/workflows/scrape-projects-co-id.yml` for automated scraping via GitHub Actions.

**Benefits**:
- ✅ No local server needed
- ✅ Runs in cloud
- ✅ Automatic commits
- ✅ Free for public repos

---

## 📝 Next Steps

1. **Update CSS Selectors**: Based on actual HTML structure
2. **Add Deduplication**: Track scraped URLs
3. **GitHub Integration**: Auto-update project table
4. **Monitoring**: Add logging and metrics

---

**Reference**: 
- Action Plan: `docs/research/projects-co-id-bot-action-plan-2025-11-16_23_33.md`
- Analysis: `docs/research/projects-co-id-deep-dive-analysis-2025-11-16_23_19.md`

