from playwright.sync_api import Page
from urllib.parse import urlparse
import re
from linkiq.model.queue import Queue
from linkiq.model.db_client import DBClient
from linkiq.model.profile import Profile
from time import sleep
import random
from datetime import datetime
from rich import print
from linkiq.controller.campaign_handler import CampaignHandler
import json

class LIProfileHandler:

    DOM_WAIT_TIMEOUT = 30000
    SELECTOR_WAIT_TIMEOUT = 10000
    INTER_PROFILE_SLEEP_MIN_THRESHOLD = 30
    INTER_PROFILE_SLEEP_MAX_THRESHOLD = 120

    def __init__(self, db_client: DBClient, page: Page):
        self.db_client = db_client
        self.page = page

    def extract_icp_traits_from_profile(self, profile_url: str) -> dict:
        print(f"Opening profile: {profile_url}")
        if not self._load_profile_page(profile_url):
            return {"url": profile_url, "error": "Failed to load page"}
        traits = {
            "url": profile_url,
            "name": self._extract_name(),
            "title": self._extract_title(),
            "company_name": self._extract_current_company_from_page(),
            "connection_degree": self._extract_connection_degree(),
            "location": self._extract_location(),
            "about": self._extract_about_section_from_page(),
            "experience": self._extract_experience_entries_from_page()
        }

        return self._clean_traits(traits)


    def _load_profile_page(self, profile_url: str) -> bool:
        try:
            self.page.goto(profile_url, wait_until="domcontentloaded", timeout=self.DOM_WAIT_TIMEOUT)
            self.page.wait_for_timeout(3000)
            self.page.wait_for_selector("main", timeout=self.SELECTOR_WAIT_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error loading page: {e}")
            return False


    def _extract_name(self) -> str:
        selectors = [
            "h1.text-heading-xlarge",
            "h1[data-generated-suggestion-target]",
            "h1.break-words",
            "main h1"
        ]
        return self._safe_extract_text(selectors)


    def _extract_title(self) -> str:
        selectors = [
            "div.text-body-medium.break-words",
            ".pv-text-details__left-panel .text-body-medium",
            ".ph5.pb5 .text-body-medium.break-words",
            ".pv-top-card--list li:first-child .text-body-medium"
        ]
        title = self._safe_extract_text(selectors)
        if not title:
            try:
                meta = self.page.locator("meta[property='og:description']").get_attribute("content")
                if meta and " at " in meta:
                    return meta.split(" at ")[0].strip()
            except:
                pass
        return title


    def _extract_location(self) -> str:
        selectors = [
            "span.text-body-small.inline.t-black--light.break-words",
            ".pv-top-card--list-bullet li:contains('location')",
            ".pv-top-card__location .geo",
            ".ph5.pb5 .text-body-small.break-words"
        ]
        return self._safe_extract_text(selectors)


    def _extract_connection_degree(self) -> str:
        selectors = [
            "span.dist-value",
            ".pv-top-card--badges .dist-value",
            "span[class*='dist-']",
            ".pv-top-card--badges span"
        ]
        return self._safe_extract_text(selectors)


    def _safe_extract_text(self, selectors: list) -> str:
        for selector in selectors:
            try:
                el = self.page.locator(selector).first
                if el.is_visible():
                    text = el.text_content()
                    if text:
                        return text.strip()
            except:
                continue
        return None


    def _extract_current_company_from_page(self) -> str:
        # Try aria-label method first
        button = self.page.locator("button[aria-label^='Current company:']").first
        if button and button.is_visible():
            label = button.get_attribute("aria-label")
            if label:
                match = re.search(r"Current company:\s*(.+?)\.\s*Click", label)
                if match:
                    return match.group(1).strip()

        # Fallback: check for div inside span inside button
        try:
            return self.page.locator("ul li button span div").first.text_content().strip()
        except:
            return None


    def _clean_traits(self, traits: dict) -> dict:
        for key, value in traits.items():
            if isinstance(value, str):
                traits[key] = " ".join(value.strip().split())
        return traits

    def _extract_about_section_from_page(self) -> str:
        try:
            # First try the most specific selector based on the HTML structure
            about_section = self.page.locator("section:has(#about) .inline-show-more-text--is-collapsed span[aria-hidden='true']").first
            
            if about_section.count() > 0:
                text = about_section.inner_text().strip()
                if text:
                    return text
            
            # Fallback: try a broader selector for the inline-show-more-text div
            about_section_fallback = self.page.locator("section:has(#about) .inline-show-more-text").first
            
            if about_section_fallback.count() > 0:
                text = about_section_fallback.inner_text().strip()
                if text:
                    return text
            
            # Last resort: try to find any text content in the about section
            about_section_broad = self.page.locator("section:has(#about)").first
            
            if about_section_broad.count() > 0:
                # Get all text but try to filter out navigation/header text
                full_text = about_section_broad.inner_text().strip()
                # Remove the "About" header text if it appears at the beginning
                if full_text.startswith("About"):
                    full_text = full_text[5:].strip()
                if full_text:
                    return full_text
                    
        except Exception as e:
            print(f"[yellow]Error extracting About section: {e}[/yellow]")

        return None


    def _extract_experience_entries_from_page(self) -> list:
        """Extract experience entries from LinkedIn profile"""
        experiences = []

        try:
            # Wait for experience section to load
            self.page.wait_for_selector("section:has(#experience)", timeout=self.SELECTOR_WAIT_TIMEOUT)

            # Try multiple selectors for experience entries
            experience_selectors = [
                "section:has(#experience) .pvs-list__paged-list-item",
                "section:has(#experience) .artdeco-list__item",
                "section:has(#experience) .pv-entity__position-group-pager li",
                "section:has(#experience) .experience-item"
            ]

            experience_items = None
            for selector in experience_selectors:
                items = self.page.locator(selector)
                if items.count() > 0:
                    experience_items = items
                    break

            if not experience_items:
                print("No experience items found")
                return experiences

            # Extract each experience entry (limit to top 3)
            max_experiences = min(3, experience_items.count())
            for i in range(max_experiences):
                try:
                    item = experience_items.nth(i)
                    experience = self._extract_single_experience(item)
                    if experience:
                        experiences.append(experience)
                except Exception as e:
                    print(f"Error extracting experience item {i}: {e}")
                    continue

        except Exception as e:
            print(f"Error extracting experience section: {e}")

        return experiences


    def _extract_single_experience(self, item) -> dict:
        """Extract details from a single experience item"""
        experience = {
            "title": None,
            "company": None,
            "duration": None,
            "location": None,
            "description": None
        }

        try:
            # Extract job title - try multiple selectors
            title_selectors = [
                ".t-bold span[aria-hidden='true']",
                ".pv-entity__summary-info h3",
                ".t-16.t-black.t-bold",
                "h3 span[aria-hidden='true']",
                ".display-flex.align-items-center span[aria-hidden='true']"
            ]

            for selector in title_selectors:
                title_elem = item.locator(selector).first
                if title_elem.count() > 0:
                    title = title_elem.inner_text().strip()
                    if title and title not in ["Experience", "Show all", "Hide"]:
                        experience["title"] = title
                        break

            # Extract company name
            company_selectors = [
                ".t-14.t-normal span[aria-hidden='true']",
                ".pv-entity__secondary-title",
                ".t-14.t-black--light span[aria-hidden='true']",
                "a span[aria-hidden='true']"
            ]

            for selector in company_selectors:
                company_elem = item.locator(selector).first
                if company_elem.count() > 0:
                    company = company_elem.inner_text().strip()
                    if company and company != experience["title"]:
                        experience["company"] = company
                        break

            # Extract duration
            duration_selectors = [
                ".t-14.t-black--light.t-normal span[aria-hidden='true']",
                ".pv-entity__bullet-item",
                ".t-12.t-black--light.t-normal span[aria-hidden='true']"
            ]

            duration_texts = []
            for selector in duration_selectors:
                elements = item.locator(selector)
                for j in range(elements.count()):
                    text = elements.nth(j).inner_text().strip()
                    if text and any(keyword in text.lower() for keyword in ["month", "year", "present", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                        duration_texts.append(text)

            if duration_texts:
                experience["duration"] = " · ".join(duration_texts[:2])  # Take first two duration-related texts

            # Extract location
            location_selectors = [
                "span[class*='t-14'][class*='t-normal'] span[aria-hidden='true']",
                ".pv-entity__location span"
            ]

            for selector in location_selectors:
                elements = item.locator(selector)
                for j in range(elements.count()):
                    text = elements.nth(j).inner_text().strip()
                    # Simple heuristic: if it contains common location indicators
                    if text and any(indicator in text for indicator in [",", "State", "Country", "Remote", "NY", "CA", "TX", "FL"]):
                        experience["location"] = text
                        break
                if experience["location"]:
                    break

            # Extract description
            description_selectors = [
                ".inline-show-more-text span[aria-hidden='true']",
                ".pv-entity__description",
                ".t-14.t-normal.t-black span[aria-hidden='true']"
            ]

            for selector in description_selectors:
                desc_elem = item.locator(selector).first
                if desc_elem.count() > 0:
                    desc = desc_elem.inner_text().strip()
                    if desc and len(desc) > 20:  # Only take substantial descriptions
                        experience["description"] = desc
                        break

        except Exception as e:
            print(f"Error extracting single experience: {e}")

        # Only return experience if we have at least title or company
        if experience["title"] or experience["company"]:
            return experience
        return {}
    
    def extract_icp_traits_from_file(self, html_file_path: str) -> dict:
        print(f"Reading saved HTML: {html_file_path}")
        try:
            with open(html_file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.page.set_content(html_content, wait_until="domcontentloaded")
            traits = {
                "url": self.profile_url,
                "name": self._extract_name(),
                "title": self._extract_title(),
                "company_name": self._extract_current_company_from_page(),
                "connection_degree": self._extract_connection_degree(),
                "location": self._extract_location(),
                "about": self._extract_about_section_from_page(),
                "experience": self._extract_experience_entries_from_page()
            }
            return self._clean_traits(traits)
        except Exception as e:
            print(f"Failed to read HTML file: {e}")
            return {"url": self.profile_url, "error": "Failed to read file"}
        

    def get_profiles(self, max_profiles: int = 20, profile_age: int = 30):
        try:
            queued_profiles = Queue.get_oldest(self.db_client, max_profiles)
            if not queued_profiles:
                print("[yellow] No profiles found in queue [/yellow]")
                return
            ch = CampaignHandler()
            for i, p in enumerate(queued_profiles):
                # remove it from the queue
                p.delete(self.db_client)
                # do the processing
                print(f"[green] Processing profile {i+1}/{len(queued_profiles)}: {p.profile} [/green]")
                profile = Profile.get(self.db_client, p.profile)
                load_new = not profile
                if profile:
                    last_udpate = profile.updated_at
                    load_new = (datetime.now() - last_udpate).days > profile_age

                if load_new:
                    traits = self.extract_icp_traits_from_profile(p.profile)
                    if not profile:
                        profile = Profile(url=p.profile)
                    profile.name = traits.get("name", profile.name)
                    profile.title = traits.get("title", profile.title)
                    profile.company = traits.get("company_name", profile.company)
                    profile.connection_degree = traits.get("connection_degree", profile.connection_degree)
                    profile.location = traits.get("location", profile.location)
                    profile.about = traits.get("about", profile.about)
                    profile.experience = json.dumps(traits.get("experience", profile.experience))
                    
                else:
                    print(f"[yellow] Skipping profile {p.profile} as it was updated less than {profile_age} days ago [/yellow]")
                
                profile.interest_signal = profile.interest_signal + 1
                print(f"[green] add/update profile {profile.url} to db [/green]")
                profile.add(self.db_client)

                ch.lead_gen(self.db_client, profile)

                # Only sleep if this is not the last post
                if i < len(queued_profiles) - 1:
                    sleep_time = random.randint(self.INTER_PROFILE_SLEEP_MIN_THRESHOLD, 
                                        self.INTER_PROFILE_SLEEP_MAX_THRESHOLD)
                    print(f"[gray] Sleeping for {sleep_time} seconds [/gray]")
                    sleep(sleep_time)
        except Exception as e:
            print(f"[red] Error processing profiles - {e}[/red]")
            return