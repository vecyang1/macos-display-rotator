---
phase: 1
plan: "01"
type: research
wave: 1
depends_on: []
files_modified:
  - .planning/phases/01-technology-decision-project-setup/TECH_DECISION.md
autonomous: true
requirements: []
must_haves:
  truths:
    - Root cause of arrangement preservation bug identified
    - Python fix effort quantified with specific tasks
    - Swift rebuild effort quantified with API references
  artifacts:
    - TECH_DECISION.md with analysis findings
  key_links:
    - screen_rotator.py (existing implementation)
    - displayplacer documentation
    - CoreGraphics Display Services API docs
---

# Plan 01: Analyze Existing Python Implementation

## Context

The project has an existing Python implementation (~750 lines) that works for most features but has a critical bug: display arrangement is not preserved after rotation. Before deciding whether to enhance Python or rebuild in Swift, we need to understand the root cause of this bug and assess the effort required to fix it.

## Tasks

<task id="01-01" type="research">
<name>Diagnose arrangement preservation bug in Python code</name>
<files>
- screen_rotator.py
- displayplacer CLI help output
</files>
<action>
Read screen_rotator.py to trace rotation flow. Examine save_current_layout() and load_saved_layout() methods. Identify why displayplacer command at line 467 only includes id, res, degree but not origin/position parameters. Check if displayplacer supports origin coordinates. Document root cause: rotation command lacks position parameters that displayplacer supports.
</action>
<verify>
Root cause documented with line numbers, explanation of partial displayplacer command issue, and identification of missing origin parameters.
</verify>
<done>false</done>
</task>

<task id="01-02" type="research">
<name>Estimate Python fix effort and assess risks</name>
<files>
- displayplacer documentation
- screen_rotator.py set_rotation() method
</files>
<action>
Check displayplacer help to confirm origin parameter support. Estimate changes needed to modify set_rotation() to include origin coordinates from saved layout. Assess reliability risks of displayplacer for position preservation. Consider coordinate transformation complexity. Evaluate long-term maintainability of Python + displayplacer architecture.
</action>
<verify>
Effort estimate documented with specific tasks, risk factors identified (displayplacer reliability, coordinate complexity), and maintainability assessment included.
</verify>
<done>false</done>
</task>

<task id="01-03" type="research">
<name>Research Swift approach and compare with Python fix</name>
<files>
- CoreGraphics Display Services API documentation
- Swift menu bar app examples
</files>
<action>
Review CGDisplaySetDisplayMode and CGConfigureDisplayOrigin APIs. Confirm CoreGraphics allows rotation and origin in single transaction. Assess Swift development effort for menu bar (NSStatusBar), hotkeys (Carbon/Cocoa), display control (CoreGraphics). Create comparison table: Python fix vs Swift rebuild. Consider native API reliability vs CLI dependency. Factor in maintenance burden.
</action>
<verify>
Swift approach documented with API references, effort comparison table created, clear recommendation with rationale, and long-term maintenance considerations included.
</verify>
<done>false</done>
</task>

## Verification Criteria

**Must verify:**
- [ ] Root cause of arrangement bug identified with code references
- [ ] Python fix effort estimated with specific tasks
- [ ] Swift rebuild effort estimated with API references
- [ ] Technology recommendation documented with clear rationale
- [ ] Decision accounts for reliability, maintainability, and user preference

**Success means:**
- Clear understanding of why arrangement preservation fails
- Quantified effort comparison between Python enhancement and Swift rebuild
- Actionable recommendation that enables Phase 2+ planning

## Goal-Backward Derivation

**Phase goal:** Establish whether to enhance Python implementation or rebuild in Swift, and set up development environment

**Must-haves to achieve goal:**
1. Root cause analysis of arrangement preservation bug
2. Effort estimate for Python enhancement path
3. Effort estimate for Swift rebuild path
4. Technology decision with documented rationale
5. Development environment setup (deferred to Plan 02)

**This plan delivers:** Items 1-4 (analysis and decision)
