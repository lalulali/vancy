# Tracking Practices

Citation numbers refer to `evidence-tracking.md`.

## Contents
1. What the tracker is for
2. Fields
3. Status definitions
4. Follow-up cadence
5. Weekly review
6. File naming and versioning
7. Reading the numbers
8. Privacy

## 1. What the tracker is for
One place that answers: *What have I applied for, with which documents, what is the status, and what must I do next?* It also stops the user from sending the wrong CV version, forgetting a follow-up, or applying twice to the same role.

## 2. Fields
| Field | Meaning |
|---|---|
| `id` | Number assigned automatically |
| `company`, `role`, `location` | Basics |
| `url`, `ad_file` | Link to the posting and the saved ad text (`--ad`, e.g. `artifacts/output/<Company>_<Role>/job-ad.txt`; postings disappear). The Job Brief is not stored here: put its path in `notes` |
| `applied_date` | Date submitted |
| `cv_version`, `letter_version` | The project-relative path of the file actually sent (for example `artifacts/output/Northwind_Senior_PM/Firstname_Lastname_CV.docx`), or a short variant label (for example `pm-payments-v2`) |
| `status` | See §3 |
| `first_response_date` | Set automatically when status first moves to a response stage |
| `next_action`, `next_action_date` | The single next step and its date |
| `contact` | Recruiter or hiring manager, with email or LinkedIn |
| `pay` | Posted range, expectation or offer (free text) |
| `notes` | Dated log appended by `--note` |

## 3. Status definitions
| Status | Meaning |
|---|---|
| `wishlist` | Interested, not started |
| `preparing` | Writing documents or researching |
| `applied` | Submitted, no reply yet |
| `screening` | Recruiter or phone screen |
| `interviewing` | Interviews in progress |
| `assessment` | Take-home, case or test |
| `offer` | Offer received, not yet decided |
| `negotiating` | In discussion over terms |
| `accepted` | Accepted |
| `rejected` | Employer declined |
| `withdrawn` | Candidate withdrew |
| `ghosted` | No reply after follow-ups; closed |

## 4. Follow-up cadence
Commonly advised practice (career-advice sources, not research) [1][2][3]:
- **After applying:** if there is no reply, one polite follow-up after about 5-7 business days (some sources say one to two weeks). Skip it if the posting says not to contact them.
- **After an interview:** thank-you within 24-48 hours; if there is a stated timeline, wait until it passes; otherwise about 5 business days before one follow-up.
- **Maximum:** about two follow-ups in total per application, then close it as `ghosted` and move on.
- `tracker.py due` flags applications with no reply after `--follow-up-days` (default 7 calendar days). Adjust it to the employer's stated timeline.
- Keep follow-ups short, courteous and useful: restate interest, add one fact, ask for a status.

## 5. Weekly review (15 minutes)
1. `tracker.py due --days 7` and handle every overdue item.
2. Update statuses and dates for everything that moved.
3. Close dead applications (`ghosted` or `withdrawn`).
4. Add new roles from `job-ad-analyzer` briefs; save each ad text.
5. Look at `stats`, and decide what to change (see §7).
6. Choose the 3 most valuable actions for the coming week.

## 6. File naming and versioning
The CV and cover-letter skills save each application's final files in `artifacts/output/<Company>_<Role>/` with the same plain names every time, so the folder, not the file name, tells you which application a file belongs to:
```
artifacts/output/<Company>_<Role>/Firstname_Lastname_CV.docx
artifacts/output/<Company>_<Role>/Firstname_Lastname_Cover_Letter.docx
artifacts/output/<Company>_<Role>/Job_Brief_<Company>_<Role>.md
artifacts/output/<Company>_<Role>/job-ad.txt
```
Never use vague names like `CV_final_v3`. If you must keep two variants for the same application, add a short label before the extension (for example `Firstname_Lastname_CV_v2.docx`) and record the one actually sent.

- Record the **project-relative path of the file you sent** in `cv_version` and `letter_version`, or a short variant label if you prefer. The path pins down exactly which document went out.
- `tracker.py stats` compares response rates **by `cv_version` value**. A unique path per application gives each application its own group, so there is nothing to compare. If you want that comparison, use a short shared variant label (for example `pm-payments-v2`) for every application that used the same CV variant, and keep the path in `notes`.
- Keep a master CV that is never edited per application. Make a tailored copy for each role family or role.

Example (applied on 2026-10-17, follow-up date 7 calendar days later, which is the `due` default; 2026-10-24 is a Saturday, so send the message on the Monday):
```bash
python3 scripts/tracker.py --file artifacts/output/job-applications.csv add --company "Northwind" --role "Senior PM" \
  --applied 2026-10-17 --status applied \
  --cv artifacts/output/Northwind_Senior_PM/Firstname_Lastname_CV.docx \
  --letter artifacts/output/Northwind_Senior_PM/Firstname_Lastname_Cover_Letter.docx \
  --ad artifacts/output/Northwind_Senior_PM/job-ad.txt \
  --note "Brief: artifacts/output/Northwind_Senior_PM/Job_Brief_Northwind_Senior_PM.md" \
  --next "Follow up if no reply" --next-date 2026-10-24
```

## 7. Reading the numbers
`tracker.py stats` shows response rate, interview rate, offers, and median days to first response, and compares response by CV version.
- Treat small samples with caution: below about 20 applications, differences between versions are mostly noise. The script says so.
- Response rates depend on role, market, season and seniority, not only on the documents.
- If many applications get no response, check targeting and keywords first (`job-ad-analyzer`), then the CV (`cv-reviewer`), then how the applications are sent.
- Do not promise that any change will raise response rates.

## 8. Privacy
The default file is `artifacts/output/job-applications.csv` (the script uses it when `artifacts/output/` exists; otherwise `job-applications.csv` in the current folder, or any path via `--file`). The CSV contains personal job-search data and possibly contact details of other people. `artifacts/` is git-ignored: keep the CSV out of git, shared folders and cloud-synced folders. If you use a different location, make sure it is also ignored by version control. Do not paste it into third-party tools without the user's consent. Delete notes about third parties that are no longer needed.
