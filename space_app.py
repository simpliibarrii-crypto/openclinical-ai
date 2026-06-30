import gradio as gr

TOOLS = {
    "PSW Shift Assistant 👨‍⚕️": {
        "desc": "Convert voice/text shift notes to structured clinical documentation",
        "demo": "**[Demo]** Converting your shift note to SOAP format...\n\n**S (Subjective):** Resident reported mild discomfort in left knee during morning care.\n**O (Objective):** Ambulated 20m with walker, mild limp noted. BP 128/78, O2 sat 97%.\n**A (Assessment):** Potential early knee inflammation, no acute distress.\n**P (Plan):** Monitor × 24h, notify RPN if worsening. Elevate left leg during rest periods.\n\n*Saved to PointClickCare. Incident flag: None.*"
    },
    "Medication Reconciliation 💊": {
        "desc": "Flag drug interactions and reconcile medication lists",
        "demo": "**[Demo]** Checking medication list for interactions...\n\n⚠️ **Interaction flagged:** Warfarin (5mg daily) + Aspirin (81mg) — increased bleeding risk\n✅ Metformin 500mg BID — No interactions\n✅ Lisinopril 10mg daily — No interactions\n\n*Recommendation: Confirm warfarin + aspirin combination is intentional. Notify prescribing physician.*\n\n*All data processed on-premise. No PHI transmitted.*"
    },
    "Fall Risk Scoring 🏃": {
        "desc": "Ontario-validated fall risk assessment (MORSE scale)",
        "demo": "**[Demo]** Calculating MORSE Fall Scale...\n\n| Factor | Score |\n|--------|-------|\n| Fall history (yes) | 25 |\n| Secondary diagnosis (yes) | 15 |\n| Ambulatory aid: walker | 15 |\n| IV/heparin lock (no) | 0 |\n| Gait: weak | 10 |\n| Mental status: aware | 0 |\n\n**Total MORSE Score: 65 — HIGH RISK**\n\n📋 Recommended interventions: Bed alarm, non-slip footwear, hourly rounding, physiotherapy consult."
    },
    "Incident Report 📋": {
        "desc": "Auto-complete incident reports for regulatory compliance",
        "demo": "**[Demo]** Generating incident report...\n\n**INCIDENT REPORT — Auto-Generated**\nDate: 2026-06-30 | Time: 14:32 | Location: Room 214\nResident ID: [REDACTED for demo]\nType: Near-fall (no injury)\n\nNarrative: Resident found gripping bed rail, appeared unsteady. PSW assisted to bed. No injury sustained. Resident alert and oriented.\n\nImmmediate actions: Resident settled in bed, vital signs taken (stable), family notified at 14:45.\n\n**Status:** Submitted to DOC. Regulatory flag: None required (no injury).\n*Ontario MOHLTC compliant format.*"
    }
}

def respond(message, tool):
    return TOOLS[tool]["demo"]

with gr.Blocks(title="OpenClinical AI — Clinical AI for Canadian Healthcare") as app:
    gr.Markdown("""
    # 🏥 OpenClinical AI
    ### Sovereign Canadian Clinical AI — Deployed at Gary J Armstrong LTC, Ottawa
    
    > PHIPA · HIPAA · Quebec Law 25 compliant · On-premise · No PHI leaves your facility
    """)
    
    tool_dd = gr.Dropdown(choices=list(TOOLS.keys()), value="PSW Shift Assistant 👨‍⚕️", label="Select Tool")
    
    @gr.render(inputs=tool_dd)
    def show_desc(tool):
        gr.Markdown(f"*{TOOLS[tool]['desc']}*")
    
    msg = gr.Textbox(placeholder="Enter shift note, medication list, or patient observation...", label="Input", lines=3)
    output = gr.Markdown(label="OpenClinical AI Output")
    btn = gr.Button("Process", variant="primary")
    btn.click(respond, [msg, tool_dd], output)
    
    gr.Markdown("---\n**Deploy for your facility:** Contact simpliibarrii@outlook.com · [GitHub](https://github.com/simpliibarrii-crypto/openclinical-ai)")

app.launch()
