# First-partner catalogue presentation — local acceptance

2026-09-17. Base source: `13360ee8e9b74f22b6e474f128bbd3ac5b5cd513`.

## Changes

- All 618 project cards and detail pages now have a visual. Eleven exact local project associations are kept separate from labelled MIRA/Phuket editorial covers. No cover is represented as the specific property.
- Project images rank first, then metadata completeness. No price, available-unit count, seller verification or commercial permission is inferred.
- Consistent card proportions, quieter availability copy, compact mobile filters and a visible connection CTA. Existing editorial and alternate designs retain their routes.
- localStorage shortlist with session fallback, storage-event and page-restoration synchronization, download/remove/clear, and return links retaining catalogue filters. Pagination uses browser history.
- Public detail pages contain no disabled registration CTA or buyer-data form. Real registration remains disabled.
- Legacy acceptance now checks the intended onboarding landing, then opens the catalogue explicitly; all 45-record and responsive assertions remain.

## Local evidence

- 83 Node tests passed using Node 22.20.0.
- 110 Python tests passed using Python 3.9.6 with a resolved temporary directory (`/private/tmp`). Includes links, fragments and image files across the catalogue and all 618 detail pages.
- Codex in-app browser: all 618 unique IDs across 26 pages; villa filter 143; search; shortlist add, remove, clear, reload persistence; downloaded file contents verified; filter-preserving return.
- Three detail pages checked: Casa de Monte, The Modeva and Andamanda Phuket (editorial-cover case). Images loaded; no buyer-data inputs.
- Landing and catalogue widths 320, 390, 768 and 1440 checked; catalogue additionally 1024. No horizontal overflow. Landing local-plan and landing → catalogue → detail navigation passed.
- Preserved editorial qualifier → onboarding → catalogue passed with 45 records. Browser console had no recorded errors/warnings in this session.
- Desktop first screen, middle catalogue, mobile catalogue and object screenshots saved as local deliverables.

The standalone Playwright/Chrome process could not launch inside this Mac execution sandbox. This is recorded separately from successful in-app browser checks; the existing CI browser suites remain in place. Publication and live-domain verification follow this source checkpoint and are not claimed here.

No real registration, external messages, customer data, DNS changes or unrelated project resources were enabled or changed.
