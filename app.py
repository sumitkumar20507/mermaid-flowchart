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
        #download-pdf-btn {{
            background-color: #1f6feb;
        }}
        #download-pdf-btn:hover:not(:disabled) {{
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
            <button id="download-pdf-btn" disabled>Download PDF</button>
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
            const downloadPdfBtn = document.getElementById("download-pdf-btn");

            const renderDiagram = async () => {{
                if (!mermaidCode.trim()) {{
                    outputDiv.innerHTML = "<p style='color: #8b949e;'>Enter Mermaid code in the text area to get started.</p>";
                    return;
                }}

                outputDiv.innerHTML = "Rendering diagram...";
                downloadSvgBtn.disabled = true;
                downloadPdfBtn.disabled = true;
                currentSvgData = "";

                try {{
                    currentDiagramId = "mermaid-" + Date.now();
                    const {{ svg }} = await mermaid.render(currentDiagramId, mermaidCode);

                    outputDiv.innerHTML = `<div id="mermaid-container">${{svg}}</div>`;
                    currentSvgData = svg;

                    downloadSvgBtn.disabled = false;
                    downloadPdfBtn.disabled = false;
                }} catch (err) {{
                    console.error("Mermaid render error:", err);
                    const errorMessage = err.message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    outputDiv.innerHTML = `<pre><b>Mermaid Error:</b>\\n${{errorMessage}}</pre>`;
                }}
            }};

            renderBtn.addEventListener("click", renderDiagram);

            // --- SVG Download ---
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

            // --- PDF Export (single page, zoomable vector) ---
            downloadPdfBtn.addEventListener("click", () => {{
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

                    const svgString = new XMLSerializer().serializeToString(svgEl);
                    const blob = new Blob([svgString], {{ type: "image/svg+xml;charset=utf-8" }});
                    const url = URL.createObjectURL(blob);

                    const printWindow = window.open("", "_blank");
                    printWindow.document.write(`
                        <html>
                        <head>
                            <title>Mermaid PDF Export</title>
                            <style>
                                @page {{
                                    size: A4 landscape;
                                    margin: 0;
                                }}
                                html, body {{
                                    margin: 0;
                                    padding: 0;
                                    height: 100%;
                                    width: 100%;
                                }}
                                img {{
                                    width: 100%;
                                    height: 100%;
                                    object-fit: contain; /* Ensures diagram fits exactly one page */
                                }}
                            </style>
                        </head>
                        <body>
                            <img src="${{url}}" onload="window.print();">
                        </body>
                        </html>
                    `);
                    printWindow.document.close();

                }} catch (error) {{
                    console.error("PDF export error:", error);
                    alert("Failed to export PDF: " + error.message);
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
- SVG downloads are vector format for infinite scaling  
- PDF downloads are **single-page, zoomable vector diagrams**  

**🔗 Mermaid Documentation:** [mermaid.js.org](https://mermaid.js.org/)
""")
