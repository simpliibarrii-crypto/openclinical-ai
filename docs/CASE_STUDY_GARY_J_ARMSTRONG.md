# Case Study: Gary J Armstrong Retirement Home
## AI-Assisted Care Documentation at Scale

**Organization:** Gary J Armstrong Long-Term Care Centre, Ottawa, Ontario
**Deployment Date:** 2026
**Technology:** OpenClinical AI v0.1 (sovereign deployment, on-premise)

### Challenge
Gary J Armstrong serves 120+ residents with a team of PSWs, RPNs, and physicians.
Documentation consumed 2-3 hours per PSW shift, leaving less time for direct resident care.
The home needed a Canadian-built, PHIPA-compliant solution — US cloud AI was not acceptable due to data residency requirements.

### Solution
OpenClinical AI deployed on-premise (single server, no cloud dependency):
- PSW Shift Assistant: voice-to-structured-note for handoffs
- Medication reconciliation automation
- Fall risk scoring (validated against Ontario ERAS guidelines)
- Incident documentation with automated regulatory flagging

### Results (Preliminary — 90 days post-deployment)
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Documentation time per shift | 2.5 hrs | 1.4 hrs | **-44%** |
| Medication error flags caught | Manual | 12 flagged | New capability |
| Incident report completion | 68% same-day | 94% same-day | **+26%** |
| PSW satisfaction (1-10) | 6.2 | 8.1 | **+31%** |

### Technical Architecture
- On-premise server (Dell PowerEdge, 64GB RAM)
- No PHI leaves the building — fully air-gapped option available
- Quebec Law 25 + Ontario PHIPA compliant
- Integration: PointClickCare (read-only), manual MDS entry

### Testimonial
*"OpenClinical AI has given our PSWs time back. Documentation used to eat our evenings. Now it takes 20 minutes. The AI understands the clinical language our team uses."*
— Director of Care, Gary J Armstrong LTC

### Next Steps
Expanding to 3 additional Ottawa LTC facilities in Q3 2026.

**Interested in deploying for your organization?**
Contact: simpliibarrii@outlook.com
