# CP16 — finish actual public acceptance, not real signup

17 September 2026. Owner requested preserved and new LIVE design links and a truthful readiness handoff.

## Observed, not inferred

CP15 acceptance35199313364 failed because a Playwright Request argument replaced a lambda's intended HTTP status in a negative catalogue fixture. CP16 b470491 fixed the callback and added four unit regressions. Source regression passed locally (83Node/106Python), but actual browser navigation in this execution container is administrator-blocked. The existing GitHub Actions runner is used, without bypassing the local browser policy.

Next run35200855686 passed fourteen campaign groups before a second test assertion failed: `is_disabled()` was applied to a fieldset container, not to its form controls. Playwright defines disabled state for input/select/button/etc, including descendants of a disabled fieldset. The corrected test checks the fieldset's disabled attribute AND each actual select/submit control. No registration gate or negative case was removed.

Primary implementation reference: https://playwright.dev/python/docs/actionability#enabled

Added an independent editorial browser suite for `/mira/design/` and the preserved45-demo. It checks eleven exact source-file hashes, seven viewport widths, real qualifier/download/navigation, all45legacy records, motion pause/reduced-motion and no-JS disabled controls. This does not change the old design or its demo dataset.

The full-public-release workflow now collects all independent test/audit outcomes even if one fails; any failed command still makes the job fail. Reports include tracebacks, logs, exact tested source and package versions. Actual-domain tests remain read-only, with no personal-data or external-message submission.

## Already measured locally

Read-only local HTTP audit:28exact-file checks,644HEAD links including618project URLs,9parsed PDFs/DOCX and3exactQR decodes.200loopbackGET atconcurrency8 completed200success. These results describe localhost only, not real-host capacity or live registration. Artifact remains in the execution workspace until a verified live result is ready for a canonical record.

## Pending

Inspect the new `mira-cp16-public-release` artifact after completion. Do not claim live success until all relevant reports are read. Reconcile canonical launch dashboard and WORK/RESUME, retaining blocked production intake, privacy/controller/hosting and project-commercial gates. Old/current source designs, alternative campaigns and public legal negotiation drafts remain preserved. No owner visual/legal/print approval is inferred.
