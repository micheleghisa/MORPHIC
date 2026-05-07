"""
MORPHIC — Content Marketing AI Agency
Flotta di 5 agenti AI per creazione contenuti social organici.
DeepSeek API per testi, ElevenLabs per voice-over, MoviePy per montaggio video.
"""

import json, os, asyncio, sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from typing import List, Dict, Optional
from services.llm_provider import get_llm_provider

llm = get_llm_provider()

# ═══════════════════════════════════════════════════════════
# PLATFORM STRATEGY
# ═══════════════════════════════════════════════════════════

PLATFORMS = {
    "reddit": {
        "priority": 1,
        "why": "Comunità looksmaxxing/skincare già attive, alto intento, contenuti testuali (facili da generare con AI), zero editing richiesto.",
        "content_types": ["text_post", "image_post", "comment", "guide"],
        "posting_frequency": "2-3x/day",
        "best_subreddits": ["r/looksmaxxing", "r/SkincareAddiction", "r/beauty", "r/HowToBeHot", "r/vindicta", "r/malegrooming"],
        "conversion_potential": "HIGH — utenti già in cerca di soluzioni estetiche",
        "ai_difficulty": "EASY — testo puro, nessun editing video",
    },
    "tiktok": {
        "priority": 2,
        "why": "Enorme reach organica, #glowup ha 200B+ views, algoritmo premia contenuti nuovi, faceless content funziona.",
        "content_types": ["faceless_reel", "slideshow_voiceover", "before_after_reveal", "science_fact"],
        "posting_frequency": "1-2x/day",
        "best_hashtags": ["#glowup", "#looksmaxxing", "#facialanalysis", "#skincareroutine", "#glowuptips", "#beautyscience"],
        "conversion_potential": "HIGH — virale, pubblico giovane ossessionato dall'estetica",
        "ai_difficulty": "MEDIUM — richiede voice-over + montaggio video base",
    },
    "instagram": {
        "priority": 2,
        "why": "Stesso contenuto di TikTok (Reels), più caroselli educativi, bio link per conversione.",
        "content_types": ["reel", "carousel", "story"],
        "posting_frequency": "1-2x/day",
        "best_hashtags": ["#glowup", "#skincaretips", "#faceshape", "#beautytips", "#glowupchallenge"],
        "conversion_potential": "MEDIUM-HIGH — pubblico beauty già presente",
        "ai_difficulty": "MEDIUM — cross-post da TikTok",
    },
    "twitter_x": {
        "priority": 3,
        "why": "Thread scientifici su estetica, facile da automatizzare, community tech/self-improvement.",
        "content_types": ["thread", "one_liner", "poll"],
        "posting_frequency": "3-5x/day",
        "best_hashtags": ["#looksmaxxing", "#selfimprovement", "#beautyscience"],
        "conversion_potential": "LOW-MEDIUM — buono per awareness, meno per conversione diretta",
        "ai_difficulty": "EASY — solo testo",
    },
    "pinterest": {
        "priority": 4,
        "why": "Traffico passivo a lungo termine, infografiche su skincare/face shapes funzionano, SEO evergreen.",
        "content_types": ["infographic", "before_after_pin"],
        "posting_frequency": "5-10 pins/day",
        "conversion_potential": "MEDIUM — traffico lento ma costante nel tempo",
        "ai_difficulty": "EASY — immagini statiche generate da AI",
    },
}

# ═══════════════════════════════════════════════════════════
# AGENT 1: CONTENT STRATEGIST
# ═══════════════════════════════════════════════════════════

CONTENT_STRATEGIST_PROMPT = """You are a senior social media strategist at a top marketing agency, specialized in beauty-tech and AI products. Your client is MORPHIC, an AI-powered facial aesthetics analysis platform.

MORPHIC analyzes faces using 478 landmark points, measures symmetry/proportions/skin health, and generates science-backed glow-up protocols without surgery.

Target audience: 18-35 year olds interested in improving their appearance, skincare enthusiasts, looksmaxxing community.

TASK: Create a content calendar and strategy. For each content idea, specify:
1. Platform (reddit, tiktok, instagram, twitter, pinterest)
2. Content type
3. Hook/title
4. Key message
5. Why it will perform well
6. Call to action

Rules:
- Content MUST be educational and science-based, never superficial
- No false promises or clickbait
- For Reddit: value-first, no direct promotion in title
- For TikTok/Reels: hook in first 1.5 seconds
- For Twitter: threads with data/citations
- Mix of: educational (50%), social proof/results (20%), engagement (15%), promotional (15%)"""

async def strategist_generate_calendar(days: int = 7, platforms: List[str] = None) -> Dict:
    """Agent 1: Genera calendario contenuti per N giorni."""
    if platforms is None:
        platforms = ["reddit", "tiktok", "instagram", "twitter_x"]

    prompt = f"""Create a {days}-day content calendar for the following platforms: {', '.join(platforms)}.

For EACH day, for EACH platform, provide ONE content idea.

Format as JSON array:
[
  {{
    "day": 1,
    "date": "Day 1",
    "platform": "reddit",
    "content_type": "text_post",
    "title": "...",
    "body_outline": "...",
    "hashtags": [],
    "cta": "...",
    "best_posting_time": "..."
  }},
  ...
]

Make every post DIFFERENT. No repetition. Make them specific and actionable."""

    result = await llm.generate(
        system_prompt=CONTENT_STRATEGIST_PROMPT,
        user_prompt=prompt,
        temperature=0.8,
        max_tokens=4000,
    )
    content = result["content"]
    # Try JSON parse, fallback to raw text
    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            calendar = json.loads(content[start:end])
        else:
            raise ValueError("No JSON array found")
    except:
        # Fallback: return as raw calendar
        calendar = [{"day": 1, "platform": "all", "content_type": "mixed", "title": "Weekly Strategy", "body_outline": content, "cta": "", "best_posting_time": ""}]
    
    return {"calendar": calendar, "provider": result["provider"]}


# ═══════════════════════════════════════════════════════════
# AGENT 2: REDDIT POST WRITER
# ═══════════════════════════════════════════════════════════

REDDIT_PROMPT = """You are a Reddit power user with 100k+ karma in beauty, skincare, and self-improvement subreddits. You know exactly what gets upvoted.

TASK: Write a Reddit post that provides genuine value. Never sound promotional. The MORPHIC mention must feel natural, like a helpful recommendation from someone who actually used it.

Subreddit rules:
- r/looksmaxxing: detailed, scientific, no vague advice
- r/SkincareAddiction: routine-focused, product-aware, science-backed
- r/beauty: practical tips, welcoming tone
- r/vindicta: female-focused, strategic beauty, evidence-based

Format the post with proper Reddit markdown (headings, bullet points, bold)."""

async def reddit_writer(subreddit: str, topic: str) -> Dict:
    """Agent 2: Scrive un post Reddit ottimizzato per upvote."""
    prompt = f"""Write a Reddit post for r/{subreddit} about: {topic}

Requirements:
- Grab attention in first sentence
- Provide 3-5 specific, actionable tips
- Include 1-2 scientific facts (real studies)
- Naturally mention MORPHIC ONCE as "I used this AI tool called MORPHIC that..." — make it feel like a personal discovery
- End with a question to drive comments
- Add appropriate flair if the subreddit uses them
- Keep it 300-600 words"""

    result = await llm.generate(system_prompt=REDDIT_PROMPT, user_prompt=prompt, temperature=0.7)
    return {"content": result["content"], "platform": "reddit", "subreddit": subreddit, "provider": result["provider"]}


# ═══════════════════════════════════════════════════════════
# AGENT 3: TIKTOK/REELS SCRIPT WRITER
# ═══════════════════════════════════════════════════════════

TIKTOK_PROMPT = """You are a viral TikTok creator in the beauty/science niche with 2M+ followers. You create faceless content using stock footage, text overlays, and AI voiceover.

CONTENT TYPES:
1. "Science Fact" — one surprising aesthetic science fact, explained fast
2. "Glow Up Tip" — one actionable tip with before/after implication  
3. "Face Analysis Reveal" — break down what makes a face attractive (use anonymous descriptions)
4. "Myth Buster" — debunk a common beauty myth with science

SCRIPT FORMAT (critical for virality):
HOOK (0-1.5s): "Did you know..." / "Stop doing X..." / "The truth about Y..."
BODY (1.5-25s): Explain with 2-3 bullet points of info
CTA (25-30s): "Follow for more science-backed glow up tips"

Voice: fast-paced, slightly dramatic, Gen Z tone but credible. Use pauses for effect."""

async def tiktok_writer(topic: str, content_type: str = "science_fact") -> Dict:
    """Agent 3: Scrive script per TikTok/Reels ottimizzato per viralità."""
    prompt = f"""Write a {content_type} TikTok script about: {topic}

Format:
HOOK: [one line, max 15 words, MUST create curiosity]
TEXT OVERLAYS: [5-8 text overlays that appear on screen, each max 5 words]
VOICEOVER: [full script, 25-35 seconds spoken at medium-fast pace]
CAPTION: [TikTok caption with 3-5 hashtags]
VISUALS: [what stock footage/images to show for each segment]"""

    result = await llm.generate(system_prompt=TIKTOK_PROMPT, user_prompt=prompt, temperature=0.8)
    return {"content": result["content"], "platform": "tiktok", "type": content_type, "provider": result["provider"]}


# ═══════════════════════════════════════════════════════════
# AGENT 4: TWITTER/X THREAD WRITER  
# ═══════════════════════════════════════════════════════════

TWITTER_PROMPT = """You are a Twitter/X creator in the self-improvement and science niche, averaging 500+ likes per thread. Your style is data-driven, slightly contrarian, and always actionable.

Thread structure:
Tweet 1: Controversial/surprising hook + "🧵"
Tweets 2-8: One insight per tweet, with data/citation
Last tweet: Summary + subtle CTA + link

Each tweet MUST be standalone punchy. Max 240 chars per tweet. Use line breaks for readability."""

async def twitter_writer(topic: str) -> Dict:
    """Agent 4: Scrive thread Twitter/X ottimizzato per engagement."""
    prompt = f"""Write a Twitter/X thread about: {topic}

Requirements:
- Hook tweet MUST make someone stop scrolling
- 6-10 tweets total
- At least 2 tweets with specific numbers/statistics
- Last tweet: CTA to try MORPHIC (natural, not salesy)
- Return as numbered tweets"""

    result = await llm.generate(system_prompt=TWITTER_PROMPT, user_prompt=prompt, temperature=0.8)
    return {"content": result["content"], "platform": "twitter", "provider": result["provider"]}


# ═══════════════════════════════════════════════════════════
# AGENT 5: VISUAL ASSET GENERATOR (Image descriptions)
# ═══════════════════════════════════════════════════════════

VISUAL_PROMPT = """You are an AI art director for a beauty-tech brand. Generate detailed image prompts for AI image generators (Midjourney/DALL-E/Stable Diffusion).

Style: clean, scientific, minimalist. White/neutral backgrounds. Anatomical accuracy. Professional aesthetic.

NO faces of real people. Use:
- Scientific diagrams
- Abstract representations of facial features
- Before/after skin texture comparisons
- Facial mapping visualizations
- Infographics with data"""

async def visual_generator(content_type: str, topic: str) -> Dict:
    """Agent 5: Genera prompt per immagini AI (da usare con DALL-E/Stable Diffusion)."""
    prompt = f"""Generate 3 image prompts for: {content_type} about "{topic}"

Each prompt must:
- Be in English for Midjourney/DALL-E
- Describe style, composition, colors, lighting
- Include "clean scientific aesthetic, white background, minimalist"
- NO realistic human faces (use mannequin, wireframe, or stylized)

Format as numbered list."""

    result = await llm.generate(system_prompt=VISUAL_PROMPT, user_prompt=prompt, temperature=0.8, max_tokens=1000)
    return {"content": result["content"], "type": content_type, "provider": result["provider"]}


# ═══════════════════════════════════════════════════════════
# BATCH CONTENT GENERATOR — RUNS ALL AGENTS
# ═══════════════════════════════════════════════════════════

async def generate_weekly_content() -> Dict:
    """Genera una settimana completa di contenuti per tutte le piattaforme."""
    print("\n" + "=" * 60)
    print("🤖 MORPHIC CONTENT AGENCY — Weekly Content Generation")
    print("=" * 60 + "\n")

    results = {
        "generated_at": datetime.now().isoformat(),
        "strategy": None,
        "reddit_posts": [],
        "tiktok_scripts": [],
        "twitter_threads": [],
        "visual_prompts": [],
    }

    # Step 1: Content strategy & calendar
    print("📅 Agent 1: Content Strategist — generating weekly calendar...")
    strategy = await strategist_generate_calendar(days=7)
    results["strategy"] = strategy
    posts_count = len(strategy.get("calendar", []))
    print(f"   ✅ Generated {posts_count} content slots across platforms\n")

    # Step 2: Reddit posts (top priority platform)
    reddit_topics = [
        "The science behind why some faces are more attractive",
        "How I improved my facial symmetry without surgery (5 methods)",
        "Skincare ingredients that actually work for skin texture (with studies)",
        "The truth about mewing and facial posture — what science says",
        "Why the golden ratio is outdated and what actually matters for facial aesthetics",
        "How to objectively measure your facial proportions at home",
        "Non-surgical ways to improve your jawline definition",
    ]
    print("📝 Agent 2: Reddit Writer — generating posts...")
    for i, topic in enumerate(reddit_topics[:7]):
        subreddit = ["looksmaxxing", "SkincareAddiction", "beauty", "vindicta", "HowToBeHot", "malegrooming", "looksmaxxing"][i]
        post = await reddit_writer(subreddit, topic)
        results["reddit_posts"].append(post)
        print(f"   ✅ r/{subreddit}: {topic[:60]}...")
    print()

    # Step 3: TikTok scripts
    tiktok_topics = [
        "What your face shape says about you (science-backed)",
        "The one skincare ingredient that actually changes your skin texture",
        "Why symmetrical faces look better (and how to improve yours)",
        "Stop doing this if you want a defined jawline",
        "Canthal tilt explained in 30 seconds",
        "The truth about facial exercises — what works and what doesn't",
        "How AI can analyze your face better than a mirror",
    ]
    print("🎬 Agent 3: TikTok Writer — generating scripts...")
    for topic in tiktok_topics:
        script = await tiktok_writer(topic, "science_fact")
        results["tiktok_scripts"].append(script)
        print(f"   ✅ {topic[:60]}...")
    print()

    # Step 4: Twitter threads
    twitter_topics = [
        "10 scientific facts about facial attractiveness that will surprise you",
        "The economics of being attractive (with real data)",
        "How I used AI to analyze my face and what I learned",
        "The truth about skincare routines — what 2000 studies say",
        "Why your facial proportions matter more than individual features",
    ]
    print("🐦 Agent 4: Twitter Writer — generating threads...")
    for topic in twitter_topics:
        thread = await twitter_writer(topic)
        results["twitter_threads"].append(thread)
        print(f"   ✅ {topic[:60]}...")
    print()

    # Step 5: Visual prompts
    visual_topics = "facial symmetry analysis, skin texture comparison, facial proportions diagram, jawline anatomy"
    print("🎨 Agent 5: Visual Generator — generating image prompts...")
    visuals = await visual_generator("infographic", visual_topics)
    results["visual_prompts"] = visuals
    print(f"   ✅ Generated visual prompts\n")

    print("=" * 60)
    print("✅ WEEKLY CONTENT GENERATION COMPLETE")
    print(f"   📅 Strategy: {posts_count} slots")
    print(f"   📝 Reddit: {len(results['reddit_posts'])} posts")
    print(f"   🎬 TikTok: {len(results['tiktok_scripts'])} scripts")
    print(f"   🐦 Twitter: {len(results['twitter_threads'])} threads")
    print(f"   🎨 Visuals: image prompts ready")
    print("=" * 60)

    return results


# ═══════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════

def export_to_markdown(results: Dict, filepath: str = None):
    """Esporta tutti i contenuti in un file Markdown pronto da usare."""
    if filepath is None:
        week_id = datetime.now().strftime("%Y-W%W")
        os.makedirs(f"content/{week_id}", exist_ok=True)
        filepath = f"content/{week_id}/content_plan.md"

    lines = []
    lines.append(f"# MORPHIC Content Plan — {results['generated_at'][:10]}\n")
    lines.append("---\n")

    # Strategy
    if results.get("strategy", {}).get("calendar"):
        lines.append("## 📅 Weekly Content Calendar\n")
        for item in results["strategy"]["calendar"]:
            lines.append(f"### Day {item.get('day', '?')} — {item.get('platform', '').upper()}")
            lines.append(f"- **Type:** {item.get('content_type', '')}")
            lines.append(f"- **Title:** {item.get('title', '')}")
            lines.append(f"- **Body:** {item.get('body_outline', '')}")
            lines.append(f"- **Best time:** {item.get('best_posting_time', '')}")
            lines.append("")

    # Reddit
    lines.append("---\n## 📝 Reddit Posts\n")
    for i, post in enumerate(results.get("reddit_posts", []), 1):
        lines.append(f"### Post {i} — r/{post.get('subreddit', '')}")
        lines.append(post.get("content", ""))
        lines.append("")

    # TikTok
    lines.append("---\n## 🎬 TikTok Scripts\n")
    for i, script in enumerate(results.get("tiktok_scripts", []), 1):
        lines.append(f"### Script {i}")
        lines.append(script.get("content", ""))
        lines.append("")

    # Twitter
    lines.append("---\n## 🐦 Twitter Threads\n")
    for i, thread in enumerate(results.get("twitter_threads", []), 1):
        lines.append(f"### Thread {i}")
        lines.append(thread.get("content", ""))
        lines.append("")

    # Visuals
    lines.append("---\n## 🎨 Visual Prompts\n")
    lines.append(results.get("visual_prompts", {}).get("content", ""))

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"\n📄 Exported to {filepath}")
    return filepath


# ═══════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════╗
║   MORPHIC Content Marketing AI Agency      ║
║   5 AI Agents — Social Media Content     ║
╚══════════════════════════════════════════╝

This will use DeepSeek API to generate:
  📅 1-week content calendar
  📝 7 Reddit posts for r/looksmaxxing, r/SkincareAddiction, etc.
  🎬 7 TikTok/Reels scripts (faceless, voiceover-ready)
  🐦 5 Twitter/X threads
  🎨 AI image generation prompts

Estimated API cost: ~$0.05-0.10
Estimated time: ~60-90 seconds
    """)

    async def main():
        results = await generate_weekly_content()
        filepath = export_to_markdown(results)
        print(f"\n✨ Done! Open {filepath} to see all content ready to post.")

    asyncio.run(main())
