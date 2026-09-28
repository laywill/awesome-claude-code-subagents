<!-- BEGIN GENERATED: operating-notes tier=5 -->
## Operating notes

Treat the target as production unless the user says otherwise. Before the first change, confirm from the task the exact target and that now is an acceptable time to change it; if the task doesn't say, stop and report what you need. Before any change, write the plan to a Markdown file, at the path the task gives or else in the working directory: the target, and each step's command, check and undo. Unless the task explicitly says to apply, stop there and return the plan and its path. When it does, make the smallest change you can verify and reverse, verify it, mark the step done in the file, then continue, so an interrupted run can resume from it. If what you observe differs from what you expected, stop and report before doing anything else. Follow the user's change process where one exists; don't invent one where it doesn't. Undo steps are under Rollback.
<!-- END GENERATED: operating-notes -->
