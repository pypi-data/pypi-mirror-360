import time
from time import sleep
import random
from rich import print
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from linkiq.model.db_client import DBClient
from linkiq.model.lead import Lead
from linkiq.controller.campaign_handler import CampaignHandler
from typing import Optional
import re

class LIMessageHandler():
    
    INTER_MESSAGE_DELAY_MIN = 30
    INTER_MESSAGE_DELAY_MAX = 120

    def __init__(self, db_client: DBClient, page):
        self.db_client = db_client
        self.page = page

    def try_click_button(self, label_patterns, root=None, click=True):
        """
        Try clicking a button whose aria-label or visible text matches any pattern.
        If `root` is provided, search is scoped to that root (e.g., a modal).
        For connect/message buttons, only search within the specific profile container.
        Handles dropdown menus by clicking "More" button if needed.
        """
        if root:
            containers = [root]
        else:
            # Very specific container path to avoid clicking wrong profile buttons
            main_section = self.page.locator("main section[class*='artdeco-card']")
            ph5_div = main_section.locator("div.ph5.pb5")
            containers = [
                ph5_div,
                ph5_div.locator("div[class*='entry-point']"),
                ph5_div.locator("div[class*='artdeco-dropdown']"),
            ]
        
        for container in containers:
            try:
                if container.count() == 0:
                    continue
            except Exception:
                continue
            
            # First try to find button in visible content
            if self._try_find_button_in_container(container, label_patterns, click):
                return True
            
            # If button not found and this is a dropdown container, try expanding it
            if "artdeco-dropdown" in str(container):
                if self._try_dropdown_expansion(container, label_patterns, click):
                    return True
        
        print(f"[red]No button matching patterns {label_patterns} found.[/red]")
        return False

    def _try_find_button_in_container(self, container, label_patterns, click=True):
        """
        Unified method to search for buttons in a container.
        Searches both role='button' elements and <button> elements.
        Matches against both aria-label and visible text.
        
        Args:
            container: The container element to search within
            label_patterns: List of regex patterns to match against
            click: Whether to click the button when found (default: True)
        
        Returns:
            bool: True if a matching button was found (and clicked if requested), False otherwise
        """
        # Define selectors to try - covers both role='button' and <button> elements
        selectors = [
            "[role='button'][aria-label]",  # Role-based buttons with aria-label
            "[role='button']",              # All role-based buttons
            "button[aria-label]",           # HTML buttons with aria-label
            "button"                        # All HTML buttons
        ]
        
        for pattern in label_patterns:
            for selector in selectors:
                try:
                    buttons = container.locator(selector)
                    button_count = buttons.count()
                    
                    for i in range(button_count):
                        button = buttons.nth(i)
                        
                        try:
                            # Check visibility first to avoid unnecessary processing
                            if not button.is_visible():
                                continue
                            
                            # Get aria-label if available
                            aria_label = button.get_attribute("aria-label") or ""
                            
                            # Get visible text, handling potential errors
                            try:
                                text = button.inner_text().strip()
                            except Exception:
                                text = ""
                            
                            # Print debug info
                            display_text = aria_label if aria_label else text
                            print(f"Button '{display_text}' found with visibility {button.is_visible()}")
                            
                            # Check aria-label match first (if present)
                            if aria_label and re.search(pattern, aria_label, re.IGNORECASE):
                                print(f"[white]Found button matching aria-label: '{aria_label}' [/white]")
                                if click:
                                    button.click()
                                return True
                            
                            # Check visible text match (if aria-label didn't match or wasn't present)
                            if text and re.search(pattern, text, re.IGNORECASE):
                                print(f"[white]Found button matching visible text: '{text}' [/white]")
                                if click:
                                    button.click()
                                return True
                                    
                        except Exception as button_e:
                            print(f"[yellow]Skipping button at index {i} in selector '{selector}' due to error: {button_e}[/yellow]")
                            continue
                            
                except Exception as selector_e:
                    print(f"[red]Exception with selector '{selector}' and pattern '{pattern}': {selector_e}[/red]")
                    continue
        
        return False

    def _try_find_button_in_container_old(self, container, label_patterns, click):
        """Helper method to search for buttons in a container"""
        for pattern in label_patterns:
            # Try aria-label match first
            try:
                buttons = container.locator("[role='button'][aria-label]")
                for i in range(buttons.count()):
                    button = buttons.nth(i)
                    aria_label = button.get_attribute("aria-label") or ""
                    print(f"{aria_label} button found with visibility {button.is_visible()}")
                    if button.is_visible() and re.search(pattern, aria_label, re.IGNORECASE):
                        print(f"[white] Found button matching aria-label: '{aria_label}' [/white]")
                        if click:
                            button.click()
                        return True
            except Exception as e:
                print(f"Exception during aria-label match: {e}")

            # Try visible text match
            try:
                buttons = container.locator("[role='button']")
                for i in range(buttons.count()):
                    button = buttons.nth(i)
                    text = button.inner_text().strip()
                    print(f"{text} button found with visibility {button.is_visible()}")
                    if button.is_visible() and re.search(pattern, text, re.IGNORECASE):
                        print(f"[white] Found button matching visible text: '{text}' [/white]")
                        if click:
                            button.click()
                        return True
            except Exception as e:
                print(f"Exception during visible text match: {e}")
        
        return False

    def _try_find_html_button_in_container(self, container, label_patterns, click=True):
        return self._try_find_button_in_container(container, label_patterns, click)
        """
        # Search for explicit <button> elements in a container based on aria-label or inner text.
        for pattern in label_patterns:
            # Match buttons by aria-label
            try:
                buttons = container.locator("button[aria-label]")
                for i in range(buttons.count()):
                    button = buttons.nth(i)
                    aria_label = button.get_attribute("aria-label") or ""
                    visible = button.is_visible()
                    print(f"Button with aria-label='{aria_label}' found (visible={visible})")
                    if visible and re.search(pattern, aria_label, re.IGNORECASE):
                        print(f"[white]Matched button via aria-label: '{aria_label}'[/white]")
                        if click:
                            button.click()
                        return True
            except Exception as e:
                print(f"[red]Exception while matching aria-label: {e}[/red]")

            # Match buttons by visible inner text
            try:
                buttons = container.locator("button")
                for i in range(buttons.count()):
                    button = buttons.nth(i)
                    try:
                        text = button.inner_text().strip()
                        visible = button.is_visible()
                        print(f"Button with text='{text}' found (visible={visible})")
                        if visible and re.search(pattern, text, re.IGNORECASE):
                            print(f"[white]Matched button via text: '{text}'[/white]")
                            if click:
                                button.click()
                            return True
                    except Exception as inner_e:
                        print(f"[yellow]Skipping button at index {i} due to error: {inner_e}[/yellow]")
            except Exception as e:
                print(f"[red]Exception while matching visible text: {e}[/red]")

        return False
        """


    def _try_dropdown_expansion(self, container, label_patterns, click):
        """Helper method to handle dropdown expansion and search"""
        try:
            # Look for "More" button to expand dropdown
            more_button = container.locator("button:has-text('More')")
            if more_button.count() > 0 and more_button.is_visible():
                print("[cyan]Clicking More button to expand dropdown...[/cyan]")
                more_button.click()
                
                # Wait for dropdown to expand
                time.sleep(1)
                
                # Try to find button in dropdown content
                dropdown_content = container.locator("div.artdeco-dropdown__content-inner")
                if dropdown_content.count() > 0:
                    print("[cyan]Searching in expanded dropdown content...[/cyan]")
                    return self._try_find_button_in_container(dropdown_content, label_patterns, click)
                else:
                    # If no specific dropdown content div, search the whole container again
                    print("[cyan]Searching in original dropdown container...[/cyan]")
                    return self._try_find_button_in_container(container, label_patterns, click)
        
        except Exception as e:
            print(f"[yellow]Error in dropdown expansion: {e}[/yellow]")
        
        return False

    def send_connect_message(self, connect_message):
        """Handle connect button click and send connection request with message"""
        if not connect_message:
            print("[red]No connect message provided. Skipping connect...[/red]")
            return None
        
        try:
            modal_container = self.page.locator("div[data-test-modal-id='send-invite-modal']")
            modal_container.wait_for(state="visible", timeout=5000)
            
            # Look for "Add a note" button in artdeco-modal__actionbar
            actionbar = modal_container.locator("div.artdeco-modal__actionbar")
            
            add_note_patterns = [r'Add a note']
            time.sleep(5)
            if self._try_find_html_button_in_container(actionbar, add_note_patterns):
        
                print("[cyan]Add a note clicked, filling message...[/cyan]")
                time.sleep(5)  # Wait for textarea to appear
                
                # Fill the textarea[name="message"]
                textarea = modal_container.locator("textarea[name='message']")
                textarea.wait_for(state="visible", timeout=3000)
                textarea.type(connect_message, delay=30)
                print("[green]Connect message typedd.[/green]")
                print("[yellow]Sleeping 5s before pressing Enter to allow visual check...[/yellow]")
                time.sleep(5)
            else:
                print("[yellow]Add a note button not found - sending default connect[/yellow]")
            
            # Click Send button in actionbar
            send_patterns = [r'^Send']
            if self._try_find_html_button_in_container(actionbar, send_patterns):
                print("[green]Connection request sent successfully![/green]")
                return "CONNECTION_REQUEST_SENT"
            else:
                print("[red]Send button not found[/red]")
                return None
                
        except Exception as e:
            print(f"[red]Error in connect flow: {e}[/red]")
            return None


    def send_first_message(self, first_message, subject_line=""):
        """Send a LinkedIn direct message after the message UI is open."""
        if not first_message:
            print("[red]No first message provided. Skipping message...[/red]")
            return None

        try:
            print("[cyan]Waiting for message textbox to appear...[/cyan]")

            # Locate the editable message input box
            message_box = self.page.locator("div.msg-form__contenteditable[contenteditable='true'][role='textbox']").first
            message_box.wait_for(state="visible", timeout=5000)

            print("[green]Message box found. Typing message...[/green]")
            message_box.fill("")  # Optional: clear existing content
            message_box.type(first_message, delay=20)  # Slow typing for debug visibility

            print("[yellow]Sleeping 5s before pressing Enter to allow visual check...[/yellow]")
            time.sleep(5)

            print("[green]Sending message...[/green]")
            message_box.press("Enter")

            print("[bold green]First message sent![/bold green]")
            return "FIRST_MESSAGE_SENT"

        except Exception as e:
            print(f"[red]Error sending message: {e}[/red]")
            return None



    def send_message(self, profile_url, connect_message, first_message, subject_line="") -> Optional[str]:    
        """Main function to handle sending messages or connection requests"""
        print(f"\n[bold yellow]Processing: {profile_url}[/bold yellow]")

        try:
            self.page.goto(profile_url, wait_until="load", timeout=60000)
            time.sleep(3)  # Allow UI elements to load completely
            connect_patterns = [r'^Connect', r'^Invite']
            message_patterns = [r'^Message']
            pending_patterns = [r'^Pending']
        
            # Check if connection is already pending
            if self.try_click_button(pending_patterns, click=False):
                print("[yellow]Connection request is pending. Skipping...[/yellow]")
                return None
            elif self.try_click_button(connect_patterns):
                print("[cyan]Processing connection request...[/cyan]")
                time.sleep(5)  # Wait for modal to appear
                return self.send_connect_message(connect_message)
            elif self.try_click_button(message_patterns):
                print("[cyan]Processing message...[/cyan]")
                time.sleep(5)  # Wait for modal to appear
                return self.send_first_message(first_message, subject_line)
            else:
                print("[red]No connect or message button found[/red]")
                return None
        except Exception as e:
            print(f"[bold red]Error with {profile_url}: {e}[/bold red]")
            return None
    
    def process_leads(self, max_connect_request, max_first_message):
        # gather leads that need message outreach
        # from campaign manager get the message to send
        # send the message and appropriately update the lead status
        try:
            for stage, limit in [("CREATED", max_connect_request), ("CONNECTION_REQUEST_SENT", max_first_message)]:
                # there is no limit to sending message just connect requests
                print(f"[white] Getting leads at {stage}. max limit: {limit}[/white]")
                leads = Lead.get_leads_for_outreach(self.db_client, [stage], limit=limit)
                if not leads:
                    print(f"[yellow] No leads found for outreach [/yellow]")
                ch = CampaignHandler()
                for i, lead in enumerate(leads):
                    campaign_name = lead.campaign_name
                    profile = lead.profile
                    campaign = ch.get_by_name(campaign_name)
                    if not campaign:
                        print(f"[red]Campaign {campaign_name} not found[/red]")
                        continue
                    connect_message = campaign.connect_message
                    first_message = campaign.first_message
                    subject_line = campaign.subject_line
                    if not connect_message and not first_message:
                        print(f"[red]No message found for campaign {campaign_name}[/red]")
                        continue
                    
                    print(f"[white] Sending {connect_message} or {first_message} to {profile} [/white]")
                    new_status = self.send_message(profile, connect_message, first_message, subject_line)
                    print(f"[white] New status: {new_status} [/white]")
                    if not new_status:
                        continue
                    lead.stage = new_status
                    lead.add(self.db_client)

                    # Only sleep if this is not the last lead
                    if i < len(leads) - 1:
                        sleep_time = random.randint(self.INTER_MESSAGE_DELAY_MIN,
                                            self.INTER_MESSAGE_DELAY_MAX)
                        print(f"[gray] Sleeping for {sleep_time} seconds [/gray]")
                        sleep(sleep_time)
        except Exception as e:
            print(f"[red]Error processing leads: {e}[/red]")
            return
           