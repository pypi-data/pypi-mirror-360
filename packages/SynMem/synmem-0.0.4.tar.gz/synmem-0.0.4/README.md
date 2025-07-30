
---

# SynMem – 4-Stage Synthetic Memory

## Overview

**SynMem** is a production-grade, multi-stage synthetic memory framework inspired by real cognition.
**Built for AI Agents, LLMs, Voice Assistants and more with advanced automation**.

**Stages:**

1. **Perception** – Immediate, in-memory (RAM) context 
   - *Optional, not required*
2. **Sensory** – Short-lived, per-user episodic memory
3. **STM (Short-Term Memory)** – Active conversation/session memory
4. **LTM (Long-Term Memory)** – Persistent archive

---

## Key Features

* **Direct, 4-stage architecture:**

  * *Perception* (RAM) *Sensory* (Per User) → *STM* (All Users) → *LTM* (All Users)
* **Thread-safe singleton:**
  One instance per process, all operations safe for concurrency.
* **Configurable:**
  All limits, expirations, are adjustable.
* **No vendor lock-in:**
  Plug into any agent, LLM, or workflow.
* **No required maintenance:**
  **Maintenance/cleanup is optional but recommended.**
  Run in a background thread no lock-in or forced schedules.
* **Bonus: Image storage and expiry:**
  Store/expire/archive images and metadata if needed—totally optional.

---

## Why SynMem?

Most “memory” modules just log history or dump to a database.
**SynMem** is layered, time-aware, and models real-world cognition.

* **Perception**: Working context—ephemeral, in-memory, no disk. (Optional Use)
* **Sensory**: Fast, expiring, per-user buffer.
* **STM**: Recent active memory, rolls into LTM automatically.
* **LTM**: Archive—retrieve by date, user, or content.
* **Image**: Use if you need; never required.

You control all layouts, all workflows.

---

## API Highlights

**Perception (RAM only):**

```python
mem.savePerception("live context chunk")
mem.retrievePerception()   # FIFO, up to limit
mem.clearPerception()
```

**Sensory / STM / LTM:**

```python
mem.saveSensory("input", "response", "user", mem.senDir)
mem.retrieveSensory(mem.getDir(mem.senDir, "user.db"))
mem.saveConversationDetails("input", "response", "user", mem.stmUserConversationDetails)
mem.retrieveConversationDetails("user", [mem.stmUserConversationDetails, mem.ltmUserConversationDetails])
```

**Bonus: Images (if needed):**

```python
mem.saveCreatedImage("subject", image_data, mem.stmCreatedImages, mem.stmCreatedImageDetails)
```

---

## Maintenance (Optional, Recommended)

* **Why?**
  For auto-cleanup, auto-archival, and expired memory removal.
* **Not required for operation.**
* **Enable any time**—runs in the background so no blocking.

**If you don’t enable maintenance, expired items will accumulate until you remove them.**

---

## Plug and Play

* No schemas, no boilerplate.
* Use with any LLM/agent plug-N-play and go.

---

## FAQ

**Q: Is perception persistent?**
A: No, it is always RAM-only.

**Q: Do I need maintenance?**
A: No, but it’s strongly recommended for any long-running use.

**Q: What if I don’t use image storage?**
A: Ignore all image APIs—they’re bonus, not core.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil