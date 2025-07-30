from playwright.sync_api import Page
from typing import List, Dict, Tuple
from rich import print
from linkiq.controller.li_handler import LIHandler
from linkiq.model.queue import Queue
from linkiq.model.db_client import DBClient
from linkiq.utils.page import random_scroll
from urllib.parse import urlparse
import time
import random
import re
from urllib.parse import urlparse, parse_qs

def normalize_linkedin_profile_url(url: str) -> str:
    """Remove query strings and trailing slashes from profile URLs."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return base.rstrip("/")

def extract_page_number(url: str) -> int:
    """
    Extract the 'page' number from a URL query string.
    Returns 1 if the 'page' parameter is not present or invalid.
    """
    try:
        query = urlparse(url).query
        params = parse_qs(query)
        page_values = params.get("page")
        if page_values and page_values[0].isdigit():
            return int(page_values[0])
    except Exception:
        pass
    return 1

class LISearchHandler:
    WAIT_TIMEOUT = 3000
    MAX_NO_NEW_ATTEMPTS = 3
    PAGE_LOAD_WAIT_TIME = 2000
    LINK_WAIT_TIMEOUT = 5000

    def __init__(self, db_client: DBClient, page: Page):
        self.db_client = db_client
        self.page = page
        self.current_page = 1
        self.base_search_url = None

    def _navigate_to_linkedin_and_wait_for_search(self) -> None:
        """Navigate to LinkedIn and wait for user to perform search."""
        search_url = "https://www.linkedin.com/"
        self.page.goto(search_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.WAIT_TIMEOUT)
        input("[green]Perform search, ensure you searching people, and press Enter when ready...[/green]")
        
        # Capture the current URL after search to use as base for pagination
        self.base_search_url = self.page.evaluate("() => window.location.href")
        self.current_page = extract_page_number(self.base_search_url) if self.base_search_url else 1
        print(f"[blue]Base search URL captured: {self.base_search_url}[/blue]")


    def _get_profile_link_elements(self) -> List:
        """Get all profile link elements from the current page."""
        all_profile_links = self.page.locator("a[href*='/in/'][data-test-app-aware-link], a.app-aware-link[href*='/in/']")
        
        try:
            all_profile_links.first.wait_for(timeout=self.LINK_WAIT_TIMEOUT)
            return all_profile_links.element_handles()
        except Exception:
            print("[yellow]No more results found or timeout occurred.[/yellow]")
            return []

    def _is_mutual_connection_link(self, link_element) -> bool:
        """Check if the link is inside a mutual connections container."""
        try:
            return link_element.evaluate("""
                (element) => {
                    return element.closest('.reusable-search-simple-insight__text-container') !== null;
                }
            """)
        except Exception:
            return False

    def _process_profile_link(self, link_element, seen_profiles: set, profiles: List[str]) -> bool:
        """
        Process a single profile link element.
        
        Returns:
            bool: True if a new profile was added, False otherwise
        """
        try:
            href = link_element.get_attribute("href")
            if not href:
                return False

            # Normalize the URL
            normalized_url = normalize_linkedin_profile_url(href)
            
            # Skip if we've already seen this URL
            if normalized_url in seen_profiles:
                return False
            
            seen_profiles.add(normalized_url)
            
            # Check if this is a mutual connection or main profile
            if self._is_mutual_connection_link(link_element):
                print(f"[blue]Found mutual connection:[/blue] {normalized_url}")
                # Store mutual connections for later processing if needed
                return False
            else:
                print(f"[green]Found main profile:[/green] {normalized_url}")
                profiles.append(normalized_url)
                return True
                
        except Exception as e:
            print(f"[red]Error processing profile link: {e}[/red]")
            return False

    def _process_current_page_profiles(self, profiles: List[str], seen_profiles: set, max_profiles: int) -> int:
        """
        Process all profile links on the current page.
        
        Returns:
            int: Number of new profiles found on this page
        """
        link_elements = self._get_profile_link_elements()
        if not link_elements:
            return 0

        new_profiles_count = 0
        
        for link_el in link_elements:
            if self._process_profile_link(link_el, seen_profiles, profiles):
                new_profiles_count += 1
                
            if len(profiles) >= max_profiles:
                break
                
        return new_profiles_count

    def _navigate_to_next_page(self) -> bool:
        """
        Navigate to the next page by incrementing the page parameter in URL.
        
        Returns:
            bool: True if successfully navigated, False if navigation failed
        """
        try:
            self.current_page += 1
            
            # Add or update the page parameter in the URL
            if '&page=' in self.base_search_url:
                # Replace existing page parameter
                
                next_url = re.sub(r'&page=\d+', f'&page={self.current_page}', self.base_search_url)
            elif '?' in self.base_search_url:
                # Add page parameter to existing query string
                next_url = f"{self.base_search_url}&page={self.current_page}"
            else:
                # Add page parameter as first query parameter
                next_url = f"{self.base_search_url}?page={self.current_page}"
            
            print(f"[blue]Navigating to page {self.current_page}: {next_url}[/blue]")
            
            self.page.goto(next_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(self.PAGE_LOAD_WAIT_TIME)
            
            # Check if we actually got results (not an error page)
            if self._page_has_search_results():
                return True
            else:
                print(f"[yellow]Page {self.current_page} has no search results - reached end.[/yellow]")
                return False
                
        except Exception as e:
            print(f"[red]Error navigating to page {self.current_page}: {e}[/red]")
            return False

    def _page_has_search_results(self) -> bool:
        """Check if the current page has search results."""
        try:
            # Look for search result indicators
            result_indicators = [
                "a[href*='/in/'][data-test-app-aware-link]",
                "a.app-aware-link[href*='/in/']",
                ".search-results-container",
                ".search-results__list"
            ]
            
            for indicator in result_indicators:
                if self.page.locator(indicator).count() > 0:
                    return True
            
            # Check for "no results" indicators
            no_results_indicators = [
                "text=No results found",
                "text=Try different keywords",
                ".search-no-results",
                ".artdeco-empty-state"
            ]
            
            for indicator in no_results_indicators:
                if self.page.locator(indicator).count() > 0:
                    return False
                    
            return False
            
        except Exception:
            return False

    def _has_reached_end_of_results(self) -> bool:
        """Check if we've reached the end of search results."""
        try:
            # Check if current page has no search results
            if not self._page_has_search_results():
                print("[yellow]No search results found on current page.[/yellow]")
                return True
            
            # Check for other end-of-results indicators
            end_markers = [
                "text=You've reached the end",
                "text=No more results",
                ".artdeco-empty-state"
            ]
            
            for marker in end_markers:
                if self.page.locator(marker).count() > 0:
                    print("[yellow]Reached end of results.[/yellow]")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"[red]Error checking end of results: {e}[/red]")
            return True  # Assume end if we can't check

    def _should_continue_searching(self, profiles: List[str], max_profiles: int, no_new_profiles_count: int) -> bool:
        """
        Determine if we should continue searching for more profiles.
        
        Returns:
            bool: True if we should continue, False if we should stop
        """
        # Stop if we have enough profiles
        if len(profiles) >= max_profiles:
            return False
            
        # Stop if we've reached maximum attempts without new profiles
        if no_new_profiles_count >= self.MAX_NO_NEW_ATTEMPTS:
            print("[yellow]No new profiles found after multiple attempts. Stopping.[/yellow]")
            return False
            
        # Stop if we've reached the end of results
        if self._has_reached_end_of_results():
            return False
            
        return True

    def gather_profiles(self, max_profiles: int = 20):
        """
        Gather LinkedIn profiles from search results.
        
        Args:
            max_profiles: Maximum number of profiles to collect
            
        Returns:
            Tuple of (profiles list, mutual connections map)
        """
        try:
            self._navigate_to_linkedin_and_wait_for_search()

            profiles = []
            seen_profiles = set()
            no_new_profiles_count = 0

            while self._should_continue_searching(profiles, max_profiles, no_new_profiles_count):
                
                
                # Process profiles on current page
                random_scroll(self.page)
                new_profiles_found = self._process_current_page_profiles(
                    profiles, seen_profiles, max_profiles
                )
                
                # Update no new profiles counter
                if new_profiles_found == 0:
                    no_new_profiles_count += 1
                    print(f"[yellow]No new profiles found. Attempt {no_new_profiles_count}/{self.MAX_NO_NEW_ATTEMPTS}[/yellow]")
                else:
                    no_new_profiles_count = 0  # Reset counter if we found new profiles

                # Break if we have enough profiles
                if len(profiles) >= max_profiles:
                    break

                # Navigate to next page using URL parameter
                if not self._navigate_to_next_page():
                    # If navigation fails, we've likely reached the end
                    break
            
            print(f"[green]Found {len(profiles)} profiles[/green]")
            Queue.bulk_insert(self.db_client, profiles)
            return
        except Exception as e:
            print(f"[red]Error gathering profiles: {e}[/red]")
            return