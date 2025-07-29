from strands.models.bedrock import BedrockModel
from strands.models.ollama import OllamaModel

# File/config paths
CONFIG_FILE_PATH = "~/.config/book-strands.conf"
DEFAULT_OUTPUT_FORMAT = "{{author}}/{{series}}/{{title}}"

# Supported formats (in priority order for downloads)
SUPPORTED_FORMATS = (
    "epub",
    "mobi",
    "azw",
    "azw3",
)

# Z-Library URLs
ZLIB_BASE_URL = "https://z-library.sk"
ZLIB_SEARCH_URL = f"{ZLIB_BASE_URL}/s/"
ZLIB_LOGIN_URL = f"{ZLIB_BASE_URL}/rpc.php"
ZLIB_LOGOUT_URL = f"{ZLIB_BASE_URL}/papi/user/logout"
ZLIB_PROFILE_URL = f"{ZLIB_BASE_URL}/profile"

# HTTP headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Prompts
BOOK_HANDLING_PROMPT = """
IMPORTANT:
The book title should be purely the title of the book, without any extra information such as series or series index.
The series name should not contain the word 'series'. If there is no series name, leave it blank.
Note that all series indexes should be in the format 1.0, 2.0, 2.5 etc based on common practice.
"""

BEDROCK_NOVA_PRO_MODEL = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
BEDROCK_CLAUDE_37_MODEL = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
)
OLLAMA_MODEL = OllamaModel(host="http://localhost:11434", model_id="qwen3:8b")
