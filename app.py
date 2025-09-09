import streamlit as st
import streamlit.components.v1 as components
import json

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Mermaid Diagram Generator")

def get_mermaid_component(mermaid_code):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Component</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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
        #download-svg-btn {{
            background-color: #238636;
        }}
        #download-svg-btn:hover:not(:disabled) {{
            background-color: #2ea043;
        }}
        #download-png-btn {{
            background-color: #1f6feb;
        }}
        #download-png-btn:hover:not(:disabled) {{
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
        .mermaid-output pre {{
            background-color: rgba(248, 81, 73, 0.1);
            color: #f85149;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            width: 100%;
        }}
        .mermaid-output svg {{
            max-width: 100%;
            height: auto;
            background-color: white;
            border-radius: 4px;
        }}
        #mermaid-container {{
            background-color: white;
            border-radius: 4px;
            padding: 20px;
            display: inline-block;
            min-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="buttons">
            <button id="render-btn">Render Diagram</button>
            <button id="download-svg-btn" disabled>Download SVG</button>
            <button id="download-png-btn" disabled>Download PNG (5x)</button>
        </div>
        <div id="output" class="mermaid-output">
            <p style="color: #8b949e;">Your rendered diagram will appear here.</p>
        </div>
    </div>

    <script>
        const mermaidCode = {json.dumps(mermaid_code)};
        let currentSvgData = "";
        let currentDiagramId = "";

        document.addEventListener("DOMContentLoaded", function () {{
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'default',
                flowchart: {{
                    htmlLabels: true,
                    curve: 'basis',
                    useMaxWidth: true,
                    nodeSpacing: 50,
                    rankSpacing: 50
                }}
            }});

            const outputDiv = document.getElementById("output");
            const renderBtn = document.getElementById("render-btn");
            const downloadSvgBtn = document.getElementById("download-svg-btn");
            const downloadPngBtn = document.getElementById("download-png-btn");

            const renderDiagram = async () => {{
                if (!mermaidCode.trim()) {{
                    outputDiv.innerHTML = "<p style='color: #8b949e;'>Enter Mermaid code in the text area to get started.</p>";
                    return;
                }}

                outputDiv.innerHTML = "Rendering diagram...";
                downloadSvgBtn.disabled = true;
                downloadPngBtn.disabled = true;
                currentSvgData = "";

                try {{
                    currentDiagramId = "mermaid-" + Date.now();
                    const {{ svg }} = await mermaid.render(currentDiagramId, mermaidCode);

                    outputDiv.innerHTML = `<div id="mermaid-container">${{svg}}</div>`;
                    currentSvgData = svg;

                    downloadSvgBtn.disabled = false;
                    downloadPngBtn.disabled = false;
                }} catch (err) {{
                    console.error("Mermaid render error:", err);
                    const errorMessage = err.message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    outputDiv.innerHTML = `<pre><b>Mermaid Error:</b>\\n${{errorMessage}}</pre>`;
                }}
            }};

            renderBtn.addEventListener("click", renderDiagram);

            downloadSvgBtn.addEventListener("click", () => {{
                if (!currentSvgData) return;

                try {{
                    const parser = new DOMParser();
                    const svgDoc = parser.parseFromString(currentSvgData, "image/svg+xml");
                    const svgEl = svgDoc.documentElement;

                    if (!svgEl.getAttribute("width") || !svgEl.getAttribute("height")) {{
                        const vb = svgEl.getAttribute("viewBox")?.split(" ");
                        if (vb && vb.length === 4) {{
                            svgEl.setAttribute("width", vb[2]);
                            svgEl.setAttribute("height", vb[3]);
                        }} else {{
                            svgEl.setAttribute("width", "1200");
                            svgEl.setAttribute("height", "800");
                        }}
                    }}
                    svgEl.setAttribute("style", "background-color:white");

                    const enhancedSvg = new XMLSerializer().serializeToString(svgEl);

                    const blob = new Blob([enhancedSvg], {{
                        type: "image/svg+xml;charset=utf-8"
                    }});
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = "mermaid-diagram.svg";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                }} catch (error) {{
                    console.error("SVG download error:", error);
                    alert("Failed to download SVG: " + error.message);
                }}
            }});

            downloadPngBtn.addEventListener("click", async () => {{
                if (!currentSvgData) return;

                const originalText = downloadPngBtn.textContent;
                downloadPngBtn.disabled = true;
                downloadPngBtn.textContent = 'Generating PNG...';

                try {{
                    const container = document.getElementById('mermaid-container');
                    const svgElement = container ? container.querySelector('svg') : null;

                    if (!svgElement) {{
                        throw new Error('No SVG element found');
                    }}

                    let svgWidth = parseInt(svgElement.getAttribute("width"));
                    let svgHeight = parseInt(svgElement.getAttribute("height"));

                    if (!svgWidth || !svgHeight) {{
                        if (svgElement.viewBox && svgElement.viewBox.baseVal) {{
                            svgWidth = svgElement.viewBox.baseVal.width || 1200;
                            svgHeight = svgElement.viewBox.baseVal.height || 800;
                        }} else {{
                            svgWidth = 1200;
                            svgHeight = 800;
                        }}
                    }}

                    const svgClone = svgElement.cloneNode(true);
                    svgClone.setAttribute('width', svgWidth);
                    svgClone.setAttribute('height', svgHeight);
                    svgClone.style.backgroundColor = 'white';

                    const svgString = new XMLSerializer().serializeToString(svgClone);
                    const svgDataUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));

                    const scale = 5;
                    const canvas = document.createElement('canvas');
                    canvas.width = svgWidth * scale;
                    canvas.height = svgHeight * scale;

                    const ctx = canvas.getContext('2d');
                    ctx.imageSmoothingEnabled = false;
                    ctx.fillStyle = '#FFFFFF';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    const img = new Image();
                    img.onload = function() {{
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                        canvas.toBlob(function(blob) {{
                            if (blob) {{
                                const url = URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = 'mermaid-diagram-5x.png';
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                URL.revokeObjectURL(url);
                            }} else {{
                                throw new Error('Failed to create PNG blob');
                            }}
                        }}, 'image/png', 1.0);
                    }};
                    img.onerror = function() {{
                        throw new Error('Failed to load SVG image');
                    }};
                    img.src = svgDataUrl;

                }} catch (error) {{
                    console.error("PNG download error:", error);
                    alert("Failed to generate PNG: " + error.message);
                }} finally {{
                    downloadPngBtn.disabled = false;
                    downloadPngBtn.textContent = originalText;
                }}
            }});

            if (mermaidCode.trim()) {{
                renderDiagram();
            }}
        }});
    </script>
</body>
</html>
"""

# --- Streamlit App Layout ---
st.title("🧜‍♀️ Mermaid Diagram Generator")
st.write("Create beautiful diagrams with Mermaid syntax. Enter your code on the left and see the high-quality rendered diagram on the right.")

# Example default
default_code = """graph TB
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px"""

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Mermaid Code")

    with st.expander("📚 Example Diagrams"):
        st.markdown("""
        **Flowchart:**
        ```
        graph TD
            A[Start] --> B{Decision}
            B -->|Yes| C[Action 1]
            B -->|No| D[Action 2]
        ```
        
        **Sequence Diagram:**
        ```
        sequenceDiagram
            Alice->>John: Hello John, how are you?
            John-->>Alice: Great!
        ```
        
        **Gantt Chart:**
        ```
        gantt
            title A Gantt Diagram
            dateFormat  YYYY-MM-DD
            section Section
            A task           :a1, 2014-01-01, 30d
        ```
        """)

    if 'mermaid_code' not in st.session_state:
        st.session_state.mermaid_code = default_code

    mermaid_code_input = st.text_area(
        "Enter your Mermaid code:",
        height=600,
        key="mermaid_code",
        placeholder="Enter your Mermaid diagram code here...",
        help="Write your Mermaid diagram syntax here. The diagram will auto-render."
    )

with col2:
    st.subheader("🎨 Rendered Diagram")
    component_html = get_mermaid_component(mermaid_code_input)
    components.html(component_html, height=700, scrolling=True)

st.markdown("---")
st.markdown("""
**💡 Tips:**
- Diagrams render automatically when you type  
- Use the white background for better contrast  
- PNG downloads are 5x resolution for crisp printing  
- SVG downloads are vector format for infinite scaling  

**🔗 Mermaid Documentation:** [mermaid.js.org](https://mermaid.js.org/)
""")
