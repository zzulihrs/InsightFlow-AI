# Project Glasswing: Securing Critical Software for the AI Era

**Source:** Anthropic Blog
**Date:** 2026-04-09
**Original URL:** https://www.anthropic.com/glasswing

---

## Introduction

Today we're announcing Project Glasswing, a new initiative that brings together Amazon Web Services, Anthropic, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, the Linux Foundation, Microsoft, NVIDIA, and Palo Alto Networks in an effort to secure the world's most critical software.

We formed Project Glasswing because of capabilities we've observed in a new frontier model trained by Anthropic that we believe could reshape cybersecurity. AI models have reached a level of coding capability where they can surpass all but the most skilled humans at finding and exploiting software vulnerabilities. Claude Mythos Preview, a general-purpose, unreleased frontier model, has identified thousands of high-severity vulnerabilities, including some in every major operating system and web browser.

Anthropic is committing $100 million in model usage credits and $4 million in direct donations to open-source security organizations to support this initiative. Over 40 additional organizations beyond the launch partners have been given access for scanning their systems.

The initiative recognizes that without proper safeguards, these powerful cyber capabilities could enable AI-augmented cyberattacks to become much more frequent and destructive, making this a critical national security priority.

---

## Cybersecurity in the Age of AI

Critical software powers banking, healthcare, logistics, and energy infrastructure. Cyberattacks have demonstrated serious real-world consequences -- healthcare disruptions, power grid compromises, and government data breaches. Global cybercrime costs are estimated at around $500 billion every year.

Traditionally, finding exploitable vulnerabilities required rare expertise. AI models have dramatically lowered this barrier. Over the past year, frontier AI models showed a striking ability to spot vulnerabilities and work out ways to exploit them. Frontier AI models are now becoming competitive with the best humans at finding and exploiting software vulnerabilities.

Claude Mythos Preview represents a substantial leap in AI cybersecurity capabilities. The model has identified vulnerabilities that survived decades of human review and millions of automated security tests. The exploits it creates show increasing sophistication. The model achieved this capability through strong agentic coding and reasoning skills, representing advancement in how AI systems can reason about and interact with code.

The same capabilities that make AI models dangerous in the wrong hands make them invaluable for finding and fixing flaws. These dangerous capabilities become invaluable defensively, producing software with far fewer security bugs. Without safeguards, however, AI-augmented cyberattacks could become much more frequent and destructive.

---

## Identifying Vulnerabilities and Exploits with Claude Mythos Preview

Claude Mythos Preview was able to identify nearly all of the following vulnerabilities entirely autonomously, without any human steering. Partners have used the model for several weeks, confirming its extraordinary capability. Three notable discoveries illustrate the model's power:

### A 27-Year-Old Vulnerability in OpenBSD

Mythos Preview identified a 27-year-old vulnerability in OpenBSD, which is regarded as one of the most security-hardened operating systems in the world and runs critical infrastructure like firewalls. This flaw enabled remote attackers to crash any machine running the system simply by connecting to it. The vulnerability had survived decades of review in one of the most rigorously audited codebases in existence.

### A 16-Year-Old Vulnerability in FFmpeg

The model discovered a 16-year-old vulnerability in FFmpeg, widely used software for video encoding and decoding. Notably, automated testing tools had executed the vulnerable code path five million times without detecting the problem. This demonstrates the model's ability to find subtle vulnerabilities that elude even exhaustive automated testing.

### Vulnerabilities in the Linux Kernel

Mythos Preview autonomously identified and chained multiple vulnerabilities in the Linux kernel, which runs most of the world's servers, enabling attackers to escalate from regular user access to complete machine control. The ability to chain multiple vulnerabilities together into a working exploit demonstrates a particularly sophisticated level of reasoning.

All identified vulnerabilities in these systems were reported to maintainers and have been patched. For many other identified flaws, Anthropic provided cryptographic hashes of details with plans to reveal specifics after fixes are implemented.

---

## Benchmark Results

Evaluation benchmarks such as CyberGym reinforce the substantial difference between Mythos Preview and Anthropic's next-best model, Claude Opus 4.6:

| Benchmark | Mythos Preview | Opus 4.6 |
|---|---|---|
| CyberGym (Cybersecurity Vulnerability Reproduction) | 83.1% | 66.6% |
| SWE-bench Pro | 77.8% | 53.4% |
| Terminal-Bench 2.0 | 82.0% | 65.4% |
| SWE-bench Multimodal | 59.0% | 27.1% |
| SWE-bench Multilingual | 87.3% | 77.8% |
| SWE-bench Verified | 93.9% | 80.8% |
| GPQA Diamond | 94.6% | 91.3% |
| Humanity's Last Exam (without tools) | 56.8% | 40.0% |
| Humanity's Last Exam (with tools) | 64.7% | 53.1% |
| BrowseComp | 86.9% | 83.7% |
| OSWorld-Verified | 79.6% | 72.7% |

---

## Plans for Project Glasswing

### Launch Partners

The 12 launch partners are Amazon Web Services, Anthropic, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, the Linux Foundation, Microsoft, NVIDIA, and Palo Alto Networks. Additionally, access was extended to over 40 other organizations that develop or maintain critical software infrastructure.

Partners will use Mythos Preview for defensive security work within their foundational systems, representing a substantial portion of the world's shared cyberattack surface. Anticipated work includes local vulnerability detection, black box testing of binaries, securing endpoints, and penetration testing.

### Partner Perspectives

**Anthony Grieco, Cisco:** "AI capabilities have crossed a threshold that fundamentally changes the urgency required to protect critical infrastructure from cyber threats."

**Amy Herzog, AWS:** "Security isn't a phase for us; it's continuous and embedded in everything we do."

**Igor Tsyganskiy, Microsoft:** "The opportunity to use AI responsibly to improve security and reduce risk at scale is unprecedented." Microsoft noted that Mythos Preview showed substantial improvements on their CTI-REALM benchmark.

**Elia Zaitsev, CrowdStrike:** "The window between a vulnerability being discovered and being exploited has collapsed -- what once took months now happens in minutes with AI."

**Jim Zemlin, Linux Foundation:** "Project Glasswing offers a credible path to changing that equation" regarding open-source security access.

### Financial Commitments

Anthropic committed $100 million in model usage credits for Mythos Preview across Project Glasswing efforts and additional participants. The company also donated $2.5 million to Alpha-Omega and OpenSSF through the Linux Foundation, plus $1.5 million to the Apache Software Foundation to help open-source software maintainers address this security landscape shift.

### Availability and Pricing

After the research preview period, Claude Mythos Preview will be available to participants at $25/$125 per million input/output tokens. Participants can access the model via the Claude API, Amazon Bedrock, Google Cloud's Vertex AI, and Microsoft Foundry.

### 90-Day Disclosure and Collaboration

Partners will share information and best practices with each other. Within 90 days, Anthropic committed to publicly reporting findings, patched vulnerabilities, and improvements that can be disclosed.

Anthropic plans to collaborate with leading security organizations to develop practical recommendations covering vulnerability disclosure, software update processes, supply-chain security, secure development practices, industry standards, triage automation, and patching automation.

---

## Safeguards and Responsible Deployment

We do not plan to make Claude Mythos Preview generally available, but our eventual goal is to enable our users to safely deploy Mythos-class models at scale. We need to make progress in developing cybersecurity safeguards that detect and block the model's most dangerous outputs. We plan to launch new safeguards with an upcoming Claude Opus model, allowing us to improve and refine them with a model that does not pose the same level of risk as Mythos Preview. Security professionals whose legitimate work is affected by these safeguards will be able to apply to an upcoming Cyber Verification Program.

---

## Conclusion

No single organization can address these cybersecurity challenges alone. The work will require involvement from frontier AI developers, technology companies, security researchers, open-source maintainers, and governments globally. Anthropic expressed hope that Project Glasswing could seed larger cross-industry and public-sector efforts, inviting other AI companies to help establish industry standards. In the medium term, an independent, third-party body bringing together private and public sector organizations might be ideal for continued large-scale cybersecurity projects.

---

## Appendix: Footnotes

1. **Project name:** The project is named for the glasswing butterfly, *Greta oto*. The metaphor can be applied in two ways: the butterfly's transparent wings let it hide in plain sight, much like the vulnerabilities discussed in this post; they also allow it to evade harm -- like the transparency we're advocating for in our approach.

2. **"Mythos" name origin:** From the Ancient Greek for "utterance" or "narrative": the system of stories through which civilizations made sense of the world.

3. **Cyber Verification Program:** Security professionals whose legitimate work is affected by these safeguards will be able to apply to an upcoming Cyber Verification Program.
