import os
import requests
import time
import logging
from .logger import setup_logger
from typing import Union, IO
import mimetypes

# from threading import Thread

# under the hood, requests uses urllib3, which raises the InsecureRequestWarning
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CIQ_HOST = "https://datahub.ninebit.in"


class NineBitCIQClient:
    """
    Client for interacting with the NineBit CIQ backend.

    Parameters:
        api_key (str): API key for authentication (sent in 'X-API-Key' header).
        log_level (int): Logging level (default logging.ERROR).
    """

    def __init__(self, api_key: str, base_url: str = CIQ_HOST, log_level=logging.INFO):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False  # TODO: SSL
        self.session.headers.update({"X-API-Key": api_key, "Content-Type": "application/json"})
        self.logger = setup_logger(log_level)

    def _trigger_workflow(self, workflow_data: dict):
        """
        Internal
        Trigger a workflow with given data, return workflow ID.
        """
        try:
            url = f"{self.base_url}/workflow-service/trigger_workflow"
            response = self.session.post(url, json=workflow_data, timeout=10)
            response.raise_for_status()
            return response.json().get("content")
        except requests.RequestException as e:
            self.logger.error(f"Error triggering workflow: {e}")
            raise

    def _get_workflow_status(self, wf_id: str):
        """
        Internal
        Check status and result of a workflow by its workflow ID.
        """
        try:
            url = f"{self.base_url}/workflow-service/rt/workflows/{wf_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error getting workflow status: {e}")
            raise

    def _wait_for_completion(self, wf_id: str, interval: int = 5, timeout: int = 300, callback=None):
        """
        Internal
        Polls workflow status until it completes or times out.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self._get_workflow_status(wf_id)
            content = status.get("content", {})
            state = content.get("status")
            self.logger.info(f"Workflow {wf_id} state: {state}")

            if state in ("completed", "success"):
                if callback:
                    callback(None, status.get("result"))
                    return  # don't return value if using callback
                return status.get("result")
            if state in ("failed", "error"):
                if callback:
                    callback(RuntimeError(f"Workflow {wf_id} failed: {status}"), None)
                    return  # don't return value if using callback
                else:
                    raise RuntimeError(f"Workflow {wf_id} failed: {status}")

            time.sleep(interval)

        if callback:
            callback(TimeoutError(f"Workflow {wf_id} timed out after {timeout} seconds."), None)
        raise TimeoutError(f"Workflow {wf_id} did not complete in {timeout} seconds.")

    def ingest_file(self, file: Union[str, IO[bytes]], associated_file_name=None, callback=None):
        """
        Reads and uploads a PDF or DOCX file to the backend for processing.

        Args:
            file (Union[str, IO[bytes]]):
                - Local file path as a string, or
                - File-like object (e.g., BytesIO) with file content.

        Returns:
            dict: Response from the backend.

        Raises:
            ValueError: If the input is invalid or unsupported.
            IOError: If the file cannot be read.
        """
        # Determine file name (only used for content type inference)
        if isinstance(file, str):
            filename = file
        elif hasattr(file, "name"):
            filename = file.name
        else:
            filename = associated_file_name or "unknown"

        # Infer content type if not explicitly provided
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"

        # Step 1: Get the pre-signed URL from the backend
        try:
            object_name = os.path.basename(filename)

            response = self.session.post(
                f"{self.base_url}/workflow-service/generate-presigned-url",
                json={"object_name": object_name, "content_type": content_type},
            )
            response.raise_for_status()
            presigned_url = response.json()["url"]
            self.logger.info("Presigned_url received")
            # self.logger.info(f"Presigned_url: {presigned_url}")
        except Exception as e:
            self.logger.error(f"Failed to get pre-signed URL: {e}")
            if callback:
                callback(e, None)
                return  # don't raise Error if using callback
            else:
                raise RuntimeError("Failed to get pre-signed URL")

        # Step 2: Upload the file to blob
        try:
            if isinstance(file, str):
                with open(file, "rb") as f:
                    data = f.read()
            else:
                file.seek(0)
                data = file.read()

            upload_response = requests.put(
                presigned_url, data=data, verify=False, headers={"Content-Type": content_type}  # TODO: SSL
            )

            if upload_response.status_code == 200:
                self.logger.info("File uploaded successfully.")
                # return True
            else:
                self.logger.error(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
                # return False

        except Exception as e:
            self.logger.error(f"File upload error: {e}")
            if callback:
                callback(e, None)
                return  # don't raise Error if using callback
            else:
                raise RuntimeError("File upload error")

        try:
            workspace = self.session.headers.get("X-API-Key")
            payload = {"workflow": "rag-consumer", "file_path": object_name, "workspace": workspace}
            wf_id = self._trigger_workflow(payload)

            self._wait_for_completion(wf_id=wf_id)

            if callback:
                callback(None, {"run_id": wf_id, "workspace": workspace})

        except Exception as e:
            self.logger.error(f"Trigger workflow error: {e}")

            if callback:
                callback(e, None)
                return  # don't raise Error if using callback
            else:
                raise RuntimeError("Trigger workflow error")

    def rag_query(self, query: str, euclidean_threshold=0.9, top_k=6, callback=None):
        """
        Performs a Retrieval-Augmented Generation (RAG) query using the provided input.

        Args:
            query (str): The user query string to retrieve relevant documents for.
            euclidean_threshold (float, optional): The distance threshold for filtering similar results.
                Lower values mean more strict similarity. Defaults to 0.9.
            top_k (int, optional): The maximum number of top documents to retrieve. Defaults to 6.
            callback (Callable, optional): A function to be called with the final result. Should accept
                two arguments: (error, result). If None, the function will return the result directly.

        Returns:
            Any: The final result if no callback is provided. Otherwise, returns None.

        Raises:
            ValueError: If the query is empty or invalid.
            RuntimeError: If retrieval or generation fails.
        """
        workspace = self.session.headers.get("X-API-Key")
        payload = {
            "workflow": "rag-query",
            "rag_query": query,
            "workspace": workspace,
            "euclidean_threshold": euclidean_threshold,
            "top_k": top_k,
        }

        try:
            wf_id = self._trigger_workflow(payload)
            response = self._wait_for_completion(wf_id=wf_id, callback=callback)
            self.logger.info("Success: rag_query")
            if callback:
                callback(None, response)
                return
            else:
                return response

        except Exception as ex:
            self.logger.error(f"Error: rag_query: {str(ex)}")
            if callback:
                callback(ex, None)
                return
            else:
                raise RuntimeError("Error: rag_query")
