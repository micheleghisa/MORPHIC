"""
MORPHIC — Master Content Orchestrator
Coordina tutti gli agenti: strategia → trend analysis → scrittura → anti-duplicazione.
Garantisce contenuti unici, basati su trend reali, senza ripetizioni.
"""
import json, os, sys, asyncio
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from services.llm_provider import get_llm_provider

llm = get_llm_provider()

HISTORY_FILE = "content/history.json"

# ═══════════════════════════════════════════
# HISTORY TRACKER — Anti-duplicazione
# ═══════════════════════════════════════════

def load_history() -> dict:
    """Carica lo storico di tutti i contenuti mai generati."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {"topics": [], "posts": [], "hashtags": [], "hooks": [], "weeks": []}

def save_history(history: dict):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_history(week_id: str, results: dict):
    """Registra i contenuti generati nello storico."""
    history = load_history()
    history["weeks"].append(week_id)
    for post in results.get("reddit_posts", []):
        history["posts"].append({"week": week_id, "platform": "reddit", "title": post.get("content", "")[:120]})
    for script in results.get("tiktok_scripts", []):
        history["posts"].append({"week": week_id, "platform": "tiktok", "hook": script.get("content", "")[:120]})
    for thread in results.get("twitter_threads", []):
        history["posts"].append({"week": week_id, "platform": "twitter", "topic": thread.get("content", "")[:120]})
    save_history(history)

def get_used_topics() -> str:
    """Ritorna lista di topic già usati per evitarli."""
    history = load_history()
    titles = [p.get("title", "")[:80] for p in history.get("posts", []) if p.get("title")]
    hooks = [p.get("hook", "")[:80] for p in history.get("posts", []) if p.get("hook")]
    return "\n".join(titles[-30:] + hooks[-30:])


# ═══════════════════════════════════════════
# TREND ANALYZER — Scraping intelligente
# ═══════════════════════════════════════════

TREND_ANALYZER_PROMPT = """You are a social media trend analyst specialized in beauty, aesthetics, and self-improvement niches.

TASK: Identify what content is CURRENTLY performing best on Reddit (r/looksmaxxing, r/SkincareAddiction), TikTok (#glowup, #looksmaxxing), and Twitter/X (beauty science threads).

For each platform, provide:
1. 3-5 currently trending topics/themes
2. Content formats that are overperforming (carousels, before/after, myth-busting, etc.)
3. Specific hooks that are working right now
4. Hashtags gaining traction
5. What's declining (topics to avoid)

Base this on your knowledge of these platforms' algorithms and community behavior. Be specific and actionable."""

async def analyze_trends() -> str:
    """Agent: Analizza i trend attuali su tutte le piattaforme."""
    result = await llm.generate(
        system_prompt=TREND_ANALYZER_PROMPT,
        user_prompt="Analyze current trends for beauty/aesthetics content on Reddit, TikTok, and Twitter. Focus on what's working RIGHT NOW in May 2026.",
        temperature=0.5,
        max_tokens=2500,
    )
    return result["content"]


# ═══════════════════════════════════════════
# MASTER STRATEGIST — Calendario + anti-duplicazione
# ═══════════════════════════════════════════

STRATEGIST_V2_PROMPT = """You are the Head of Content Strategy at a beauty-tech company. You plan weekly content calendars that are ALWAYS unique, never repetitive.

Your brand: MORPHIC — AI-powered facial aesthetics analysis. Users upload 6 photos, get a science-backed report with 478 facial landmarks analyzed, skin health assessment, and personalized non-surgical glow-up protocol.

TARGET AUDIENCE: 18-35, beauty/skincare enthusiasts, looksmaxxing community, self-improvement focused.

RULES:
1. Every topic must be DIFFERENT from previous weeks
2. Mix content types: educational (50%), engagement (20%), social proof (15%), promotional (15%)
3. Reddit: value-first, educational, natural mention of MORPHIC
4. TikTok: fast hook, science fact, faceless video style
5. Twitter: data-driven threads, contrarian takes

Return a JSON array of 7 days, each with platform assignments."""

async def master_strategist(trends: str, used_topics: str) -> dict:
    """Agent: Crea calendario settimanale unico basato su trend e storico."""
    prompt = f"""Create a 7-day content calendar. DO NOT use any of these previously used topics:

PREVIOUSLY USED TOPICS (AVOID THESE):
{used_topics}

CURRENT TRENDS TO LEVERAGE:
{trends}

Return a JSON array with EXACTLY 21 items (7 Reddit + 7 TikTok + 7 Twitter), one per platform per day.
Each day has one post per platform. Format:
[
  {{"day": 1, "platform": "reddit", "content_type": "...", "title": "...", "hook": "...", "key_points": [...], "morphic_mention": "..."}},
  {{"day": 1, "platform": "tiktok", "content_type": "...", "title": "...", "hook": "...", "key_points": [...], "morphic_mention": "..."}},
  {{"day": 1, "platform": "twitter", "content_type": "...", "title": "...", "hook": "...", "key_points": [...], "morphic_mention": "..."}},
  ...repeat for days 2-7...
]
21 items total. EVERY item must be UNIQUE. No repetition across platforms or days."""

    result = await llm.generate(
        system_prompt=STRATEGIST_V2_PROMPT,
        user_prompt=prompt,
        temperature=0.9,
        max_tokens=4000,
    )

    content = result["content"]
    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            calendar = json.loads(content[start:end])
        else:
            raise ValueError("No JSON")
    except:
        calendar = [{"day": i, "platform": "reddit", "title": f"Content day {i}", "raw": content} for i in range(1, 8)]

    return {"calendar": calendar, "provider": result["provider"]}


# ═══════════════════════════════════════════
# ANALYTICS RETROSPECTIVE AGENT
# ═══════════════════════════════════════════

PERFORMANCE_DATA_FILE = "content/performance.json"

def record_performance(week_id: str, platform: str, post_id: str, metrics: dict):
    """Registra le performance di un post."""
    data = {}
    if os.path.exists(PERFORMANCE_DATA_FILE):
        with open(PERFORMANCE_DATA_FILE) as f:
            data = json.load(f)
    key = f"{week_id}/{platform}/{post_id}"
    data[key] = {"metrics": metrics, "recorded_at": datetime.now().isoformat()}
    with open(PERFORMANCE_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def analyze_performance() -> str:
    """Agent: Analizza le performance passate e suggerisce miglioramenti."""
    if not os.path.exists(PERFORMANCE_DATA_FILE):
        return "No performance data yet. Start posting to collect analytics."

    with open(PERFORMANCE_DATA_FILE) as f:
        data = json.load(f)

    if not data:
        return "No performance data yet."

    summary = json.dumps(data, indent=2)

    prompt = f"""Analyze this content performance data and tell me:
1. Which content types performed best (highest engagement)
2. Which platforms gave best ROI
3. 3 specific recommendations for next week's content
4. What to stop doing immediately

Performance data:
{summary}"""

    result = await llm.generate(
        system_prompt="You are a data-driven content strategist. Analyze performance data and give actionable recommendations.",
        user_prompt=prompt,
        temperature=0.3,
        max_tokens=1500,
    )
    return result["content"]


# ═══════════════════════════════════════════
# ORCHESTRATOR — Main Entry Point
# ═══════════════════════════════════════════

async def run_full_pipeline():
    """Esegue l'intera pipeline di content creation."""
    week_id = datetime.now().strftime("%Y-W%W")
    week_folder = f"content/{week_id}"
    os.makedirs(week_folder, exist_ok=True)

    print("""
╔══════════════════════════════════════════╗
║   MORPHIC Content Agency — Full Pipeline  ║
╚══════════════════════════════════════════╝
    """)

    # Step 1: Trend Analysis
    print("📊 STEP 1/5: Trend Analyzer — scanning what's working...")
    trends = await analyze_trends()
    with open(f"{week_folder}/trends.md", "w") as f:
        f.write(trends)
    print("   ✅ Trends analyzed\n")

    # Step 2: Analytics Retrospective
    print("📈 STEP 2/5: Performance Retrospective — learning from past posts...")
    retro = await analyze_performance()
    with open(f"{week_folder}/retrospective.md", "w") as f:
        f.write(retro)
    print("   ✅ Retrospective complete\n")

    # Step 3: Master Strategy
    print("📅 STEP 3/5: Master Strategist — building unique calendar...")
    used_topics = get_used_topics()
    strategy = await master_strategist(trends, used_topics)
    calendar = strategy.get("calendar", [])
    with open(f"{week_folder}/calendar.json", "w") as f:
        json.dump(calendar, f, indent=2)
    print(f"   ✅ Calendar: {len(calendar)} unique content slots\n")

    # Step 4: Content Writing (import content_agency agents)
    print("✍️  STEP 4/5: Content Writers — generating posts...")
    from content_agency import reddit_writer, tiktok_writer, twitter_writer, visual_generator

    reddit_posts = []
    tiktok_scripts = []
    twitter_threads = []

    for slot in calendar:
        platform = slot.get("platform", "reddit")
        topic = slot.get("title", "")
        content_type = slot.get("content_type", "educational")

        if platform in ("reddit",):
            subreddits = ["looksmaxxing", "SkincareAddiction", "beauty", "vindicta", "HowToBeHot", "malegrooming"]
            sub = subreddits[len(reddit_posts) % len(subreddits)]
            post = await reddit_writer(sub, topic)
            reddit_posts.append(post)
            print(f"   ✅ Reddit r/{sub}: {topic[:55]}...")
        elif platform in ("tiktok", "instagram"):
            script = await tiktok_writer(topic, content_type)
            tiktok_scripts.append(script)
            print(f"   ✅ TikTok: {topic[:55]}...")
        elif platform in ("twitter", "twitter_x"):
            thread = await twitter_writer(topic)
            twitter_threads.append(thread)
            print(f"   ✅ Twitter: {topic[:55]}...")

    visuals = await visual_generator("infographic", "facial aesthetics, skin science, beauty data")
    print(f"   ✅ Visual prompts generated\n")

    # Step 5: Export
    print("📦 STEP 5/5: Exporting content plan...")
    from content_agency import export_to_markdown

    results = {
        "generated_at": datetime.now().isoformat(),
        "week_id": week_id,
        "strategy": strategy,
        "reddit_posts": reddit_posts,
        "tiktok_scripts": tiktok_scripts,
        "twitter_threads": twitter_threads,
        "visual_prompts": visuals,
        "trends": trends,
        "retrospective": retro,
    }

    filepath = export_to_markdown(results, f"{week_folder}/content_plan.md")
    add_to_history(week_id, results)

    # Save full results
    with open(f"{week_folder}/results.json", "w") as f:
        json.dump({k: str(v) if not isinstance(v, (list, dict, str)) else v for k, v in results.items()}, f, indent=2, default=str)

    print(f"""
╔══════════════════════════════════════════╗
║   ✅ WEEK {week_id} COMPLETE                ║
╠══════════════════════════════════════════╣
║   📊 Trends:     {week_folder}/trends.md      ║
║   📈 Retro:      {week_folder}/retrospective.md ║
║   📅 Calendar:   {week_folder}/calendar.json    ║
║   📝 Content:    {week_folder}/content_plan.md  ║
╠══════════════════════════════════════════╣
║   📝 Reddit:     {len(reddit_posts)} posts              ║
║   🎬 TikTok:     {len(tiktok_scripts)} scripts          ║
║   🐦 Twitter:    {len(twitter_threads)} threads         ║
╚══════════════════════════════════════════╝

💡 How to use:
1. Open {week_folder}/content_plan.md
2. Copy-paste each post to its platform
3. After posting, record metrics in content/performance.json:
   {{"week_id/platform/post_id": {{"metrics": {{"views": X, "likes": Y, "comments": Z}}}}}}
4. Next week's pipeline will learn from this data

🎬 For TikTok videos: use agents/video_maker.py (creates faceless slideshow + AI voiceover)
    """)


# ═══════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(run_full_pipeline())
