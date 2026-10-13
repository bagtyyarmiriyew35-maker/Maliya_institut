import urllib.request
import json
import re
import ssl
import socket
import logging
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import BilimNews

logger = logging.getLogger(__name__)

BILIM_NEWS_URL = "https://bilim.tm/tk/news"
BILIM_IP = "95.85.125.73"

# Resilient DNS fallback for local TM network environments
_orig_getaddrinfo = socket.getaddrinfo

def _safe_getaddrinfo(host, port, *args, **kwargs):
    try:
        return _orig_getaddrinfo(host, port, *args, **kwargs)
    except socket.gaierror:
        if host in ('bilim.tm', 'merkez.bilim.tm', 'www.bilim.tm'):
            return _orig_getaddrinfo(BILIM_IP, port, *args, **kwargs)
        raise

socket.getaddrinfo = _safe_getaddrinfo


def get_unverified_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_news_from_bilim(limit=9):
    """
    Fetches the latest news items from bilim.tm/tk/news.
    Returns a list of dicts with news details.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tk,en-US,en;q=0.9,ru;q=0.8",
    }
    req = urllib.request.Request(BILIM_NEWS_URL, headers=headers)
    ctx = get_unverified_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as response:
            html = response.read().decode("utf-8")
    except Exception as e:
        logger.error(f"Error requesting {BILIM_NEWS_URL}: {e}")
        return []

    # Search for initialItems array in Next.js Server Components payload
    match = re.search(r'\\"initialItems\\":(\[.*?\]),\\"initialCount\\"', html)
    if not match:
        match = re.search(r'"initialItems":(\[.*?\]),"initialCount"', html)

    if not match:
        logger.error("Could not find initialItems payload in bilim.tm response")
        return []

    try:
        raw_json = match.group(1).replace(r'\"', '"').replace(r'\\', '\\')
        items = json.loads(raw_json)
    except Exception as e:
        logger.error(f"Error parsing initialItems JSON from bilim.tm: {e}")
        return []

    results = []
    for item in items[:limit]:
        item_id = item.get("id")
        title = (item.get("title") or "").strip()
        slug = item.get("slug") or ""
        image = item.get("image_thumbnail") or item.get("image") or ""
        published_str = item.get("published_date")
        views = item.get("views") or 0
        desc = (item.get("description") or "").strip()

        pub_date = None
        if published_str:
            pub_date = parse_datetime(published_str)
        if not pub_date:
            pub_date = timezone.now()

        source_url = f"https://bilim.tm/tk/news/{slug}" if slug else BILIM_NEWS_URL

        results.append({
            "external_id": item_id,
            "title": title,
            "slug": slug,
            "description": desc,
            "image_url": image,
            "published_date": pub_date,
            "views_count": views,
            "source_url": source_url,
        })

    return results


def fetch_article_multilingual(item_id, fallback_title=""):
    """
    Fetches title, description and full HTML body for tk, en, and ru from bilim.tm.
    """
    data = {
        'tm': {'title': fallback_title, 'description': '', 'content': ''},
        'en': {'title': '', 'description': '', 'content': ''},
        'ru': {'title': '', 'description': '', 'content': ''},
    }

    if not item_id:
        return data

    lang_map = {
        'tk': 'tm',
        'en': 'en',
        'ru': 'ru',
    }

    body_pattern = r'<div class="bilim-prose[^"]*">(.*?)</div>\s*<a[^>]*href="[^"]*news"[^>]*>Yza</a>'
    fallback_body_pattern = r'<div class="bilim-prose[^"]*">(.*?)</div>\s*<a'
    title_pattern = r'<h1[^>]*>(.*?)</h1>'

    ctx = get_unverified_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    for remote_lang, local_lang in lang_map.items():
        url = f"https://bilim.tm/{remote_lang}/news/{item_id}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
                html = response.read().decode("utf-8")

                # Extract Title
                m_title = re.search(title_pattern, html)
                if m_title:
                    clean_t = m_title.group(1).strip()
                    if clean_t:
                        data[local_lang]['title'] = clean_t

                # Extract Body HTML
                m_body = re.search(body_pattern, html, re.DOTALL)
                if not m_body:
                    m_body = re.search(fallback_body_pattern, html, re.DOTALL)
                if not m_body:
                    m_body = re.search(r'<div class="bilim-prose[^"]*">(.*?)</div>', html, re.DOTALL)

                if m_body:
                    body_html = m_body.group(1).strip()
                    data[local_lang]['content'] = body_html

                    # Extract plain text description for cards
                    plain_text = re.sub(r'<[^>]+>', ' ', body_html)
                    plain_text = ' '.join(plain_text.split())
                    data[local_lang]['description'] = plain_text[:280] + '...' if len(plain_text) > 280 else plain_text
        except Exception as e:
            logger.warning(f"Could not fetch {remote_lang} for news {item_id}: {e}")

    # Fallback to TM if EN or RU were missing on remote site
    if not data['en']['title']:
        data['en']['title'] = data['tm']['title']
    if not data['en']['content']:
        data['en']['content'] = data['tm']['content']
    if not data['en']['description']:
        data['en']['description'] = data['tm']['description']

    if not data['ru']['title']:
        data['ru']['title'] = data['tm']['title']
    if not data['ru']['content']:
        data['ru']['content'] = data['tm']['content']
    if not data['ru']['description']:
        data['ru']['description'] = data['tm']['description']

    return data


def sync_bilim_news(limit=9):
    """
    Syncs the latest news from bilim.tm in all available languages (TM, EN, RU).
    Saves exactly the latest `limit` (default 9) items to BilimNews.
    Maintains a maximum of `limit` items in the database by removing oldest items.
    """
    items = fetch_news_from_bilim(limit=limit)
    if not items:
        return {
            "success": False,
            "message": "Bilim.tm sahypasyndan täzelikleri alyp bolmady (Baglanyşygy barlaň).",
            "added": 0,
            "updated": 0,
            "total": BilimNews.objects.count(),
        }

    added_count = 0
    updated_count = 0
    synced_pks = []

    for data in items:
        ext_id = data.get("external_id")

        # Fetch multilingual versions (TM, EN, RU)
        multi = fetch_article_multilingual(ext_id, fallback_title=data["title"])

        title_tm = multi['tm']['title'] or data["title"]
        title_en = multi['en']['title'] or title_tm
        title_ru = multi['ru']['title'] or title_tm

        desc_tm = multi['tm']['description'] or data.get("description", "")
        desc_en = multi['en']['description'] or desc_tm
        desc_ru = multi['ru']['description'] or desc_tm

        content_tm = multi['tm']['content'] or desc_tm or title_tm
        content_en = multi['en']['content'] or desc_en or title_en
        content_ru = multi['ru']['content'] or desc_ru or title_ru

        obj, created = BilimNews.objects.get_or_create(
            external_id=ext_id,
            defaults={
                "title_tm": title_tm,
                "title_en": title_en,
                "title_ru": title_ru,
                "slug": data["slug"],
                "description_tm": desc_tm,
                "description_en": desc_en,
                "description_ru": desc_ru,
                "content_tm": content_tm,
                "content_en": content_en,
                "content_ru": content_ru,
                "image_url": data["image_url"],
                "source_url": data["source_url"],
                "published_date": data["published_date"],
                "views_count": data["views_count"],
            }
        )

        if created:
            added_count += 1
        else:
            obj.title_tm = title_tm
            if title_en:
                obj.title_en = title_en
            if title_ru:
                obj.title_ru = title_ru

            obj.slug = data["slug"]

            if desc_tm:
                obj.description_tm = desc_tm
            if desc_en:
                obj.description_en = desc_en
            if desc_ru:
                obj.description_ru = desc_ru

            if multi['tm']['content']:
                obj.content_tm = multi['tm']['content']
            if multi['en']['content']:
                obj.content_en = multi['en']['content']
            if multi['ru']['content']:
                obj.content_ru = multi['ru']['content']

            if data["image_url"] and not obj.image:
                obj.image_url = data["image_url"]
            obj.source_url = data["source_url"]
            obj.published_date = data["published_date"]
            if data["views_count"] > obj.views_count:
                obj.views_count = data["views_count"]
            obj.save()
            updated_count += 1

        synced_pks.append(obj.pk)

    # Clean up: keep only the latest `limit` items in the database!
    top_pks = list(
        BilimNews.objects.order_by("-published_date", "-id")
        .values_list("pk", flat=True)[:limit]
    )
    deleted_count, _ = BilimNews.objects.exclude(pk__in=top_pks).delete()

    total_count = BilimNews.objects.count()

    return {
        "success": True,
        "message": f"Üstünlikli täzelendi: {added_count} täze goşuldy, {updated_count} täzelendi. Jemi {total_count} sany saklandy.",
        "added": added_count,
        "updated": updated_count,
        "deleted": deleted_count,
        "total": total_count,
    }
