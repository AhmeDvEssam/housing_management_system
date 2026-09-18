import time
import logging
from django.db import connection

logger = logging.getLogger(__name__)

class QueryProfilingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignore static and media files to avoid spam in the console
        if request.path.startswith('/static/') or request.path.startswith('/media/') or '/favicon.ico' in request.path:
            return self.get_response(request)

        # Record initial queries and start time
        initial_queries = len(connection.queries)
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate results
        total_time_ms = (time.time() - start_time) * 1000
        final_queries = len(connection.queries)
        queries_run = final_queries - initial_queries

        # Prepare the log message
        print("\n" + "="*80)
        print(f"🚀 [PROFILER] Page Visited: {request.path}")
        print(f"⏱️  Time Taken: {total_time_ms:.2f} ms")
        print(f"💾 DB Queries: {queries_run} queries executed")
        
        # Highlight bottlenecks
        if queries_run > 50:
            print("🚨 WARNING: HIGH NUMBER OF DB QUERIES! (Possible N+1 problem detected)")
        if total_time_ms > 1000:
            print("🚨 WARNING: SLOW PAGE RESPONSE! (>1 second)")
            
        print("="*80 + "\n")

        return response
