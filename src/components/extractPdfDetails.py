from ..utils.functions import getConfig, convertImageToBase64, getYaml
from pdf2image import convert_from_bytes
from ..utils.logger import logger
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import math
import os

load_dotenv()

class ExtractPdfDetails:
    def __init__(self):
        logger.info("INITIALIZING EXTRACT PDF DETAILS")
        self.config = getConfig(os.path.join(os.getcwd(), "config.ini"))
        self.prompts = getYaml(os.path.join(os.getcwd(), "prompts.yaml"))
        self.llmClient = OpenAI(
            base_url = self.config["GROQ CONFIG"]["BASEURL"],
            api_key = os.environ["GROQ_API_KEY"]
        )

    def convertToImages(self, pdfBytes: str) -> list[Image.Image]:
        """
        Convert a pdf to a list of images
        Args:
            pdfBytes: bytes of the pdf file
        Returns:
            list[Image.Image]: list of pdf pages as images
        """
        try:
            logger.info(f"Converting pdf to images")
            images = convert_from_bytes(pdfBytes)
            return images
        except Exception as e:
            logger.exception(f"Error converting pdf to images: {e}")
            return None

    def chunkImages(self, images: list[Image.Image]) -> list[list[Image.Image]]:
        """
        Chunk the images into smaller chunks
        Args:
            images: list of images
        Returns:
            chunks: list of chunks of images
        """
        try:
            logger.info("Chunking the images")
            batchSize = self.config.getint("DETAIL EXTRACTOR", "BATCHSIZE")
            nBatches = math.ceil(len(images) / batchSize)
            chunks = [images[batchSize * x: batchSize * x + batchSize] for x in range(nBatches)]
            return chunks
        except Exception as e:
            logger.exception(f"Error chunking the images: {e}")
            return None

    def extractDetailsFromChunk(self, images: list[Image.Image]) -> str:
        """
        Extract details from a chunk of images
        Args:
            images: list of images
        Returns:
            details: string of details extracted from the images
        """
        try:
            logger.info("Extracting details from the images")
            completion = self.llmClient.chat.completions.create(
                model = self.config.get("DETAIL EXTRACTOR", "VLM"),
                messages = [
                    {"role": "system", "content": self.prompts["detailExtractorPrompt"]},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": convertImageToBase64(image)}} for image in images]}
                ],
                temperature = self.config.getfloat("DETAIL EXTRACTOR", "TEMPERATURE"),
                max_tokens = self.config.getint("DETAIL EXTRACTOR", "MAXTOKENS"),
                stream = False
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            logger.exception(f"Error extracting details from the images: {e}")
            return None