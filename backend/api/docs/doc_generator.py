"""
Documentation Generator
Epic 7 Sprint 3 - Task 2: Generate API Documentation

Generates comprehensive documentation including HTML pages and interactive docs.
"""

from flask import Flask, render_template_string
from datetime import datetime
import os
import json
from .openapi_spec import generate_openapi_spec


def generate_documentation(app: Flask, output_dir: str = "docs/output"):
    """Generate comprehensive API documentation"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate OpenAPI spec
    spec = generate_openapi_spec(app)
    
    # Generate various documentation formats
    generated_files = []
    
    # 1. OpenAPI Specification Files
    spec_files = _save_openapi_spec(spec, output_dir)
    generated_files.extend(spec_files)
    
    # 2. HTML Documentation
    html_file = _generate_html_documentation(spec, output_dir)
    generated_files.append(html_file)
    
    # 3. Markdown Documentation
    md_file = _generate_markdown_documentation(spec, output_dir)
    generated_files.append(md_file)
    
    # 4. Interactive Swagger UI
    swagger_files = _generate_swagger_ui(spec, output_dir)
    generated_files.extend(swagger_files)
    
    # 5. Postman Collection
    postman_file = _generate_postman_collection(spec, output_dir)
    generated_files.append(postman_file)
    
    return generated_files


def _save_openapi_spec(spec: dict, output_dir: str) -> list:
    """Save OpenAPI specification in JSON and YAML formats"""
    files = []
    
    # JSON format
    json_path = os.path.join(output_dir, "openapi.json")
    with open(json_path, 'w') as f:
        json.dump(spec, f, indent=2)
    files.append(json_path)
    
    # YAML format
    yaml_path = os.path.join(output_dir, "openapi.yaml") 
    try:
        import yaml
        with open(yaml_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        files.append(yaml_path)
    except ImportError:
        print("PyYAML not available, skipping YAML generation")
    
    return files


def _generate_html_documentation(spec: dict, output_dir: str) -> str:
    """Generate HTML documentation"""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .header .version {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .section {
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .section h2 {
            color: #2d3748;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .endpoint {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }
        .method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8em;
            color: white;
            margin-right: 10px;
        }
        .method.get { background-color: #28a745; }
        .method.post { background-color: #007bff; }
        .method.put { background-color: #ffc107; color: #333; }
        .method.delete { background-color: #dc3545; }
        .path {
            font-family: Monaco, monospace;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .description {
            margin: 10px 0;
            color: #6c757d;
        }
        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            margin: 2px;
        }
        .servers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .server {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .server h4 {
            margin: 0 0 5px 0;
            color: #007bff;
        }
        .server .url {
            font-family: Monaco, monospace;
            font-size: 0.9em;
            color: #495057;
        }
        .toc {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .toc h3 {
            margin-top: 0;
            color: #495057;
        }
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        .toc ul ul {
            padding-left: 20px;
            list-style: disc;
        }
        .toc a {
            color: #667eea;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        .generated-info {
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="version">Version {{ version }}</div>
        <p style="margin: 10px 0 0 0;">{{ description_short }}</p>
    </div>

    <div class="toc">
        <h3>📋 Table of Contents</h3>
        <ul>
            <li><a href="#overview">Overview</a></li>
            <li><a href="#servers">Servers</a></li>
            <li><a href="#authentication">Authentication</a></li>
            <li><a href="#rate-limiting">Rate Limiting</a></li>
            <li><a href="#error-handling">Error Handling</a></li>
            <li><a href="#endpoints">API Endpoints</a>
                <ul>
                    {% for tag in tags %}
                    <li><a href="#{{ tag.name.lower().replace(' ', '-') }}">{{ tag.name }}</a></li>
                    {% endfor %}
                </ul>
            </li>
        </ul>
    </div>

    <div class="section" id="overview">
        <h2>🚀 Overview</h2>
        <div>{{ description | safe }}</div>
    </div>

    <div class="section" id="servers">
        <h2>🌐 Servers</h2>
        <div class="servers">
            {% for server in servers %}
            <div class="server">
                <h4>{{ server.description }}</h4>
                <div class="url">{{ server.url }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="section" id="authentication">
        <h2>🔐 Authentication</h2>
        <p>Currently in development mode. Production authentication will be added in future sprints.</p>
    </div>

    <div class="section" id="rate-limiting">
        <h2>⏱️ Rate Limiting</h2>
        <ul>
            <li><strong>Global Limits:</strong> 100 requests/minute, 2000 requests/hour per client</li>
            <li><strong>Headers:</strong> Rate limit info included in response headers</li>
            <li><strong>Bypass:</strong> Health check endpoints excluded from rate limiting</li>
        </ul>
    </div>

    <div class="section" id="error-handling">
        <h2>❌ Error Handling</h2>
        <p>All errors return standardized JSON format with:</p>
        <ul>
            <li><strong>Timestamp:</strong> ISO 8601 timestamp</li>
            <li><strong>Error Type:</strong> Categorized error type</li>
            <li><strong>Request Info:</strong> Method, path, and endpoint context</li>
            <li><strong>Epic Context:</strong> Epic 7 project identification</li>
        </ul>
    </div>

    <div class="section" id="endpoints">
        <h2>📡 API Endpoints</h2>
        
        {% for tag in tags %}
        <div id="{{ tag.name.lower().replace(' ', '-') }}">
            <h3>{{ tag.name }}</h3>
            <p class="description">{{ tag.description }}</p>
            
            {% for path, methods in paths.items() %}
                {% for method, endpoint in methods.items() %}
                    {% if tag.name in endpoint.tags %}
                    <div class="endpoint">
                        <div>
                            <span class="method {{ method.lower() }}">{{ method.upper() }}</span>
                            <span class="path">{{ path }}</span>
                        </div>
                        <h4>{{ endpoint.summary }}</h4>
                        <p class="description">{{ endpoint.description }}</p>
                        {% if endpoint.tags %}
                        <div>
                            {% for endpoint_tag in endpoint.tags %}
                            <span class="tag">{{ endpoint_tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endif %}
                {% endfor %}
            {% endfor %}
        </div>
        {% endfor %}
    </div>

    <div class="generated-info">
        Generated on {{ generated_date }} by Epic 7 Sprint 3 Documentation Generator
    </div>
</body>
</html>
    """
    
    # Prepare template data
    info = spec.get('info', {})
    template_data = {
        'title': info.get('title', 'API Documentation'),
        'version': info.get('version', '1.0.0'),
        'description': info.get('description', '').replace('\n', '<br>'),
        'description_short': 'Epic 7: API Architecture Rationalization - Complete API reference',
        'servers': spec.get('servers', []),
        'tags': spec.get('tags', []),
        'paths': spec.get('paths', {}),
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Render template
    html_content = render_template_string(html_template, **template_data)
    
    # Save HTML file
    html_path = os.path.join(output_dir, "api_documentation.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_path


def _generate_markdown_documentation(spec: dict, output_dir: str) -> str:
    """Generate Markdown documentation"""
    
    info = spec.get('info', {})
    
    md_content = f"""# {info.get('title', 'API Documentation')}

**Version:** {info.get('version', '1.0.0')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{info.get('description', '')}

## 🌐 Servers

"""
    
    for server in spec.get('servers', []):
        md_content += f"- **{server.get('description', 'Server')}**: `{server.get('url', '')}`\n"
    
    md_content += """
## 📡 API Endpoints

"""
    
    # Group endpoints by tags
    for tag in spec.get('tags', []):
        md_content += f"### {tag.get('name', '')}\n\n"
        md_content += f"{tag.get('description', '')}\n\n"
        
        # Find endpoints for this tag
        for path, methods in spec.get('paths', {}).items():
            for method, endpoint in methods.items():
                if tag.get('name') in endpoint.get('tags', []):
                    md_content += f"#### `{method.upper()}` {path}\n\n"
                    md_content += f"**Summary:** {endpoint.get('summary', '')}\n\n"
                    md_content += f"{endpoint.get('description', '')}\n\n"
                    
                    # Add responses
                    responses = endpoint.get('responses', {})
                    if responses:
                        md_content += "**Responses:**\n"
                        for status, response_info in responses.items():
                            md_content += f"- `{status}`: {response_info.get('description', '')}\n"
                        md_content += "\n"
        
        md_content += "---\n\n"
    
    md_content += f"""
## 📝 Additional Information

### Rate Limiting
- **Global Limits**: 100 requests/minute, 2000 requests/hour per client
- **Headers**: Rate limit info included in response headers
- **Bypass**: Health check endpoints excluded from rate limiting

### Error Handling
All errors return standardized JSON format with:
- **Timestamp**: ISO 8601 timestamp
- **Error Type**: Categorized error type  
- **Request Info**: Method, path, and endpoint context
- **Epic Context**: Epic 7 project identification

### Authentication
Currently in development mode. Production authentication will be added in future sprints.

---
*Generated by Epic 7 Sprint 3 Documentation Generator*
"""
    
    # Save Markdown file
    md_path = os.path.join(output_dir, "API_DOCUMENTATION.md")
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    return md_path


def _generate_swagger_ui(spec: dict, output_dir: str) -> list:
    """Generate Swagger UI for interactive documentation"""
    
    swagger_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PineOpt API - Interactive Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        .topbar { display: none !important; }
        .swagger-ui .info .title { color: #667eea; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const spec = """ + json.dumps(spec) + """;
            
            const ui = SwaggerUIBundle({
                spec: spec,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null
            });
        };
    </script>
</body>
</html>
    """
    
    swagger_path = os.path.join(output_dir, "swagger-ui.html")
    with open(swagger_path, 'w') as f:
        f.write(swagger_html)
    
    return [swagger_path]


def _generate_postman_collection(spec: dict, output_dir: str) -> str:
    """Generate Postman collection from OpenAPI spec"""
    
    info = spec.get('info', {})
    servers = spec.get('servers', [])
    base_url = servers[0].get('url', 'http://localhost:5007') if servers else 'http://localhost:5007'
    
    collection = {
        "info": {
            "name": info.get('title', 'PineOpt API'),
            "description": info.get('description', ''),
            "version": info.get('version', '1.0.0'),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "baseUrl",
                "value": base_url,
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group endpoints by tags
    for tag in spec.get('tags', []):
        tag_folder = {
            "name": tag.get('name', ''),
            "description": tag.get('description', ''),
            "item": []
        }
        
        # Add endpoints for this tag
        for path, methods in spec.get('paths', {}).items():
            for method, endpoint in methods.items():
                if tag.get('name') in endpoint.get('tags', []):
                    request_item = {
                        "name": endpoint.get('summary', f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "url": {
                                "raw": "{{baseUrl}}" + path,
                                "host": ["{{baseUrl}}"],
                                "path": path.strip('/').split('/') if path != '/' else []
                            },
                            "description": endpoint.get('description', '')
                        }
                    }
                    
                    # Add request body for POST/PUT requests
                    if method.lower() in ['post', 'put'] and 'requestBody' in endpoint:
                        request_body = endpoint['requestBody']
                        if 'application/json' in request_body.get('content', {}):
                            schema_content = request_body['content']['application/json']
                            if 'example' in schema_content:
                                request_item["request"]["body"] = {
                                    "mode": "raw",
                                    "raw": json.dumps(schema_content['example'], indent=2),
                                    "options": {
                                        "raw": {
                                            "language": "json"
                                        }
                                    }
                                }
                    
                    tag_folder["item"].append(request_item)
        
        if tag_folder["item"]:  # Only add folder if it has items
            collection["item"].append(tag_folder)
    
    # Save Postman collection
    postman_path = os.path.join(output_dir, "PineOpt_API.postman_collection.json")
    with open(postman_path, 'w') as f:
        json.dump(collection, f, indent=2)
    
    return postman_path


def create_interactive_docs(app: Flask, route_prefix: str = "/docs"):
    """Add interactive documentation routes to the Flask app"""
    
    @app.route(f"{route_prefix}/")
    def docs_index():
        """Documentation index page"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PineOpt API Documentation</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }
                .header { text-align: center; margin-bottom: 40px; }
                .links { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
                .link-card { 
                    background: white; border: 1px solid #ddd; border-radius: 8px; 
                    padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .link-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
                .link-card h3 { margin-top: 0; color: #667eea; }
                .link-card a { color: #667eea; text-decoration: none; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 PineOpt API Documentation</h1>
                <p>Epic 7: API Architecture Rationalization</p>
            </div>
            <div class="links">
                <div class="link-card">
                    <h3>📋 Interactive API Explorer</h3>
                    <p>Swagger UI for testing endpoints</p>
                    <a href="{{ url_for('docs_swagger') }}">Open Swagger UI →</a>
                </div>
                <div class="link-card">
                    <h3>📖 API Specification</h3>
                    <p>OpenAPI JSON specification</p>
                    <a href="{{ url_for('docs_openapi') }}">View OpenAPI Spec →</a>
                </div>
                <div class="link-card">
                    <h3>🏥 System Health</h3>
                    <p>Check API health status</p>
                    <a href="/api/v1/health/">Health Check →</a>
                </div>
                <div class="link-card">
                    <h3>⚙️ Configuration</h3>
                    <p>Middleware and system config</p>
                    <a href="/api/v1/rate-limit/status">Rate Limits →</a>
                </div>
            </div>
        </body>
        </html>
        """)
    
    @app.route(f"{route_prefix}/openapi.json")
    def docs_openapi():
        """Return OpenAPI specification"""
        return generate_openapi_spec(app)
    
    @app.route(f"{route_prefix}/swagger")
    def docs_swagger():
        """Interactive Swagger UI"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PineOpt API - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
            <style>
                .topbar { display: none !important; }
                .swagger-ui .info .title { color: #667eea; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    const ui = SwaggerUIBundle({
                        url: '{{ url_for("docs_openapi") }}',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout",
                        validatorUrl: null
                    });
                };
            </script>
        </body>
        </html>
        """)
    
    return app