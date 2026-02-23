"""
LLMOrchestrator - Handles LLM interactions via LangChain.

Supports multiple LLM providers (OpenAI, Anthropic, etc.) and manages
prompt construction, execution, and response parsing.
"""

from typing import Optional, Dict, Any, List
from loguru import logger
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class LLMOrchestrator:
    """
    Orchestrates LLM calls for skill execution.

    Handles:
    - LLM initialization and configuration
    - Prompt construction from step instructions
    - Context injection (luggage, reference files)
    - Response parsing and validation
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the LLM orchestrator.

        Args:
            llm_provider: LLM provider ("openai", "anthropic")
            model_name: Model name (e.g., "gpt-4", "claude-3-opus-20240229")
            temperature: Sampling temperature
            api_key: API key (optional, can use environment variables)
            **kwargs: Additional model parameters
        """
        self.llm_provider = llm_provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs

        self.llm = self._initialize_llm()
        self.parser = StrOutputParser()
        self.conversation_history: List[Any] = []

        logger.info(f"Initialized LLM: {llm_provider}/{model_name}")

    def _initialize_llm(self):
        """Initialize the LLM based on provider."""
        if self.llm_provider == "openai":
            from langchain_openai import ChatOpenAI
            # Build kwargs for OpenAI
            llm_kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                **self.kwargs
            }
            if self.api_key:
                llm_kwargs["api_key"] = self.api_key

            try:
                return ChatOpenAI(**llm_kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                logger.info("Available models: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo")
                raise

        elif self.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            # Build kwargs for Anthropic - uses 'anthropic_api_key' parameter
            llm_kwargs = {
                "model": self.model_name,
                "temperature": self.temperature,
                **self.kwargs
            }
            if self.api_key:
                llm_kwargs["anthropic_api_key"] = self.api_key

            try:
                return ChatAnthropic(**llm_kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
                logger.info("Try one of these models:")
                logger.info("  - claude-3-5-sonnet-20241022 (recommended)")
                logger.info("  - claude-3-5-sonnet-20240620")
                logger.info("  - claude-3-opus-20240229")
                logger.info("  - claude-3-sonnet-20240229")
                logger.info("  - claude-3-haiku-20240307")
                raise

        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def execute_step(
        self,
        instruction: str,
        context: Optional[str] = None,
        reference_files_content: Optional[Dict[str, str]] = None,
        luggage_context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        expected_format: Optional[str] = None,
        api_context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a single skill step with the LLM.

        Args:
            instruction: The step instruction/prompt
            context: General context about the skill
            reference_files_content: Dictionary of file paths to their content
            luggage_context: Context from the skill luggage (previous outputs, variables)
            system_prompt: Custom system prompt
            expected_format: Description of expected output format
            api_context_data: Dictionary of API responses keyed by alias

        Returns:
            LLM response as string
        """
        # Build the full prompt
        messages = self._build_messages(
            instruction=instruction,
            context=context,
            reference_files_content=reference_files_content,
            luggage_context=luggage_context,
            system_prompt=system_prompt,
            expected_format=expected_format,
            api_context_data=api_context_data
        )

        # Execute LLM call
        try:
            chain = self.llm | self.parser
            response = chain.invoke(messages)

            # Store in conversation history
            self.conversation_history.append({
                "instruction": instruction,
                "response": response
            })

            logger.info(f"LLM execution complete ({len(response)} chars)")
            return response

        except Exception as e:
            logger.error(f"LLM execution failed: {str(e)}")
            raise

    def _build_messages(
        self,
        instruction: str,
        context: Optional[str] = None,
        reference_files_content: Optional[Dict[str, str]] = None,
        luggage_context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        expected_format: Optional[str] = None,
        api_context_data: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Build message list for the LLM.

        Args:
            instruction: Main instruction
            context: General context
            reference_files_content: Reference file contents
            luggage_context: Luggage state context
            system_prompt: Custom system prompt
            expected_format: Expected output format
            api_context_data: Dictionary of API responses keyed by alias

        Returns:
            List of messages
        """
        messages = []

        # System message
        if system_prompt:
            system_message = system_prompt
        else:
            system_message = self._build_default_system_prompt()

        messages.append(SystemMessage(content=system_message))

        # Build human message with all context
        human_message_parts = []

        # Add skill context
        if context:
            human_message_parts.append(f"## Skill Context\n{context}")

        # Add luggage context (previous outputs, variables)
        if luggage_context:
            human_message_parts.append(f"## Current State\n{luggage_context}")

        # Add reference files
        if reference_files_content:
            human_message_parts.append("## Reference Files")
            for file_path, content in reference_files_content.items():
                human_message_parts.append(f"### File: {file_path}")
                human_message_parts.append(f"```\n{content}\n```")

        # Add API context data
        if api_context_data:
            import json
            human_message_parts.append("## API Context Data")
            for alias, data in api_context_data.items():
                human_message_parts.append(f"### {alias}")
                if isinstance(data, (dict, list)):
                    formatted = json.dumps(data, indent=2, default=str)
                    human_message_parts.append(f"```json\n{formatted}\n```")
                else:
                    human_message_parts.append(str(data))

        # Add the main instruction
        human_message_parts.append(f"## Your Task\n{instruction}")

        # Add expected format if specified
        if expected_format:
            human_message_parts.append(f"## Expected Output Format\n{expected_format}")

        human_message = "\n\n".join(human_message_parts)
        messages.append(HumanMessage(content=human_message))

        return messages

    def _build_default_system_prompt(self) -> str:
        """Build default system prompt for skill execution."""
        return """You are an AI assistant executing a structured skill workflow.

Your role is to:
1. Carefully read and understand the task instruction
2. Use the provided context and reference files
3. Follow the expected output format if specified
4. Produce accurate, well-structured outputs
5. Be precise and thorough in your analysis

Important guidelines:
- Stay focused on the specific task at hand
- Use information from reference files when relevant
- Consider previous step outputs when making decisions
- Format your output clearly and consistently
- If data is missing or unclear, state it explicitly
"""

    def verify_output(
        self,
        output: str,
        verification_rules: List[str],
        required_elements: List[str]
    ) -> tuple[bool, str]:
        """
        Verify an output against verification criteria using the LLM.

        Args:
            output: The output to verify
            verification_rules: List of rules to check
            required_elements: List of elements that must be present

        Returns:
            Tuple of (passed: bool, explanation: str)
        """
        verification_prompt = self._build_verification_prompt(
            output, verification_rules, required_elements
        )

        messages = [
            SystemMessage(content="You are a verification assistant. Carefully check if the output meets all specified criteria."),
            HumanMessage(content=verification_prompt)
        ]

        chain = self.llm | self.parser
        response = chain.invoke(messages)

        # Parse response to determine if verification passed
        passed = self._parse_verification_response(response)

        logger.info(f"Verification result: {'PASSED' if passed else 'FAILED'}")
        return passed, response

    def _build_verification_prompt(
        self,
        output: str,
        rules: List[str],
        required_elements: List[str]
    ) -> str:
        """Build verification prompt."""
        parts = [
            "## Output to Verify",
            f"```\n{output}\n```",
            "",
            "## Verification Criteria",
            ""
        ]

        if rules:
            parts.append("### Rules to Check:")
            for i, rule in enumerate(rules, 1):
                parts.append(f"{i}. {rule}")
            parts.append("")

        if required_elements:
            parts.append("### Required Elements:")
            for elem in required_elements:
                parts.append(f"- Must contain: {elem}")
            parts.append("")

        parts.extend([
            "## Your Task",
            "Verify if the output meets ALL criteria above.",
            "",
            "Respond with:",
            "VERDICT: PASS or FAIL",
            "EXPLANATION: [Brief explanation of your verdict]",
            "",
            "If any criterion is not met, the verdict must be FAIL."
        ])

        return "\n".join(parts)

    def _parse_verification_response(self, response: str) -> bool:
        """Parse verification response to extract pass/fail."""
        response_upper = response.upper()

        # Look for explicit PASS verdict
        if "VERDICT: PASS" in response_upper or "VERDICT:PASS" in response_upper:
            return True

        # Look for explicit FAIL verdict
        if "VERDICT: FAIL" in response_upper or "VERDICT:FAIL" in response_upper:
            return False

        # Fallback: look for PASS/FAIL keywords
        if "PASS" in response_upper and "FAIL" not in response_upper:
            return True

        # Default to fail if unclear
        return False

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history
