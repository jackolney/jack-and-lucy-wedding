# Jack & Lucy — 5th June 2027

The wedding website. Plain HTML and CSS, no build step, no framework. Open
`index.html` in a browser and it works.

```
index.html     all the words — this is the only file you need to edit
styles.css     colours, type and layout (taken from Lucy's save-the-date)
images/        the barn, the floral frame, our photos
art/           Lucy's master artwork, and the scripts that cut the site images from it
```

## Changing the words

1. Open `index.html` in any text editor.
2. Find the text you want to change and type over it.
3. Save, commit, push. Vercel redeploys in about 30 seconds.

Anything still undecided is marked in the page like this:

```html
<span class="tbc">to confirm</span>
```

It shows on the site as a small "to confirm" tag so guests know it isn't final.
When you settle it, replace the text and delete that `<span>`.

Currently marked to confirm:

- Length of the ceremony
- Taxi firms to recommend
- Whether to open up camping at the barn
- Gift wording
- Confetti in the churchyard
- The RSVP deadline
- The RSVP email address itself — `jackandlucy2027@gmail.com` is a placeholder.
  Create it (or swap in whichever address you want) in **two** places in
  `index.html`: the `href="mailto:..."` and the visible text next to it.

## Adding a section

Copy any existing `<section class="section" id="...">` block, change the `id`,
the title and the contents, and add a matching link to the `<nav>` at the top.

## Adding a photo

Drop the file into `images/`, then copy one of the `<figure class="plate">`
blocks in the "Us" section and point it at the new filename. Resize large
photos to about 1400px on the long edge first, so the page stays quick on
phones.

## Deploying

See `DEPLOY.md`.

## The artwork

All of it is Lucy's. The two masters live in `art/source/` and everything the
site uses is derived from them, so those two files are the only ones to keep
safe:

```
art/source/card.png           the save-the-date, 1056x1489
art/source/floral-sides.png   the two flower columns, transparent
```

`art/build_assets.py` cuts the site's images out of them:

```bash
python3 art/build_assets.py
```

| Produces | From |
| -------- | ---- |
| `images/save-the-date.jpg` | the card, sized down for the page |
| `images/barn.webp` | the barn, lifted off the card |
| `images/floral-spray.webp` | the coral cluster at the foot of the card |
| `images/floral-left.webp`, `floral-right.webp` | the flower columns, split and cropped |

Two things that script does which are worth knowing if you ever adjust it.

The barn and the spray are cut out of the card, so the paper behind them has to
go or they'd sit on a faint cream rectangle. Rather than masking to a flat
colour, it turns the paper into transparency and divides it back out of the
ink, which keeps the pencil its own warm grey instead of washing it out.

The wreath overlaps the barn at both ends, so no rectangle around the barn is
free of flowers. The barn is neutral pencil and the flowers are not, so the
barn's transparency is also gated on saturation — anything coloured drops out,
which clears the fragments without hand-masking.

**If you replace a master**, drop the new file into `art/source/` under the same
name, re-run the script, and commit. If you swap in a card with a different
layout, the crop boxes at the top of the script (`BARN_BOX`, `SPRAY_BOX`) will
need moving.

## Colours

From Lucy's save-the-date, sampled from the artwork itself:

| Token          | Hex       | Where it's used                  |
| -------------- | --------- | -------------------------------- |
| `--paper`      | `#f8f6f2` | page background (the card stock) |
| `--ink`        | `#4a443c` | body text                        |
| `--ink-quiet`  | `#8a8076` | headings, the card's lettering   |
| `--rose`       | `#e3a09b` | underlines, links                |
| `--cornflower` | `#93accb` | accents                          |
| `--coral`      | `#ec9e77` | the note panels                  |
| `--olive`      | `#8e9670` | times in the running order       |

These are the same colours as the bridesmaids' dresses and the buttonholes.
