# --- START OF FILE app.py ---

import streamlit as st
import streamlit.components.v1 as components
import base64
import json

# --- Page Configuration ---
# Set the page to a wide layout with a dark theme by default.
st.set_page_config(layout="wide", page_title="Mermaid Diagram Generator")

# --- HTML & JavaScript Component ---
# This self-contained component handles the frontend, including the dark theme styling,
# Mermaid.js rendering, and the SVG/PNG download logic.
def get_mermaid_component(mermaid_code):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Component</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        /* --- Dark Theme Styling --- */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            background-color: #0e1117;
            color: #f0f6fc;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 100%;
        }}
        .buttons {{
            margin: 15px 0;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        button {{
            background-color: #21262d;
            border: 1px solid #30363d;
            color: #f0f6fc;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        button:hover {{
            background-color: #30363d;
            border-color: #8b949e;
        }}
        button:disabled {{
            background-color: #161b22;
            color: #8b949e;
            cursor: not-allowed;
            border-color: #30363d;
        }}
        /* Specific styles for download buttons */
        #download-svg-btn {{
            background-color: #238636; /* Green */
        }}
        #download-svg-btn:hover {{
            background-color: #2ea043;
        }}
        #download-png-btn {{
            background-color: #1f6feb; /* Blue */
        }}
        #download-png-btn:hover {{
            background-color: #388bfd;
        }}
        .mermaid-output {{
            margin-top: 20px;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            background-color: #0d1117;
            overflow: auto;
            min-height: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        /* Style for error messages */
        .mermaid-output pre {{
            background-color: rgba(248, 81, 73, 0.1);
            color: #f85149;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="buttons">
            <button id="render-btn">Render Diagram</button>
            <button id="download-svg-btn" disabled>Download SVG</button>
            <button id="download-png-btn" disabled>Download PNG</button>
        </div>
        <div id="output" class="mermaid-output">
            <p style="color: #8b949e;">Your rendered diagram will appear here.</p>
        </div>
    </div>

    <script>
        // Mermaid code injected from Streamlit
        const mermaidCode = {json.dumps(mermaid_code)};

        document.addEventListener("DOMContentLoaded", function () {{
            mermaid.initialize({{ startOnLoad: false, theme: 'dark' }});

            let currentSvgData = "";
            const outputDiv = document.getElementById("output");
            const renderBtn = document.getElementById("render-btn");
            const downloadSvgBtn = document.getElementById("download-svg-btn");
            const downloadPngBtn = document.getElementById("download-png-btn");

            const renderDiagram = async () => {{
                if (!mermaidCode.trim()) {{
                    outputDiv.innerHTML = "<p style='color: #8b949e;'>Enter Mermaid code in the text area to get started.</p>";
                    return;
                }}
                
                outputDiv.innerHTML = "Rendering...";
                downloadSvgBtn.disabled = true;
                downloadPngBtn.disabled = true;
                currentSvgData = "";

                try {{
                    const graphId = "graphDiv_" + new Date().getTime();
                    const {{ svg }} = await mermaid.render(graphId, mermaidCode);
                    outputDiv.innerHTML = svg;
                    currentSvgData = svg;
                    downloadSvgBtn.disabled = false;
                    downloadPngBtn.disabled = false;
                }} catch (err) {{
                    const errorMessage = err.message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    outputDiv.innerHTML = `<pre><b>Error:</b>\\n${{errorMessage}}</pre>`;
                }}
            }};
            
            renderBtn.addEventListener("click", renderDiagram);

            downloadSvgBtn.addEventListener("click", () => {{
                if (!currentSvgData) return;
                const blob = new Blob([currentSvgData], {{ type: "image/svg+xml;charset=utf-8" }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = "diagram.svg";
                link.click();
                URL.revokeObjectURL(url);
            }});

            downloadPngBtn.addEventListener("click", () => {{
                if (!currentSvgData) return;

                const img = new Image();
                const svgBlob = new Blob([currentSvgData], {{ type: 'image/svg+xml' }});
                const url = URL.createObjectURL(svgBlob);

                img.onload = function() {{
                    const scale = 3; // For high-resolution PNG
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width * scale;
                    canvas.height = img.height * scale;
                    
                    const ctx = canvas.getContext('2d');
                    // Fill background with white for better compatibility
                    ctx.fillStyle = '#FFFFFF';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                    const link = document.createElement('a');
                    link.download = 'diagram.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    URL.revokeObjectURL(url);
                }};
                
                img.onerror = () => URL.revokeObjectURL(url);
                img.src = url;
            }});

            // Initial render on page load
            renderDiagram();
        }});
    </script>
</body>
</html>
"""

# --- Streamlit App Layout ---

st.title("Mermaid Diagram Generator")
st.write("Enter your Mermaid code on the left and see the rendered diagram on the right. Download as SVG or high-resolution PNG.")

# Default example code to get users started
default_code = """graph TD
    A[Start] --> B{Is it?}
    B -->|Yes| C[OK]
    C --> D[Rethink]
    D --> B
    B ---->|No| E[End]"""

col1, col2 = st.columns(spec=[1, 1], gap="large")

with col1:
    st.subheader("Mermaid Code")
    if 'mermaid_code' not in st.session_state:
        st.session_state.mermaid_code = default_code
    
    mermaid_code_input = st.text_area(
        "Enter your Mermaid code below:", 
        height=750, 
        key="mermaid_code",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("Rendered Diagram")
    
    # Generate the HTML component with the current Mermaid code
    component_html = get_mermaid_component(mermaid_code_input)
    
    # Render the component
    components.html(component_html, height=800, scrolling=True)