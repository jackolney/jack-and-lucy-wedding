# Putting the site online

One-off setup, then every future change is three commands.

You need a GitHub account and a Vercel account. Both are free for this, and
Vercel will let you sign in with GitHub so it's one login.

---

## 1. Put the code on GitHub

Install the GitHub CLI once (`brew install gh` on a Mac), then from inside this
folder:

```bash
gh auth login              # follow the prompts, choose GitHub.com + browser
gh repo create jack-and-lucy-wedding --private --source=. --push
```

That creates a private repository and pushes everything up.

**Without the CLI:** create a new private repository at
<https://github.com/new>, call it `jack-and-lucy-wedding`, don't add a README,
then run the three commands GitHub shows you on the next screen.

---

## 2. Connect it to Vercel

1. Go to <https://vercel.com/new> and sign in with GitHub.
2. Pick `jack-and-lucy-wedding` from the list and click **Import**.
3. Leave every setting alone. Framework preset will say "Other"; there's no
   build command and no output directory, which is correct — it's plain HTML.
4. Click **Deploy**.

About thirty seconds later you'll have a live URL, something like
`jack-and-lucy-wedding.vercel.app`. That's the address to put on the
invitations.

To change the subdomain: **Project → Settings → Domains**, edit the
`.vercel.app` name to whatever's free — `jackandlucy.vercel.app` if you're
lucky.

---

## 3. Making changes from now on

Edit `index.html`, then:

```bash
git add -A
git commit -m "Add taxi firms"
git push
```

Vercel notices the push and rebuilds automatically. Refresh the site in half a
minute and the change is there.

Every version is kept, so nothing is ever lost. `git log` lists the history,
and Vercel's Deployments tab lets you click any previous version to preview it
or roll back to it.

---

## Using your own domain later

Worth doing if you'd rather the invitations read `jackandlucy.wedding` than a
`.vercel.app` address. Roughly £10–30 a year.

1. Buy the domain. Cloudflare and Namecheap are both cheap and painless.
   `.co.uk` and `.com` are the cheapest; `.wedding` costs a bit more.
2. In Vercel: **Project → Settings → Domains → Add**, type the domain.
3. Vercel shows you the DNS records to create. Add them at your registrar.
4. Wait — usually minutes, occasionally a few hours. Vercel sorts the HTTPS
   certificate out on its own.

The `.vercel.app` address keeps working alongside it, so you can switch
whenever without breaking any link you've already shared.

---

## If something looks wrong

- **Site loads but has no styling** — `styles.css` didn't get committed. Check
  `git status`, then `git add -A && git commit -m "Add stylesheet" && git push`.
- **Photos missing** — the filename in `index.html` doesn't match the file in
  `images/`. Capital letters matter on Vercel even though they don't on a Mac.
- **Change hasn't appeared** — check the Deployments tab in Vercel. If the
  latest deployment isn't there, the push didn't land: run `git push` again.
- **Page looks stale in a browser** — a hard refresh (Cmd+Shift+R) clears it.
