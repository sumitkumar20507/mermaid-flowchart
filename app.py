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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
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
        .loading {{
            color: #8b949e;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .spinner {{
            border: 2px solid #30363d;
            border-top: 2px solid #1f6feb;
            border-radius: 50%;
            width: 16px;
            height: 16px;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
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
                }},
                // High DPI settings for better quality
                dpi: 300,
                scale: 2
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

                outputDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Rendering diagram...</div>';
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

            // --- Enhanced PDF Export with Auto Page Sizing ---
            downloadPdfBtn.addEventListener("click", async () => {{
                if (!currentSvgData) return;

                try {{
                    downloadPdfBtn.disabled = true;
                    downloadPdfBtn.textContent = "Generating PDF...";

                    // Parse SVG and get dimensions
                    const parser = new DOMParser();
                    const svgDoc = parser.parseFromString(currentSvgData, "image/svg+xml");
                    const svgEl = svgDoc.documentElement;

                    // Create a temporary canvas to render SVG
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    // Get SVG dimensions
                    let svgWidth = parseFloat(svgEl.getAttribute('width')) || 800;
                    let svgHeight = parseFloat(svgEl.getAttribute('height')) || 600;

                    // If no width/height, try viewBox
                    if (!svgEl.getAttribute('width') && svgEl.getAttribute('viewBox')) {{
                        const viewBox = svgEl.getAttribute('viewBox').split(' ');
                        svgWidth = parseFloat(viewBox[2]);
                        svgHeight = parseFloat(viewBox[3]);
                    }}

                    // High resolution for better quality
                    const scale = 3;
                    canvas.width = svgWidth * scale;
                    canvas.height = svgHeight * scale;

                    // Create image from SVG
                    const img = new Image();
                    
                    await new Promise((resolve, reject) => {{
                        img.onload = () => {{
                            // Fill canvas with white background
                            ctx.fillStyle = 'white';
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            
                            // Draw image scaled
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            resolve();
                        }};
                        img.onerror = reject;
                        
                        // Convert SVG to data URL
                        const svgBlob = new Blob([currentSvgData], {{type: 'image/svg+xml;charset=utf-8'}});
                        const url = URL.createObjectURL(svgBlob);
                        img.src = url;
                    }});

                    // Convert canvas to image data
                    const imgData = canvas.toDataURL('image/jpeg', 1.0);

                    // Calculate page size in mm (with margins)
                    const margin = 10; // 10mm margin
                    const maxWidth = 297 - (margin * 2); // A4 width minus margins
                    const maxHeight = 420 - (margin * 2); // A4 height minus margins (extended for larger diagrams)

                    // Calculate actual dimensions in mm
                    const aspectRatio = svgWidth / svgHeight;
                    let pdfWidth, pdfHeight;

                    if (aspectRatio > 1) {{
                        // Landscape-ish
                        pdfWidth = Math.min(maxWidth, svgWidth * 0.75);
                        pdfHeight = pdfWidth / aspectRatio;
                    }} else {{
                        // Portrait-ish
                        pdfHeight = Math.min(maxHeight, svgHeight * 0.75);
                        pdfWidth = pdfHeight * aspectRatio;
                    }}

                    // Create PDF with custom page size
                    const {{ jsPDF }} = window.jspdf;
                    const pdf = new jsPDF({{
                        orientation: aspectRatio > 1 ? 'landscape' : 'portrait',
                        unit: 'mm',
                        format: [pdfWidth + (margin * 2), pdfHeight + (margin * 2)]
                    }});

                    // Add image to PDF
                    pdf.addImage(imgData, 'JPEG', margin, margin, pdfWidth, pdfHeight);

                    // Download PDF
                    pdf.save('mermaid-diagram.pdf');

                }} catch (error) {{
                    console.error("PDF export error:", error);
                    alert("Failed to export PDF: " + error.message);
                }} finally {{
                    downloadPdfBtn.disabled = false;
                    downloadPdfBtn.textContent = "Download PDF";
                }}
            }});

            // Auto-render if code is provided
            if (mermaidCode.trim()) {{
                renderDiagram();
            }}
        }});
    </script>
</body>
</html>
"""

# --- Streamlit App Layout ---
st.title("Mermaid Diagram Generator")
st.write("Create diagrams with Mermaid syntax. Enter your code on the left and render it on the right.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Mermaid Code")

    if 'mermaid_code' not in st.session_state:
        st.session_state.mermaid_code = ""  # Empty by default

    mermaid_code_input = st.text_area(
        "Enter your Mermaid code:",
        height=600,
        key="mermaid_code",
        placeholder="Enter your Mermaid diagram code here..."
    )

    # Add example buttons for quick testing
    st.subheader("Quick Examples")
    col1a, col1b = st.columns(2)
    
    with col1a:
        if st.button("Flowchart Example"):
            st.session_state.mermaid_code = """flowchart TD
    A[Start] --> B{{Is it?}}
    B -->|Yes| C[OK]
    C --> D[Rethink]
    D --> B
    B ---->|No| E[End]"""
            st.rerun()
    
    with col1b:
        if st.button("Sequence Example"):
            st.session_state.mermaid_code = """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob, how are you?
    B-->>A: Great!
    A-)B: See you later!"""
            st.rerun()

with col2:
    st.subheader("Rendered Diagram")
    component_html = get_mermaid_component(mermaid_code_input)
    components.html(component_html, height=700, scrolling=True)