#!/usr/bin/env python3
"""
Documentation Generation Script
Epic 7 Sprint 3 - Task 2: Generate API Documentation

Generates comprehensive API documentation for Epic 7 consolidated architecture.
"""

import os
import sys
from app import create_app
from docs.doc_generator import generate_documentation
from docs.openapi_spec import save_openapi_spec


def main():
    """Generate comprehensive API documentation"""
    
    print("📚 Epic 7 Sprint 3 - Generating API Documentation")
    print("=" * 60)
    
    # Create Flask app
    app = create_app('development')
    
    # Set up output directory
    output_dir = os.path.join(os.path.dirname(__file__), "docs", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    print()
    
    with app.app_context():
        try:
            # Generate all documentation formats
            print("🚀 Generating documentation...")
            generated_files = generate_documentation(app, output_dir)
            
            print("✅ Documentation generated successfully!")
            print()
            print("📄 Generated Files:")
            for file_path in generated_files:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  • {os.path.basename(file_path)} ({file_size:,} bytes)")
            
            print()
            print("🌐 Interactive Documentation:")
            print(f"  • Documentation Hub: http://localhost:5007/docs/")
            print(f"  • Swagger UI: http://localhost:5007/docs/swagger")
            print(f"  • OpenAPI Spec: http://localhost:5007/docs/openapi.json")
            print(f"  • API Info: http://localhost:5007/api")
            
            print()
            print("📊 Documentation Summary:")
            
            # Count endpoints
            from docs.openapi_spec import generate_openapi_spec
            spec = generate_openapi_spec(app)
            
            total_endpoints = 0
            endpoints_by_tag = {}
            
            for path, methods in spec.get('paths', {}).items():
                for method, endpoint in methods.items():
                    total_endpoints += 1
                    for tag in endpoint.get('tags', ['Untagged']):
                        endpoints_by_tag[tag] = endpoints_by_tag.get(tag, 0) + 1
            
            print(f"  • Total Endpoints: {total_endpoints}")
            print(f"  • API Categories: {len(spec.get('tags', []))}")
            print(f"  • Servers Configured: {len(spec.get('servers', []))}")
            
            print()
            print("📋 Endpoints by Category:")
            for tag in spec.get('tags', []):
                tag_name = tag.get('name', 'Unknown')
                count = endpoints_by_tag.get(tag_name, 0)
                print(f"  • {tag_name}: {count} endpoints")
            
            print()
            print("🎯 Epic 7 Sprint 2 Components Documented:")
            print("  ✅ Consolidated Blueprints (5 blueprints)")
            print("  ✅ Production Middleware (4 middleware components)")
            print("  ✅ Standardized Responses (consistent format)")
            print("  ✅ Health Monitoring (comprehensive status)")
            print("  ✅ Error Handling (standardized errors)")
            
        except Exception as e:
            print(f"❌ Error generating documentation: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print()
    print("🎉 Epic 7 Sprint 3 Task 2 - API Documentation Complete!")
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)