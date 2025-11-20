# app/scenarios/pubsub.py

"""
Test Scenario: Publish/Subscribe

Verifies the functionality of the Pub/Sub messaging system:
- SUBSCRIBE: Subscribes to a channel.
- PUBLISH: Posts a message to a channel.
- Message Reception: Checks if the subscriber receives the message correctly.

The goal is to ensure that the basic message passing mechanism works as expected.
"""

import time

def run(client) -> dict:
    """
    Executes the Pub/Sub test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "pubsub"
    channel = f"{scenario_name}_channel"
    message = "test_message"
    
    try:
        pubsub = client.pubsub(ignore_subscribe_messages=False)
        pubsub.subscribe(channel)
        
        # Wait for the subscription confirmation message, with a longer timeout
        confirmation = pubsub.get_message(timeout=3.0)
        if confirmation is None or confirmation['type'] != 'subscribe':
            pubsub.close()
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "Failed to receive subscription confirmation within 3 seconds."
            }
        
        # Add a brief pause to ensure subscription is processed server-side
        time.sleep(0.05)

        # Publish the message
        num_subscribers = client.publish(channel, message)
        
        # If we are subscribed, we expect at least one subscriber.
        if num_subscribers == 0:
            pubsub.unsubscribe(channel)
            pubsub.close()
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "PUBLISH reported 0 subscribers even after subscription confirmation."
            }

        # Check for the received message (the actual content)
        received_message = pubsub.get_message(timeout=3.0)
        
        pubsub.unsubscribe(channel)
        pubsub.close()

        if received_message is None:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "Subscriber did not receive a message within 3 seconds."
            }
            
        if received_message['data'].decode() != message:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"Received message content incorrect. Got: '{received_message['data'].decode()}', Expected: '{message}'"
            }

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "Message published and received successfully."
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
    finally:
        # Ensure cleanup
        if 'pubsub' in locals() and pubsub.connection:
            pubsub.close()
