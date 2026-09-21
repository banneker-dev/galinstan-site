# Rules for this repository

`00_Start_Here/CURRENT_STATE_REPO.md` in the Galinstan drive is the living document for
the code and wins over anything here. This file holds only what a session working in this
repository needs in front of it.

1. **Do not write page copy.** Copy comes from `50_Claude_Outputs/SITE_COPY_STAGE1.md`
   and is entered in `src/page_copy.py` with its status. Do not promote a string from
   `pending` to `approved`: approval is Antwain's, and the date and wording are recorded
   with it.
2. **Do not delete a guard to make a build pass.** If a guard is wrong, change it on
   purpose, in its own commit, with the reason in the commit message.
3. **Almost nothing is fetched at page load, and on demo paths, nothing at all.** No font
   service, no CDN, no library, no image host, no tag manager. **One** exception exists on
   marketing paths: the Cloudflare Web Analytics beacon, which is injected at the edge and
   is named in `PERMITTED_BEACON_HOSTS` in `tools/guards.py`. Adding a second name to that
   set is a decision with a written reason, not a fix. Anything served under `/demo`
   carries the product's rule instead: nothing, no exception. `docs/ANALYTICS.md` has the
   reasoning, including why the build-time guard alone was not enough to enforce it.
4. **Add a file to `public/` only through the allowlist in `build.py`.** Files in the
   repository are not published; files in the allowlist are.
5. **No dependencies.** Python 3.12 and the standard library. If something seems to need
   a package, it is worth being sure the page needs the something.
6. **A placeholder renders as a visible marker, never as a blank.** A blank and a zero
   read differently, and a silent blank ships.
