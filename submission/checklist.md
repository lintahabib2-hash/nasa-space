# Final submission checklist

> Owner: Member 6 (Backend, Integration, QA & Deployment). Tick everything, in order, before pressing Submit.
> Do the release steps at least 2 hours before the deadline.

## 1. Code is green and merged
- [ ] All six member branches are merged into `main` through PRs (merge order: M5 check-in schema, M2 analytics, M4 environment, M3 UI, then docs)
- [ ] `CI` is green on `main` (`backend` and `frontend` jobs)
- [ ] `python backend/scripts/export_static_snapshot.py --check` passes (the offline snapshot is current)
- [ ] No placeholder text left: search the repo for `TODO`, `MEMBER`, `<paste`
- [ ] No secrets, tokens, personal data or large raw datasets in git (`git log -p | grep -i -E "secret|token|apikey"`)

## 2. Deployed and verified
- [ ] `Deploy` workflow green, including the `verify-live` job
- [ ] Live URL opens in a private window with no login
- [ ] Offline test done on the live URL: [offline-qa-checklist.md](../docs/offline-qa-checklist.md), desktop **and** phone
- [ ] Verification record filled in (`docs/deployment.md`)

## 3. Repository quality
- [ ] A stranger can run it from a fresh clone using only the README commands
- [ ] README: live URL, team table with real names, source table (C01-C05, D01..., X01), threshold rationale, limitations
- [ ] `docs/thresholds.md` matches what the app does (the test enforces the numbers)
- [ ] `CODEOWNERS` has real usernames; `main` is protected
- [ ] A license file is present
- [ ] Release tagged: `git tag v1.0-submission && git push --tags`

## 4. Honesty and consistency
- [ ] Every screen, slide and video clip that shows crew data says it is **simulated**
- [ ] No claim of diagnosis, probability, validated score or personal radiation dose (`docs/claims-to-use-avoid.md`)
- [ ] Slides, video, README and the live app tell the same story and cite the same source IDs
- [ ] `docs/ai-assistance.md` is complete

## 5. Submit
- [ ] All four links open in a private window: live app, repo, slides, video
- [ ] Submitted with time to spare; screenshot of the confirmation saved
