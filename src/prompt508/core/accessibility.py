"""
Accessibility hint injection module for prompt508.
Injects Section 508 compliance reminders and accessibility guidelines into prompts.
"""

from typing import Dict, List, Optional
from .utils import load_json_rules, clean_text


class AccessibilityInjector:
    """
    Injector for accessibility hints and Section 508 compliance reminders.
    
    Adds structured accessibility instructions to prompts to ensure AI outputs
    follow Section 508 guidelines for alt text, captions, structure, etc.
    """
    
    def __init__(
        self,
        include_alt_text: bool = True,
        include_captions: bool = True,
        include_structure: bool = True,
        include_links: bool = True,
        strict_mode: bool = False
    ):
        """
        Initialize the accessibility injector.
        
        Args:
            include_alt_text: Include alt text reminders
            include_captions: Include caption/transcript reminders
            include_structure: Include document structure reminders
            include_links: Include link text reminders
            strict_mode: Use stricter, more detailed instructions
        """
        self.include_alt_text = include_alt_text
        self.include_captions = include_captions
        self.include_structure = include_structure
        self.include_links = include_links
        self.strict_mode = strict_mode
        
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load accessibility rules from Section 508 JSON."""
        try:
            section508_rules = load_json_rules("section508.json")
            self.accessibility_hints = section508_rules.get("accessibility_hints", {})
            self.output_instructions = section508_rules.get("output_instructions", {})
        except Exception as e:
            # Fallback to minimal defaults
            self.accessibility_hints = {}
            self.output_instructions = {}
    
    def inject_hints(self, prompt: str, content_type: Optional[str] = None) -> str:
        """
        Inject accessibility hints into a prompt.
        
        Args:
            prompt: Original prompt text
            content_type: Type of content expected ("images", "multimedia", "documents", 
                         "links", "forms", or None for general)
            
        Returns:
            Prompt with injected accessibility instructions
        """
        cleaned_prompt = clean_text(prompt)
        
        if not cleaned_prompt:
            return prompt
        
        # Build accessibility instructions
        instructions = self._build_instructions(content_type)
        
        if not instructions:
            return prompt
        
        # Format and inject instructions
        injected_prompt = self._format_injected_prompt(cleaned_prompt, instructions)
        
        return injected_prompt
    
    def _build_instructions(self, content_type: Optional[str] = None) -> List[str]:
        """
        Build list of accessibility instructions based on settings.
        
        Args:
            content_type: Specific content type or None for general
            
        Returns:
            List of instruction strings
        """
        instructions = []
        
        # Add general accessibility reminder
        if self.output_instructions.get("default"):
            instructions.append(self.output_instructions["default"])
        
        # Add content-type specific instructions
        if content_type:
            type_instruction = self.output_instructions.get(content_type)
            if type_instruction:
                instructions.append(type_instruction)
        
        # Add specific category hints
        if self.include_alt_text and "images" in self.accessibility_hints:
            instructions.extend(self._format_hints("Images", self.accessibility_hints["images"]))
        
        if self.include_captions and "multimedia" in self.accessibility_hints:
            instructions.extend(self._format_hints("Multimedia", self.accessibility_hints["multimedia"]))
        
        if self.include_structure and "documents" in self.accessibility_hints:
            instructions.extend(self._format_hints("Document Structure", self.accessibility_hints["documents"]))
        
        if self.include_links and "links" in self.accessibility_hints:
            instructions.extend(self._format_hints("Links", self.accessibility_hints["links"]))
        
        # Add language hints if strict mode
        if self.strict_mode and "language" in self.accessibility_hints:
            instructions.extend(self._format_hints("Language", self.accessibility_hints["language"]))
        
        return instructions
    
    def _format_hints(self, category: str, hints: List[str]) -> List[str]:
        """
        Format hints for a specific category.
        
        Args:
            category: Category name
            hints: List of hints
            
        Returns:
            Formatted hint strings
        """
        if self.strict_mode:
            # In strict mode, include all hints with category labels
            return [f"[{category}] {hint}" for hint in hints]
        else:
            # In normal mode, take first 2-3 most important hints
            return hints[:2]
    
    def _format_injected_prompt(self, original_prompt: str, 
                                instructions: List[str]) -> str:
        """
        Format the final prompt with injected instructions.
        
        Args:
            original_prompt: Original prompt text
            instructions: List of accessibility instructions
            
        Returns:
            Formatted prompt with instructions
        """
        if not instructions:
            return original_prompt
        
        # Build instruction block
        instruction_block = "\n\n[Accessibility Requirements]\n"
        for instruction in instructions:
            instruction_block += f"- {instruction}\n"
        
        # Append to original prompt
        injected = original_prompt + instruction_block
        
        return injected
    
    def get_hints_for_content(self, content_type: str) -> List[str]:
        """
        Get accessibility hints for a specific content type.
        
        Args:
            content_type: Content type ("images", "multimedia", "documents", etc.)
            
        Returns:
            List of relevant hints
        """
        return self.accessibility_hints.get(content_type, [])
    
    def generate_compliance_checklist(self) -> str:
        """
        Generate a Section 508 compliance checklist.
        
        Returns:
            Formatted checklist string
        """
        checklist = """
Section 508 Compliance Checklist:

□ Images and Graphics
  □ All images have descriptive alt text
  □ Complex images have extended descriptions
  □ Decorative images have empty alt text (alt="")

□ Multimedia
  □ Videos have captions
  □ Audio content has transcripts
  □ Video descriptions provided for visual content

□ Document Structure
  □ Proper heading hierarchy (H1, H2, H3)
  □ Semantic markup used appropriately
  □ Tables have proper headers
  □ Lists use appropriate tags

□ Links
  □ Link text is descriptive and meaningful
  □ Link purpose clear from text alone
  □ No "click here" or generic link text

□ Language and Readability
  □ Plain language (8th grade level or below)
  □ Technical terms defined on first use
  □ Active voice used
  □ Sentences under 20 words when possible

□ Color and Contrast
  □ Color contrast meets WCAG AA (4.5:1)
  □ Information not conveyed by color alone

□ Forms (if applicable)
  □ Labels associated with form controls
  □ Clear instructions provided
  □ Error messages are specific and helpful
"""
        return checklist.strip()


def inject_accessibility_hints(
    prompt: str,
    content_type: Optional[str] = None,
    include_alt_text: bool = True,
    include_captions: bool = True,
    include_structure: bool = True,
    strict_mode: bool = False
) -> str:
    """
    Convenience function to inject accessibility hints into a prompt.
    
    Args:
        prompt: Original prompt
        content_type: Expected content type
        include_alt_text: Include alt text reminders
        include_captions: Include caption reminders
        include_structure: Include structure reminders
        strict_mode: Use strict mode with detailed instructions
        
    Returns:
        Prompt with accessibility hints
    """
    injector = AccessibilityInjector(
        include_alt_text=include_alt_text,
        include_captions=include_captions,
        include_structure=include_structure,
        strict_mode=strict_mode
    )
    return injector.inject_hints(prompt, content_type)
