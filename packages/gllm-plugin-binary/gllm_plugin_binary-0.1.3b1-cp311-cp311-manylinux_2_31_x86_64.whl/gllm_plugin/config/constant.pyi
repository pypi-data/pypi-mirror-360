from enum import StrEnum

class SearchType(StrEnum):
    """The type of search to perform.

    Values:
        NORMAL: Get answer from chatbot knowledge.
        SMART: Get more relevant information from your stored documents and knowledge base.
            Knowledge Search is an AI with specialized knowledge. No agents are available in this mode.
        WEB: Get more relevant information from the web.
            Web Search uses real-time data. Agent selection isn't available in this mode.
    """
    NORMAL = 'normal'
    SMART = 'smart'
    WEB = 'web'
