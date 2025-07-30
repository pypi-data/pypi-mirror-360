import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from rich import print

SESSION_FILE = os.path.expanduser("~/.linkiq/session.json")


class LIHandler:
    _instance = None

    LI_URL = "https://www.linkedin.com"
    LI_SESSION_TEST_URL = "https://www.linkedin.com/feed/"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LIHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        
        self.playwright = sync_playwright().start()
        self._browser_context_map = {}
        for headless in [True, False]:
            browser = self.playwright.chromium.launch(headless=headless)
            context = browser.new_context()
            self._browser_context_map[headless] = (browser, context)
        
        self._ensure_session()
        self._initialized = True

    def _ensure_session(self):
        """Check if a valid session exists, otherwise initiate login"""
        if not os.path.exists(SESSION_FILE) or not self._is_session_valid():
            print("[yellow]No valid session found. Please log in.[/yellow]")
            self._login_and_save_session()
        else:
            print("[green]Valid session found.[/green]")

    def _is_session_valid(self):
        """Simple session validation based on URL redirection"""
        try:
            headless = False
            page = self.get_page(headless=headless)            
            print(f"[yellow]Validating login by visiting {self.LI_SESSION_TEST_URL} [/yellow]")
            page.goto(self.LI_SESSION_TEST_URL, wait_until='domcontentloaded', timeout=15000)

            # check the page url post loading
            current_url = page.url
            is_logged_in = '/login' not in current_url and '/uas/login' not in current_url
            print(f"[green] Session valid check: logged_in {is_logged_in} based on URL: {current_url}[/green]")
            page.close()
            return is_logged_in
        except Exception as e:
            print(f"[yellow]Session validation failed: {e}[/yellow]")
            return False

    def _login_and_save_session(self):
        try:
            headless = False
            browser, context = self._browser_context_map[headless]
            page = context.new_page()
            page.goto(self.LI_URL)
            
            input("[green]Log in to LinkedIn and press Enter here when done...[/green]")
            
            # Verify login was successful by checking if we can access the feed
            
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=10000)
           
            # Check if we're still redirected to login
            if '/login' in page.url or '/uas/login' in page.url:
                raise Exception("Login verification failed - please ensure you're logged in")
            
            self._save_session_cookies(context)
            print("[green]Session saved successfully.[/green]")
            page.close()
        except Exception as e:
            print(f"[red]Error during login: {e}[/red]")
            raise
            
    def _save_session_cookies(self, context):
        try:
            cookies = context.cookies()
            session_dir = os.path.dirname(SESSION_FILE)
            Path(session_dir).mkdir(parents=True, exist_ok=True)
            with open(SESSION_FILE, "w") as f:
                json.dump(cookies, f, indent=2)
        except Exception as e:
            print(f"[red]Error saving session cookies: {e}[/red]")
            raise

    def _load_session_cookies(self, context):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    cookies = json.load(f)
                    if cookies:  # Only add cookies if the list is not empty
                        context.add_cookies(cookies)
            except (json.JSONDecodeError, Exception) as e:
                print(f"[yellow]Error loading session cookies: {e}[/yellow]")
                # Continue without cookies if there's an error
    
    def get_page(self, headless=False):
        browser, context = self._browser_context_map[headless]
        self._load_session_cookies(context)
        return context.new_page()

    def stop(self):
        for headless, (browser, context) in self._browser_context_map.items():
            context.close()
            browser.close()
        self._browser_context_map = {}
        if hasattr(self, 'playwright'):
            self.playwright.stop()
