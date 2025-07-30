
from linkiq.model.db_client import DBClient
from linkiq.model.queue import Queue
from datetime import datetime 
from rich import print
import re
import random
import time

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

class LIViewHandler:

    def __init__(self, db_client: DBClient, page):
            self.db_client = db_client
            self.page = page

    def gather_profile_views_old(self):
        try:
            self.page.goto("https://www.linkedin.com/me/profile-views/")
            

            html = self.page.content()

            list_items = list_items = self.page.locator("li.artdeco-list__item.member-analytics-addon-entity-list__item").all()
            profile_count = 0

            for li in list_items:
                try:
                    link = li.locator("a[href*='/in/']")
                    url = link.get_attribute("href")

                    # Get time since viewed
                    age_div = li.locator("div.artdeco-entity-lockup__caption")
                    age_text = age_div.inner_text()
                    age_text = extract_post_age(age_text)
                    age = age_text_to_days(age_text)
                    print(f"found {url} who viewed your profile {age} days ago")
                    if url:
                        profile = Queue(PROFILE=url, CREATED_AT=datetime.now())
                        profile.add(self.db_client)
                        profile_count += 1
                except Exception as e:
                    continue

            print(f"[green]Collected {profile_count} profiles.[/green]")
            return
        except Exception as e:
            print(f"[red]Error gathering profile views: {e}[/red]")
            return
        
    def _human_scroll_to_bottom(self, max_idle_rounds=2):
        """Scroll to bottom, waiting for new content to load each time."""
        idle_rounds = 0
        last_seen_count = 0

        while idle_rounds < max_idle_rounds:
            # Get number of current <li> items
            current_count = self.page.locator("li.artdeco-list__item.member-analytics-addon-entity-list__item").count()

            if current_count == last_seen_count:
                idle_rounds += 1
            else:
                idle_rounds = 0
                last_seen_count = current_count

            # Jitter scroll up/down a bit like a human
            for _ in range(random.randint(2, 4)):
                jitter = random.choice([-1, 1]) * random.randint(30, 100)
                self.page.mouse.wheel(0, jitter)
                time.sleep(random.uniform(0.1, 0.3))

            # Scroll down to load more
            self.page.mouse.wheel(0, random.randint(400, 700))
            time.sleep(random.uniform(1.0, 1.5))  # give time for LinkedIn to load

        print(f"[cyan]Scrolling stopped after {idle_rounds} idle rounds (no new views loaded).[/cyan]")


    def _extract_profile_info(self, li_element):
        try:
            url_el = li_element.locator("a[href*='/in/']")
            url = url_el.get_attribute("href")

            caption_el = li_element.locator("div.artdeco-entity-lockup__caption")
            age_text = caption_el.inner_text().strip()
            age_text = extract_post_age(age_text)
            age_days = age_text_to_days(age_text)  # Assume you have this method

            return url, age_days
        except Exception:
            return None, None
    
    def _bulk_extract_profiles(self):
        # Run this inside the page context to extract all profiles at once
        data_list = self.page.evaluate("""
            () => {
                const lis = Array.from(document.querySelectorAll('li.artdeco-list__item.member-analytics-addon-entity-list__item'));
                return lis.map(li => {
                    const anchor = li.querySelector('a[href*="/in/"]');
                    const url = anchor ? anchor.href : null;
                    const ageDiv = li.querySelector('div.artdeco-entity-lockup__caption');
                    const ageText = ageDiv ? ageDiv.innerText : '';
                    return { url, ageText };
                });
            }
        """)
        return data_list


    def gather_profile_views_last(self, max_days_old: int = 14):
        try:
            # Go to 2-week filtered profile views
            self.page.goto("https://www.linkedin.com/me/profile-views/?timeRange=past_2_weeks", wait_until="domcontentloaded")
            self.page.wait_for_selector("li.artdeco-list__item.member-analytics-addon-entity-list__item", timeout=10000)

            # Scroll like a human to bottom
            self._human_scroll_to_bottom()

            # Gather all profile view entries
            lis = self.page.locator("li.artdeco-list__item.member-analytics-addon-entity-list__item").all()

            profile_count = 0
            seen_urls = set()

            for li in lis:
                url, age_days = self._extract_profile_info(li)
                if not url or url in seen_urls:
                    continue
                if age_days > max_days_old:
                    break
                seen_urls.add(url)                
                profile_count += 1
                print(f"found {url} who viewed your profile {age_days} days ago")

            profiles = list(seen_urls)
            if not profiles:
                Queue.bulk_insert(self.db_client, profiles)
            
            print(f"[green]Collected {profile_count} profiles who viewed your profile within {max_days_old} days.[/green]")

        except Exception as e:
            print(f"[red]Error gathering profile views: {e}[/red]")

    def gather_profile_views(self, max_days_old: int = 14):
        try:
            # Go to 2-week filtered profile views
            self.page.goto("https://www.linkedin.com/me/profile-views/?timeRange=past_2_weeks", wait_until="domcontentloaded")
            self.page.wait_for_selector("li.artdeco-list__item.member-analytics-addon-entity-list__item", timeout=10000)

            # Scroll like a human to bottom
            self._human_scroll_to_bottom()

            bulk_profiles = self._bulk_extract_profiles()
            seen_urls = set()
            profile_count = 0
            
            for entry in bulk_profiles:
                url = entry.get('url')
                age_text = entry.get('ageText')
                if not url or url in seen_urls:
                    continue
                
                # Assume you have a helper to convert ageText like '2w' to days
                age_text = extract_post_age(age_text)
                age_days = age_text_to_days(age_text)
                
                if age_days > max_days_old:
                    break
                
                seen_urls.add(url)
                profile_count += 1
                print(f"found {url} who viewed your profile {age_days} days ago")

            profiles = list(seen_urls)
            if not profiles:
                Queue.bulk_insert(self.db_client, profiles)
            
            print(f"[green]Collected {profile_count} profiles who viewed your profile within {max_days_old} days.[/green]")

        except Exception as e:
            print(f"[red]Error gathering profile views: {e}[/red]")