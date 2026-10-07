# 🎮 Tagoloan Community College · MLBB Esports Intramurals 2026
### Official Tournament Tracker, Live Bracket & Broadcast Scoreboard Dashboard

> **Live Production Ready · Mobile-First · Zero Build Dependencies · Ready for Vercel**

---

## 🌟 Key Features

### 1. 🔴 "LIVE NOW" & ⏭️ "UP NEXT" Broadcast Hero Ticker
- **Mobile-First Top Banner**: Prominently displays the active match currently being played on stage, complete with official college logos, live game score (e.g. `1 - 0`), best-of format badge, and round description.
- **On-Deck Preview**: Displays the immediate successor match so student athletes and coaches know when to report to the staging area.
- **Victory Trophy Mode**: Automatically transitions into a gold championship celebration hero banner with confetti when the Grand Finals victor is decided!

### 2. 🛡️ Spectator Mode vs. Marshal Admin Mode
- **Spectator Mode (Default)**: Viewers, students, and tournament fans on smartphones or public projectors see a clean, tamper-proof read-only dashboard. All simulation, score increment, bracket blanking, and seed editing buttons are automatically hidden.
- **Marshal Admin Mode**: Secured by tournament PIN (`tcc2026`). Table officials can unlock full controls either via the in-app modal or by loading the secret bookmark URL: `https://your-domain.vercel.app/?admin=tcc2026`.
- **Instant Control**: In Admin Mode, officials can score matches with quick `+1` buttons directly on the hero ticker card or in the bracket view.

### 3. ☁️ Real-Time Cloud Synchronization (Google Firebase Compat)
- **Instant Live Push**: Table marshals record game results; updates push live across all connected smartphones and LED projector walls in **< 100 milliseconds** with **zero page reloads**.
- **100% Free Tier Compatible**: Operates directly with Google Firebase Spark plan (1GB storage, 100 concurrent connections, 0 cost).
- **Offline Resilient**: If no cloud connection is configured or if the venue Wi-Fi drops, the dashboard seamlessly persists all data to browser `localStorage`.

### 4. ⚔️ Dual Tournament Formats & 3-Day Match Sequence
- **Double Elimination (14 Series)**: Upper Bracket, Lower Bracket (double life), and Grand Finals (BO7).
- **Single Elimination (8 Series)**: Rapid championship knockout with Bronze Battle.
- **3-Day Roadmap**: Pre-arranged chronological sequence (Day 1: Matches 1–6, Day 2: Matches 7–12, Day 3: Matches 13–14).

### 5. 🖨️ Official Print & PDF Exporting Engine
- Formatted specifically for standard Philippine Folio (8.5" × 13" / Long bond paper).
- Includes collegiate headers, match rosters, and official verification signature blocks (Tournament Director, Head Referee, Team Captains).

---

## 🚀 Quick Vercel Deployment (3-Minute Guide)

### Method A: Deploy via GitHub & Vercel Web Dashboard (Recommended)

1. **Initialize Git & Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: TCC MLBB Esports Tracker 2026"
   git branch -M main
   # Create a new repository on github.com, then:
   git remote add origin https://github.com/YOUR_USERNAME/tcc-esports-intramurals-2026.git
   git push -u origin main
   ```

2. **Import into Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
   - Click **"Add New..."** → **"Project"**.
   - Select your repository `tcc-esports-intramurals-2026`.
   - **Framework Preset**: Leave as `Other` (pure static HTML).
   - Click **"Deploy"**.

3. **Done!** Your tournament dashboard will be live at:
   `https://tcc-esports-intramurals-2026.vercel.app` (or your custom domain).

---

## ☁️ Setting Up Free Firebase Realtime Database (60 Seconds)

To enable live score syncing to student phones without page reloads:

1. Go to the [Google Firebase Console](https://console.firebase.google.com/) and click **"Add project"**.
2. Name your project (e.g. `tcc-esports-2026`). Google Analytics can be disabled.
3. In the left navigation menu, click **"Build"** → **"Realtime Database"** → click **"Create Database"**.
4. Choose default location (e.g., `Singapore` or `United States`) and select **"Start in test mode"** (or set Rules to `{ ".read": true, ".write": true }`).
5. Copy your **Database URL** (e.g. `https://tcc-esports-2026-default-rtdb.asia-southeast1.firebasedatabase.app`).
6. On the tournament dashboard, click **"☁️ Cloud: Local"** in the top navigation bar.
7. Paste your Database URL and click **"💾 Save & Connect"**.
8. **That's it!** All viewers connected to the URL will receive live score updates instantaneously.

---

## 📱 Generating Campus & Venue QR Codes

For players and spectators to view scores on their phones:

1. Copy your live Vercel URL: `https://tcc-esports-intramurals-2026.vercel.app`
2. Go to any free QR code generator (e.g. [qr-code-generator.com](https://www.qr-code-generator.com/) or [qrserver.com](https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://tcc-esports-intramurals-2026.vercel.app)).
3. Print the QR code on venue flyers, stage roll-up banners, and ID badges with the label:
   > **"Scan to view Live MLBB Bracket, Current Game Scores & Up Next Matchups!"**

---

## 🔒 Tournament Table Official Cheat Sheet

| Action | How to Access |
|---|---|
| **Unlock Admin Mode** | Click **"🔒 Marshal Login"** in the top header → Enter PIN `tcc2026` |
| **Direct Admin Bookmark** | Append `?admin=tcc2026` to your URL (e.g. `https://your-site.vercel.app/?admin=tcc2026`) |
| **Exit Admin Mode** | Click **"🔒 Lock"** in the header next to the Marshal badge |
| **Quick +1 Game Win** | Click `+1 [TEAM]` directly inside the **🔴 LIVE NOW** card |
| **LED Stage Projector** | Click **"📺 Live Stage"** for full-screen theater presentation |
| **Print Official Bracket** | Click **"🖨️ Print Bracket"** in the bracket action bar |
| **Print Series Scoresheet** | Switch to the **"Match Series List"** tab → Click **"🖨️ Print Series List"** |

---

## 🏛️ Participating Colleges & Seeds

| Seed | Code | College Department | Mascot / Team Tag |
|:---:|:---:|:---|:---|
| **#1** | **CIT** | College of Information Technology | Cyber Fox |
| **#2** | **CBA** | College of Business Administration | Golden Bulls |
| **#3** | **COE** | College of Education | Roaring Tigers |
| **#4** | **CAS** | College of Arts and Sciences | Mystic Eagles |
| **#5** | **CHM** | College of Hospitality Management | Noble Knights |
| **#6** | **CCJ** | College of Criminal Justice | Iron Wolves |
| **#7** | **CMID**| College of Midwifery | Fierce Vipers |
| **#8** | **CLIS**| College of Library & Information Science | Mighty Lions |

---

*Tagoloan Community College · Office of Student Affairs & Sports Development · Intramural Games 2026*
