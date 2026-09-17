# Controlled agency intake — operational handoff

The owner approved the versioned notice `mira-agency-2026-09-18-v1` and controlled intake on 2026-09-18. The live notice is https://pilot.wegc.fund/mira/agency-privacy.html. Do not silently change its text while reusing the same version: retain the old notice and assign a new version for a material revision.

## Operator workflow

1. Invite only an owner-agreed email through the existing Access policy. Adding it grants authentication, not agency membership or operator rights. Do not use Everyone.
2. The representative enters their own OTP and submits the three-step form with explicit consent. Record the receipt privately. A technical test must be labelled as such; do not represent it as a commercial agency activation.
3. Open Operator → application. Review facts and record a reasoned stage. Compose-email opens the operator's own mail client; templates require review. The application does not send messages or track sent mail.
4. Assign an agency representative only from the verified application and only after reviewing their authority. An active agency requires a real, current agreement reference. No agreement means no activation; never manufacture evidence for a green test.

## Privacy operations

The company privacy mailbox and the 24-month limit for enquiries without engagement were confirmed by the owner. The notice describes foreign Cloudflare processing and the observed D1 region; this is not a legal clearance for unrestricted cross-border collection.

- Record access/correction/withdrawal requests privately and verify the requester against the existing account. Never ask for an OTP or authentication cookie.
- The operator owns the enquiry record, consent and review-journal retention process. There is no automated purge and no deletion button in the current UI. Track the last actual contact separately when it differs from the stored application update time; do not treat every administrative update as new applicant contact.
- Review enquiries against the approved 24-month limit and any separately established legal hold. Prepare a targeted deletion/anonymisation plan including related records and backups, obtain authorization for irreversible deletion, and preserve only the minimum lawful audit. Do not delete production data as a test.
- Buyer documents, passports, banking details and signed contracts are not uploaded through this form. Contract evidence points to a separately controlled private archive.

## Live acceptance still required

Second allowed email → OTP → own application → receipt → same-attempt retry → logout/login → own receipt → operator review/decision. Confirm ordinary API access cannot read another identity or call admin routes. Current successful signed-fixture browser tests are separate evidence. Without a real agreement, production acceptance stops at a correct denial of activation.

## Recovery

The preceding Worker version is recorded in WORK-STATUS.md. The preserved admin checkpoint and its private configuration keep intake disabled. Do not execute a rollback or restore a database merely to test it: recovery acceptance uses a separate test database. A previous real D1 export was restored into isolated local SQLite; remote D1 disaster recovery has not been exercised.
