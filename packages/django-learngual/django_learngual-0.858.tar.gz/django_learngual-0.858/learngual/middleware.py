import logging
import time
import tracemalloc
import zoneinfo
from logging import getLogger
from logging.handlers import RotatingFileHandler

import pytz
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin

from .utils import get_language_code

logger = getLogger(__file__)


class TimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_header = request.headers.get("TZ")

        if tz_header:
            try:
                timezone.activate(tz_header)
            except (pytz.UnknownTimeZoneError, zoneinfo.ZoneInfoNotFoundError):
                logger.error("Invalid timezone %s", tz_header)
                pass  # Handle unknown timezone error here
        else:
            # Set default timezone if TZ header is not provided
            timezone.activate("UTC")

        response = self.get_response(request)
        timezone.deactivate()
        return response


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract language from _lang query parameter
        lang = request.GET.get("_lang")
        if lang:
            lang = get_language_code(lang).upper()
        if lang:
            # Activate the new language if it's valid
            translation.activate(lang)
        else:
            # Fallback to default language if not valid
            translation.activate("EN")

        response = self.get_response(request)
        # Restore the original language
        translation.activate("EN")
        return response


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record the start time
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate the time taken
        duration = time.time() - start_time
        logger.info(f"Request to {request.path} took {duration:.4f} seconds")

        response["X-Request-Duration"] = f"{duration:.4f} seconds"
        return response


class MemoryUsageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tracemalloc.start()  # Start tracking memory

    def process_response(self, request, response):
        _, peak_memory = tracemalloc.get_traced_memory()
        peak_memory_mb = peak_memory / 1024 / 1024  # Convert to MB
        tracemalloc.stop()  # Stop tracking

        logger.info(
            f"[{request.method}] {request.path} - Peak Memory Used: {peak_memory_mb:.2f} MB"
        )
        return response


class ResponseTimeLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("metric_logger")
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                "metric.log", maxBytes=5 * 1024 * 1024, backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start) * 1000)
        path = request.path
        method = request.method
        self.logger.info(
            f"Method: {method} | Path: {path} | Response Time: {duration_ms} ms"
        )
        return response
