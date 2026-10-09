import { lazy } from "react";

// slug -> page component. Add a line here when a use case page is built.
// Slugs not listed here show the "coming soon" page.
export const pages = {
  "what-is-jev": lazy(() => import("./WhatIsJev.jsx")),
  "jev-vs-llm-vs-agents": lazy(() => import("./JevVsLlmVsAgents.jsx")),
  "jev-supervisor": lazy(() => import("./JevSupervisor.jsx")),
  "score-a-table": lazy(() => import("./ScoreATable.jsx")),
  "guard-the-agent": lazy(() => import("./GuardTheAgent.jsx")),
  "moderation-lab": lazy(() => import("./ModerationLab.jsx")),
  "model-router": lazy(() => import("./ModelRouter.jsx")),
  "structured-decisions": lazy(() => import("./StructuredDecisions.jsx")),
  "grounded-answers": lazy(() => import("./GroundedAnswers.jsx")),
};
