"""
Test script for the RateLimitClient to fetch rate limit information and update drawing usage.
This script runs both standard and IAP authentication tests sequentially.
"""

import os
import asyncio
from botrun_flow_lang.utils.clients.rate_limit_client import RateLimitClient


async def test_get_rate_limit_without_iap():
    """Test the get_rate_limit method without IAP authentication."""
    print("\n=== Setting up get_rate_limit test without IAP ===")
    # Set environment variables for standard authentication
    os.environ["BOTRUN_BACK_API_BASE"] = "https://dev.botrun.ai/api"
    os.environ.pop("IAP_CLIENT_ID", None)  # Remove if exists
    os.environ.pop("IAP_SERVICE_ACCOUNT_KEY_FILE", None)  # Remove if exists

    print(f"API Base: {os.environ.get('BOTRUN_BACK_API_BASE')}")
    print(f"IAP Client ID: {os.environ.get('IAP_CLIENT_ID', 'Not Set')}")
    print(
        f"IAP Service Account Key File: {os.environ.get('IAP_SERVICE_ACCOUNT_KEY_FILE', 'Not Set')}"
    )

    # Initialize the client
    client = RateLimitClient()

    try:
        # Get rate limit information for a user
        username = "sebastian.hsu@gmail.com"
        rate_limit_info = await client.get_rate_limit(username)

        print(f"\nRate limit information for {username}:")
        print(rate_limit_info)
        print("\nTest get_rate_limit without IAP completed successfully.")
    except ValueError as e:
        print(f"\nError in non-IAP get_rate_limit test: {e}")


async def test_get_rate_limit_with_iap():
    """Test the get_rate_limit method with IAP authentication."""
    print("\n=== Setting up get_rate_limit test with IAP ===")
    # Set environment variables for IAP authentication
    os.environ["BOTRUN_BACK_API_BASE"] = "https://tryai.nat.gov.tw/lab32/api"
    os.environ["IAP_CLIENT_ID"] = (
        "693845073420-sr08ejqcg309nai4hpq5ga9qi5j4mcvv.apps.googleusercontent.com"
    )
    os.environ["IAP_SERVICE_ACCOUNT_KEY_FILE"] = "./keys/ailab-436501-8d3dc0f2a103.json"

    print(f"API Base: {os.environ.get('BOTRUN_BACK_API_BASE')}")
    print(f"IAP Client ID: {os.environ.get('IAP_CLIENT_ID', 'Not Set')[:20]}...")
    print(
        f"IAP Service Account Key File: {os.environ.get('IAP_SERVICE_ACCOUNT_KEY_FILE', 'Not Set')}"
    )

    # Initialize the client
    client = RateLimitClient()

    try:
        # Get rate limit information for a user
        username = "sebastian.hsu@gmail.com"
        rate_limit_info = await client.get_rate_limit(username)

        print(f"\nRate limit information for {username}:")
        print(rate_limit_info)
        print("\nTest get_rate_limit with IAP completed successfully.")
    except ValueError as e:
        print(f"\nError in IAP get_rate_limit test: {e}")


async def test_update_drawing_usage_without_iap():
    """Test the update_drawing_usage method without IAP authentication."""
    print("\n=== Setting up update_drawing_usage test without IAP ===")
    # Set environment variables for standard authentication
    os.environ["BOTRUN_BACK_API_BASE"] = "https://dev.botrun.ai/api"
    os.environ.pop("IAP_CLIENT_ID", None)  # Remove if exists
    os.environ.pop("IAP_SERVICE_ACCOUNT_KEY_FILE", None)  # Remove if exists

    print(f"API Base: {os.environ.get('BOTRUN_BACK_API_BASE')}")
    print(f"IAP Client ID: {os.environ.get('IAP_CLIENT_ID', 'Not Set')}")
    print(
        f"IAP Service Account Key File: {os.environ.get('IAP_SERVICE_ACCOUNT_KEY_FILE', 'Not Set')}"
    )

    # Initialize the client
    client = RateLimitClient()

    try:
        # Update drawing usage for a user
        username = "sebastian.hsu@gmail.com"
        update_result = await client.update_drawing_usage(username)

        print(f"\nDrawing usage update result for {username}:")
        print(update_result)
        print("\nTest update_drawing_usage without IAP completed successfully.")
    except ValueError as e:
        print(f"\nError in non-IAP update_drawing_usage test: {e}")


async def test_update_drawing_usage_with_iap():
    """Test the update_drawing_usage method with IAP authentication."""
    print("\n=== Setting up update_drawing_usage test with IAP ===")
    # Set environment variables for IAP authentication
    os.environ["BOTRUN_BACK_API_BASE"] = "https://tryai.nat.gov.tw/lab32/api"
    os.environ["IAP_CLIENT_ID"] = (
        "693845073420-sr08ejqcg309nai4hpq5ga9qi5j4mcvv.apps.googleusercontent.com"
    )
    os.environ["IAP_SERVICE_ACCOUNT_KEY_FILE"] = "./keys/ailab-436501-8d3dc0f2a103.json"

    print(f"API Base: {os.environ.get('BOTRUN_BACK_API_BASE')}")
    print(f"IAP Client ID: {os.environ.get('IAP_CLIENT_ID', 'Not Set')[:20]}...")
    print(
        f"IAP Service Account Key File: {os.environ.get('IAP_SERVICE_ACCOUNT_KEY_FILE', 'Not Set')}"
    )

    # Initialize the client
    client = RateLimitClient()

    try:
        # Update drawing usage for a user
        username = "sebastian.hsu@gmail.com"
        update_result = await client.update_drawing_usage(username)

        print(f"\nDrawing usage update result for {username}:")
        print(update_result)
        print("\nTest update_drawing_usage with IAP completed successfully.")
    except ValueError as e:
        print(f"\nError in IAP update_drawing_usage test: {e}")


async def test_user_not_found():
    """Test error handling when user is not found."""
    print("\n=== Setting up user not found test ===")
    os.environ["BOTRUN_BACK_API_BASE"] = "https://tryai.nat.gov.tw/lab32/api"

    # Initialize the client
    client = RateLimitClient()

    try:
        # Try to update drawing usage for a non-existent user
        username = "nonexistent.user@example.com"
        update_result = await client.update_drawing_usage(username)
        print("\nUnexpected success for non-existent user!")
    except ValueError as e:
        print(f"\nExpected error for non-existent user: {e}")
        print("\nTest user not found completed successfully.")


async def main():
    """Run all test cases sequentially."""
    print("Starting RateLimitClient tests...")

    # Test get_rate_limit without IAP
    await test_get_rate_limit_without_iap()

    # Test get_rate_limit with IAP
    await test_get_rate_limit_with_iap()

    # Test update_drawing_usage without IAP
    # 先 comment 掉，怕用完
    # await test_update_drawing_usage_without_iap()

    # Test update_drawing_usage with IAP
    # 先 comment 掉，怕用完
    # await test_update_drawing_usage_with_iap()

    # Test get_rate_limit without IAP
    await test_get_rate_limit_without_iap()

    # Test get_rate_limit with IAP
    await test_get_rate_limit_with_iap()

    # Test error handling for non-existent user
    # await test_user_not_found()

    print("\nAll tests completed.")


if __name__ == "__main__":
    asyncio.run(main())
