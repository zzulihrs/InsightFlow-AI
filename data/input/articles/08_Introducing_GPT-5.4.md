# Introducing GPT-5.4

**Source:** OpenAI Blog
**Date:** April 8, 2026
**Original URL:** <https://openai.com/index/introducing-gpt-5-4/>

---

GPT-5.4 is OpenAI's first mainline reasoning model that incorporates the frontier coding capabilities of GPT-5.3-codex. It is rolling out across ChatGPT, the API, and Codex simultaneously. OpenAI also introduced a higher-end variant, GPT-5.4 Pro, positioned for maximum performance and deeper reasoning on complex workloads.

## Reasoning and Coding

GPT-5.4 represents a significant step forward in combining reasoning and coding into one model. It is the first general-purpose OpenAI model to unify the frontier coding capabilities previously exclusive to GPT-5.3-codex with deep reasoning in a single system.

In ChatGPT, GPT-5.4 Thinking can now provide an upfront plan of its thinking -- a preamble -- so users can adjust course mid-response while it is working, and arrive at a final output that is more closely aligned with what they need. For longer, more complex queries, the model will outline its work with this preamble before diving into the details.

GPT-5.4 matches or exceeds industry professionals in 83.0% of 44-occupation comparisons on the GDPval professional knowledge work benchmark, compared to 70.9% for GPT-5.2. On SWE-Bench Pro coding benchmarks, GPT-5.4 scores 57.7% versus GPT-5.2's 55.6%. On Terminal-Bench 2.0, GPT-5.4 achieves 75.1% compared to GPT-5.2's 62.2%. OpenAI also reports a 33% reduction in factual errors compared to GPT-5.2.

## Computer Use

GPT-5.4 is the first general-purpose OpenAI model released with native, state-of-the-art computer-use capabilities, enabling agents to operate computers and carry out complex workflows across applications. The model can move across applications using screenshots plus keyboard and mouse actions.

On OSWorld-Verified tasks involving desktop environment interaction, GPT-5.4 achieved a 75.0% success rate, surpassing GPT-5.2's 47.3% and approaching the average human baseline of 72.4%. In testing on approximately 30,000 HOA and property tax portals, GPT-5.4 achieved a 95% success rate on the first attempt and 100% within three attempts, while completing sessions approximately 3x faster and using approximately 70% fewer tokens.

In Codex and the API, GPT-5.4 enables agents to interact directly with user interfaces -- viewing screenshots and generating mouse and keyboard coordinates in real-time. Use cases include automated reporting, visual debugging, and cross-app workflows.

## Enhanced Vision

Starting with GPT-5.4, OpenAI introduced an original image input detail level which supports full-fidelity perception up to 10.24 million total pixels or 6,000-pixel maximum dimension. This enables the model to process high-resolution images with much greater accuracy and detail than previous versions.

## Tool Search

GPT-5.4 introduces tool search, which allows models to work efficiently when given many tools. With tool search, GPT-5.4 receives a lightweight list of available tools along with a tool search capability. When the model needs to use a tool, it can look up that tool's definition and append it to the conversation at that moment.

This approach dramatically reduces the number of tokens required for tool-heavy workflows, helping agents find and use the right tools more efficiently without sacrificing intelligence. Tool search also supports Model Context Protocol (MCP) integration for large tool inventories, enabling GPT-5.4 to scale across larger tool ecosystems.

## Context Window and Technical Specifications

GPT-5.4 supports up to 1,050,000 tokens of context, allowing agents to plan, execute, and verify tasks across long horizons. The Pro variant supports up to 128,000 output tokens. The model's knowledge cutoff date is August 31, 2025.

The API supports a `reasoning.effort` parameter with five configurable levels: none, low, medium, high, and xhigh, allowing developers to control the depth of reasoning based on their use case.

## Deep Research

GPT-5.4 offers enhanced deep research functionality with improved efficiency, using fewer tokens than GPT-5.2 Thinking for similar research tasks. On the BrowseComp web research benchmark, GPT-5.4 scores 82.7%, while GPT-5.4 Pro reaches 89.3%.

## Presentations

In evaluations of presentation quality, human raters preferred GPT-5.4's output 68.0% of the time over GPT-5.2's presentations, indicating substantial improvements in document and slide generation capabilities.

## Pricing

Through the OpenAI API, GPT-5.4 is available at the following pricing:

- **gpt-5.4**: $2.50 per 1M input tokens, $15 per 1M output tokens
- **gpt-5.4-pro**: $30 per 1M input tokens, $180 per 1M output tokens
- For contexts exceeding 272K tokens: 2x input pricing, 1.5x output pricing

## Availability

In ChatGPT, GPT-5.4 Thinking is available starting March 5, 2026 to ChatGPT Plus, Team, and Pro users, replacing GPT-5.2 Thinking as the default reasoning model. GPT-5.4 Pro is available to Pro and Enterprise plans.

GPT-5.2 Thinking will remain available for three months for paid users, after which it will be retired on June 5, 2026.

GPT-5.4 is also available through the API (model ID: `gpt-5.4`) and in Codex. Enterprise deployment is available through Microsoft Foundry with private endpoints.

## Product Integrations

Alongside the GPT-5.4 launch, OpenAI introduced ChatGPT for Excel in beta, with financial data integrations to enhance professional workflows.

## Safety

GPT-5.4 has been designated as "High cyber capability" with appropriate mitigations in place. OpenAI notes that cybersecurity safeguards may produce false positives during the initial calibration period.

## Additional Variants

On March 17, 2026, OpenAI released two additional variants: GPT-5.4 mini (available to free users) and GPT-5.4 nano (API-only). GPT-5.4 mini significantly improves over GPT-5 mini across coding, reasoning, multimodal understanding, and tool use, while running more than 2x faster.
