from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from src.pipelines.pipeline import Pipeline
from datetime import datetime
import streamlit as st
from io import BytesIO
import tempfile
import requests
import time

# Configure the page
st.set_page_config(
    page_title="AlphaExtract — Your AI-powered PDF Summarizer",
    page_icon="📈",
    layout="wide"
)

# Custom styling
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f9fbfd;
    }

    .main-header {
        font-size: 3rem;
        color: #0A66C2;
        font-weight: 700;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2.5rem;
    }

    .summary-header {
        font-size: 1.8rem;
        color: #00695C;
        font-weight: 600;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }

    .stDownloadButton > button {
        background-color: #0A66C2;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        margin-top: 1rem;
        transition: background-color 0.3s ease;
    }

    .stDownloadButton > button:hover {
        background-color: #084B8A;
    }

    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize the pipeline
pipeline = Pipeline()

# Cache font download
@st.cache_resource(show_spinner=False)
def getDejaVuFontPath():
    fontUrl = "https://github.com/senotrusov/dejavu-fonts-ttf/raw/refs/heads/master/ttf/DejaVuSans.ttf"
    response = requests.get(fontUrl)
    tempFontFile = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf")
    tempFontFile.write(response.content)
    tempFontFile.close()
    return tempFontFile.name

# Cache summary generation
@st.cache_data(show_spinner=False, ttl=3600)
def generateSummary(_pipeline, pdfBytes):
    return pipeline.run(pdfBytes)

# Cache PDF generation
@st.cache_data(show_spinner=False, ttl=3600)
def generatePdfBytes(summary, fontPath):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    pdfmetrics.registerFont(TTFont("DejaVu", fontPath))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="summaryStyle",
        fontName="DejaVu",
        fontSize=12,
        leading=18,
        spaceAfter=12
    ))

    story = [
        Paragraph("PDF Summary", styles["Heading1"]),
        Spacer(1, 0.2 * inch),
        Paragraph(summary.replace("\n", "<br/>"), styles["summaryStyle"])
    ]

    doc.build(story)
    pdfValue = buffer.getvalue()
    buffer.close()
    return pdfValue

# Sidebar
with st.sidebar:
    st.markdown("## 📄 Upload PDF")
    uploadedFile = st.file_uploader("Drop your PDF here", type=["pdf"])

    if uploadedFile:
        st.markdown("### 🔍 File Info")
        pdfDetails = {
            "📁 File Name": uploadedFile.name,
            "📦 Size": f"{round(len(uploadedFile.getvalue()) / 1024, 2)} KB",
            "⏰ Uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        for key, value in pdfDetails.items():
            st.write(f"**{key}**: {value}")

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.9rem; line-height: 1.4;'>
    Inference by <strong>Groq</strong><br>
    using Meta's <strong>LLaMA 4 MOE Maverick</strong><br>
    for blazing-fast, high-precision summaries.
    </div>
    """, unsafe_allow_html=True)


# Main content
st.markdown("<h1 class='main-header'>Welcome to <span style='color:#2E7D32'>AlphaExtract</span></h1>", unsafe_allow_html=True)
st.write("Upload a PDF to instantly receive a professional-grade analytical summary.")

if uploadedFile:
    statusContainer = st.empty()
    summaryContainer = st.empty()

    with statusContainer.container():
        st.markdown("### ⏳ Processing Status")
        statusBox = st.empty()

        try:
            startTime = time.time()
            statusBox.info("📘 Reading PDF file...")
            pdfBytes = uploadedFile.getvalue()
            readDuration = time.time() - startTime
            statusBox.success(f"✅ PDF file read successfully ({readDuration:.2f}s)")

            statusBox.info("🧠 Generating summary...")
            summary = generateSummary(pipeline, pdfBytes)
            totalTime = time.time() - startTime

            if summary:
                statusBox.success(f"✅ Summary generated successfully (Total time: {totalTime:.2f}s)")

                with summaryContainer.container():
                    st.markdown("<h2 class='summary-header'>📊 Generated Summary</h2>", unsafe_allow_html=True)
                    st.markdown(summary)

                    try:
                        fontPath = getDejaVuFontPath()
                        pdfBytesOut = generatePdfBytes(summary, fontPath)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                        st.download_button(
                            label="⬇️ Download Summary as PDF",
                            data=pdfBytesOut,
                            file_name=f"summary_{timestamp}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Error creating PDF: {str(e)}")
            else:
                statusBox.error("❌ Failed to generate summary. Please try again.")
        except Exception as e:
            statusBox.error(f"❌ Error processing PDF: {str(e)}")
else:
    st.info("🚀 Please upload a PDF file using the sidebar to get started.")