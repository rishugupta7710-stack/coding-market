# 🚀 Coding Market — GitHub Auto Setup

## Folder Structure (EXACT yahi rakho!)
```
your-repo/
├── .github/
│   └── workflows/
│       └── daily_update.yml   ← GitHub Actions
├── CodingMarket_New.html      ← Website
├── data_fetcher.py            ← Auto updater script
└── README.md
```

## Setup Steps (10 minutes!)

### Step 1 — GitHub pe Repo Banao
1. github.com → New Repository
2. Name: `coding-market` (ya kuch bhi)
3. Public rakho (free GitHub Pages ke liye)

### Step 2 — Files Upload Karo
1. Repo mein sab files upload karo
2. `.github/workflows/` folder bhi upload karo

### Step 3 — Netlify se Connect Karo
1. netlify.com → New site → Import from Git
2. GitHub select karo → apna repo select karo
3. Build command: (khaali rakho)
4. Publish directory: `.` (dot)
5. Deploy!

### Step 4 — GitHub Actions Permission
1. Repo → Settings → Actions → General
2. "Workflow permissions" → Read and write ✅
3. Save

## How It Works
```
Roz 10 PM IST
    ↓
GitHub Actions chalti hai
    ↓
data_fetcher.py → NSE CSV fetch
    ↓
CodingMarket_New.html update
    ↓
Auto commit + push to GitHub
    ↓
Netlify auto deploy
    ↓
Website live with new data! 🎉
```

## Manual Trigger
GitHub → Actions tab → "Daily NSE Data Update" → Run workflow

## Troubleshooting
- NSE block kare → manually update using website's Update tab
- Actions fail → check Actions tab for error logs
- Netlify deploy fail → check deploy logs
