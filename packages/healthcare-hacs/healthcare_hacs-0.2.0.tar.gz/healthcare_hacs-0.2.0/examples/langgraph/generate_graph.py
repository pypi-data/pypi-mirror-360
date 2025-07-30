#!/usr/bin/env python3
"""
Generate visual representation of the HACS + LangGraph workflow.

This script creates a PNG image of the workflow graph using LangGraph's
built-in visualization capabilities.
"""

import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from graph import create_workflow_graph


def generate_workflow_image():
    """Generate and save the workflow graph image."""

    print("🎨 Generating LangGraph workflow visualization...")

    try:
        # Create the workflow graph
        app = create_workflow_graph()

        # Try to generate the graph visualization
        try:
            # This creates a PNG image of the workflow
            graph_image = app.get_graph().draw_mermaid_png()

            # Save the image
            output_path = "langgraph_workflow.png"
            with open(output_path, "wb") as f:
                f.write(graph_image)

            print(f"✅ Workflow graph saved as: {output_path}")
            print("📊 Graph shows the complete clinical assessment workflow")

            return output_path

        except ImportError as e:
            print(f"⚠️  Visualization dependencies not available: {e}")
            print("💡 To enable graph visualization:")
            print(
                "   1. Install system graphviz: apt-get install graphviz (Ubuntu) or brew install graphviz (macOS)"
            )
            print("   2. Install Python bindings: pip install pygraphviz")
            print("   3. Alternative: pip install graphviz (Python-only)")

            # Generate text representation instead
            return generate_text_representation(app)

        except Exception as viz_error:
            print(f"⚠️  Graph visualization failed: {viz_error}")
            print("💡 Falling back to text representation...")
            return generate_text_representation(app)

    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None


def generate_text_representation(app):
    """Generate a text representation of the workflow when visualization fails."""
    try:
        # Get the graph structure
        graph = app.get_graph()

        # Create text representation
        text_output = []
        text_output.append("🏥 HACS + LangGraph Clinical Workflow Structure")
        text_output.append("=" * 50)
        text_output.append("")
        text_output.append("Nodes:")

        # List all nodes
        for node_id in graph.nodes:
            text_output.append(f"  • {node_id}")

        text_output.append("")
        text_output.append("Edges (workflow flow):")

        # List all edges
        for edge in graph.edges:
            text_output.append(f"  {edge.source} → {edge.target}")

        text_output.append("")
        text_output.append("Workflow sequence:")
        text_output.append("  1. Initialize → Set up patient data and system messages")
        text_output.append("  2. Assess Risk → Calculate cardiovascular risk from BP")
        text_output.append("  3. Search Evidence → Find relevant clinical guidelines")
        text_output.append("  4. Generate Recommendations → Create treatment plan")
        text_output.append("")
        text_output.append("📝 For visual diagram, install: pip install pygraphviz")

        # Save text representation
        output_path = "langgraph_workflow.txt"
        with open(output_path, "w") as f:
            f.write("\n".join(text_output))

        print(f"📄 Text representation saved as: {output_path}")
        print("🔍 Contains workflow structure and node descriptions")

        return output_path

    except Exception as e:
        print(f"❌ Error generating text representation: {e}")
        return None


if __name__ == "__main__":
    generate_workflow_image()
