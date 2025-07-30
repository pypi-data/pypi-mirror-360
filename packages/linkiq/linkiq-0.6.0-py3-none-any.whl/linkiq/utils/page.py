import random
import time
from playwright.sync_api import Page  # if you're using sync API

def random_scroll(page: Page):
    """
    Simulates random human-like scrolling behavior on a page.
    Scrolls up and down randomly, then ensures we hit the bottom once.
    """
    # Get page dimensions
    page_height = page.evaluate("() => document.body.scrollHeight")
    viewport_height = page.evaluate("() => window.innerHeight")
    
    num_scrolls = random.randint(3, 8)
    current_position = 0

    for _ in range(num_scrolls):
        scroll_direction = random.choice(['up', 'down'])
        scroll_distance = random.randint(200, 800)

        if scroll_direction == 'down':
            target_position = min(current_position + scroll_distance, page_height - viewport_height)
        else:
            target_position = max(current_position - scroll_distance, 0)

        # Use JS arrow function syntax to allow dynamic interpolation
        page.evaluate(f"""() => window.scrollTo({{top: {target_position}, behavior: 'smooth'}})""")
        current_position = target_position
        time.sleep(random.uniform(0.5, 2.0))

    # Scroll to bottom at the end
    page.evaluate("""() => window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})""")
    time.sleep(random.uniform(5.0, 10.0))
