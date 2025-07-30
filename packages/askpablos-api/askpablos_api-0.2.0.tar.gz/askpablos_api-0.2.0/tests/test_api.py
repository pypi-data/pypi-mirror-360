"""
Test suite for the AskPablos API client.

This file demonstrates how to use the AskPablos API client to make real requests.
Replace the placeholder credentials with your actual API keys to test.
"""

from askpablos_api import AskPablos


def test_basic_get_request():
    """Test basic GET request functionality."""
    print("Testing basic GET request...")

    # Initialize the client with your credentials
    client = AskPablos(
        api_key="SNXLjcXYG4RSCHA2uFPeMXaeyOTVTdhI",
        secret_key="485A4373B3452B7D27A2F25A45865"
    )

    # try:
        # Simple GET request
    for u in range(0, 1000):
        url = f"https://httpbin.org/ip?no={u}"
        print(url)
        # Fixed: Use browser=True when screenshot=True
        response = client.get(url, browser=False, screenshot=True, wait_for_load=True)
        print(response.elapsed_time, response.json.get('sid'))
        print('--' * 50)

            # with open('scc.png', "wb") as sc:
            #     sc.write(response.screenshot)
            #     print("-" * 50)
        # return True
    # except Exception as e:
    #     print(f"Test failed with exception: {e}")
    #     return False


test_basic_get_request()
