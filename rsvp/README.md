# RSVP form → Google Sheet

The RSVP form on the website is styled to match the site. Behind the scenes
each reply is sent to a Google Form, which saves it as a row in a Google Sheet
in your Drive. Guests never see Google's own form page.

Until this is set up, the form still works: pressing **Send** opens the
guest's email app with their answers filled in, addressed to
iball.lucy+wedding@gmail.com.

## One-off setup (about 5 minutes)

1. Sign in to Google as whichever account should own the replies (Lucy's,
   if the wedding Drive is hers).
2. Go to <https://script.google.com> → **New project**.
3. Delete what's there, paste in the whole of `create-google-form.gs`, and
   save.
   - If your wedding folder in Drive isn't called `Wedding`, change
     `DRIVE_FOLDER_NAME` at the top first.
4. Make sure `createRsvpForm` is selected in the toolbar and press **Run**.
   Google will ask for permission to create forms and sheets in your Drive —
   allow it. (It may warn the app is unverified: **Advanced → Go to project**.
   It's your own script.)
5. Open the **Execution log** at the bottom. Copy the block between the
   `=====` lines.
6. In `index.html`, find `var RSVP_GOOGLE_FORM = {` near the bottom and paste
   the copied block over it (from `var` to the closing `};`).
7. Commit and push. Send a test RSVP from the live site and check it lands in
   the **Jack & Lucy — RSVPs** sheet.

Delete the test row afterwards.

## Good to know

- Don't edit the questions in the Google Form itself. Renaming is fine, but
  deleting or re-creating a question changes its code and replies to it will
  silently stop arriving. If you want different questions, change both
  `create-google-form.gs` and the form in `index.html`, then run the script
  again to make a fresh form.
- People who say they can't come only answer the first two questions.
- To close RSVPs later, open the Google Form → **Responses** → turn off
  **Accepting responses**, and take the form off the website.
