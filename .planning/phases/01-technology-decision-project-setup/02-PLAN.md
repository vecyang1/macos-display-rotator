---
phase: 1
plan: "02"
type: setup
wave: 2
depends_on: [01]
files_modified:
  - .planning/phases/01-technology-decision-project-setup/TECH_DECISION.md
  - .planning/phases/01-technology-decision-project-setup/DEV_SETUP.md
  - README.md (if setup instructions need updating)
autonomous: true
requirements: []
must_haves:
  truths:
    - Technology choice made (Python or Swift)
    - Decision rationale documented
    - Development environment verified working
  artifacts:
    - TECH_DECISION.md with final decision
    - DEV_SETUP.md with setup instructions
  key_links:
    - Plan 01 analysis findings
    - Chosen technology documentation
---

# Plan 02: Make Technology Decision and Document

## Context

Based on the analysis from Plan 01, we need to make a final technology decision and document it clearly. This decision will determine the entire approach for Phases 2-6. The decision should optimize for solving the arrangement preservation bug reliably while considering development velocity and maintainability.

## Tasks

<task id="02-01" type="decision">
<name>Make final technology decision based on analysis</name>
<files>
- .planning/phases/01-technology-decision-project-setup/TECH_DECISION.md (Plan 01 findings)
</files>
<action>
Review Plan 01 analysis. Evaluate decision factors: reliability (which solves arrangement preservation permanently), effort delta (Python fix vs Swift rebuild), maintainability, dependencies (native vs CLI). Choose Option A (enhance Python with origin coordinates) or Option B (rebuild in Swift with CoreGraphics). Document in TECH_DECISION.md: chosen option, primary rationale, trade-offs, risk mitigation.
</action>
<verify>
Decision clearly stated (Python or Swift), rationale explains arrangement preservation solution, trade-offs documented, risk mitigation included, decision enables Phase 2+ planning.
</verify>
<done>false</done>
</task>

<task id="02-02" type="documentation">
<name>Document development environment setup</name>
<files>
- .planning/phases/01-technology-decision-project-setup/DEV_SETUP.md
</files>
<action>
Create DEV_SETUP.md based on chosen technology. If Python: document Python 3.12+, dependencies (rumps, pynput, displayplacer), venv setup, py2app build, testing. If Swift: document Xcode version, Swift version, macOS target, frameworks (AppKit, CoreGraphics, Carbon), project structure, build/signing, testing. Include step-by-step instructions any developer can follow.
</action>
<verify>
DEV_SETUP.md created with complete setup steps, actionable instructions, dependencies with versions, build process documented, testing approach defined.
</verify>
<done>false</done>
</task>

<task id="02-03" type="setup">
<name>Verify development environment works</name>
<files>
- DEV_SETUP.md
- Project build artifacts
</files>
<action>
Follow DEV_SETUP.md from scratch. Install dependencies. Build project (existing Python or new Swift skeleton). Run application. Verify menu bar icon appears. Document issues and update DEV_SETUP.md. If Swift chosen and no skeleton exists: create minimal Swift menu bar app, verify compile/run, commit to git.
</action>
<verify>
Environment set up successfully, project builds without errors, application runs with menu bar icon, DEV_SETUP.md verified accurate (or updated), Swift skeleton committed if applicable.
</verify>
<done>false</done>
</task>

## Verification Criteria

**Must verify:**
- [ ] Technology decision documented in TECH_DECISION.md
- [ ] Decision rationale is clear and technically sound
- [ ] Development environment documented in DEV_SETUP.md
- [ ] Development environment verified working (can build and run)
- [ ] All setup steps tested and confirmed accurate

**Success means:**
- Clear technology choice that enables Phase 2+ planning
- Any developer can set up the environment using DEV_SETUP.md
- Build process works reliably
- Ready to start implementation in Phase 2

## Goal-Backward Derivation

**Phase goal:** Establish whether to enhance Python implementation or rebuild in Swift, and set up development environment

**Must-haves to achieve goal:**
1. Root cause analysis (delivered by Plan 01)
2. Effort comparison (delivered by Plan 01)
3. Technology decision with rationale (this plan, task 02-01)
4. Development environment setup (this plan, task 02-02)
5. Verified working build process (this plan, task 02-03)

**This plan delivers:** Items 3-5 (decision and setup)
