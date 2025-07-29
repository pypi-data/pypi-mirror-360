# AI Prompt Manager Templates

This directory contains customizable prompt templates used by the AI Prompt Manager for various operations. These templates can be customized to improve the quality and relevance of prompts for your specific use case.

## Available Templates

### System Templates

- **`default_prompt_template.txt`**: Default template for general prompt formatting
  - Used for standard prompt generation and enhancement
  - Supports variables: `{content}`, `{category}`, `{tags}`, `{user_context}`
  - Customize this to improve prompt quality for your domain

- **`enhancement_template.txt`**: Template for prompt enhancement operations
  - Used when enhancing existing prompts for better performance
  - Supports variables: `{original_prompt}`, `{enhancement_instructions}`, `{target_model}`
  - Helps standardize enhancement operations

### Domain-Specific Templates

- **`business_template.txt`**: Template optimized for business use cases
  - Focus on business terminology, KPIs, and strategic context
  - Ideal for marketing, sales, and management prompts

- **`technical_template.txt`**: Template for technical documentation and development
  - Emphasizes technical accuracy, code examples, and implementation details
  - Perfect for software development and engineering prompts

- **`creative_template.txt`**: Template for creative writing and content generation
  - Optimized for storytelling, marketing copy, and creative tasks
  - Includes style, tone, and audience considerations

- **`analytical_template.txt`**: Template for data analysis and research tasks
  - Structured for logical reasoning, data interpretation, and analysis
  - Includes methodology and evidence-based approaches

## Customizing Templates

### For General Prompts

1. **Copy the default template**:
   ```bash
   cp default_prompt_template.txt my_custom_template.txt
   ```

2. **Edit the template** to include domain-specific instructions:
   ```
   Create a prompt optimized for [your domain] use cases.
   Focus on [specific concepts/terminology] relevant to [your use case].
   ```

3. **Configure AI Prompt Manager** to use your custom template:
   ```bash
   export PROMPT_TEMPLATE="/path/to/templates/my_custom_template.txt"
   ```

### Template Variables

When creating custom templates, you can use these variables:

- `{content}`: The main prompt content
- `{category}`: Prompt category (Business, Technical, Creative, etc.)
- `{tags}`: Comma-separated tags associated with the prompt
- `{user_context}`: Additional user-provided context
- `{enhancement_instructions}`: Specific enhancement directions (for enhancement templates)
- `{target_model}`: Target AI model for optimization (for enhancement templates)
- `{original_prompt}`: Original prompt content (for enhancement templates)

### Best Practices

1. **Be Specific**: Include domain-specific terminology and concepts
2. **Provide Context**: Explain the intended use case for the prompts
3. **Keep It Focused**: Avoid overly complex templates that might confuse the model
4. **Test and Iterate**: Experiment with different templates and measure prompt quality
5. **Consider Your Model**: Different AI models may respond better to different template styles

## Configuration

Set the template path in your environment:

```bash
# Use a custom prompt template
export PROMPT_TEMPLATE="/path/to/templates/my_template.txt"

# Use a custom enhancement template
export ENHANCEMENT_TEMPLATE="/path/to/templates/my_enhancement_template.txt"

# Use default templates (no configuration needed)
# AI Prompt Manager will use default_prompt_template.txt by default
```

Or configure via the application settings:

```python
config = AppConfig(
    external_services=ExternalServicesConfig(
        prompt_template="templates/my_custom_template.txt",
        enhancement_template="templates/my_enhancement_template.txt"
    )
)
```

## Examples

### Marketing/Sales Template
```
Create a compelling prompt for {category} use case:

Context: {user_context}
Focus Areas:
- Target audience identification
- Value proposition clarity
- Call-to-action effectiveness
- Brand voice consistency

Content: {content}
Tags: {tags}
```

### Software Development Template
```
Generate a technical prompt for {category} development:

Requirements: {user_context}
Technical Focus:
- Code quality and best practices
- Performance considerations
- Security implications
- Documentation standards

Prompt Content: {content}
Keywords: {tags}
```

### Creative Writing Template
```
Craft a creative prompt for {category} content:

Creative Brief: {user_context}
Style Guidelines:
- Tone and voice
- Target audience
- Brand personality
- Content format

Base Content: {content}
Themes: {tags}
```

### Data Analysis Template
```
Develop an analytical prompt for {category} analysis:

Analysis Context: {user_context}
Methodology Focus:
- Data sources and quality
- Statistical methods
- Visualization approach
- Actionable insights

Query Content: {content}
Analysis Areas: {tags}
```