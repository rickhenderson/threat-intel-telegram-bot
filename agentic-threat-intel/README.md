# Agentic Threat Intel


August 4, 2026:

* The Agentic bot still has trouble finding recent CVE announcements, but the cron job now runs correctly. Here's the latest report:

1. Google Patches Fifth Chrome Zero-Day of 2026
CVE-2026-11645, an out-of-bounds read/write in the V8 JavaScript engine, was exploited in the wild and could bypass ASLR to enable arbitrary code execution inside the sandbox. Patched across Windows, Mac, and Linux builds.
🔗 https://www.bleepingcomputer.com/news/security/google-patches-fifth-chrome-zero-day-bug-exploited-in-attacks-this-year/amp/

2. Chrome Zero-Day in Dawn/WebGPU Hits 3.5 Billion Users
CVE-2026-5281, a use-after-free in Chrome's Dawn WebGPU component, was confirmed exploited and added to CISA's KEV catalog — one of four Chrome zero-days patched in Q1 2026 alone (vs. 8 for all of 2025).
🔗 https://www.forbes.com/sites/daveywinder/2026/04/03/google-issues-zero-day-attack-alert-for-35-billion-chrome-users/

---

📦 Open Source Library Vulnerabilities (npm / pip)

1. Axios npm Package Compromised — Cross-Platform RAT, DPRK Ties
Attackers hijacked the lead maintainer account of Axios (100M+ weekly downloads) and published two poisoned versions (1.14.1, 0.30.4) injecting a phantom dependency (plain-crypto-js) that dropped a self-destructing remote access trojan on Windows, macOS, and Linux. Multiple threat intel teams attribute the attack to North Korea-linked actor UNC1069. Revert to axios@1.14.0 or @0.30.3 and rotate all exposed credentials.
🔗 https://www.trendmicro.com/en_us/research/26/c/axios-npm-package-compromised.html

2. "Mini Shai-Hulud" Wave Compromises 32 npm Packages
A new supply-chain campaign compromised at least 32 packages under the @redhat-cloud-services npm namespace (~80,000 combined weekly downloads), part of an escalating pattern of coordinated npm/PyPI attacks throughout 2026.
🔗 https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/

---

📅 Briefing Date: Tuesday, August 4, 2026

 💬 "Security is not a product, but a process." — Bruce Schneier

Stay patched, stay paranoid. 🔐
--
* The report on Mini Shai-Hulud is from July 15, so outside a 7 day window but it may keep reporting Shai-Hulud references because I had discussed with the AI a few months ago.
* I do like the tag lines and the quote from Bruce Schneier, but the bot only recycles about 4 quotes and they're all from Bruce.
---
* I asked Claude Opus 5 some tips on the architecture for a threat intel bot, and it said don't use LLM for the important stuff. So I am now more apt to trust Claude :).
* I'll be writing about that on my [Substack threat intelligence blog](https://rickhendersonco.substack.com/).
* If I was going to continue to use Hermes Agent for a threat intelligence bot, I'd be moving most of the work to skills. You should [learn how to write skills](https://claude.com/resources/tutorials/teach-claude-your-way-of-working-using-skills). The [Anthropic Academy](https://www.anthropic.com/learn) has very good courses if you can access it.
* The agent can also insert entries into a MISP instance I have running locally.
* I'll likely be following Claude's code suggestions and use Python for collectors and directly pull threat info via API feeds, and use LLM/Hermes agent for narrative and article summaries.
---

In May/June 2026 I started using a Hermes Agent to act as a threat intel bot that can be interacted with via Telegram.

* First I had it running as a single VPS on Hostinger as a trial.
* Then I moved the configuration back to my desktop and it worked fine.
* June 14, 2026 I re-created it as a managed Hermes Agent on Hostinger but the response is quite slow.
* There are still problems with getting the agent to perform the cron job regularly, then publish the threat feed to a separately Telegram channel.
