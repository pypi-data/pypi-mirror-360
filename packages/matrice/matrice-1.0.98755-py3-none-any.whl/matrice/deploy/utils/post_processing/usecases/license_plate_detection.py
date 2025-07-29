from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import deque
from datetime import datetime, timezone

from ..core.base import (
    BaseProcessor,
    ProcessingContext,
    ProcessingResult,
    ConfigProtocol,
    ResultFormat
)
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    apply_category_mapping,
    calculate_counting_summary,
    match_results_structure,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)
from ..advanced_tracker import AdvancedTracker, TrackerConfig

@dataclass
class LicensePlateConfig(BaseConfig):
    """Configuration for license plate detection use case."""

    # Detection settings
    confidence_threshold: float = 0.6

    # Category settings
    license_plate_categories: List[str] = field(
        default_factory=lambda: ["License_Plate", "license_plate"]
    )

    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    # Time window configuration
    time_window_minutes: int = 60
    enable_unique_counting: bool = True

    # Smoothing configuration
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"  # "window" or "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5

    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {0: "License_Plate"}
    )

    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")

class LicensePlateUseCase(BaseProcessor):
    """License plate detection use case with counting and analytics."""

    def __init__(self):
        """Initialize license plate detection use case."""
        super().__init__("license_plate_detection")
        self.category = "license_plate"
        self.smoothing_tracker = None
        self.tracker = AdvancedTracker(TrackerConfig())
        # Track ID storage for total count calculation
        self._total_track_ids = set()  # Store all unique track IDs seen across calls
        self._current_frame_track_ids = set()  # Store track IDs from current frame
        self._total_count = 0  # Cached total count
        self._last_update_time = time.time()  # Track when last updated
        
        # Frame counter for tracking total frames processed
        self._total_frame_counter = 0  # Total frames processed across all calls
        self._global_frame_offset = 0  # Offset for global frame numbering
        self._frames_in_current_chunk = 0  # Number of frames in current chunk

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for license plate detection."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for detections",
                },
                "license_plate_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["License_Plate", "license_plate"],
                    "description": "Category names that represent license plates",
                },
                "index_to_category": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from category indices to names",
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for alerts",
                        }
                    },
                },
                "enable_smoothing": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable bounding box smoothing",
                },
                "smoothing_algorithm": {
                    "type": "string",
                    "enum": ["window", "observability"],
                    "default": "observability",
                    "description": "Smoothing algorithm to use",
                },
                "smoothing_window_size": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 20,
                    "description": "Size of the smoothing window",
                },
                "smoothing_cooldown_frames": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 5,
                    "description": "Number of frames to wait before removing a track",
                },
                "smoothing_confidence_range_factor": {
                    "type": "number",
                    "minimum": 0.0,
                    "default": 0.5,
                    "description": "Factor for confidence range in smoothing",
                },
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False,
        }

    def create_default_config(self, **overrides) -> LicensePlateConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "license_plate_categories": ["License_Plate", "license_plate"],
            "enable_smoothing": True,
            "smoothing_algorithm": "observability",
            "smoothing_window_size": 20,
            "smoothing_cooldown_frames": 5,
            "smoothing_confidence_range_factor": 0.5,
        }
        defaults.update(overrides)
        return LicensePlateConfig(**defaults)

    def process(
        self,
        data: Any,
        config: ConfigProtocol,
        context: Optional[ProcessingContext] = None,
        stream_info: Optional[Dict[str, Any]] = None,
    ) -> ProcessingResult:
        """
        Process license plate detection use case.
        """
        start_time = time.time()
        tracking_results = self.tracker.update(data)

        try:
            if not isinstance(config, LicensePlateConfig):
                return self.create_error_result(
                    "Invalid configuration type for license plate detection",
                    usecase=self.name,
                    category=self.category,
                    context=context,
                )

            if context is None:
                context = ProcessingContext()

            input_format = match_results_structure(tracking_results)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold

            self.logger.info(
                f"Processing license plate detection with format: {input_format.value}"
            )

            # Check if data is frame-based tracking format
            is_frame_based_tracking = (
                isinstance(tracking_results, dict)
                and all(isinstance(k, (str, int)) for k in tracking_results.keys())
                and input_format == ResultFormat.OBJECT_TRACKING
            )

            if is_frame_based_tracking:
                # Apply smoothing to tracking results if enabled
                if config.enable_smoothing:
                    if self.smoothing_tracker is None:
                        smoothing_config = BBoxSmoothingConfig(
                            smoothing_algorithm=config.smoothing_algorithm,
                            window_size=config.smoothing_window_size,
                            cooldown_frames=config.smoothing_cooldown_frames,
                            confidence_threshold=config.confidence_threshold,
                            confidence_range_factor=config.smoothing_confidence_range_factor,
                            enable_smoothing=True
                        )
                        self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
                    
                    smoothed_tracking_data = bbox_smoothing(tracking_results, self.smoothing_tracker.config, self.smoothing_tracker)
                    self.logger.debug(f"Applied bbox smoothing to tracking results with {len(smoothed_tracking_data)} frames")
                    
                    return self._process_frame_wise_tracking(smoothed_tracking_data, config, context, stream_info)
                else:
                    return self._process_frame_wise_tracking(tracking_results, config, context, stream_info)
            else:
                return self._process_single_frame_data(tracking_results, config, context, stream_info)

        except Exception as e:
            self.logger.error(f"Error in license plate processing: {str(e)}")
            return self.create_error_result(
                f"License plate processing failed: {str(e)}",
                error_type="LicensePlateProcessingError",
                usecase=self.name,
                category=self.category,
                context=context,
            )

    def _process_frame_wise_tracking(self, data: Dict, config: LicensePlateConfig, context: ProcessingContext, stream_info: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process frame-wise tracking data to generate frame-specific events and tracking stats."""
        
        frame_events = {}
        frame_tracking_stats = {}
        all_events = []
        all_tracking_stats = []
        
        frames_in_this_call = len(data)
        self._total_frame_counter += frames_in_this_call
        
        for frame_key, frame_detections in data.items():
            local_frame_id = self._extract_frame_id_from_tracking(frame_detections, frame_key, stream_info)
            global_frame_id = self.get_global_frame_id(local_frame_id)
            
            frame_result = self._process_single_frame_detections(frame_detections, config, context, global_frame_id)
            
            if frame_result.is_success():
                events = frame_result.data.get("events", [])
                tracking_stats = frame_result.data.get("tracking_stats", [])
                
                for event in events:
                    event["frame_id"] = global_frame_id
                
                if events:
                    frame_events[global_frame_id] = events
                    all_events.extend(events)
                
                frame_tracking_stats[global_frame_id] = tracking_stats
                all_tracking_stats.extend(tracking_stats)
        
        self.update_global_frame_offset(frames_in_this_call)
        
        result_data = {
            "events": frame_events,
            "tracking_stats": frame_tracking_stats,
            "all_events": all_events,
            "all_tracking_stats": all_tracking_stats,
            "total_count": self.get_total_count(),
            "global_frame_offset": self._global_frame_offset,
            "frames_in_chunk": frames_in_this_call
        }
        
        return self.create_result(
            result_data,
            self.name,
            self.category,
            context
        )

    def _extract_frame_id_from_tracking(self, frame_detections: List[Dict], frame_key: str, stream_info: Optional[Dict[str, Any]] = None) -> str:
        """Extract frame ID from tracking data or stream_info."""
        if stream_info and "input_settings" in stream_info:
            frame_number = stream_info.get("input_settings", {}).get("start_frame")
            if frame_number is not None:
                return str(frame_number)
        
        if frame_detections and len(frame_detections) > 0:
            first_detection = frame_detections[0]
            if "frame" in first_detection:
                return str(first_detection["frame"])
            elif "timestamp" in first_detection:
                return str(int(first_detection["timestamp"]))
        
        return str(frame_key)

    def _process_single_frame_detections(self, frame_detections: List[Dict], config: LicensePlateConfig, context: ProcessingContext, frame_id: Optional[str] = None) -> ProcessingResult:
        """Process detections from a single frame."""
        
        if config.confidence_threshold is not None:
            frame_detections = [d for d in frame_detections if d.get("confidence", 0) >= config.confidence_threshold]
        
        if config.index_to_category:
            frame_detections = apply_category_mapping(frame_detections, config.index_to_category)
        
        license_detections = [
            det for det in frame_detections
            if det.get('category', '').lower() in [cat.lower() for cat in config.license_plate_categories]
        ]
        
        license_counting_summary = {
            "total_objects": len(license_detections),
            "by_category": {"License_Plate": len(license_detections)},
            "detections": license_detections,
        }
        
        self._update_tracking_state(license_counting_summary)
        
        insights = self._generate_insights(license_counting_summary, config)
        alerts = self._check_alerts(license_counting_summary, config)
        
        events = self._generate_events(license_counting_summary, alerts, config, frame_id)
        tracking_stats = self._generate_tracking_stats(license_counting_summary, insights, "", config, frame_id)
        
        return self.create_result(
            data={
                "events": events[0][frame_id] if events else [],
                "tracking_stats": tracking_stats[0][frame_id] if tracking_stats else [],
                "license_plate_summary": license_counting_summary,
            },
            usecase=self.name,
            category=self.category,
            context=context
        )

    def _process_single_frame_data(
        self,
        data: Any,
        config: LicensePlateConfig,
        context: ProcessingContext,
        stream_info: Optional[Dict[str, Any]] = None,
    ) -> ProcessingResult:
        """
        Process single frame data for license plate detection.
        """
        start_time = time.time()

        try:
            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(
                    processed_data, config.confidence_threshold
                )
                self.logger.debug(
                    f"Applied confidence filtering with threshold {config.confidence_threshold}"
                )

            if config.index_to_category:
                processed_data = apply_category_mapping(
                    processed_data, config.index_to_category
                )
                self.logger.debug("Applied category mapping")

            # Apply bbox smoothing if enabled
            if config.enable_smoothing:
                if self.smoothing_tracker is None:
                    smoothing_config = BBoxSmoothingConfig(
                        smoothing_algorithm=config.smoothing_algorithm,
                        window_size=config.smoothing_window_size,
                        cooldown_frames=config.smoothing_cooldown_frames,
                        confidence_threshold=config.confidence_threshold,
                        confidence_range_factor=config.smoothing_confidence_range_factor,
                        enable_smoothing=True
                    )
                    self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)

                # Apply smoothing to license plate detections
                license_detections = [
                    det for det in processed_data
                    if det.get('category', '').lower()
                    in [cat.lower() for cat in config.license_plate_categories]
                ]
                smoothed_licenses = bbox_smoothing(license_detections, self.smoothing_tracker.config, self.smoothing_tracker)

                processed_data = smoothed_licenses

            license_counting_summary = self._calculate_license_plate_summary(
                processed_data, config
            )
            general_counting_summary = calculate_counting_summary(processed_data)

            self._update_tracking_state(license_counting_summary)

            insights = self._generate_insights(license_counting_summary, config)
            alerts = self._check_alerts(license_counting_summary, config)
            metrics = self._calculate_metrics(license_counting_summary, config, context)
            predictions = self._extract_predictions(processed_data, config)
            summary = self._generate_summary(license_counting_summary, general_counting_summary, alerts)

            # Extract frame information from stream_info
            frame_number = None
            if stream_info:
                input_settings = stream_info.get("input_settings", {})
                start_frame = input_settings.get("start_frame")
                end_frame = input_settings.get("end_frame")
                if start_frame is not None and end_frame is not None and start_frame == end_frame:
                    frame_number = start_frame
                elif start_frame is not None:
                    frame_number = start_frame

            # Generate structured events and tracking stats
            events = self._generate_events(license_counting_summary, alerts, config, frame_number)
            tracking_stats = self._generate_tracking_stats(license_counting_summary, insights, summary, config, frame_number)

            context.mark_completed()

            result = self.create_result(
                data={
                    "license_plate_summary": license_counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_license_plates": license_counting_summary.get(
                        "total_objects", 0
                    ),
                    "events": events[0][str(frame_number) if frame_number is not None else "current_frame"],
                    "tracking_stats": tracking_stats[0][str(frame_number) if frame_number is not None else "current_frame"],
                    "total_count": self.get_total_count()
                },
                usecase=self.name,
                category=self.category,
                context=context,
            )

            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics

            return result

        except Exception as e:
            self.logger.error(f"Error in license plate processing: {str(e)}")
            return self.create_error_result(
                f"License plate processing failed: {str(e)}",
                error_type="LicensePlateProcessingError",
                usecase=self.name,
                category=self.category,
                context=context,
            )

    def _calculate_license_plate_summary(self, data: Any, config: LicensePlateConfig) -> Dict[str, Any]:
        """Calculate summary for license plates only."""
        if isinstance(data, list):
            license_detections = [
                det
                for det in data
                if det.get("category", "").lower()
                in [cat.lower() for cat in config.license_plate_categories]
            ]

            return {
                "total_objects": len(license_detections),
                "by_category": {"License_Plate": len(license_detections)},
                "detections": license_detections,
            }
        return {"total_objects": 0, "by_category": {}, "detections": []}

    def _generate_insights(self, license_summary: Dict, config: LicensePlateConfig) -> List[str]:
        """Generate human-readable insights from detection results."""
        insights = []

        total_plates = license_summary.get("total_objects", 0)

        if total_plates == 0:
            insights.append("EVENT: No license plates detected in the scene")
        else:
            insights.append(
                f"EVENT: Detected {total_plates} license plate{'s' if total_plates != 1 else ''}"
            )

        intensity_threshold = None
        if (
            config.alert_config
            and config.alert_config.count_thresholds
            and "license_plate" in config.alert_config.count_thresholds
        ):
            intensity_threshold = config.alert_config.count_thresholds["license_plate"]
        elif (
            config.alert_config
            and config.alert_config.count_thresholds
            and "all" in config.alert_config.count_thresholds
        ):
            intensity_threshold = config.alert_config.count_thresholds["all"]

        if intensity_threshold is not None:
            percentage = (total_plates / intensity_threshold) * 100

            if percentage < 20:
                insights.append(
                    f"INTENSITY: Low traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 50:
                insights.append(
                    f"INTENSITY: Moderate traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 70:
                insights.append(
                    f"INTENSITY: High traffic volume ({percentage:.1f}% of expected capacity)"
                )
            else:
                insights.append(
                    f"INTENSITY: Very high traffic density ({percentage:.1f}% of expected capacity)"
                )
        else:
            if total_plates > 10:
                insights.append(
                    f"INTENSITY: High traffic density with {total_plates} license plates detected"
                )
            elif total_plates == 1:
                insights.append("INTENSITY: Light traffic conditions")

        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(license_summary)
            if unique_count is not None:
                insights.append(f"Unique license plate count: {unique_count}")
                if unique_count != total_plates:
                    insights.append(f"Detection efficiency: {unique_count}/{total_plates} unique tracks")

        return insights

    def _check_alerts(self, license_summary: Dict, config: LicensePlateConfig) -> List[Dict]:
        """Alerts are disabled in this use case."""
        return []

    def _calculate_metrics(
        self,
        license_summary: Dict,
        config: LicensePlateConfig,
        context: ProcessingContext,
    ) -> Dict[str, Any]:
        """Calculate detailed metrics for analytics."""
        total_plates = license_summary.get("total_objects", 0)

        metrics = {
            "total_license_plates": total_plates,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
        }

        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(license_summary)
            if unique_count is not None:
                metrics["unique_license_plates"] = unique_count
                metrics["tracking_efficiency"] = (unique_count / total_plates) * 100 if total_plates > 0 else 0

        return metrics

    def _extract_predictions(self, data: Any, config: LicensePlateConfig) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []

        try:
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        prediction = {
                            "category": item.get(
                                "category", item.get("class", "unknown")
                            ),
                            "confidence": item.get(
                                "confidence", item.get("score", 0.0)
                            ),
                            "bounding_box": item.get(
                                "bounding_box", item.get("bbox", {})
                            ),
                            "track_id": item.get("track_id")
                        }
                        predictions.append(prediction)

            elif isinstance(data, dict):
                for frame_id, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            prediction = {
                                "category": item.get("category", item.get("class", "unknown")),
                                "confidence": item.get("confidence", item.get("score", 0.0)),
                                "bounding_box": item.get("bounding_box", item.get("bbox", {})),
                                "track_id": item.get("track_id"),
                                "frame_id": frame_id
                            }
                            predictions.append(prediction)

        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")

        return predictions

    def _generate_summary(self, license_summary: Dict, general_summary: Dict, alerts: List) -> str:
        """Generate human-readable summary."""
        total_plates = license_summary.get("total_objects", 0)

        if total_plates == 0:
            return "No license plates detected"

        summary_parts = []

        if total_plates > 0:
            summary_parts.append(
                f"{total_plates} license plate{'s' if total_plates != 1 else ''} detected"
            )

        if alerts:
            alert_count = len(alerts)
            summary_parts.append(
                f"{alert_count} alert{'s' if alert_count != 1 else ''}"
            )

        return ", ".join(summary_parts)

    def _generate_events(self, license_summary: Dict, alerts: List, config: LicensePlateConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured events for the output format."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        
        events = [{frame_key: []}]
        frame_events = events[0][frame_key]
        total_plates = license_summary.get("total_objects", 0)

        if total_plates > 0:
            level = "info"
            intensity = 5.0

            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("license_plate", config.alert_config.count_thresholds.get("all", 10))
                intensity = min(10.0, (total_plates / threshold) * 10) if total_plates > 0 else 3.0

                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
                else:
                    level = "info"
            else:
                if total_plates > 15:
                    level = "critical"
                    intensity = 9.0
                elif total_plates > 8:
                    level = "warning"
                    intensity = 7.0
                else:
                    level = "info"
                    intensity = min(10.0, total_plates / 2.0) if total_plates > 0 else 3.0

            event = {
                "type": "license_plate_detection",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "License Plate Detection System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: License Plate Detection\nLicense Plates: {total_plates} detected."
            }
            frame_events.append(event)

        for alert in alerts:
            alert_event = {
                "type": alert.get("type", "license_plate_alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "License Plate Alert System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": "License plate alert triggered"
            }
            frame_events.append(alert_event)

        return events

    def _generate_tracking_stats(self, license_summary: Dict, insights: List[str], summary: str, config: LicensePlateConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured tracking stats for the output format."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        tracking_stats = [{frame_key: []}]
        frame_tracking_stats = tracking_stats[0][frame_key]
        total_plates = license_summary.get("total_objects", 0)
        
        if total_plates > 0:
            total_unique_count = self.get_total_count()
            current_frame_count = self.get_current_frame_count()
            
            frame_identifier = frame_key
            
            tracking_stat = {
                "tracking_start_time": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "all_results_for_tracking": {
                    "total_license_plates": total_plates,
                    "license_plate_summary": license_summary,
                    "detection_rate": (total_plates / config.time_window_minutes * 60) if config.time_window_minutes else 0,
                    "cumulative_total": total_unique_count,
                    "current_frame_count": current_frame_count,
                    "track_ids_info": self.get_track_ids_info(),
                    "global_frame_offset": self._global_frame_offset,
                    "local_frame_id": frame_identifier
                },
                "human_text": self._generate_human_text_for_tracking(total_plates, total_unique_count, insights, config),
                "frame_id": frame_identifier,
                "frames_in_this_call": 1,
                "total_frames_processed": self._total_frame_counter,
                "current_frame_number": frame_identifier,
                "global_frame_offset": self._global_frame_offset
            }
            frame_tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, total_plates: int, total_unique_count: int, insights: List[str], config: LicensePlateConfig) -> str:
        """Generate human-readable text for tracking stats."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        
        text_parts = [
            f"Tracking Start Time: {timestamp}",
            f"License Plates Detected: {total_plates}",
            f"Total Unique License Plates: {total_unique_count}"
        ]
        
        return "\n".join(text_parts)
    
    def _count_unique_tracks(self, license_summary: Dict, config: LicensePlateConfig = None) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        self._update_tracking_state(license_summary)
        
        if config and config.enable_unique_counting:
            return self._total_count if self._total_count > 0 else None
        else:
            return None

    def _update_tracking_state(self, counting_summary: Dict) -> None:
        """Update tracking state with current frame data."""
        detections = counting_summary.get("detections", [])
        
        if not detections:
            return
        
        current_frame_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                current_frame_tracks.add(track_id)
        
        old_total_count = len(self._total_track_ids)
        self._total_track_ids.update(current_frame_tracks)
        self._current_frame_track_ids = current_frame_tracks
        
        self._total_count = len(self._total_track_ids)
        self._last_update_time = time.time()
        
        if len(current_frame_tracks) > 0:
            new_tracks = current_frame_tracks - (self._total_track_ids - current_frame_tracks)
            if new_tracks:
                self.logger.debug(f"Tracking state updated: {len(new_tracks)} new track IDs added, total unique tracks: {self._total_count}")
            else:
                self.logger.debug(f"Tracking state updated: {len(current_frame_tracks)} current frame tracks, total unique tracks: {self._total_count}")

    def get_total_count(self) -> int:
        """Get the total count of unique license plates tracked across all calls."""
        return self._total_count

    def get_current_frame_count(self) -> int:
        """Get the count of license plates in the current frame."""
        return len(self._current_frame_track_ids)

    def get_total_frames_processed(self) -> int:
        """Get the total number of frames processed across all calls."""
        return self._total_frame_counter

    def set_global_frame_offset(self, offset: int) -> None:
        """Set the global frame offset for video chunk processing."""
        self._global_frame_offset = offset
        self.logger.info(f"Global frame offset set to: {offset}")

    def get_global_frame_offset(self) -> int:
        """Get the current global frame offset."""
        return self._global_frame_offset

    def update_global_frame_offset(self, frames_in_chunk: int) -> None:
        """Update global frame offset after processing a chunk."""
        old_offset = self._global_frame_offset
        self._global_frame_offset += frames_in_chunk
        self.logger.info(f"Global frame offset updated: {old_offset} -> {self._global_frame_offset} (added {frames_in_chunk} frames)")

    def get_global_frame_id(self, local_frame_id: str) -> str:
        """Convert local frame ID to global frame ID."""
        try:
            local_frame_num = int(local_frame_id)
            global_frame_num = local_frame_num + self._global_frame_offset
            return str(global_frame_num)
        except (ValueError, TypeError):
            return local_frame_id

    def get_track_ids_info(self) -> Dict[str, Any]:
        """Get detailed information about track IDs."""
        return {
            "total_count": self._total_count,
            "current_frame_count": len(self._current_frame_track_ids),
            "total_unique_track_ids": len(self._total_track_ids),
            "current_frame_track_ids": list(self._current_frame_track_ids),
            "last_update_time": self._last_update_time,
            "total_frames_processed": self._total_frame_counter
        }

    def get_tracking_debug_info(self) -> Dict[str, Any]:
        """Get detailed debugging information about tracking state."""
        return {
            "total_track_ids": list(self._total_track_ids),
            "current_frame_track_ids": list(self._current_frame_track_ids),
            "total_count": self._total_count,
            "current_frame_count": len(self._current_frame_track_ids),
            "total_frames_processed": self._total_frame_counter,
            "last_update_time": self._last_update_time,
            "global_frame_offset": self._global_frame_offset,
            "frames_in_current_chunk": self._frames_in_current_chunk
        }

    def get_frame_info(self) -> Dict[str, Any]:
        """Get detailed information about frame processing and global frame offset."""
        return {
            "global_frame_offset": self._global_frame_offset,
            "total_frames_processed": self._total_frame_counter,
            "frames_in_current_chunk": self._frames_in_current_chunk,
            "next_global_frame": self._global_frame_offset + self._frames_in_current_chunk
        }

    def reset_tracking_state(self) -> None:
        """Completely reset ALL tracking data including cumulative totals."""
        self._total_track_ids.clear()
        self._current_frame_track_ids.clear()
        self._total_count = 0
        self._last_update_time = time.time()
        
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self._frames_in_current_chunk = 0
        
        self.logger.warning("⚠️ FULL tracking state reset - all track IDs, frame counter, and global frame offset cleared. Cumulative totals lost!")

    def clear_current_frame_tracking(self) -> int:
        """Clear only current frame tracking data while preserving cumulative totals."""
        old_current_count = len(self._current_frame_track_ids)
        self._current_frame_track_ids.clear()
        
        self._last_update_time = time.time()
        
        self.logger.info(f"Cleared {old_current_count} current frame tracks. Cumulative total preserved: {self._total_count}")
        return old_current_count

    def reset_frame_counter(self) -> None:
        """Reset only the frame counter."""
        old_count = self._total_frame_counter
        self._total_frame_counter = 0
        self.logger.info(f"Frame counter reset from {old_count} to 0")

    def clear_expired_tracks(self, max_age_seconds: float = 300.0) -> int:
        """Clear current frame tracking data if no updates for a while."""
        current_time = time.time()
        if current_time - self._last_update_time > max_age_seconds:
            cleared_count = self.clear_current_frame_tracking()
            self.logger.info(f"Manual cleanup: cleared {cleared_count} expired current frame tracks (age > {max_age_seconds}s)")
            return cleared_count
        return 0

    def test_tracking_persistence(self) -> Dict[str, Any]:
        """Test method to verify tracking state persists across calls."""
        test_data = [
            [
                {"category": "License_Plate", "confidence": 0.8, "track_id": "track_1", "bounding_box": [100, 100, 200, 200]},
                {"category": "License_Plate", "confidence": 0.9, "track_id": "track_2", "bounding_box": [300, 300, 400, 400]}
            ],
            [
                {"category": "License_Plate", "confidence": 0.8, "track_id": "track_1", "bounding_box": [110, 110, 210, 210]},
                {"category": "License_Plate", "confidence": 0.7, "track_id": "track_3", "bounding_box": [500, 500, 600, 600]}
            ]
        ]
        
        config = self.create_default_config(enable_unique_counting=True)
        results = []
        
        for i, frame_data in enumerate(test_data):
            counting_summary = {
                "total_objects": len(frame_data),
                "detections": frame_data,
                "by_category": {"License_Plate": len(frame_data)}
            }
            
            self._update_tracking_state(counting_summary)
            
            result = {
                "call_number": i + 1,
                "frame_license_plates": len(frame_data),
                "total_unique_tracks": self._total_count,
                "track_ids": list(self._total_track_ids),
                "current_frame_tracks": list(self._current_frame_track_ids)
            }
            results.append(result)
        
        return {
            "test_results": results,
            "final_total_count": self._total_count,
            "final_track_ids": list(self._total_track_ids),
            "debug_info": self.get_tracking_debug_info()
        }