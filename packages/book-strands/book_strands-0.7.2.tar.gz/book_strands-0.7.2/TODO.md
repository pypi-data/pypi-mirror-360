# To-do list

1. Split out filesystem checks to it's own separate agent flow - this should greatly reduce token usage since the file list won't stay in the conversation history. Or make it a fuzzy match file search instead?
2. Make use of existing file formats/author names more accurate
3. Update cost measurements to account for sub-agents as well
4. Test using an agent-based approach instead of the current scraper for downloads
5. Add support for LiteLLM and/or Ollama models
