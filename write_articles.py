"""
Part 3: Transform Transcripts into Magazine Articles using AI
Takes raw video transcripts and turns them into polished, readable articles.

Supports switchable model providers (OpenAI-compatible protocol):
- DeepSeek (default)  -> https://api.deepseek.com
- GLM (Z.ai Coding Plan) -> https://api.z.ai/api/coding/paas/v4
If the primary provider fails (e.g. quota exhausted), it automatically
falls back to the other provider when that one has a key configured.
"""

import os
import requests
from dotenv import load_dotenv

# Load your API keys
load_dotenv()

# ========================================
# MODEL PROVIDER CONFIGURATION
# Switch by setting ARTICLE_PROVIDER in .env (deepseek / glm)
# ========================================
ARTICLE_PROVIDER = os.getenv("ARTICLE_PROVIDER", "deepseek").strip().lower()

PROVIDERS = {
    "deepseek": {
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "label": "DeepSeek",
    },
    "glm": {
        "base_url": os.getenv("GLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
        "api_key": os.getenv("GLM_API_KEY", ""),
        "model": os.getenv("GLM_MODEL", "glm-4.5-air"),
        "label": "GLM",
    },
}

MAX_OUTPUT_TOKENS = int(os.getenv("ARTICLE_MAX_TOKENS", "8000"))


def _is_configured(provider):
    """A provider is usable when a real API key is set (not a placeholder)."""
    key = provider["api_key"]
    return bool(key) and "your_" not in key and "here" not in key


def _chat(prompt, provider_name):
    """
    Call an OpenAI-compatible chat completions endpoint.
    Returns the reply text, or raises an exception with the failure reason.
    """
    p = PROVIDERS[provider_name]
    response = requests.post(
        f"{p['base_url'].rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {p['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": p["model"],
            "max_tokens": MAX_OUTPUT_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=600,
    )

    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")

    content = response.json()["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("empty response")
    return content.strip()


def write_article(video):
    """
    Use an LLM to transform a video transcript into a magazine-style article.
    Tries the primary provider first, then falls back to the other one.
    """
    prompt = f"""You are a skilled magazine writer. Transform this YouTube video transcript into a well-written, engaging article.

VIDEO TITLE: {video['title']}
CHANNEL: {video['channel']}
VIDEO URL: {video['url']}

VIDEO DESCRIPTION:
{video['description']}

TRANSCRIPT:
{video['transcript']}

---

Remix this YouTube transcript into a magazine article. Guidelines:
- Use the video title and description to correct any transcription errors, especially names of people, companies, or technical terms. The description often contains the correct spellings.
- Start with an engaging headline (different from the video title)
- The audience is a curious individual who is generally smart but not a specialist or expert in the area mentioned in the video
- Highly engaging and readable. Wherever jargon or obscure references appear, explain them. Extremely well-written; think New Yorker or the Atlantic
- Capture the key insights, especially contrarian viewpoints, memorable anecdotes, and surprising insights. Preserve key quotes (clean up filler words or transcription errors).
- There's no fixed length requirement; it depends on the length of the original article as well as the insight density. Make your own judgment. This should be a satisfying long-read.
- Do NOT include phrases like "In this video" - write it as a standalone article. Assume the reader has not watched the video and has zero context about it. This article is meant to be as a replacement, not complement, for watching the video.

Format the article in clean markdown."""

    # Primary provider first, then the other provider as fallback
    order = [ARTICLE_PROVIDER] + [k for k in PROVIDERS if k != ARTICLE_PROVIDER]

    for name in order:
        provider = PROVIDERS[name]
        if not _is_configured(provider):
            continue

        try:
            text = _chat(prompt, name)
            used = f"{provider['label']} ({provider['model']})"
            if name != ARTICLE_PROVIDER:
                print(f"  ↩ Primary provider failed, article written by {used}")
            else:
                print(f"  ✓ Written by {used}")
            return text
        except Exception as e:
            print(f"  ⚠ {provider['label']} ({provider['model']}) failed: {e}")

    print("  ✗ All model providers failed")
    return None


def write_articles_for_videos(videos):
    """
    Generate articles for all videos with transcripts.
    """
    print("\nGenerating articles with AI...\n")
    print("=" * 60)

    articles = []

    for video in videos:
        print(f"Writing article: {video['title'][:50]}...")

        article = write_article(video)

        if article:
            articles.append({
                "title": video["title"],
                "channel": video["channel"],
                "url": video["url"],
                "article": article
            })
            print(f"  ✓ Article generated!\n")
        else:
            print(f"  ✗ Failed to generate article\n")

    print("=" * 60)
    print(f"Generated {len(articles)} articles")

    return articles


# Test it standalone
if __name__ == "__main__":
    # Test with a mock video
    test_video = {
        "title": "Test Video",
        "channel": "Test Channel",
        "url": "https://youtube.com/watch?v=test",
        "transcript": "Hello everyone, today we're going to talk about something really exciting. I've been working on this project for months and I can't wait to share it with you. The main idea is simple but powerful..."
    }

    print(f"Active provider: {PROVIDERS[ARTICLE_PROVIDER]['label']} ({PROVIDERS[ARTICLE_PROVIDER]['model']})")
    print("Testing article generation...")
    article = write_article(test_video)
    if article:
        print("\nGenerated article:\n")
        print(article)
