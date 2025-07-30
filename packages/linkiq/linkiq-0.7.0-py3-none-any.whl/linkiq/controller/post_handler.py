from typing import List, Dict
import re
from rich import print
from datetime import datetime, timedelta, timezone
from linkiq.model.post import Post

def normalize_post_url(href: str) -> str:
    if "/feed/update/urn:li:activity:" in href:
        base = href.split("?")[0]
        return base.rstrip("/")
    return None

def extract_post_age(age_text: str) -> str:
    """
    Extracts age like '3w', '5d', '2mo', '1yr', '1y', etc. from a string.
    """
    # Match patterns like 3w, 2 mo, 1yr, etc.
    match = re.search(r'\b\d+\s?(y|yr|mo|w|d|h)\b', age_text)
    if match:
        return match.group(0).replace(" ", "")
    return ""

def age_text_to_days(age_text: str) -> int:
    """
    Converts age string like '5h', '3w', '2mo', '1yr' to estimated days.
    Returns -1 if parsing fails.
    """
    age_text = age_text.strip().lower()
    match = re.match(r"(\d+)\s*(h|d|w|mo|yr)", age_text)
    if not match:
        return -1

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "h":
        return 0  # within the same day
    elif unit == "d":
        return value
    elif unit == "w":
        return value * 7
    elif unit == "mo":
        return value * 30
    elif unit == "yr":
        return value * 365
    else:
        return -1


class LIPostHandler:
    
    WAIT_TIMEOUT = 3000

    def __init__(self, db_client, page):
        self.db_client = db_client
        self.page = page

    
    def get_post_urls(self, age=7, max_posts=10):
        try:
            today = datetime.now(timezone.utc).date()
            seven_days_ago = today - timedelta(days=age)

            start_date_str = seven_days_ago.strftime("%Y-%m-%d")
            end_date_str = today.strftime("%Y-%m-%d")

            base_url = (
                f"https://www.linkedin.com/analytics/creator/top-posts"
                f"?timeRange=past_7_days&metricType=ENGAGEMENT&startDate={start_date_str}&endDate={end_date_str}"
            )

            print(f"Navigating directly to top posts URL:\n{base_url}")
            self.page.goto(base_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(LIPostHandler.WAIT_TIMEOUT)

            post_data = []

            while len(post_data) < max_posts:
                anchors = self.page.locator("a[href*='/feed/update/']")
                elements = anchors.element_handles()

                for anchor in elements:
                    href = anchor.get_attribute("href")
                    url = normalize_post_url(href)
                    if not url or not url.startswith("https://") or any(item["url"] == url for item in post_data):
                        continue

                    # Find relative time text inside the anchor, if available
                    try:
                        time_span = anchor.query_selector(".feed-mini-update-contextual-description__text")
                        age_text = time_span.inner_text().strip() if time_span else ""
                    except Exception:
                        age_text = ""
                    age_text = extract_post_age(age_text)
                    age_text_in_days = age_text_to_days(age_text) 

                    print(f"[white]{age_text} {age_text_in_days}[/white]")
                    print(f"[green]Found post[/green] {url} | [blue]{age_text}[/blue]")
                    post_data.append({"url": url, "age": age_text_in_days})

                    if len(post_data) >= max_posts:
                        break

                # Pagination
                next_link = self.page.locator("a:has(span.member-analytics-addon__cta-list-item-title:has-text('Show more'))")

                if next_link.count() > 0 and next_link.first.is_visible():
                    next_url = next_link.first.get_attribute("href")
                    if not next_url:
                        print("[yellow]No href found on 'Show more' link, stopping.[/yellow]")
                        break
                    print(f"Loading next page: {next_url}")
                    self.page.goto(next_url)
                    self.page.wait_for_timeout(self.WAIT_TIMEOUT)
                else:
                    print("[yellow]No more 'Show more' links found, stopping.[/yellow]")
                    break
            
            Post.bulk_insert_if_new(self.db_client, post_data)

            return  # list of dicts with 'url' and 'age'
        except Exception as e:
            print("[red]Error in get_post_urls - {e}[/red]")
            return
