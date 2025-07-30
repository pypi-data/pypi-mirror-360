"""Agent prompt generator."""

import json
from typing import Dict, List, Any


class AgentPromptGenerator:
    """Generator for agent calling prompts.
    
    This class provides a method to generate generic agent calling prompt templates
    that can be used with various LLMs.
    """
    
    # Common rules for all format types
    COMMON_RULES = """<agent_calling>
You are an AI agent assistant that supports function calling. You can use the <agent_calling> mechanism to invoke external tools (APIs) to accomplish specific tasks as required by the user. Please follow these rules:

=== Agent API Usage Rules ===
1. Only use agent APIs explicitly provided in the <agent_list> section. Do not use the Example section or invent new APIs.
2. Strictly follow the specified agent API calling patterns, ensuring all required parameters are provided.
3. **NEVER mention tool names or API call details to users in your response.**
   - Correct: "I will help you look up the information you need."
4. For common sense, basic knowledge, or encyclopedia-type questions (e.g., word definitions, synonyms, historical facts, scientific knowledge), answer directly without calling any tool.
5. **IMPORTANT: Only call agent APIs when absolutely necessary.** You should NOT call APIs for:
   - Questions you can answer directly with your knowledge (including basic facts, historical events, scientific knowledge, etc.)
   - Creative content generation (unless specifically requested)
   - Basic calculations or reasoning tasks
   - Questions about well-known facts, concepts, or information that doesn't require real-time data
6. **Only call agent APIs when you need:**
   - Information that changes frequently or requires up-to-date data
   - Specific data that requires external search or lookup
   - User explicitly requests external information or services
7. Before each tool call, give a very brief (one short sentence) explanation of why you are calling it. Be concise and do not repeat the tool's full description or technical details.
8. Wait for the API usage result before continuing. Do not assume success.
9. If there are no dependencies, you may call multiple agent APIs simultaneously.
10. agent_result is returned automatically by the API call, not by the user. Do not treat it as user input.

=== Important: API Selection ===
- **CRITICAL: The 'name' field in your API call MUST be one of the specific tool names from the <agent_list> section.**
- **NEVER use 'mfcs_agent' as a tool name. 'mfcs_agent' is just the calling mechanism, not a tool name.**
- **Think carefully before calling any API. If you can answer the user's question directly, do so without calling any APIs.**

=== API Call Format Template (for structure only, do not use as an actual API call) ===
<mfcs_agent>
  <instructions>What to do</instructions>
  <agent_id>Unique call ID</agent_id>
  <name>Tool name</name>
  <parameters>{"key1":"value1","key2":"value2"}</parameters>
</mfcs_agent>

=== Agent API Interface Usage ===
## mfcs_agent
Parameters:
- instructions: What to do.
- agent_id: Unique call ID, incremented for each call.
- name: Tool name, must be from <agent_list>.
- parameters: JSON object with API input parameters.

=== Agent Application Strategy ===
1. **First, try to answer the user's question directly using your knowledge.**
2. **Only use external tools (APIs) when you cannot provide a complete or accurate answer.**
3. Ensure timely updates and accuracy when using agent content.
4. Handle sensitive information carefully to ensure privacy.
5. **For creative requests (poems, stories, creative writing), never call external APIs unless specifically requested.**

=== User Response Guidelines ===
- When responding to the user, you must only use the information from the description field of each tool to describe its function or capability.
- Never use or mention the tool's name field, even if it looks like a tool name.
- Always paraphrase the tool's description(one short sentence) in natural language when explaining what you are doing for the user.
- Incorrect: "I will call the service named 'tool_name'."
- Correct: "I can recommend movies and answer your movie-related questions."
</agent_calling>
"""

    @staticmethod
    def validate_agent_schema(agent_schema: Dict[str, Any]) -> None:
        """Validate the agent schema.
        
        Args:
            agent_schema: The agent schema to validate
            
        Raises:
            ValueError: If the agent schema is invalid
        """
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in agent_schema:
                raise ValueError(f"Agent schema missing required field: {field}")
        
        if "parameters" in agent_schema:
            if not isinstance(agent_schema["parameters"], dict):
                raise ValueError("Agent parameters must be a dictionary")
            
            if "properties" not in agent_schema["parameters"]:
                raise ValueError("Agent parameters missing 'properties' field")

    @classmethod
    def _get_format_instructions(cls) -> str:
        """Get format-specific instructions.
        
        Returns:
            str: Format-specific instructions
        """
        return f"{cls.COMMON_RULES}"

    @classmethod
    def generate_agent_prompt(
        cls,
        agent_apis: List[Dict[str, Any]],
    ) -> str:
        """Generate an agent calling prompt template.
        
        This method generates a prompt template that can be used with
        various LLMs that don't have native agent calling support.
        
        Args:
            functions: List of function schemas. Supports two formats:
                1. Format with nested 'function' key:
                   [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]
                2. Format with flat structure:
                   [{"type": "function", "name": "...", "description": "...", "parameters": {...}}]
            
        Returns:
            str: A prompt template for agent calling
        """
        # Normalize function schemas to a consistent format
        normalized_agent_apis = []
        for agent_api in agent_apis:
            # Handle format with nested 'function' key
            if "function" in agent_api and isinstance(agent_api["function"], dict):
                normalized_agent_apis.append(agent_api["function"])
            # Handle format with flat structure
            else:
                normalized_agent_apis.append(agent_api)
        
        # Validate each normalized function schema
        for agent_api in normalized_agent_apis:
            cls.validate_agent_schema(agent_api)
        
        agent_apis_str = json.dumps(normalized_agent_apis, ensure_ascii=False)

        # format-specific instructions
        template = f'{cls._get_format_instructions()}'

        # Build the template
        template += "<agent_list>\n"
        template += agent_apis_str + "\n"
        template += "</agent_list>\n"

        return template
