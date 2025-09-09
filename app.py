# --- START OF FILE app.py ---

import streamlit as st
import base64

# Set page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Mermaid Diagram Generator")

# --- HTML & JavaScript Component ---
# This component contains all the frontend logic: rendering the diagram
# and handling SVG/PNG downloads. It's a self-contained unit.
mermaid_component = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Component</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 100%;
        }
        .buttons {
            margin: 15px 0;
            text-align: left;
        }
        button {
            background: #007bff;
            border: none;
            color: #fff;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 1em;
            margin: 0 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
        #download-png-btn {
            background-color: #28a745;
        }
        #download-png-btn:hover {
            background-color: #218838;
        }
        .mermaid-output {
            margin-top: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fff;
            overflow: auto;
            min-height: 200px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .mermaid-output pre {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
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
            <p>Your rendered diagram will appear here.</p>
        </div>
    </div>

    <script>
        // Use a placeholder for the mermaid code that Streamlit will replace
        const mermaidCode = `%MERMAID_CODE%`;

        document.addEventListener("DOMContentLoaded", function () {
            mermaid.initialize({ startOnLoad: false });

            let currentSvgData = "";
            const outputDiv = document.getElementById("output");
            const renderBtn = document.getElementById("render-btn");
            const downloadSvgBtn = document.getElementById("download-svg-btn");
            const downloadPngBtn = document.getElementById("download-png-btn");

            // Main rendering function
            const renderDiagram = async () => {
                if (!mermaidCode.trim()) {
                    outputDiv.innerHTML = "<p>Enter some Mermaid code in the text area above to get started.</p>";
                    return;
                }
                
                outputDiv.innerHTML = "Rendering...";
                downloadSvgBtn.disabled = true;
                downloadPngBtn.disabled = true;
                currentSvgData = "";

                try {
                    // Unique ID for each render to avoid caching issues
                    const graphId = "graphDiv_" + new Date().getTime();
                    const { svg } = await mermaid.render(graphId, mermaidCode);
                    outputDiv.innerHTML = svg;
                    currentSvgData = svg;
                    downloadSvgBtn.disabled = false;
                    downloadPngBtn.disabled = false;
                } catch (err) {
                    const errorMessage = err.message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    outputDiv.innerHTML = `<pre><b>Error:</b>\\n${errorMessage}</pre>`;
                }
            };
            
            // Event Listeners
            renderBtn.addEventListener("click", renderDiagram);

            downloadSvgBtn.addEventListener("click", () => {
                if (!currentSvgData) {
                    alert("Please render a diagram first!");
                    return;
                }
                const blob = new Blob([currentSvgData], { type: "image/svg+xml;charset=utf-8" });
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = "diagram.svg";
                link.click();
                URL.revokeObjectURL(url);
            });

            downloadPngBtn.addEventListener("click", () => {
                if (!currentSvgData) {
                    alert("Please render a diagram first!");
                    return;
                }

                // --- Canvas-based PNG Conversion ---
                const img = new Image();
                const svgBlob = new Blob([currentSvgData], { type: 'image/svg+xml' });
                const url = URL.createObjectURL(svgBlob);

                img.onload = function() {
                    // Define a scale for higher resolution
                    const scale = 3; 

                    const canvas = document.createElement('canvas');
                    canvas.width = img.width * scale;
                    canvas.height = img.height * scale;
                    
                    const ctx = canvas.getContext('2d');
                    // Fill background with white, otherwise it will be transparent
                    ctx.fillStyle = '#FFFFFF';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // Draw the SVG image on the canvas
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                    // Trigger download
                    const link = document.createElement('a');
                    link.download = 'diagram.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();

                    // Clean up the object URL
                    URL.revokeObjectURL(url);
                };
                
                img.onerror = function() {
                    alert("Failed to load SVG for PNG conversion.");
                    URL.revokeObjectURL(url);
                }

                img.src = url;
            });

            // Initial render on load
            renderDiagram();
        });
    </script>
</body>
</html>
"""

# --- Streamlit App Layout ---

st.title("Meruflownaut: An Enhanced Mermaid Diagram Generator")
st.write("Create, render, and download high-quality diagrams with ease. Powered by Streamlit and Mermaid.js.")

# Example code for the user
default_code = """
graph TD
    A[Start] --> B{Is it working?};
    B -- Yes --> C[Great!];
    B -- No --> D[Check console];
    C --> E[Finish];
    D --> B;
"""

# Two-column layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Mermaid Code")
    # Using session state to preserve code between reruns
    if 'mermaid_code' not in st.session_state:
        st.session_state.mermaid_code = default_code
    
    mermaid_code_input = st.text_area(
        "Enter your Mermaid code below:", 
        height=700, 
        key="mermaid_code",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("Rendered Diagram")
    
    # Escape backticks and other special characters for JavaScript
    escaped_code = base64.b64encode(mermaid_code_input.encode('utf-8')).decode('utf-8')
    
    # Inject the user's code into the HTML component
    component_with_code = mermaid_component.replace(
        "'%MERMAID_CODE%'", 
        f"atob('{escaped_code}')"
    )
    
    st.components.v1.html(component_with_code, height=800, scrolling=True)