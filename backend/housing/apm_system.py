import time
import json
import uuid
import os
from django.db import connection
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt

# Log file will be saved in d:\housing\backend\apm_telemetry.log
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apm_telemetry.log')

def write_log(entry):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass

class AdvancedAPMMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return
        request.apm_id = str(uuid.uuid4())
        request.apm_start_time = time.time()
        request.apm_initial_queries = len(connection.queries)

    def process_response(self, request, response):
        if not hasattr(request, 'apm_start_time') or request.path == '/apm-endpoint/':
            return response

        total_time_ms = (time.time() - request.apm_start_time) * 1000
        queries_run = len(connection.queries) - request.apm_initial_queries

        # 1. Log Backend Metrics
        log_data = {
            "type": "SERVER_BACKEND",
            "req_id": request.apm_id,
            "path": request.path,
            "method": request.method,
            "status": response.status_code,
            "server_time_ms": round(total_time_ms, 2),
            "db_queries": queries_run,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        write_log(log_data)

        # 2. Inject Frontend APM Script to track Clients over the Network
        if 'text/html' in response.get('Content-Type', '') and response.status_code == 200:
            script = f"""
            <!-- ANTIGRAVITY APM INJECTION -->
            <script>
            window.addEventListener('load', function() {{
                setTimeout(function() {{
                    try {{
                        let perf = window.performance.timing;
                        let pageLoadTime = perf.loadEventEnd - perf.navigationStart;
                        let domRenderTime = perf.domComplete - perf.domLoading;
                        let ttfb = perf.responseStart - perf.navigationStart;
                        fetch('/apm-endpoint/', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                req_id: '{request.apm_id}',
                                path: window.location.pathname,
                                client_total_load_time_ms: pageLoadTime,
                                browser_dom_render_time_ms: domRenderTime,
                                network_ttfb_ms: ttfb,
                                user_agent: navigator.userAgent
                            }})
                        }});
                    }} catch(e) {{}}
                }}, 1000);
            }});
            </script>
            """
            content = response.content.decode('utf-8', errors='ignore')
            if '</body>' in content:
                content = content.replace('</body>', script + '</body>')
                response.content = content.encode('utf-8')
                if 'Content-Length' in response:
                    response['Content-Length'] = str(len(response.content))
        
        # 3. Force offline mode (Block all external CDNs instantly)
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:;"
            
        return response

@csrf_exempt
def apm_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data["type"] = "CLIENT_FRONTEND"
            data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            write_log(data)
        except Exception:
            pass
    return JsonResponse({"status": "ok"})
