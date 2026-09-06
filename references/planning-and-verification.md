# Planning and verification

## Choose Direct or planned execution

Use Direct when the intended change is small and clear, has a narrow blast radius, is easy to reverse, and can be checked with one or a few focused commands. A single bug fix or localized behavior or configuration adjustment normally qualifies even when it touches a test beside the implementation.

Use planned execution when one or more of these materially changes the risk:

- several dependent stages or multiple subsystems must change together;
- an API, database schema, persisted data, authentication, authorization, or external contract changes;
- deployment, migration, rollback, or environment isolation matters;
- the cause or desired product behavior is still ambiguous enough that coding could head in different directions;
- the work is likely to span a session boundary or needs a durable recovery point.

File count is supporting evidence, not the decision rule. A mechanical multi-file rename can stay Direct; a one-line authorization change may need a plan and targeted verification.

## Planning and authorization

Present one recommended direction with its scope and important tradeoff. Infer routine implementation choices from the request and repository evidence, then proceed within the user's authorization. A plan, cross-module change, or deployment boundary alone does not require another approval. Preserve established task scope when the user asks a follow-up question or gives a correction.

Ask only when a missing choice materially changes the outcome or the next action requires authority the user has not supplied. Finish the independent inspection and preparation needed to make that question concrete. Do not silently expand scope into a new architecture, destructive migration, external message, or additional deployment target. Respect workspace-specific release steps when release is already authorized.

Write an actionable plan in the conversation or active planning facility. Create a workspace plan file only when local policy requires one, the work must cross a session boundary, or the user asks for a durable plan. Include the following where relevant:

1. target outcome and explicit non-goals;
2. affected components, contracts, data, and runtime boundaries;
3. ordered implementation steps with concrete files or modules;
4. focused verification for each risky behavior;
5. restart, migration, release, rollback, and archive steps when applicable.

Keep the plan proportional. Do not turn ordinary edits into project management ceremony. Once an approved plan is clear, execute it without asking again at each reversible implementation step.

Planning never replaces specialist skill routing. Use explicitly named skills and the smallest set of unambiguously applicable domain skills under their own trigger rules. Do not load every loosely related skill merely because a plan has several steps.

## Verification budget

Choose the smallest checks that can falsify the changed behavior:

- run focused tests for the edited behavior first;
- avoid broad regression suites when focused coverage is decisive;
- do not build every component in the workspace by habit;
- run a full build or broad suite only when workspace instructions, release policy, dependency or build configuration changes, or the blast radius requires it;
- do not repeat an equivalent passing check without new evidence;
- report checks that were intentionally left to the developer.

For user-interface appearance, do not use browser automation, screenshots, or computer vision as an implicit acceptance gate. Make the code-level checks that are useful and leave visual review to the developer unless the user explicitly requests visual inspection.

## Runtime restart budget

Restart only the runtime whose loaded code or configuration requires it. Discover the component model and commands from workspace-local instructions, manifests, and existing scripts; do not assume any particular component split, language, framework, process manager, or service topology.

- Reuse a healthy live-reload or hot-reload mechanism only when the workspace already provides one and it covers the changed files.
- Rebuild or restart a compiled or long-running component only when its loaded artifact or configuration is stale and local instructions require that lifecycle.
- Documentation, skills, tests, and inactive templates normally do not require runtime restarts.
- If no affected runtime is running, do not start one solely for ceremony unless workspace instructions or the requested acceptance require it.
