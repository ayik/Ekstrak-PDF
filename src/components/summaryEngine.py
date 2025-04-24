from ..utils.functions import getConfig, getYaml
from ..utils.logger import logger
import litellm
import os

class SummaryEngine:
    def __init__(self):
        logger.info("INITIALIZING SUMMARY ENGINE")
        self.config = getConfig(os.path.join(os.getcwd(), "config.ini"))
        self.prompts = getYaml(os.path.join(os.getcwd(), "prompts.yaml"))

    def summarize(self, texts: list[str]) -> str:
        """
        Summarize a text
        Args:
            texts: list of texts to summarize
        Returns:
            summary: summary of the texts
        """
        try:
            logger.info("Summarizing the details extracted from the images")
            allSummaries = "\n".join(texts)
            completion = litellm.completion(
                model = self.config.get("SUMMARIZER", "LLM"),
                api_key = os.environ["GROQ_API_KEY"],
                api_base = self.config["GROQ CONFIG"]["BASEURL"],
                messages = [
                    {"role": "system", "content": self.prompts["summaryEnginePrompt"]},
                    {"role": "user", "content": f"AGGEREGATED SUMMARIES: {allSummaries}"}
                ],
                max_tokens = self.config.getint("SUMMARIZER", "MAXTOKENS"),
                temperature = self.config.getfloat("SUMMARIZER", "TEMPERATURE")
            )
            response = completion["choices"][0]["message"]["content"]
            logger.info("Summary generated successfully")
            return response
        except Exception as e:
            logger.exception(f"Error summarizing the text: {e}")
            return None