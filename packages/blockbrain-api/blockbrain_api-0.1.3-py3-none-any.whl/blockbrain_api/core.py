import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests


class BlockBrainCore:
    """Core BlockBrain API functionality with low-level API methods."""

    def __init__(
        self,
        base_url: str = "https://blocky.theblockbrain.ai",
        token: Optional[str] = None,
        tenant_domain: Optional[str] = None,
        enable_logging: bool = False,
        log_level: str = "INFO",
    ):
        self.base_url = base_url
        self.token = token
        self.tenant_domain = tenant_domain
        self.session = requests.Session()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        if enable_logging:
            self.logger.setLevel(getattr(logging, log_level.upper()))

            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            # Disable logging by setting to CRITICAL level and adding a null handler
            self.logger.setLevel(logging.CRITICAL + 1)
            if not self.logger.handlers:
                self.logger.addHandler(logging.NullHandler())

        if token:
            headers = {"authorization": f"Bearer {token}", "Content-Type": "application/json"}

            # Add tenant-specific Referer header if provided
            if tenant_domain:
                headers["Referer"] = f"https://{tenant_domain}.kb.theblockbrain.ai/"
                if enable_logging:
                    self.logger.info(f"Using tenant domain: {tenant_domain}")

            self.session.headers.update(headers)
            if enable_logging:
                self.logger.info("BlockBrain API client initialized with token")
        else:
            if enable_logging:
                self.logger.warning("BlockBrain API client initialized without token")

    def set_token(self, token: str) -> None:
        self.token = token
        self.session.headers.update({"authorization": f"Bearer {token}"})
        if hasattr(self, "logger") and self.logger.level <= logging.INFO:
            self.logger.info("Token updated successfully")

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with logging and error handling."""
        self.logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"Response status: {response.status_code}")

            if response.status_code >= 400:
                self.logger.error(f"HTTP error {response.status_code}: {response.text}")
            else:
                self.logger.info(f"Request successful: {method} {url}")

            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def _parse_response(self, response: requests.Response, stream: bool = False) -> Union[str, Dict[str, Any], Any]:
        """Parse response content based on response type and streaming mode."""
        if response.status_code >= 400:
            # For errors, return structured error info
            try:
                error_content = response.json()
            except:
                error_content = response.text
            return {"error": True, "status_code": response.status_code, "content": error_content}

        # Handle streaming responses
        if stream and "text/event-stream" in response.headers.get("content-type", ""):
            return self._parse_stream_response(response)

        # Handle regular responses
        try:
            return response.json()
        except:
            return response.text

    def _parse_stream_response(self, response: requests.Response) -> str:
        """Parse Server-Sent Events (SSE) from streaming response."""
        content = ""
        try:
            current_event = None
            for line in response.iter_lines(decode_unicode=True):
                # Track the current event type
                if line.startswith("event: "):
                    current_event = line[7:].strip()
                    continue

                if line.startswith("data: "):
                    data_part = line[6:]  # Remove 'data: ' prefix
                    if data_part.strip() == "[DONE]":
                        break

                    # Only process new_token events for assistant responses
                    if current_event == "new_token":
                        try:
                            # Try to parse as JSON and extract content
                            data = json.loads(data_part)
                            if isinstance(data, dict) and data.get("role") == "assistant":
                                # Extract the token content
                                chunk_content = data.get("token", "")
                                if chunk_content:
                                    content += chunk_content
                        except json.JSONDecodeError:
                            # If not JSON, skip
                            pass
        except Exception as e:
            self.logger.error(f"Error parsing stream response: {e}")
            return response.text

        return content

    def user_prompt(
        self,
        content: str,
        session_id: str,
        convo_id: str,
        message_type: str = "user-question",
        action_type: str = "user",
        message_id: Optional[str] = None,
        selected_strategy: Optional[str] = None,
        selected_action: Optional[str] = None,
        agent_task_id: Optional[str] = None,
        target_text: Optional[str] = None,
        message_ids: Optional[list] = None,
        target_full_content: Optional[str] = None,
        model: Optional[str] = None,
        files: Optional[list] = None,
        stream: bool = True,
    ) -> Union[str, Dict[str, Any]]:
        url = f"{self.base_url}/cortex/completions/v2/user-input"

        payload = {
            "content": content,
            "actionType": action_type,
            "messageType": message_type,
            "sessionId": session_id,
            "convoId": convo_id,
        }

        # Add optional parameters if provided
        if message_id:
            payload["messageId"] = message_id
        if selected_strategy:
            payload["selectedStrategy"] = selected_strategy
        if selected_action:
            payload["selectedAction"] = selected_action
        if agent_task_id:
            payload["agentTaskId"] = agent_task_id
        if target_text:
            payload["targetText"] = target_text
        if message_ids:
            payload["messageIds"] = message_ids
        if target_full_content:
            payload["targetFullContent"] = target_full_content
        if model:
            payload["model"] = model
        if files:
            payload["files"] = files

        headers = self.session.headers.copy()
        if stream:
            headers["Accept"] = "text/event-stream"

        response = self._make_request("POST", url, json=payload, headers=headers)
        return self._parse_response(response, stream=stream)

    def create_data_room(
        self,
        convo_name: str,
        session_id: str,
        bot_id: str,
        default_language: str = "English",
        is_default_convo_name: bool = True,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/cortex/active-bot/{bot_id}/convo"

        payload = {
            "convoName": convo_name,
            "sessionId": session_id,
            "defaultLanguage": default_language,
            "isDefaultConvoName": is_default_convo_name,
        }

        response = self._make_request("POST", url, json=payload)
        result = self._parse_response(response)

        # If model is specified and data room was created successfully, set the model
        if model and isinstance(result, dict) and not result.get("error"):
            # Extract conversation ID from response
            convo_id = (
                result.get("id")
                or result.get("convoId")
                or result.get("dataRoomId")
                or result.get("body", {}).get("dataRoomId")
                or result.get("body", {}).get("_id")
            )

            if convo_id:
                try:
                    model_response = self.change_data_room_model(convo_id, model)
                    if isinstance(model_response, dict) and model_response.get("error"):
                        self.logger.warning(f"Failed to set model {model} for data room {convo_id}: {model_response}")
                except Exception as e:
                    self.logger.warning(f"Failed to set model {model} for data room {convo_id}: {e}")

        return result

    def upload_file(self, file_path: Union[str, Path], convo_id: str, session_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/cortex/conversation/{convo_id}/attachment"

        file_path = Path(file_path)

        with open(file_path, "rb") as file:
            files = {"attachment": (file_path.name, file, "application/octet-stream")}
            data = {"session_id": session_id}

            headers = {key: value for key, value in self.session.headers.items() if key.lower() != "content-type"}

            response = requests.post(url, files=files, data=data, headers=headers)
            return self._parse_response(response)

    def add_context(self, convo_id: str, context: str) -> Dict[str, Any]:
        url = f"{self.base_url}/cortex/conversation/{convo_id}/context"

        payload = {"convoId": convo_id, "context": context}

        response = self._make_request("PUT", url, json=payload)
        return self._parse_response(response)

    def change_model(
        self,
        convo_id: str,
        model: Optional[str] = None,
        name: Optional[str] = None,
        knowledge_base: Optional[list] = None,
        enable_auto_response: Optional[bool] = None,
        knowledge_base_destination_insight: Optional[list] = None,
        enable_web_search: Optional[bool] = None,
        web_search_type: Optional[str] = None,
        web_search_config: Optional[dict] = None,
        enable_reranker: Optional[bool] = None,
        enable_agent_retrieval: Optional[bool] = None,
        enable_generate_image: Optional[bool] = None,
        length_preset: Optional[str] = None,
        chat_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/cortex/conversation/{convo_id}"

        payload = {}

        # Add optional parameters if provided
        if model:
            payload["model"] = model
        if name:
            payload["name"] = name
        if knowledge_base:
            payload["knowledgeBase"] = knowledge_base
        if enable_auto_response is not None:
            payload["enableAutoResponse"] = enable_auto_response
        if knowledge_base_destination_insight:
            payload["knowledgeBaseDestinationInsight"] = knowledge_base_destination_insight
        if enable_web_search is not None:
            payload["enableWebSearch"] = enable_web_search
        if web_search_type:
            payload["webSearchType"] = web_search_type
        if web_search_config:
            payload["webSearchConfig"] = web_search_config
        if enable_reranker is not None:
            payload["enableReranker"] = enable_reranker
        if enable_agent_retrieval is not None:
            payload["enableAgentRetrieval"] = enable_agent_retrieval
        if enable_generate_image is not None:
            payload["enableGenerateImage"] = enable_generate_image
        if length_preset:
            payload["lengthPreset"] = length_preset
        if chat_mode:
            payload["chatMode"] = chat_mode

        response = self._make_request("PATCH", url, json=payload)
        return self._parse_response(response)

    def delete_data_room(self, convo_id: str) -> Dict[str, Any]:
        """Delete a data room/conversation."""
        url = f"{self.base_url}/cortex/conversation/{convo_id}"
        response = self._make_request("DELETE", url)
        return self._parse_response(response)

    def check_file_upload_status(self, convo_id: str) -> Dict[str, Any]:
        """Check the status of uploaded files in a conversation."""
        url = f"{self.base_url}/cortex/conversation/{convo_id}/attachment"
        response = self._make_request("GET", url)
        return self._parse_response(response)

    def wait_for_file_processing(
        self, convo_id: str, timeout: int = 300, poll_interval: int = 5
    ) -> Union[str, Dict[str, Any]]:
        """Wait for file processing to complete."""
        import time

        start_time = time.time()

        self.logger.info(f"Waiting for file processing in conversation {convo_id}")

        while time.time() - start_time < timeout:
            try:
                status_response = self.check_file_upload_status(convo_id)

                if isinstance(status_response, dict) and status_response.get("error"):
                    return {
                        "success": False,
                        "error": f"Failed to check upload status: {status_response.get('status_code', 'unknown')}",
                        "response": status_response,
                    }

                files = status_response.get("body", []) if isinstance(status_response, dict) else []

                if not files:
                    return {"success": False, "error": "No files found in conversation"}

                # Check all files status
                all_processed = True
                files_status = []

                for file_info in files:
                    status = file_info.get("status", "UNKNOWN")
                    calculated_status = file_info.get("calculatedStatus", "UNKNOWN")
                    file_name = file_info.get("name", "Unknown")

                    files_status.append(
                        {
                            "name": file_name,
                            "status": status,
                            "calculatedStatus": calculated_status,
                            "processed": status != "IN_PROGRESS",
                        }
                    )

                    if status == "IN_PROGRESS":
                        all_processed = False

                if all_processed:
                    self.logger.info(f"All files processed successfully in {time.time() - start_time:.1f}s")
                    return {"success": True, "files": files_status, "processing_time": time.time() - start_time}

                # Still processing, wait and check again
                self.logger.debug(f"Files still processing, waiting {poll_interval}s...")
                time.sleep(poll_interval)

            except Exception as e:
                self.logger.error(f"Error checking file status: {e}")
                return {"success": False, "error": str(e)}

        # Timeout reached
        return {
            "success": False,
            "error": f"Timeout reached ({timeout}s) waiting for file processing",
            "files": files_status if "files_status" in locals() else [],
        }

    def continue_chat(
        self, question: str, convo_id: str, session_id: Optional[str] = None, stream: bool = True
    ) -> Union[str, Dict[str, Any]]:
        """Continue an existing chat conversation."""
        if not session_id:
            import uuid

            session_id = str(uuid.uuid4())
        return self.user_prompt(question, session_id, convo_id, stream=stream)

    def list_data_rooms(
        self, bot_id: Optional[str] = None, session_id: Optional[str] = None, page: int = 1, size: int = 999
    ) -> Dict[str, Any]:
        """List all data rooms/conversations for a bot."""
        if not bot_id:
            raise ValueError("bot_id is required for listing data rooms")

        url = f"{self.base_url}/cortex/active-bot/{bot_id}/convo"

        params = {
            "bot_id": bot_id,
            "page": page,
            "size": size,
            "key": "",
        }

        if session_id:
            params["session_id"] = session_id

        response = self._make_request("GET", url, params=params)
        return self._parse_response(response)

    def get_data_room(self, convo_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a specific data room/conversation."""
        url = f"{self.base_url}/cortex/conversation/{convo_id}"

        params = {}
        if session_id:
            params["session_id"] = session_id

        response = self._make_request("GET", url, params=params)
        return self._parse_response(response)

    def get_conversation(self, convo_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation details (alias for get_data_room)."""
        return self.get_data_room(convo_id, session_id)

    def get_upload_status(self, convo_id: str) -> Dict[str, Any]:
        """Get upload status (alias for check_file_upload_status)."""
        return self.check_file_upload_status(convo_id)

    def get_available_models(self) -> Dict[str, Any]:
        """Get all available LLM models."""
        url = f"{self.base_url}/llm_model_usage"
        response = self._make_request("GET", url)
        return self._parse_response(response)

    def change_data_room_model(self, convo_id: str, model: str) -> Dict[str, Any]:
        """Change the model for a specific data room/conversation."""
        return self.change_model(convo_id, model=model)
