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
3. **Nothing is fetched at page load.** No font service, no CDN, no analytics script that
   pulls a second file, no image host. The habit is the product's constraint practised
   where it is cheap.
4. **Add a file to `public/` only through the allowlist in `build.py`.** Files in the
   repository are not published; files in the allowlist are.
5. **No dependencies.** Python 3.12 and the standard library. If something seems to need
   a package, it is worth being sure the page needs the something.
6. **A placeholder renders as a visible marker, never as a blank.** A blank and a zero
   read differently, and a silent blank ships.
