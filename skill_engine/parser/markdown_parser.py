"""
SkillMarkdownParser - Parses Markdown files into Skill objects.

This parser uses mistune to extract structured sections from a .md file
and converts them into a Skill object with metadata, steps, and verification criteria.
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import mistune
from loguru import logger

from skill_engine.models.skill import (
    Skill,
    SkillStep,
    SkillMetadata,
    VerificationCriteria,
    StepType,
    ApiContextDefinition,
    HttpMethod,
    McpContextDefinition,
    McpTransport,
)


class SkillMarkdownParser:
    """
    Parser for converting Markdown skill definitions into Skill objects.

    Expected Markdown Structure:
    ---
    # Skill Name: Credit Memo Generator
    ## Metadata
    - Version: 1.0.0
    - Author: John Doe
    - Tags: finance, credit

    ## Context
    Background information about this skill...

    ## Reference Files
    - path/to/file1.txt
    - path/to/file2.pdf

    ## Steps

    ### Step 1: Extract Financial Data
    **Instruction:**
    Extract key financial figures...

    **Reference Files:**
    - financial_statement.pdf

    **Expected Output:**
    JSON format with fields...

    **Verification:**
    - Must contain revenue field
    - Must contain expenses field

    ### Step 2: Perform Risk Analysis
    ...

    ## Final Output Format
    Description of final output...

    ## Success Criteria
    The skill is successful when...
    ---
    """

    def __init__(self):
        """Initialize the parser."""
        self.markdown = mistune.create_markdown()

    def parse_file(self, file_path: str) -> Skill:
        """
        Parse a Markdown file into a Skill object.

        Args:
            file_path: Path to the .md file

        Returns:
            Skill object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_markdown(content)

    def parse_markdown(self, content: str) -> Skill:
        """
        Parse Markdown content into a Skill object.

        Args:
            content: Markdown content as string

        Returns:
            Skill object
        """
        # Extract sections using regex
        sections = self._extract_sections(content)

        # Parse metadata
        metadata = self._parse_metadata(sections)

        # Parse context
        context = sections.get("Context", None)

        # Parse global reference files
        global_ref_files = self._parse_reference_files(
            sections.get("Reference Files", "")
        )

        # Parse global API context
        global_api_context = self._parse_api_context_section(
            sections.get("API Context", "")
        )

        # Parse global MCP context
        global_mcp_context = self._parse_mcp_context_section(
            sections.get("MCP Context", "")
        )

        # Parse steps
        steps = self._parse_steps(sections.get("Steps", ""))

        # Parse final output format
        final_output = sections.get("Final Output Format", None)

        # Parse success criteria
        success_criteria = sections.get("Success Criteria", None)

        skill = Skill(
            metadata=metadata,
            context=context,
            steps=steps,
            global_reference_files=global_ref_files,
            global_api_context=global_api_context,
            global_mcp_context=global_mcp_context,
            final_output_format=final_output,
            success_criteria=success_criteria
        )

        logger.info(f"Parsed skill: {metadata.name} with {len(steps)} steps")
        return skill

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract major sections from the Markdown content.

        Args:
            content: Full Markdown content

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}

        # Split by ## headers (level 2)
        level2_pattern = r'^## (.+?)$'
        parts = re.split(level2_pattern, content, flags=re.MULTILINE)

        # Extract skill name from # header
        name_match = re.search(r'^# (?:Skill Name: )?(.+?)$', content, re.MULTILINE)
        if name_match:
            sections["_skill_name"] = name_match.group(1).strip()

        # Process parts (odd indices are headers, even indices are content)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                section_name = parts[i].strip()
                section_content = parts[i + 1].strip()
                sections[section_name] = section_content

        return sections

    def _parse_metadata(self, sections: Dict[str, str]) -> SkillMetadata:
        """
        Parse metadata section.

        Args:
            sections: Dictionary of all sections

        Returns:
            SkillMetadata object
        """
        skill_name = sections.get("_skill_name", "Unnamed Skill")
        metadata_content = sections.get("Metadata", "")

        # Extract metadata fields
        version = self._extract_field(metadata_content, "Version", "1.0.0")
        author = self._extract_field(metadata_content, "Author")
        description = self._extract_field(metadata_content, "Description")
        tags_str = self._extract_field(metadata_content, "Tags", "")
        tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []

        return SkillMetadata(
            name=skill_name,
            description=description,
            version=version,
            author=author,
            tags=tags
        )

    def _extract_field(self, content: str, field_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Extract a field value from metadata content.

        Args:
            content: Metadata section content
            field_name: Name of the field to extract
            default: Default value if not found

        Returns:
            Field value or default
        """
        # Try bullet list format: - Field: value
        pattern = rf'^\s*-\s*{field_name}\s*:\s*(.+?)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try key-value format: Field: value
        pattern = rf'^\s*{field_name}\s*:\s*(.+?)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return default

    def _parse_reference_files(self, content: str) -> List[str]:
        """
        Parse reference files from a section.

        Args:
            content: Reference files section content

        Returns:
            List of file paths
        """
        files = []
        # Match bullet points
        pattern = r'^\s*[-*]\s*(.+?)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            file_path = match.group(1).strip()
            files.append(file_path)
        return files

    def _parse_steps(self, content: str) -> List[SkillStep]:
        """
        Parse steps section into SkillStep objects.

        Args:
            content: Steps section content

        Returns:
            List of SkillStep objects
        """
        steps = []

        # Split by ### headers (step headers)
        step_pattern = r'^### Step (\d+):\s*(.+?)$'
        parts = re.split(step_pattern, content, flags=re.MULTILINE)

        # Process steps (groups of 3: step_num, step_name, step_content)
        for i in range(1, len(parts), 3):
            if i + 2 < len(parts):
                step_num = int(parts[i])
                step_name = parts[i + 1].strip()
                step_content = parts[i + 2].strip()

                step = self._parse_single_step(step_num, step_name, step_content)
                steps.append(step)

        return sorted(steps, key=lambda s: s.step_number)

    def _parse_single_step(self, step_num: int, step_name: str, content: str) -> SkillStep:
        """
        Parse a single step's content.

        Args:
            step_num: Step number
            step_name: Step name
            content: Step content

        Returns:
            SkillStep object
        """
        # Extract instruction
        instruction = self._extract_subsection(content, "Instruction")
        if not instruction:
            # If no explicit instruction subsection, use the first paragraph
            instruction = content.split("\n\n")[0] if content else ""

        # Extract description
        description = self._extract_subsection(content, "Description")

        # Extract reference files
        ref_files_content = self._extract_subsection(content, "Reference Files")
        reference_files = self._parse_reference_files(ref_files_content) if ref_files_content else []

        # Extract expected output format
        expected_output = self._extract_subsection(content, "Expected Output")

        # Extract verification criteria
        verification = self._parse_verification(content)

        # Extract step type
        step_type_str = self._extract_subsection(content, "Type")
        step_type = StepType(step_type_str.lower()) if step_type_str else StepType.INSTRUCTION

        # Extract step-level API context
        api_context = self._parse_step_api_context(content)

        # Extract step-level MCP context
        mcp_context = self._parse_step_mcp_context(content)

        return SkillStep(
            step_number=step_num,
            name=step_name,
            description=description,
            instruction=instruction,
            step_type=step_type,
            reference_files=reference_files,
            expected_output_format=expected_output,
            verification=verification,
            api_context=api_context,
            mcp_context=mcp_context,
        )

    def _extract_subsection(self, content: str, subsection_name: str) -> Optional[str]:
        """
        Extract a subsection from step content.

        Args:
            content: Step content
            subsection_name: Name of subsection to extract

        Returns:
            Subsection content or None
        """
        # Try **Subsection:** format
        pattern = rf'\*\*{subsection_name}:?\*\*\s*\n(.+?)(?=\n\*\*|\n###|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try #### Subsection format
        pattern = rf'^####\s*{subsection_name}:?\s*\n(.+?)(?=\n####|\n###|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _parse_verification(self, content: str) -> Optional[VerificationCriteria]:
        """
        Parse verification criteria from step content.

        Args:
            content: Step content

        Returns:
            VerificationCriteria or None
        """
        verification_content = self._extract_subsection(content, "Verification")
        if not verification_content:
            return None

        # Extract rules (bullet points)
        rules = []
        required_elements = []
        pattern = r'^\s*[-*]\s*(.+?)$'
        matches = re.finditer(pattern, verification_content, re.MULTILINE)
        for match in matches:
            rule = match.group(1).strip()
            # Check if it's a "must contain" rule
            if "must contain" in rule.lower() or "required" in rule.lower():
                # Extract the element name
                elem_match = re.search(r'["\']?(\w+)["\']?', rule)
                if elem_match:
                    required_elements.append(elem_match.group(1))
            rules.append(rule)

        description = verification_content.split("\n")[0] if verification_content else "Verify output"

        return VerificationCriteria(
            description=description,
            rules=rules,
            required_elements=required_elements
        )

    def _parse_api_context_section(self, content: str) -> List[ApiContextDefinition]:
        """
        Parse global ## API Context section with ### API: <alias> sub-headers.

        Args:
            content: API Context section content

        Returns:
            List of ApiContextDefinition objects
        """
        if not content or not content.strip():
            return []

        apis = []

        # Split by ### API: headers
        api_pattern = r'^### API:\s*(.+?)$'
        parts = re.split(api_pattern, content, flags=re.MULTILINE)

        # parts[0] is content before first ### API:, then alternating alias/content
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                alias = parts[i].strip()
                api_content = parts[i + 1].strip()
                api_def = self._parse_single_api_definition(alias, api_content)
                if api_def:
                    apis.append(api_def)

        return apis

    def _parse_single_api_definition(self, alias: str, content: str) -> Optional[ApiContextDefinition]:
        """
        Parse a single API definition from bullet-list content.

        Args:
            alias: The alias/key name for this API
            content: The bullet-list content defining the API

        Returns:
            ApiContextDefinition or None if endpoint is missing
        """
        endpoint = self._extract_field(content, "Endpoint")
        if not endpoint:
            logger.warning(f"API context '{alias}' missing Endpoint, skipping")
            return None

        method_str = self._extract_field(content, "Method", "GET")
        query_params = self._extract_field(content, "Query Params")
        body = self._extract_field(content, "Body")
        extract = self._extract_field(content, "Extract")
        description = self._extract_field(content, "Description")

        try:
            method = HttpMethod(method_str.upper())
        except ValueError:
            logger.warning(f"Invalid HTTP method '{method_str}' for API '{alias}', defaulting to GET")
            method = HttpMethod.GET

        return ApiContextDefinition(
            alias=alias,
            endpoint=endpoint,
            method=method,
            query_params=query_params,
            body=body,
            extract=extract,
            description=description,
        )

    def _parse_step_api_context(self, content: str) -> List[ApiContextDefinition]:
        """
        Parse step-level **API Context:** subsection.

        Args:
            content: Step content

        Returns:
            List of ApiContextDefinition objects (typically 0 or 1)
        """
        api_content = self._extract_subsection(content, "API Context")
        if not api_content:
            return []

        endpoint = self._extract_field(api_content, "Endpoint")
        if not endpoint:
            return []

        alias = self._extract_field(api_content, "Alias", "api_response")
        method_str = self._extract_field(api_content, "Method", "GET")
        query_params = self._extract_field(api_content, "Query Params")
        body = self._extract_field(api_content, "Body")
        extract = self._extract_field(api_content, "Extract")

        try:
            method = HttpMethod(method_str.upper())
        except ValueError:
            method = HttpMethod.GET

        return [ApiContextDefinition(
            alias=alias,
            endpoint=endpoint,
            method=method,
            query_params=query_params,
            body=body,
            extract=extract,
        )]

    # ------------------------------------------------------------------
    # MCP Context parsing
    # ------------------------------------------------------------------

    def _parse_mcp_context_section(self, content: str) -> List[McpContextDefinition]:
        """
        Parse global ## MCP Context section with ### MCP: <alias> sub-headers.

        Expected format:
            ## MCP Context
            ### MCP: my_alias
            - Server: http://localhost:3000/sse
            - Tool: get_data
            - Arguments: {"key": "value"}
            - Transport: sse
            - Description: Fetch data from MCP server

        Args:
            content: MCP Context section content

        Returns:
            List of McpContextDefinition objects
        """
        if not content or not content.strip():
            return []

        mcps = []

        # Split by ### MCP: headers
        mcp_pattern = r'^### MCP:\s*(.+?)$'
        parts = re.split(mcp_pattern, content, flags=re.MULTILINE)

        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                alias = parts[i].strip()
                mcp_content = parts[i + 1].strip()
                mcp_def = self._parse_single_mcp_definition(alias, mcp_content)
                if mcp_def:
                    mcps.append(mcp_def)

        return mcps

    def _parse_single_mcp_definition(self, alias: str, content: str) -> Optional[McpContextDefinition]:
        """
        Parse a single MCP definition from bullet-list content.

        Args:
            alias: The alias/key name for this MCP call
            content: The bullet-list content defining the MCP call

        Returns:
            McpContextDefinition or None if required fields are missing
        """
        import json as _json

        server = self._extract_field(content, "Server")
        if not server:
            logger.warning(f"MCP context '{alias}' missing Server, skipping")
            return None

        tool = self._extract_field(content, "Tool")
        if not tool:
            logger.warning(f"MCP context '{alias}' missing Tool, skipping")
            return None

        arguments_str = self._extract_field(content, "Arguments")
        arguments = None
        if arguments_str:
            try:
                arguments = _json.loads(arguments_str)
            except _json.JSONDecodeError:
                logger.warning(f"MCP context '{alias}' has invalid JSON in Arguments, ignoring")

        transport_str = self._extract_field(content, "Transport", "auto")
        try:
            transport = McpTransport(transport_str.lower())
        except ValueError:
            logger.warning(f"Invalid transport '{transport_str}' for MCP '{alias}', defaulting to auto")
            transport = McpTransport.AUTO

        description = self._extract_field(content, "Description")

        return McpContextDefinition(
            alias=alias,
            server=server,
            tool=tool,
            arguments=arguments,
            transport=transport,
            description=description,
        )

    def _parse_step_mcp_context(self, content: str) -> List[McpContextDefinition]:
        """
        Parse step-level **MCP Context:** subsection.

        Expected format inside a step:
            **MCP Context:**
            - Alias: my_alias
            - Server: http://localhost:3000/sse
            - Tool: get_data
            - Arguments: {"key": "value"}

        Args:
            content: Step content

        Returns:
            List of McpContextDefinition objects (typically 0 or 1)
        """
        mcp_content = self._extract_subsection(content, "MCP Context")
        if not mcp_content:
            return []

        alias = self._extract_field(mcp_content, "Alias", "mcp_response")
        mcp_def = self._parse_single_mcp_definition(alias, mcp_content)
        return [mcp_def] if mcp_def else []
