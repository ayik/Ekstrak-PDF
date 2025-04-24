from ..components.extractPdfDetails import ExtractPdfDetails
from ..components.summaryEngine import SummaryEngine
from concurrent.futures import ThreadPoolExecutor
from ..utils.logger import logger

class Pipeline:
    def __init__(self):
        logger.info("INITIALIZING PIPELINE")
        self.extractPdfDetails = ExtractPdfDetails()
        self.summaryEngine = SummaryEngine()

    def run(self, pdfBytes: bytes) -> str:
        """
        Run the pipeline
        Args:
            pdfBytes: bytes of the pdf file
        Returns:
            summary: summary of the pdf file
        """
        try:
            logger.info("Running the pipeline")
            images = self.extractPdfDetails.convertToImages(pdfBytes = pdfBytes)
            chunks = self.extractPdfDetails.chunkImages(images = images)
            with ThreadPoolExecutor(max_workers = 30) as executor:
                futures = [executor.submit(self.extractPdfDetails.extractDetailsFromChunk, chunk) for chunk in chunks]
                summaries = [future.result() for future in futures]
            summary = self.summaryEngine.summarize(texts = summaries)
            return summary
        except Exception as e:
            logger.exception(f"Error running the pipeline: {e}")
            return None