"""
Video-related operations for the NomadicML SDK.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import time
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Union
import random
from typing_extensions import deprecated
from .client import NomadicML
from .types import (
    VideoSource, 
)
from .utils import (
    format_error_message, infer_source,
    get_file_mime_type, get_filename_from_path
)
from .exceptions import VideoUploadError, NomadicMLError, ValidationError

logger = logging.getLogger("nomadicml")
from pathlib import Path
from typing import Sequence, Union, List, Dict, Any, Optional, overload
# ──────────────────────────────────────────────────────────────────────────────
# Type aliases
# ──────────────────────────────────────────────────────────────────────────────
VideoInput   = Union[str, Path]           # paths or URLs/video IDs as str
VideoInputs  = Union[VideoInput, Sequence[VideoInput]]
VideoID      = str
VideoIDList  = Sequence[VideoID]

class AnalysisType(str, Enum):
    VIOLATION      = "violation"
    EDGE_CASE      = "edge_case"
    SEARCH         = "search"
    RAPID_REVIEW   = "rapid_review" 

class CustomCategory(str, Enum):
    DRIVING        = "driving"
    AERIAL         = "aerial"
    SECURITY       = "security"
    ENVIRONMENT  = "environment"

# Helper ----------------------------------------------------------------------

def _is_iterable(obj):
    """True for list / tuple / set but *not* for strings or Path."""
    return isinstance(obj, Sequence) and not isinstance(obj, (str, Path))


class VideoClient:
    """
    Client for video upload and analysis operations.
    
    This class extends the base NomadicML client with video-specific operations.
    
    Args:
        client: An initialized NomadicML client.
    """
    _status_ranks = {
        "NOT_STARTED": 0,
        "PREPARE_IN_PROGRESS": 0.5,
        "PREPARE_COMPLETED": 1,
        "UPLOADED": 1,
        "DETECTING_IN_PROGRESS": 1.5,
        "PROCESSING": 1.5,
        "DETECTING_COMPLETED": 2,
        "DETECTING_COMPLETED_NO_EVENTS": 2.1,
        "SUMMARIZING_IN_PROGRESS": 2.5,
        "SUMMARIZING_COMPLETED": 3,
        "COMPLETED": 3,
    }

    _BACKEND_SPLIT_SYMBOL = "-----------EVENT_DESCRIPTION-----------"
    _SEARCH_SPLIT_SYMBOL = "<SPLIT CHARACTER>"
    
    def __init__(self, client: NomadicML):
        """
        Initialize the video client with a NomadicML client.
        
        Args:
            client: An initialized NomadicML client.
        """
        self.client = client
        self._user_info = None

    def _print_status_bar(
        self,
        item_id: str,
        *,
        status: str | None = None,
        percent: float | None = None,
        width: int = 30,
    ) -> None:
        """
        Log a tidy ASCII progress-bar.

        Parameters
        ----------
        item_id : str
            Identifier shown in the log line (video_id, sweep_id, …).
        status : str | None
            Human-readable stage label ("UPLOADED", "PROCESSING"…).  
            Ignored when an explicit `percent` is supplied.
        percent : float | None
            0 – 100 exact progress.  If omitted, the method falls back to the
            coarse-grained stage → rank mapping stored in ``self._status_ranks``.
        width : int
            Total bar characters (default 30).
        """
        # ── compute percentage ────────────────────────────────────────────────
        if percent is None:
            # coarse mode: derive % from status → rank table
            rank = self._status_ranks.get((status or "").upper(), 0)
            max_rank = max(self._status_ranks.values()) or 1
            percent = (rank / max_rank) * 100

        # clamp & build bar
        percent = max(0, min(percent, 100))
        filled  = int(percent / 100 * width)
        bar     = "[" + "=" * filled + " " * (width - filled) + "]"

        # choose label
        label = f"{percent:3.0f}%" if status is None else status.upper()

        logger.info(f"{item_id}: {bar} {label}")
            
    async def _get_auth_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the authenticated user information.
        
        Returns:
            A dictionary with user information if available, None otherwise.
        """
        if self.user_info:
            return self.user_info
            
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify",
            )
            
            self.user_info = response.json()
            return self.user_info
        except Exception as e:
            logger.warning(f"Failed to get authenticated user info: {e}")
            return None

    def _get_api_events(self, analysis_json: Dict[str, Any]):
        """Return the list of events from either the new or legacy payload."""
        events = (
            analysis_json.get("metadata", {})
                        .get("visual_analysis", {})
                        .get("events")
        )
        if events is not None:
            return events
        return (
            analysis_json
            .get("events", {})
            .get("visual_analysis", {})
            .get("status", {})
            .get("quick_summary", {})
            .get("events")
        )

    def _parse_api_events(self, analysis_json):
            """
            Parse the API analysis JSON into a list of event dictionaries.
            
            Args:
                analysis_json: The raw JSON dict returned from the API.
                default_duration: Default duration (in seconds) to assume if an event only has a single time point.
                
            Returns:
                list: List of events dictionaries with label, start_time, and end_time
            """
            results = []
            
            # Debug: Print top-level keys to help understand structure
            logger.debug(f"Parsing API events. Top-level keys: {list(analysis_json.keys())}")
            
            # Try different possible paths for events
            events_list = self._get_api_events(analysis_json)

            if not events_list:
                logger.debug("events list empty in API response")
                return results
                
            # Process each event
            for event in events_list:
                # We'll treat 'description' as the label.
                label = event.get("description", "Unknown")
                
                # Print event structure for debugging
                logger.debug(f"Processing event: {label}")
                
                # Try to extract start and end time information
                start_time = None
                end_time = None
            
                if "time" in event:
                    time_str = event.get("time", "")
                    match = re.search(r"t=(\d+(\.\d+)?)", time_str)
                    if match:
                        start_time = float(match.group(1))
                    
                if "end_time" in event:
                    end_time_str = event.get("end_time", "")
                    match = re.search(r"t=(\d+(\.\d+)?)", end_time_str)
                    if match:
                        end_time = float(match.group(1))
                        
                
                # Check for refined_events if present
                used_refined_events = False
                refined = event.get("refined_events", "")
                if refined:
                    try:
                        refined_data = json.loads(refined)  # Expecting a list of intervals like [start, end, text]
                        if isinstance(refined_data, list):
                            for item in refined_data:
                                if isinstance(item, list) and len(item) >= 2:
                                    st = float(item[0])
                                    en = float(item[1])
                                    results.append({
                                        "label": label,
                                        "start_time": st,
                                        "end_time": en
                                    })
                                    used_refined_events = True
                                    logger.debug(f"  Added refined event: {label} from {st}s to {en}s")
                    except json.JSONDecodeError:
                        logger.warning(f"  Failed to parse refined_events JSON: {refined[:50]}...")
                        pass

                # If no refined intervals and we found basic timing, use that
                if not used_refined_events and start_time is not None and end_time is not None:
                    results.append({
                        "label": label,
                        "start_time": start_time,
                        "end_time": end_time
                    })
                    logger.debug(f"  Added event: {label} from {start_time}s to {end_time}s")
            
            logger.info(f"Total events extracted: {len(results)}")
            return results
    
    def _parse_upload_response(self, video_id: str, payload: Dict[str, Any]) -> Dict[str, str]:
        """Return the compact {{video_id, status}} dict expected by callers."""
        status = (payload.get("status")
                or payload.get("visual_analysis", {})
                        .get("status", {})
                        .get("status", "unknown"))
        return {"video_id": video_id, "status": str(status).lower()}

    
    def get_user_id(self) -> Optional[str]:
        """
        Get the authenticated user ID.
        
        Returns:
            The user ID if available, None otherwise.
        """
        # Try to get cached user info
        if self._user_info and "user_id" in self._user_info:
            return self._user_info["user_id"]
        
        # Make a synchronous request to get user info
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify"
            )
            self._user_info = response.json()
            return self._user_info.get("user_id")
        except Exception as e:
            logger.warning(f"Failed to get user ID: {str(e)}")
            return None
    
    def _custom_event_detection(
        self,
        video_id: str,
        custom_category: CustomCategory | str,
        event_description: str
    ) -> Dict[str, Any]:
        """
        Ask the backend to derive structured events for ``video_id`` by asking a specific question.
        Mirrors the frontend's call to POST /ask-question with prompt_type="rapid_review".

        Args:
            video_id: The ID of the video.
            custom_category: The category enum or string value, used to form the prompt.
            event_description: The description of the event, used to form the prompt.

        Returns:
            A dictionary with the backend's response.
            
        Raises:
            NomadicMLError: If the request fails.
        """
        if not event_description:
            raise ValueError("event_description cannot be empty for analysis type rapid_review.")
        if not custom_category:
            raise ValueError("custom_category cannot be empty for analysis type rapid_review.")
        
        # Extract the string value whether it's an enum or string
        category_value = custom_category.value if isinstance(custom_category, CustomCategory) else custom_category
        prompt = f"{category_value}{self._BACKEND_SPLIT_SYMBOL}{event_description}"

        payload = {
            "question": prompt,
            "prompt_type": "rapid_review",
            "video_id": video_id,
        }

        resp = self.client._make_request("POST", "/api/ask-question", data=payload)
        if not 200 <= resp.status_code < 300:
            error_msg = resp.json() if resp.content else "Unknown error"
            raise NomadicMLError(f"Failed to generate events via /ask-question: {format_error_message(error_msg)}")
        return resp.json()
    
    ###### UPLOAD#######################################################################
    @overload
    def upload(self, videos: VideoInput, /, *,
                edge_case_category: str | None = None,
                folder: str | None = None,
                upload_timeout: int = 1_200,
                wait_for_uploaded: bool = True
                ) -> Dict[str, Any]: ...

    @overload
    def upload(self, videos: Sequence[VideoInput], /, *,
                edge_case_category: str | None = None,
                folder: str | None = None,
                upload_timeout: int = 1_200,
                wait_for_uploaded: bool = True
                ) -> List[Dict[str, Any]]: ...

    def upload(self, videos: VideoInputs, /, *,
                edge_case_category: str | None = None,
                folder: str | None = None,
                upload_timeout: int = 1_200,
                wait_for_uploaded: bool = True,
                **_):  # swallow unknown kwargs for forward compat
    # noqa: E701 – keep signature readable
        """Upload one or many videos from local paths or URLs.

        Parameters
        ----------
        videos            : a single string/``Path`` or a sequence thereof, or URLs
        edge_case_category: if supplied, routes through `upload_video_edge`
        upload_timeout    : seconds to wait in `_wait_for_uploaded`
        wait_for_uploaded : block until backend reports "UPLOADED"
        """
        if _is_iterable(videos):
            paths = list(videos)
            if not paths:
                raise ValueError("No paths provided")
            return self._upload_many(
                paths,
                edge_case_category,
                upload_timeout,
                wait_for_uploaded,
                folder,
            )
        return self._upload_single(
            videos,
            edge_case_category,
            upload_timeout,
            wait_for_uploaded,
            folder,
        )

    #  ── helpers ──────────────────────────────────────────────────────
    def _upload_single(
        self,
        video: VideoInput,
        edge_case_category: str | None,
        timeout: int,
        wait: bool,
        folder: str | None = None,
    ) -> Dict[str, Any]:
        """Delegate to low‑level helper plus optional wait."""
        if edge_case_category:
            res = self._upload_video_edge(
                file_path=str(video),
                category=edge_case_category,
                folder=folder,
            )
        else:
            res = self._upload_video(file_path=str(video), folder=folder)

        vid = res["video_id"]

        if wait:
            self._wait_for_uploaded(vid, timeout=timeout)
            res = self.get_video_status(vid)   # refreshed payload

        return self._parse_upload_response(vid, res)
    

    def _upload_many(self, videos: List[VideoInput],
                    edge_case_category: str | None,
                    timeout: int,
                    wait: bool,
                    folder: str | None = None) -> List[Dict[str, Any]]:
        """Parallel uploader with basic type checking.

        Raises **TypeError** if any item in *videos* is not a ``str`` or ``Path``.
        This helps catch accidental mistakes like ``[Path(...), True]`` where a
        bool sneaks into the list when the caller meant to pass a keyword arg.
        """
        for v in videos:
            if not isinstance(v, (str, Path)):
                raise TypeError(
                    "upload(videos=…) expects paths or strings – got %r of type %s" %
                    (v, type(v).__name__))

        with ThreadPoolExecutor(max_workers=len(videos)) as exe:
            futs = [
                exe.submit(
                    self._upload_single,
                    v,
                    edge_case_category,
                    timeout,
                    wait,
                    folder,
                )
                for v in videos
            ]
            return [f.result() for f in futs]  # preserves input order

    ####################################### #ANALYZE #################


    #Single Video decorato
    @overload
    def analyze(self, ids: VideoID, /, *,
                analysis_type: AnalysisType = AnalysisType.VIOLATION,
                model_id: str = "Nomadic-VL-XLarge",
                timeout: int = 2_400,
                wait_for_completion: bool = True,
                folder: str | None = None,
                search_query: str | None = None,
                custom_event: str | None = None,
                custom_category: CustomCategory | str | None = None,
                edge_case_category: str | None = None,
                concept_ids: List[str] | None = None,
                mode: str = "assistant",
                return_subset: bool = False
                ) -> Dict[str, Any]: ...
    
    #Batch Analyze decorator
    @overload
    def analyze(self, ids: VideoIDList, /, *,
                analysis_type: AnalysisType = AnalysisType.VIOLATION,
                model_id: str = "Nomadic-VL-XLarge",
                timeout: int = 2_400,
                wait_for_completion: bool = True,
                folder: str | None = None,
                search_query: str | None = None,
                custom_event: str | None = None,
                custom_category: CustomCategory | str | None = None,
                edge_case_category: str | None = None,
                concept_ids: List[str] | None = None,
                mode: str = "assistant",
                return_subset: bool = False
                ) -> List[Dict[str, Any]]: ...

    def analyze(self, ids: Union[VideoID, VideoIDList, None] = None, /, *,
                analysis_type: AnalysisType = AnalysisType.VIOLATION,
                model_id: str = "Nomadic-VL-XLarge",
                timeout: int = 2_400,
                wait_for_completion: bool = True,
                folder: str | None = None,
                search_query: str | None = None,
                custom_event: str | None = None,
                custom_category: CustomCategory | str | None = None,
                edge_case_category: str | None = None,
                concept_ids: List[str] | None = None,
                mode: str = "assistant",
                return_subset: bool = False,
                **_):
        """Trigger analysis for one or many video IDs with explicit type."""
        if ids is None and folder is None:
            raise ValueError("Must provide either ids or folder")
        
        if folder and ids is not None:
            raise ValueError("Provide either ids or folder, not both")

        if folder:
            vids_info = self.my_videos(folder_id=folder)
            ids = [v["video_id"] for v in vids_info]
            if not ids:
                raise ValueError(f"No videos found in folder '{folder}'")

        # vector dispatch
        if _is_iterable(ids):
            vids = list(ids)
            if not vids:
                raise ValueError("No video_ids provided")
            return self._analyze_many(vids, analysis_type, model_id,
                                      timeout, wait_for_completion,
                                      search_query, custom_event,
                                      custom_category, edge_case_category,
                                      concept_ids, mode, return_subset)
        return self._analyze_single(ids, analysis_type, model_id,
                                    timeout, wait_for_completion,
                                    search_query, custom_event,
                                    custom_category, edge_case_category,
                                    concept_ids, mode, return_subset)

    #  ── analyze helpers ──────────────────────────────────────────────
    def _validate_kwargs(self, analysis_type: AnalysisType | str, *,
                         search_query: str | None,
                         custom_event: str | None,
                         edge_case_category: str | None,
                         custom_category: CustomCategory | str | None):
        """Ensure required kwargs are provided for each analysis type."""
        if analysis_type is None or analysis_type not in [cat.value for cat in AnalysisType]:
            valid_values = ", ".join([f"'{cat.value}'" for cat in AnalysisType])
            raise ValueError(f"analysis_type must be one of {valid_values}")        

        if search_query and analysis_type is not AnalysisType.SEARCH:
            raise ValueError("search_query is only allowed when analysis_type='search'")
        if custom_event and analysis_type is not AnalysisType.RAPID_REVIEW:
            raise ValueError("custom_event is only allowed when analysis_type='rapid_review'")
        if edge_case_category and analysis_type is not AnalysisType.EDGE_CASE:
            raise ValueError("edge_case_category is only allowed when analysis_type='edge_case'")
        if custom_category and analysis_type is not AnalysisType.RAPID_REVIEW:
            raise ValueError("custom_category is only allowed when analysis_type='rapid_review'")

        if analysis_type is AnalysisType.SEARCH and not search_query:
            raise ValueError("search_query is required when analysis_type='search'")
        if analysis_type is AnalysisType.RAPID_REVIEW and not custom_event:
            raise ValueError("custom_event is required when analysis_type='rapid_review'")
        if analysis_type is AnalysisType.EDGE_CASE and not edge_case_category:
            raise ValueError("edge_case_category is required when analysis_type='edge_case'")
        if custom_category is not None and custom_category not in [cat.value for cat in CustomCategory]:
            valid_values = ", ".join([f"'{cat.value}'" for cat in CustomCategory])
            raise ValueError(f"custom_category must be one of {valid_values}")

    def _analyze_single(self,
                    video_id: str,
                    analysis_type: AnalysisType | str,
                    model_id: str,
                    timeout: int,
                    wait_for_completion: bool,
                    search_query: str | None = None,
                    custom_event: str | None = None,
                    custom_category: CustomCategory | str | None = None,
                    edge_case_category: str | None = None,
                    concept_ids: list[str] | None = None,
                    mode: str = "assistant",
                    return_subset: bool = True) -> dict:
        """Run ONE analysis job and hand back a compact dict."""

        # 1) sanity-check combo of flags
        self._validate_kwargs(analysis_type,
                        search_query=search_query,
                        custom_event=custom_event,
                        edge_case_category=edge_case_category,
                        custom_category=custom_category)

        # 2) dispatch by AnalysisType
        if analysis_type is AnalysisType.SEARCH:
            sweep = self.search_events(video_id, search_query, model_id=model_id,
                                    timeout=timeout)
            return {
                "video_id": video_id,
                "mode":     "search",
                "status":   "completed",
                "hits":     sweep.get("hits", []),
            }

        if analysis_type is AnalysisType.RAPID_REVIEW:
            events = self._custom_event_detection(
                video_id=video_id,
                custom_category=custom_category,
                event_description=custom_event,
            )
            return {
                "video_id": video_id,
                "mode":     "rapid_review",
                "status":   "completed",
                "events":   events,
            }

        # EDGE_CASE or VIOLATION share flow
        if analysis_type is AnalysisType.EDGE_CASE:
            self.analyze_video_edge(video_id=video_id,
                                    edge_case_category=edge_case_category,
                                    model_id=model_id,
                                    concept_ids=concept_ids,
                                    mode=mode)
            mode_label = "edge_case"
        else:   # VIOLATION (default)
            self.analyze_video(video_id=video_id, model_id=model_id)
            mode_label = "violation"

        # 3) optionally wait
        if not wait_for_completion:
            return {"video_id": video_id, "mode": mode_label, "status": "started"}

        self.wait_for_analysis(video_id, timeout=timeout)
        payload = self.get_video_analysis(video_id)
        #Note that _parse_api_events is parsing the currently in video root doc visual_analysis
        events = self._parse_api_events(payload)

        # Return consistent format for all analysis types
        return {
            "video_id": video_id,
            "mode": mode_label,
            "status": "completed", 
            "events": events,
        }


# ───────────────────────── analyze (many) ───────────────────────────
    def _analyze_many(self,
                    video_ids: list[str],
                    analysis_type: AnalysisType | str,
                    model_id: str,
                    timeout: int,
                    wait_for_completion: bool,
                    search_query: str | None,
                    custom_event: str | None,
                    custom_category: CustomCategory | str | None,
                    edge_case_category: str | None,
                    concept_ids: list[str] | None,
                    mode: str,
                    return_subset: bool) -> list[dict]:
        """Submit N analyses in parallel and preserve input order."""
        with ThreadPoolExecutor(max_workers=len(video_ids)) as ex:
            futs = [
                ex.submit(self._analyze_single,
                        vid, analysis_type, model_id, timeout,
                        wait_for_completion, search_query, custom_event,
                        custom_category, edge_case_category,
                        concept_ids, mode, return_subset)
                for vid in video_ids
            ]
            return [fut.result() for fut in futs]   # keeps original order
    #########################


    def _upload_video(
        self,
        file_path: str,
        *,
        folder: Optional[str] = None,
        # ¦ deprecated ------------------------------------------------------
        source: Union[str, VideoSource, None] = None,
     ) -> Dict[str, Any]:
        """
        Upload a video for analysis.
        
        Args:
            file_path: Local path or remote URL of the video.
            source: Deprecated. Ignored by the SDK.
        
        Returns:
            A dictionary with the upload status and video_id.
        
        Raises:
            ValidationError: If the input parameters are invalid.
            VideoUploadError: If the upload fails.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        if source is not None:
            logger.warning("'source' parameter is deprecated and ignored; the SDK infers the source automatically.")
        
        if not file_path:
            raise ValidationError("Must provide file_path")

        # ── determine source type -----------------------------------------
        inferred_source = infer_source(file_path)
        
        # Only support FILE and VIDEO_URL, not SAVED
        if inferred_source == VideoSource.SAVED:
            raise ValidationError("Cannot upload from saved video ID. Use analyze() to analyze existing videos.")

        # Prepare request data ----------------------------------------------
        endpoint = "/api/upload-video"

        form_data: Dict[str, Any] = {
            "source": inferred_source.value,
            "firebase_collection_name": self.client.collection_name,
            "chunked":True
        }
        if folder:
            form_data["folder"] = folder
        files = None

        if inferred_source == VideoSource.FILE:
            filename = get_filename_from_path(file_path)
            mime_type = get_file_mime_type(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
            files = {"file": (filename, file_content, mime_type)}
            logger.info(f"Uploading local file: {filename}")
        elif inferred_source == VideoSource.VIDEO_URL:
            form_data["video_url"] = file_path
            logger.info(f"Uploading by URL: {file_path}")

        # Make the request ---------------------------------------------------
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=form_data,
            files=files,
            timeout=self.client.timeout * 20,
        )

        if not (200 <= response.status_code < 300):
            raise VideoUploadError(f"Failed to upload video: {format_error_message(response.json())}")

        logger.info(f"Upload (source={inferred_source.value}) response: {response.json()}")

        return response.json()

    def _upload_video_edge(
        self,
        file_path: str,
        *,
        category: Optional[str] = None,
        folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a video specifically for edge case detection."""
        if not file_path:
            raise ValidationError("Must provide file_path")

        inferred_source = infer_source(file_path)
        
        # Only support FILE and VIDEO_URL, not SAVED
        if inferred_source == VideoSource.SAVED:
            raise ValidationError("Cannot upload from saved video ID. Use analyze_video_edge() to analyze existing videos.")

        endpoint = "/api/upload-video-edge"

        form_data: Dict[str, Any] = {
            "source": inferred_source.value,
            "firebase_collection_name": self.client.collection_name,
            "chunked": True,
        }
        if category is not None:
            form_data["category"] = category
        if folder:
            form_data["folder"] = folder
        files = None

        if inferred_source == VideoSource.FILE:
            filename = get_filename_from_path(file_path)
            mime_type = get_file_mime_type(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
            files = {"file": (filename, file_content, mime_type)}
            logger.info(f"Uploading local file: {filename}")
        elif inferred_source == VideoSource.VIDEO_URL:
            form_data["video_url"] = file_path
            logger.info(f"Uploading by URL: {file_path}")

        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=form_data,
            files=files,
            timeout=self.client.timeout * 20,
        )

        if not (200 <= response.status_code < 300):
            raise VideoUploadError(f"Failed to upload video: {format_error_message(response.json())}")

        logger.info(f"Upload edge (source={inferred_source.value}) response: {response.json()}")

        return response.json()

    def analyze_video(self, video_id: str, model_id: Optional[str] = "Nomadic-VL-XLarge") -> Dict[str, Any]:
        """
        Start analysis for an uploaded video.
        
        Args:
            video_id: The ID of the video to analyze.
            
        Returns:
            A dictionary with the analysis status.
            
        Raises:
            AnalysisError: If the analysis fails to start.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/analyze-video/{video_id}"
        
        # Prepare form data with the collection name
        data = {
            "firebase_collection_name": self.client.collection_name,
            "model_id": model_id,
        }
        
        # Make the request
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=data,
        )
        
        # Return the parsed JSON response
        return response.json()

    def analyze_video_edge(
        self,
        video_id: str,
        edge_case_category: str,
        *,
        model_id: Optional[str] = "Nomadic-VL-XLarge",
        concept_ids: Optional[List[str]] = None,
        mode: str = "assistant",
    ) -> Dict[str, Any]:
        """Start edge case detection analysis for an uploaded video.

        Args:
            video_id: The ID of the uploaded video.
            edge_case_category: Category string used to select the edge case pipeline.
            model_id: (Optional) model to use.
            concept_ids: (Optional) extra concept IDs used by the backend.
            mode: ``"assistant"`` or ``"agent"``.
        """
        endpoint = f"/api/analyze-video-edge/{video_id}"

        data = {
            "firebase_collection_name": self.client.collection_name,
            "model_id": model_id,
            "edge_case_category": edge_case_category,
            "concepts_json": json.dumps(concept_ids or []),
            "mode": mode,
        }

        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=data,
        )

        return response.json()
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video analysis.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            A dictionary with the video status.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/status"
        
        # Add the required collection_name parameter
        params = {"firebase_collection_name": self.client.collection_name}
        
        # Make the request
        response = self.client._make_request("GET", endpoint, params=params)
        
        # Return the parsed JSON response
        return response.json()
        
    def wait_for_analysis(
        self,
        video_id: str,
        timeout: int = 2_400, # Default 40 minutes
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        """
        Block until the video analysis completes or times out.
        
        Args:
            video_id: The ID of the video to wait for.
            timeout: Maximum time to wait in seconds before raising TimeoutError.
            poll_interval: Time between status checks in seconds.
            
        Returns:
            A dictionary with the final video status payload.
            
        Raises:
            TimeoutError: If the analysis doesn't complete within the timeout period.
        """
        start_time = time.time()
        
        while True:
            payload = self.get_video_status(video_id)
            status = str(payload.get("status", "")).upper()
            self._print_status_bar(video_id, status=status)
            logger.debug(f"Video {video_id} - Status: '{status}', payload: '{payload}'")
            
            if status in {"COMPLETED", "FAILED"}:
                logger.info(f"Video {video_id} reached terminal status: {status}.")
                return payload
                
            if time.time() - start_time > timeout:
                msg = f"Analysis for {video_id} did not complete in {timeout}s. Last status: {status}"
                logger.error(msg)
                raise TimeoutError(msg)
                
            time.sleep(poll_interval)

    def wait_for_analyses(
        self,
        video_ids,
        timeout: int = 4800,
        poll_interval: int = 5
    ) -> dict:
        """
        Wait for multiple video analyses in parallel, with pretty status bars.
        """
        ids = list(video_ids)
        results = {}
        with ThreadPoolExecutor(max_workers=len(ids)) as executor:
            futures = {executor.submit(self.wait_for_analysis, vid, timeout, poll_interval): vid for vid in ids}
            for fut in as_completed(futures):
                vid = futures[fut]
                try:
                    results[vid] = fut.result()
                except Exception as e:
                    results[vid] = e
        return results
    
    def get_video_analysis(self, video_id: str) -> Dict[str, Any]:
        """
        Get the complete analysis of a video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            The complete video analysis.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/analysis"
        params = {"firebase_collection_name": self.client.collection_name}
                
        response = self.client._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )
        
        return response.json()
    
    def get_video_analyses(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get analyses for multiple videos.
        
        Args:
            video_ids: List of video IDs.
            
        Returns:
            A list of analyses for each video.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        analyses = []
        for vid in video_ids:
            analysis = self.get_video_analysis(vid)
            analyses.append(analysis)
        return analyses
    
    def get_detected_events(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get detected events for a video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            A list of detected events.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        return self._parse_api_events(self.get_video_analysis(video_id))

    # ------------------------------------------------------------------
    # Semantic search across multiple videos
    # ------------------------------------------------------------------

    def _summary_text(self, raw: Any) -> str:
        """Return a trimmed summary string or an empty string."""
        return raw.strip() if isinstance(raw, str) and raw.strip() else ""

    def _has_valid_analysis_content(self, text: Optional[str]) -> bool:
        """Check if an aiAnalysis field has useful content."""
        if text is None:
            return False
        if "No information available" in text:
            return False
        if text == "[SUMMARY UNAVAILABLE]":
            return False
        return bool(text.strip())

    def _build_search_context(self, analyses: Sequence[Dict[str, Any]]) -> str:
        """Convert analyses to JSONL search context used by /ask-question."""
        items: List[str] = []
        for analysis in analyses:
            vid = (
                analysis.get("video_id")
                or analysis.get("id")
                or analysis.get("metadata", {}).get("video_id")
            )
            if not vid:
                continue
            summary = self._summary_text(
                analysis.get("metadata", {}).get("pre_summary")
                or analysis.get("pre_summary")
            )
            if summary:
                items.append(
                    json.dumps({
                        "videoId": vid,
                        "eventIndex": -1,
                        "description": "[VIDEO SUMMARY]",
                        "analysis": summary[:5000],
                    })
                )

            events = (
                analysis.get("metadata", {})
                        .get("visual_analysis", {})
                        .get("events", [])
            )
            for idx, ev in enumerate(events or []):
                ai = ev.get("aiAnalysis")
                if not self._has_valid_analysis_content(ai):
                    continue
                items.append(
                    json.dumps({
                        "videoId": vid,
                        "eventIndex": idx,
                        "description": str(ev.get("description", ""))[:1000],
                        "analysis": str(ai)[:5000],
                    })
                )

        # Truncate to ~1 MB to keep Gemini happy
        max_chars = 1_040_000
        total = 0
        selected: List[str] = []
        for line in items:
            if total + len(line) > max_chars:
                break
            selected.append(line)
            total += len(line)
        return "\n".join(selected)

    def search_videos(
        self,
        query: str,
        folder: str,
        *,
        reasoning_trace_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search across videos in a folder for a natural language query.
        
        Args:
            query: Natural language search query
            folder: Name of the folder to search videos in
            reasoning_trace_path: Optional path for reasoning trace
            
        Returns:
            Dict containing matches and summary
            
        Raises:
            ValueError: If no videos found in the specified folder
            NomadicMLError: For API errors
        """
        # Get videos from the specified folder
        videos_info = self.my_videos(folder_id=folder)
        
        if not videos_info:
            raise ValueError(f"No videos found in folder '{folder}'")
        
        # Extract video IDs from the folder
        video_ids = [video["video_id"] for video in videos_info]
        
        # Get analyses for all videos in the folder
        analyses = self.get_video_analyses(video_ids)
        context = self._build_search_context(analyses)

        if not context:
            return {"matches": [], "summary": ""}

        payload = {
            "question": f"{query}{self._SEARCH_SPLIT_SYMBOL}{context}",
            "prompt_type": "search",
        }
        if reasoning_trace_path:
            payload["reasoning_trace_path"] = reasoning_trace_path

        resp = self.client._make_request("POST", "/api/ask-question", data=payload)
        data = resp.json().get("answer", "{}")
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON returned from /ask-question: %s", data)
            return {"matches": [], "summary": ""}
        return {
            "matches": parsed.get("matches", []),
            "summary": parsed.get("summary", ""),
        }
    
    ############### 
    # ──────────────── Long Video Event Search ────────────────────────────────────────
    ###############

    def apply_search(self, parent_id: str, query: str,
                    model_id: str = "Nomadic-VL-XLarge") -> Dict[str, Any]:
        payload = {
            "query":      query,
            "model_id":   model_id,
            "collection": self.client.collection_name,
        }
        r = self.client._make_request(
            "POST", f"/api/videos/{parent_id}/apply-search", data=payload
        )
        if r.status_code >= 400:
            raise NomadicMLError(format_error_message(r.json()))
        return r.json()                       # {"sweep_id": "...", ...}

    def get_sweep_status(self, parent_id: str, sweep_id: str) -> Dict[str, Any]:
        params = {"collection": self.client.collection_name}
        r = self.client._make_request(
            "GET", f"/api/videos/{parent_id}/sweeps/{sweep_id}", params=params
        )
        if r.status_code >= 400:
            raise NomadicMLError(format_error_message(r.json()))
        return r.json()

    def wait_for_search(self, parent_id: str, sweep_id: str,
                        timeout: int = 1_800, poll_interval: int = 5) -> Dict[str, Any]:
        start = time.time()
        while True:
            p = self.get_sweep_status(parent_id, sweep_id)
            status = (p.get("status") or "").upper()
            progress = int(p.get("progress", 0))
            self._print_status_bar(sweep_id,
                        percent=progress,
                        status="SEARCH")
            if status in {"SUCCEEDED", "FAILED"}:
                return p
            if time.time() - start > timeout:
                raise TimeoutError(f"Sweep {sweep_id} timed-out after {timeout}s")
            time.sleep(poll_interval)

    def search_events(self, parent_id: str, query: str, *,
                    model_id: str = "Nomadic-VL-XLarge",
                    timeout: int = 1_800, poll_interval: int = 5) -> Dict[str, Any]:
        sweep = self.apply_search(parent_id, query, model_id)
        return self.wait_for_search(parent_id, sweep["sweep_id"],
                                    timeout=timeout, poll_interval=poll_interval)

    def my_videos(self, folder_id: str | None = None) -> List[Dict[str, Any]]:
        params = {"firebase_collection_name": self.client.collection_name}
        if folder_id:
            params["folder"] = folder_id
        resp = self.client._make_request("GET", "/api/my-videos", params=params)
        return resp.json().get("videos", [])

    def delete_video(self, video_id: str) -> Dict[str, Any]:
        params = {"firebase_collection_name": self.client.collection_name}
        resp = self.client._make_request("DELETE", f"/api/video/{video_id}", params=params)
        return resp.json()
    

    # ─────────────────────── wait until status == UPLOADED ───────────── CHANGED
    def _wait_for_uploaded(self,
                           video_id: str,
                           timeout: int = 1200,
                           initial_delay: int = 15,
                           max_delay: int = 30,
                           multiplier: int = 2) -> None:
        """Block until video upload is finished.

        Handles both single videos and chunked uploads. When ``chunks_total`` is
        present in metadata, this waits until all chunks are reported as
        uploaded; otherwise it waits for ``visual_analysis.status.status`` to become
        ``UPLOADED``.
        """
        delay = initial_delay
        deadline = time.time() + timeout

        while True:
            payload = self.get_video_status(video_id)
            meta = payload.get("metadata", {})

            state = (self._status_from_metadata(meta) or "").upper()
            total = meta.get("chunks_total")
            uploaded = meta.get("chunks_uploaded", 0)

            if isinstance(total, int) and total > 0:
                if uploaded >= total:
                    logger.info(f"Upload completed for video {video_id}")
                    return
            elif state == "UPLOADED":
                logger.info(f"Upload completed for video {video_id}: status={state}")
                return

            if state in ("UPLOADING_FAILED", "FAILED"):
                raise VideoUploadError(f"Upload failed (backend status={state})")
            if time.time() > deadline:
                raise TimeoutError(f"Backend never reached UPLOADED in {timeout}s")

            sleep_for = max(0, delay + random.uniform(-1, 1))
            time.sleep(sleep_for)

            delay = min(delay * multiplier, max_delay)
            
    @deprecated("upload_and_analyze() has been deprecated. Use separate upload() and analyze() calls instead. See documentation for examples: https://docs.nomadicml.com/api-reference/sdk-examples")
    def upload_and_analyze(self,*args, **kwargs):
        raise NotImplementedError(
            "Deprecated: Use separate upload() and analyze() calls instead. "
            "See documentation for examples: https://docs.nomadicml.com/api-reference/sdk-examples"
        )

    def _status_from_metadata(self, meta: dict) -> Optional[str]:
        """
        Return the processing state stored in the scalar Firestore field
        `visual_analysis.status.status`.
        """
        return meta.get("visual_analysis", {}).get("status", {}).get("status")
