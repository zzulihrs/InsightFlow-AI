# Anthropic's Model Context Protocol Hits 97 Million Installs on March 25 -- MCP Transitions from Experimental to Foundation Layer for Agentic AI

**Source:** Artur Markus  
**Date:** April 2, 2026  
**Original URL:** https://www.arturmarkus.com/anthropics-model-context-protocol-hits-97-million-installs-on-march-25-mcp-transitions-from-experimental-to-foundation-layer-for-agentic-ai/

---

On March 25, 2026, Anthropic's Model Context Protocol crossed 97 million installs -- a figure that represents the fastest adoption curve for any AI infrastructure standard in history. To contextualize: Kubernetes required nearly four years to achieve comparable enterprise deployment density.

The significance extends beyond raw numbers. All major AI providers -- OpenAI, Google DeepMind, Cohere, Mistral -- integrated MCP-compatible tooling as default functionality by mid-March. This represents industry-wide standardization rather than optional adoption.

MCP functions as a protocol specification enabling AI agents to communicate with external tools and data sources, comparable to HTTP's role in web infrastructure: foundational, invisible, and essential.

**Before MCP**, connecting agents to databases required custom integration code. Each additional data source demanded separate connectors. Enterprise deployments maintained hundreds of these integrations, creating numerous failure points.

MCP standardizes this interaction. Agents speak MCP to tool servers; servers respond via MCP. Agents discover capabilities, required parameters, and expected responses through a single protocol rather than custom implementations.

The architecture comprises three components:

**Hosts** are AI applications -- Claude desktop apps, custom frameworks, enterprise copilots -- that initiate connections and maintain session state.

**Clients** handle protocol communication. One host can operate multiple clients, each connecting to different tool servers.

**Servers** expose capabilities. A GitHub MCP server might offer repository search, file reading, and pull request creation. Servers advertise capabilities; clients decide what to utilize.

This separation provides security advantages. Servers control exposed capabilities; clients control initiated requests; hosts control authorized access. Three permission boundaries replace one monolithic integration.

## Timing Context

Q1 2026 marked when Fortune 500 companies transitioned agentic AI from pilots to production. Pilot programs tolerate custom integrations; production environments cannot.

Block eliminated 340 custom connectors through MCP deployment. Apollo reduced integration maintenance overhead by 60%. Replit built their entire development environment on MCP primitives. These constituted architectural commitments rather than experiments.

Enterprise pressure created coordination needs. No single vendor wanted adopting competitors' standards. Yet every vendor required standardization to avoid integration chaos customers rejected. MCP provided a solution: open specification, permissive licensing, and development by a non-platform company.

Anthropic's positioning enabled adoption. As a model company rather than platform provider, MCP doesn't favor Claude over GPT-4 or Gemini. This model-agnosticism made adoption safe for OpenAI and Google.

## Technical Architecture

MCP employs JSON-RPC 2.0 as wire format, running over stdio locally or HTTP with Server-Sent Events remotely. This conservative approach reflects established standards -- JSON-RPC has existed 15 years with mature language implementations. No new serialization formats or exotic protocols require learning.

Capability negotiation occurs at connection initialization. When clients connect to servers, they receive manifests describing:

**Tools:** Executable functions agents can invoke, with names, descriptions, and JSON schemas defining input parameters.

**Resources:** Readable data sources -- files, databases, API responses -- representable as text or structured data.

**Prompts:** Pre-defined instruction templates servers recommend for specific tasks.

This dynamic discovery enables agents to reason about tool capabilities before invocation. Agents access Slack server manifests and immediately understand available message-sending functions without hardcoded knowledge.

Claude's tool-use error rates decreased 40% in March 2026 through enhanced computer use capabilities. Better tool calling ensures more reliable MCP interactions. Improved reliability drives enterprise confidence, increasing installations.

## Common Misconceptions

Narrative focus emphasizes convenience -- fewer integrations, faster deployment, simplified architecture. This misses strategic implications.

MCP doesn't merely reduce integration work; it redistributes integration control.

Previously, platform vendors owned connector ecosystems. Salesforce controlled which agents accessed Salesforce data and methods. AWS controlled Lambda agent invocation. Each platform represented a walled garden.

MCP transfers control to tool server operators. Running internal API MCP servers allows any compatible agent connection without vendor partnership agreements. Agents require only protocol fluency.

Incumbent platform vendors haven't fully grasped this shift, treating MCP as supplementary to proprietary APIs. This underestimates developer momentum toward universal protocols once available. Nobody writes raw TCP socket code for web applications; they use HTTP. Similarly, engineers will abandon custom agent integrations for MCP.

Second misconception: MCP is "merely" specification. The specification comprises approximately 20% of value; ecosystem comprises 80%.

Anthropic and community shipped production-quality reference servers for:

- Filesystem access with permission boundaries
- Git and GitHub operations
- Postgres, SQLite, databases
- Slack, Google Drive, productivity tools
- Kubernetes cluster management
- AWS resource provisioning

These implement security boundaries, error handling, and edge cases that production deployments require. The ecosystem, beyond specifications, drives adoption.

## Security Model

How does a universal agent-to-tool protocol prevent malicious or compromised agents from causing damage?

MCP operates on explicit capability grants. Servers expose only chosen tools. Hosts authorize only approved connections. The protocol lacks mechanisms for agents discovering or accessing ungranted capabilities.

Server implementations typically add layers:

**Authentication:** Most remote servers require OAuth tokens or API keys before accepting connections. The protocol doesn't mandate specific auth mechanisms, leaving that to implementers understanding their security contexts.

**Audit logging:** Every tool invocation passes through servers, creating natural audit points. Enterprise deployments integrate these into SIEM systems for compliance and anomaly detection.

**Rate limiting:** Servers throttle requests per client, preventing runaway agents from overwhelming backends.

**Sandboxing:** The filesystem reference server accepts allowed directory lists. Requests outside these paths fail at the server level regardless of agent attempts.

Architecture assumes compromise occurs. When agents misbehave, blast radius limits to explicitly granted capabilities. Compromised code assistants cannot pivot to production databases without granted MCP connections to those servers.

Security depends entirely on server implementation quality. Poorly written servers can expose everything underlying systems access. The protocol doesn't prevent self-inflicted vulnerabilities.

## Practical Implementation

For production AI agents without MCP adoption, priority ordering suggests:

**First**, inventory current integrations. List every tool and data source agents access. Note proprietary versus custom connectors. This audit reveals migration surface area.

**Second**, identify pre-built servers. Check MCP registries for existing implementations matching tools. GitHub, Slack, major databases, cloud providers likely have servers already. Don't build replicated functionality.

**Third**, design authorization models. Determine which agents access which servers. Map this to existing IAM structures. MCP connections should flow through normal security governance.

**Fourth**, run shadow deployments. Stand up MCP servers alongside existing integrations. Route agent traffic percentages through MCP while maintaining legacy paths. Compare reliability, latency, and failures.

**Fifth**, sunset custom connectors. Once MCP shows equivalent or better performance, migrate fully and decommission maintenance burdens.

For teams building new agent systems, starting with MCP requires simpler analysis. The ecosystem matured sufficiently that custom integrations should require explicit justification.

Code implementation in Python:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(server_path) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("query_database", 
            arguments={"sql": "SELECT * FROM users LIMIT 10"})
```

TypeScript and other language SDKs follow similar patterns. Learning curves measure in hours rather than weeks.

## Vendor Landscape Impact

MCP adoption creates clear winners and losers within twelve months.

**Winners:**

Infrastructure companies shipping MCP servers gain stickiness. Teams using MCP servers represent persistent integrations across agent vendor switches. Datadog, Snowflake, MongoDB shipped official MCP servers in Q1 2026, understanding competitive dynamics.

Agent framework developers benefit from reduced surface area. LangChain, CrewAI, and similar platforms can focus on orchestration rather than maintaining connector libraries. Integration layers become others' responsibility.

Enterprise security vendors gain standardized interception points. Every MCP connection becomes auditable. Companies like Wiz and Snyk ship MCP-aware security scanning.

**Losers:**

Platform vendors relying on proprietary APIs lose moat advantages. Universal agent access via MCP commoditizes exclusive partnerships with specific AI vendors.

Integration Platform as a Service companies lose use cases. Zapier, Make, and similar platforms connected disparate systems. Direct agent connections through MCP thin middleware layers.

Companies betting heavily on custom agent frameworks face rewrite costs. Technical debt in bespoke integration code becomes urgent when industry standardizes elsewhere.

## Future Developments

The 97 million milestone marks adoption. Next twelve months determine whether MCP becomes truly foundational.

Three developments warrant watching:

**Streaming and real-time data.** Current MCP excels at request-response patterns. Agentic workflows increasingly need streaming -- market feeds, log tails, real-time metrics. Streaming support exists in specifications; production implementations lag. Expect major iteration by Q3 2026.

**Multi-agent coordination.** MCP defines client-server communication, not agent-to-agent protocols. Complex agentic systems require coordination primitives MCP doesn't provide. Anthropic published early multi-agent specification drafts.

**Formal verification.** Enterprise security teams want mathematical capability boundary guarantees rather than implementation claims. Research groups work on formally verified MCP server implementations. First production-certified verified servers will command premiums in regulated industries.

Long-term trajectory suggests MCP as assumed infrastructure. Enterprise architecture diagrams in 2027 won't label MCP connections anymore than they label HTTPS. It becomes default, unremarkable, invisible.

## Underappreciated Application

Everyone focuses on MCP connecting agents to external tools. The more significant application connects agents to internal systems predating AI era.

Every enterprise maintains legacy databases, internal APIs, and custom systems lacking AI access design. These expose SQL interfaces, REST endpoints, or inferior alternatives.

MCP servers wrap these interfaces without modifying underlying systems. Legacy databases remain untouched. MCP servers handle capability discovery, permission enforcement, and response formatting. Agents gain structured, safe data access that would otherwise require custom per-vendor integration.

This pattern -- MCP as translation layer for pre-AI infrastructure -- represents bulk enterprise deployment value. Greenfield systems receive press coverage. Brownfield integration pays bills.

## Architectural Strategy

The MCP milestone forces strategic questions every technical leader must answer regarding agentic AI protocol layer strategy.

Three options exist:

**Full adoption:** Standardize on MCP for all agent-to-tool communication. Accept ecosystem direction, focus engineering elsewhere.

**Selective adoption:** Use MCP where proven servers exist and quality proves solid. Maintain custom integrations for critical paths requiring maximum control.

**Protocol abstraction:** Build internal abstraction layers enabling MCP alternative swaps. Hedge against protocol evolution or fragmentation.

For most organizations, options one or two make sense. Option three adds architectural complexity rarely justifying itself. Protocol standards entrench once reaching MCP adoption levels. Betting against MCP means betting against considerable momentum.

More productive questions address adoption without creating security exposure or abandoning existing operational visibility in current integrations.

## Conclusion

MCP's 97 million installs don't represent a technology trend -- they represent the moment when AI agent infrastructure stopped being optional architecture and started being assumed plumbing.
