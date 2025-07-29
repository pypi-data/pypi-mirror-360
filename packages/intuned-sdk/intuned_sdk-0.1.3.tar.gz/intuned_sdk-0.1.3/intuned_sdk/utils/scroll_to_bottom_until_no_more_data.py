import asyncio
from typing import Callable

from playwright.async_api import Page, Locator

from .wait_for_network_idle import wait_for_network_idle


@wait_for_network_idle(max_inflight_requests=0, timeout=10)
async def scroll_by_amount(page: Page, scrollable_container: Locator | None, amount: int = 700):
    scrollable = scrollable_container if scrollable_container else page 
    if hasattr(scrollable, 'mouse'):
        await scrollable.mouse.wheel(0, amount)
    else:
        await scrollable.evaluate(f'element => element.scrollBy(0, {amount})')

async def get_scroll_position(scrollable: Page | Locator) -> tuple[float, float]:
    """Get current scroll position and total height."""
    current = await scrollable.evaluate("window.scrollY + window.innerHeight")
    total = await scrollable.evaluate("document.body.scrollHeight")
    return current, total

async def scroll_to_bottom_until_no_more_data(
    page: Page, 
    heartbeat: Callable[[], None] = lambda: None,
    *,
    scrollable_container: Locator | None = None, 
    max_scrolls: int = 1000,
    scroll_amount: int = 700,
    scroll_delay: float = 1.0,
    position_threshold: float = 5.0
):
    """
    Scroll to the bottom of a page or container until no more content can be loaded.
    
    Args:
        page: Playwright Page object
        heartbeat: Optional callback function to execute on each scroll
        scrollable_container: Optional scrollable container Locator
        max_scrolls: Maximum number of scroll attempts
        scroll_amount: Pixels to scroll each time
        scroll_delay: Delay between scrolls in seconds
        position_threshold: Threshold for considering bottom reached
    """
    scrollable = scrollable_container if scrollable_container else page
    
    for _ in range(max_scrolls):
        heartbeat()
        
        current_position, total_height = await get_scroll_position(scrollable)
        remaining_scroll = total_height - current_position

        if remaining_scroll <= 0:
            break

        await scroll_by_amount(page, scrollable, scroll_amount)
        await asyncio.sleep(scroll_delay)

        new_position, new_total_height = await get_scroll_position(scrollable)

        # Break if we've reached the bottom (allowing for small rounding differences)
        if (abs(new_position - new_total_height) < position_threshold and 
            new_total_height == total_height):
            break
