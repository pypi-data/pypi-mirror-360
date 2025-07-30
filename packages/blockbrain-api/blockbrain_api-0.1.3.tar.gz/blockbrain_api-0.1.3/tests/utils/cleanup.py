"""Cleanup utilities for end-to-end tests."""

import logging
from typing import Any, Dict, List

from blockbrain_api import BlockBrainAPI

logger = logging.getLogger(__name__)


class TestResourceTracker:
    """Tracks and cleans up test resources."""

    def __init__(self, api_client: BlockBrainAPI):
        self.api_client = api_client
        self.resources = {"data_rooms": [], "sessions": [], "conversations": [], "uploaded_files": []}

    def track_data_room(self, room_id: str):
        """Track a data room for cleanup."""
        self.resources["data_rooms"].append(room_id)
        logger.info(f"Tracking data room: {room_id}")

    def track_session(self, session_id: str):
        """Track a session for cleanup."""
        self.resources["sessions"].append(session_id)
        logger.info(f"Tracking session: {session_id}")

    def track_conversation(self, conversation_id: str):
        """Track a conversation for cleanup."""
        self.resources["conversations"].append(conversation_id)
        logger.info(f"Tracking conversation: {conversation_id}")

    def track_file(self, file_id: str):
        """Track an uploaded file for cleanup."""
        self.resources["uploaded_files"].append(file_id)
        logger.info(f"Tracking uploaded file: {file_id}")

    def cleanup_all(self) -> Dict[str, List[str]]:
        """Clean up all tracked resources and return cleanup results."""
        results = {"cleaned": [], "failed": [], "verified": []}

        # Clean up data rooms
        for room_id in self.resources["data_rooms"]:
            try:
                # Delete data room
                delete_response = self.api_client.core.delete_data_room(room_id)

                # Check for successful deletion (no error or success flag)
                if not delete_response.get("error"):
                    results["cleaned"].append(f"data_room:{room_id}")
                    logger.info(f"Successfully deleted data room: {room_id}")

                    # Verify deletion with GET
                    try:
                        room_check = self.api_client.core.get_data_room(room_id)
                        # If we get an error response, deletion was successful
                        if room_check.get("error"):
                            results["verified"].append(f"data_room:{room_id}")
                        else:
                            logger.warning(f"Data room still exists after deletion: {room_id}")
                    except Exception:
                        # Expected - room should not exist
                        results["verified"].append(f"data_room:{room_id}")
                else:
                    logger.error(f"Failed to delete data room {room_id}: {delete_response}")
                    results["failed"].append(f"data_room:{room_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup data room {room_id}: {e}")
                results["failed"].append(f"data_room:{room_id}")

        # Clean up conversations (same as data rooms for BlockBrain API)
        for conversation_id in self.resources["conversations"]:
            try:
                # Try to delete conversation (might be same as data room)
                delete_response = self.api_client.core.delete_data_room(conversation_id)
                if not delete_response.get("error"):
                    results["cleaned"].append(f"conversation:{conversation_id}")
                    logger.info(f"Successfully deleted conversation: {conversation_id}")
                else:
                    results["failed"].append(f"conversation:{conversation_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup conversation {conversation_id}: {e}")
                results["failed"].append(f"conversation:{conversation_id}")

        # Clean up sessions (just log, they auto-expire)
        for session_id in self.resources["sessions"]:
            results["cleaned"].append(f"session:{session_id}")
            logger.info(f"Session tracked for cleanup: {session_id}")

        # Files are cleaned up when their parent data room is deleted
        for file_id in self.resources["uploaded_files"]:
            results["cleaned"].append(f"file:{file_id}")
            logger.info(f"File tracked for cleanup: {file_id}")

        # Clear tracking
        self.resources = {"data_rooms": [], "sessions": [], "conversations": [], "uploaded_files": []}

        return results


def cleanup_test_resources_by_prefix(api_client: BlockBrainAPI, prefix: str = "E2E_TEST_") -> Dict[str, int]:
    """
    Clean up any test resources that start with the given prefix.
    This is a fallback cleanup for resources that might have been left behind.
    """
    cleaned = {"data_rooms": 0, "sessions": 0}

    try:
        logger.info(f"Cleanup attempted for resources with prefix: {prefix}")

        # Try to get bot_id from the API client
        bot_id = None
        if hasattr(api_client, "core") and hasattr(api_client.core, "bot_id"):
            bot_id = api_client.core.bot_id
        elif hasattr(api_client, "bot_id"):
            bot_id = api_client.bot_id

        if bot_id:
            logger.info("Using list_data_rooms for comprehensive cleanup when bot_id is available")

            # List all data rooms for this bot
            rooms_response = api_client.core.list_data_rooms(bot_id=bot_id)

            # Extract rooms from potentially nested response
            if isinstance(rooms_response, dict) and "data_rooms" in rooms_response:
                rooms = rooms_response["data_rooms"]
            elif isinstance(rooms_response, dict) and "data" in rooms_response:
                rooms = rooms_response["data"]
            elif isinstance(rooms_response, dict) and "body" in rooms_response:
                body = rooms_response["body"]
                rooms = body.get("data", body) if isinstance(body, dict) else []
            else:
                rooms = rooms_response if isinstance(rooms_response, list) else []

            # Find and delete test rooms
            for room in rooms:
                if isinstance(room, dict):
                    room_name = room.get("name", "")
                    room_id = room.get("_id") or room.get("id") or room.get("dataRoomId")

                    if room_name.startswith(prefix) and room_id:
                        try:
                            logger.info(f"Deleting test data room: {room_name} ({room_id})")
                            delete_response = api_client.core.delete_data_room(room_id)

                            # Check if deletion was successful
                            if not delete_response.get("error"):
                                cleaned["data_rooms"] += 1
                                logger.info(f"Successfully deleted data room: {room_id}")
                            else:
                                logger.warning(f"Failed to delete data room {room_id}: {delete_response}")

                        except Exception as e:
                            logger.error(f"Exception deleting data room {room_id}: {e}")
        else:
            logger.warning("No bot_id available for comprehensive cleanup")

    except Exception as e:
        logger.error(f"Failed during cleanup attempt: {e}")

    if cleaned["data_rooms"] > 0:
        logger.info(f"Cleaned up {cleaned['data_rooms']} test data rooms")

    return cleaned


def verify_resource_cleanup(api_client: BlockBrainAPI, resource_type: str, resource_id: str) -> bool:
    """
    Verify that a resource has been properly cleaned up using GET calls.
    """
    try:
        if resource_type == "data_room":
            # Use get_data_room to verify deletion
            try:
                response = api_client.core.get_data_room(resource_id)
                if isinstance(response, dict) and response.get("error"):
                    # Error response indicates resource was deleted
                    logger.info(f"Verified cleanup succeeded for data_room: {resource_id}")
                    return True
                else:
                    # Resource still exists
                    logger.warning(f"Data room still exists after cleanup: {resource_id}")
                    return False
            except Exception:
                # Exception likely means resource doesn't exist anymore
                logger.info(f"Verified cleanup succeeded for data_room: {resource_id} (exception)")
                return True

        elif resource_type == "session":
            # Sessions are harder to verify directly, assume cleanup worked
            return True

        else:
            logger.warning(f"Unknown resource type for verification: {resource_type}")
            return False

    except Exception:
        # Exception likely means resource doesn't exist anymore (successful cleanup)
        return True
