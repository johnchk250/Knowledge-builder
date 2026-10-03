# Sol / other-agent continuation entry

Updated 1 October 2026. Use the [current ready-to-paste prompt](READY_TO_PASTE_PROMPT.md), supported by [CONTINUATION_GUIDE.md](CONTINUATION_GUIDE.md). These are model-independent and include the completed silo and crusher pilots. This compatibility entry replaces the older prompt so there is one maintained starter text.

For the next coal-flow section after crushing, prepend:

```text
Target: B36 — EBA-18A/B and UEF-13. Preserve the accepted crusher interfaces and examine the relevant B02/B04 service boundaries. Leave B37 sampling/access for a separate run, retaining its documented connections.
```

For another section, substitute its name or batch ID. Without a target, the prompt selects the next unfinished dependency-ready package after reconciling the live model and checkpoints; it does not assume a completed pilot needs to be recreated.

The v510 inventory remains historical. B30/B31 reached v527; B32–B35 reached v558. Check live state before working. The main handoff is [PLANT_MODEL_IMPLEMENTATION_HANDOFF.md](../../PLANT_MODEL_IMPLEMENTATION_HANDOFF.md).
