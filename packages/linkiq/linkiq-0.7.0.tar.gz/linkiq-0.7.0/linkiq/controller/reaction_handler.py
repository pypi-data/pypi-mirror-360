from rich import print
from playwright.sync_api import Page
from urllib.parse import urlparse
from linkiq.model.db_client import DBClient
from linkiq.model.post import Post
from linkiq.model.queue import Queue
from datetime import datetime
from time import sleep
import random
def normalize_linkedin_profile_url(url):
    """Remove query strings and trailing slashes from profile URLs."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return base.rstrip("/")

class LIReactionHandler:
    """Handles extraction of reactor profiles from LinkedIn posts with intelligent scrolling."""
    WAIT_TIMEOUT = 3000
    INTER_POST_SLEEP_MIN_THRESHOLD = 60 #seconds
    INTER_POST_SLEEP_MAX_THRESHOLD = 120 #seconds

    def __init__(self, db_client: DBClient, page: Page):
        self.db_client = db_client
        self.page = page
        self.profile_urls = set()
        
        # Scroll tracking
        self.scroll_position = 0
        self.scroll_step = 100
        
        # Termination conditions
        self.last_profile_count = 0
        self.profiles_unchanged_count = 0
        self.max_profiles_unchanged = 5
        
        self.last_scroll_height = 0
        self.scroll_height_unchanged_count = 0
        self.max_scroll_height_unchanged = 4
        
        self.last_scroll_position = 0
        self.scroll_position_stuck_count = 0
        self.max_scroll_position_stuck = 3
        
        # Recovery tracking
        self.recovery_attempts = 0
        self.consecutive_failed_recoveries = 0
        self.max_consecutive_failed_recoveries = 3
        self.total_successful_recoveries = 0
        
        # Configuration
        self.grace_period_iterations = 10
        self.check_interval = 3  # Check conditions every N iterations
    

    def open_post_and_click_reactions(self, post_url: str) -> bool:
        """Opens the post and clicks the reactions button. Returns True if successful."""
        print(f"[blue]Opening post: {post_url}[/blue]")
        self.page.goto(post_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(LIReactionHandler.WAIT_TIMEOUT)

        try:
            reaction_button = self.page.locator("button.social-details-social-counts__count-value").first
            reaction_button.scroll_into_view_if_needed()
            reaction_button.wait_for(state="visible", timeout=5000)
            reaction_button.click()
            print("[green]Clicked reactions button[/green]")
            self.page.wait_for_timeout(2000)
            return True
        except Exception as e:
            print(f"[red]Could not find or click reactions button:[/red] {e}")
            return False
    
    def click_all_reactions_tab(self) -> None:
        """Clicks the 'All' reactions tab if visible."""
        try:
            all_tab = self.page.locator("button[data-js-reaction-tab='ALL']").first
            if all_tab and all_tab.is_visible():
                all_tab.click()
                print("[green]Clicked 'All' reactions tab[/green]")
                self.page.wait_for_timeout(1500)
        except Exception as e:
            print(f"[yellow]Failed to click 'All' tab: {e}[/yellow]")
    
    def find_scroll_container(self):
        """Finds and returns the appropriate scroll container element."""
        scroll_containers = [
            ".social-details-reactors-modal__content",
            ".scaffold-finite-scroll__content",
            ".artdeco-modal__content"
        ]
        
        for selector in scroll_containers:
            container = self.page.locator(selector).first
            if container.count() > 0:
                print(f"[green]Using scroll container: {selector}[/green]")
                return container.element_handle()
        
        print("[red]No scroll container found[/red]")
        return None
    
    def perform_scroll_step(self, scroll_element) -> None:
        """Performs a single scroll step."""
        self.scroll_position += self.scroll_step
        self.page.evaluate(f"(el) => el.scrollTo(0, {self.scroll_position})", scroll_element)
        
        # Also try scrolling the inner scaffold content
        try:
            inner_scroll = self.page.locator(".scaffold-finite-scroll__content").first
            if inner_scroll.count() > 0:
                self.page.evaluate(f"(el) => el.scrollTo(0, {self.scroll_position})", inner_scroll.element_handle())
        except:
            pass
        
        self.page.wait_for_timeout(800)
    
    def get_current_metrics(self, scroll_element) -> dict:
        """Gets current scrolling and content metrics."""
        return {
            'profile_count': self.page.locator("a[href*='/in/']").count(),
            'scroll_height': self.page.evaluate("(el) => el.scrollHeight", scroll_element),
            'scroll_top': self.page.evaluate("(el) => el.scrollTop", scroll_element)
        }
    
    def update_termination_counters(self, metrics: dict) -> None:
        """Updates counters used for termination conditions."""
        current_profile_count = metrics['profile_count']
        current_scroll_height = metrics['scroll_height']
        current_scroll_top = metrics['scroll_top']
        
        # Profile count tracking
        if current_profile_count == self.last_profile_count:
            self.profiles_unchanged_count += 1
            print(f"[yellow]Profiles unchanged for {self.profiles_unchanged_count} checks[/yellow]")
        else:
            self.profiles_unchanged_count = 0
            print(f"[green]Found {current_profile_count - self.last_profile_count} new profiles![/green]")
        
        # Scroll height tracking
        if current_scroll_height == self.last_scroll_height:
            self.scroll_height_unchanged_count += 1
            print(f"[yellow]Scroll height unchanged for {self.scroll_height_unchanged_count} checks[/yellow]")
        else:
            self.scroll_height_unchanged_count = 0
        
        # Scroll position tracking
        if abs(current_scroll_top - self.last_scroll_position) < 10:
            self.scroll_position_stuck_count += 1
            print(f"[yellow]Scroll position stuck for {self.scroll_position_stuck_count} checks[/yellow]")
        else:
            self.scroll_position_stuck_count = 0
        
        # Update last known values
        self.last_profile_count = current_profile_count
        self.last_scroll_height = current_scroll_height
        self.last_scroll_position = current_scroll_top
    
    def should_terminate(self) -> tuple[bool, str]:
        """Checks if we should terminate scrolling. Returns (should_stop, reason)."""
        if self.profiles_unchanged_count >= self.max_profiles_unchanged:
            return True, f"No new profiles found for {self.profiles_unchanged_count} consecutive checks"
        
        if self.scroll_height_unchanged_count >= self.max_scroll_height_unchanged:
            return True, f"Scroll height unchanged for {self.scroll_height_unchanged_count} consecutive checks"
        
        if self.scroll_position_stuck_count >= self.max_scroll_position_stuck:
            return True, f"Cannot scroll further for {self.scroll_position_stuck_count} consecutive checks"
        
        if self.consecutive_failed_recoveries >= self.max_consecutive_failed_recoveries:
            return True, f"Content appears fully loaded ({self.consecutive_failed_recoveries} consecutive failed recoveries)"
        
        return False, ""
    
    def should_attempt_recovery(self) -> bool:
        """Determines if we should attempt a recovery scroll."""
        return (
            (self.profiles_unchanged_count >= 2 or self.scroll_height_unchanged_count >= 2) and
            self.consecutive_failed_recoveries < self.max_consecutive_failed_recoveries
        )
    
    def attempt_recovery(self, scroll_element) -> bool:
        """Attempts recovery by scrolling to bottom. Returns True if successful."""
        self.recovery_attempts += 1
        print(f"[blue]Recovery attempt #{self.recovery_attempts} (consecutive failures: {self.consecutive_failed_recoveries})...[/blue]")
        
        # Store current metrics
        pre_recovery_metrics = self.get_current_metrics(scroll_element)
        
        # Perform recovery scroll
        self.page.evaluate("(el) => el.scrollTo(0, el.scrollHeight)", scroll_element)
        self.page.wait_for_timeout(2000)
        
        # Check if recovery worked
        post_recovery_metrics = self.get_current_metrics(scroll_element)
        
        recovery_successful = (
            post_recovery_metrics['profile_count'] > pre_recovery_metrics['profile_count'] or
            post_recovery_metrics['scroll_height'] > pre_recovery_metrics['scroll_height']
        )
        
        if recovery_successful:
            self.total_successful_recoveries += 1
            self.consecutive_failed_recoveries = 0
            new_profiles = post_recovery_metrics['profile_count'] - pre_recovery_metrics['profile_count']
            print(f"[green]Recovery #{self.recovery_attempts} successful! Found {new_profiles} new profiles (total successful: {self.total_successful_recoveries})[/green]")
            
            # Reset stagnation counters
            self.profiles_unchanged_count = 0
            self.scroll_height_unchanged_count = 0
            self.scroll_position_stuck_count = 0
        else:
            self.consecutive_failed_recoveries += 1
            print(f"[yellow]Recovery #{self.recovery_attempts} failed (consecutive failures: {self.consecutive_failed_recoveries}/{self.max_consecutive_failed_recoveries})[/yellow]")
        
        # Update scroll position
        self.scroll_position = self.page.evaluate("(el) => el.scrollTop", scroll_element)
        return recovery_successful
    
    def collect_profile_urls(self) -> list[str]:
        """Collects and normalizes all profile URLs from the page."""
        print("[blue]Collecting all profile links...[/blue]")
        self.page.wait_for_timeout(2000)
        
        final_count = self.page.locator("a[href*='/in/']").count()
        print(f"[blue]Final profile count in DOM: {final_count}[/blue]")
        
        anchors = self.page.locator("a[href*='/in/']")
        hrefs = anchors.evaluate_all("nodes => nodes.map(n => n.href)")
        
        for href in hrefs:
            if href and '/in/' in href:
                norm = normalize_linkedin_profile_url(href)
                if norm and norm not in self.profile_urls:
                    self.profile_urls.add(norm)

        return list(self.profile_urls)
    
    def debug_if_low_collection(self) -> None:
        """Provides debug info if we collected fewer profiles than expected."""
        if len(self.profile_urls) < 50:
            print("[yellow]Collected fewer profiles than expected. Debug info:[/yellow]")
            try:
                buttons = self.page.locator("button").all()
                for button in buttons[:10]:
                    text = button.text_content() or ""
                    if any(word in text.lower() for word in ['more', 'load', 'show', 'view']):
                        print(f"[yellow]Found button: '{text}'[/yellow]")
            except:
                pass
    
    def perform_intelligent_scroll(self, scroll_element, max_scrolls: int = 200) -> None:
        """Main scrolling loop with intelligent termination."""
        print("[blue]Starting intelligent scroll with multiple termination conditions...[/blue]")
        iteration = 0
        
        while iteration < max_scrolls:
            iteration += 1
            
            # Perform scroll step
            self.perform_scroll_step(scroll_element)
            
            # Check conditions periodically
            if iteration % self.check_interval == 0:
                metrics = self.get_current_metrics(scroll_element)
                print(f"[blue]Iteration {iteration}: Profiles: {metrics['profile_count']}, ScrollHeight: {metrics['scroll_height']}px, ScrollTop: {metrics['scroll_top']}px[/blue]")
                
                # Only start checking conditions after grace period
                if iteration > self.grace_period_iterations:
                    self.update_termination_counters(metrics)
                    
                    # Check if we should terminate
                    should_stop, reason = self.should_terminate()
                    if should_stop:
                        print(f"[green]Terminating: {reason}[/green]")
                        print(f"[blue]Final stats: {self.recovery_attempts} total recovery attempts, {self.total_successful_recoveries} successful[/blue]")
                        break
                    
                    # Attempt recovery if needed
                    if self.should_attempt_recovery():
                        self.attempt_recovery(scroll_element)
            
            # Safety valve near iteration limit
            if iteration == max_scrolls - 10:
                print("[blue]Near iteration limit, making final attempt to load remaining content...[/blue]")
                self.page.evaluate("(el) => el.scrollTo(0, el.scrollHeight)", scroll_element)
                self.page.wait_for_timeout(3000)
        
        print(f"[blue]Scroll completed after {iteration} iterations[/blue]")


    def extract_reactors_from_post(self, post_url: str, max_scrolls: int = 200) -> list[str]:
        """
        Extracts reactor profile URLs from a LinkedIn post.
        
        Args:
            post_url: URL of the LinkedIn post
            max_scrolls: Maximum number of scroll iterations
        
        Returns:
            List of normalized LinkedIn profile URLs
        """
        
        # Step 1: Open post and click reactions
        if not self.open_post_and_click_reactions(post_url):
            return []
        
        # Step 2: Click 'All' reactions tab
        self.click_all_reactions_tab()
        
        # Step 3: Find scroll container
        scroll_element = self.find_scroll_container()
        if not scroll_element:
            return []
        
        # Step 4: Perform intelligent scrolling
        self.perform_intelligent_scroll(scroll_element, max_scrolls)
        
        # Step 5: Collect profile URLs
        profile_urls = self.collect_profile_urls()

        for p in profile_urls:
            profile_to_queue = Queue(PROFILE=p,
                                     CREATED_AT=datetime.now())
            profile_to_queue.add(self.db_client)
            print(f"[gray] found profile {p} [/gray]")
        
        print(f"[green]Total unique profiles collected: {len(profile_urls)}[/green]")
        return profile_urls
    
    def gather_reactions(self, max_age=7):
        try:
            posts = Post.get_unscanned_by_max_age(self.db_client, max_age)
            if not posts or len(posts) <=0:
                print("[yellow]No posts found to scan[/yellow]")
                return
            for i, p in enumerate(posts):
                p.scanned_count += 1
                p.last_scanned_at = datetime.now()
                p.add(self.db_client)
                self.extract_reactors_from_post(p.url)

                # Only sleep if this is not the last post
                if i < len(posts) - 1:
                    sleep_time = random.randint(self.INTER_POST_SLEEP_MIN_THRESHOLD, 
                                        self.INTER_POST_SLEEP_MAX_THRESHOLD)
                    print(f"[gray] Sleeping for {sleep_time} seconds [/gray]")
                    sleep(sleep_time)
        except Exception as e:
            print(f"[red]Error in gather_reactions: {e}[/red]")
            return


