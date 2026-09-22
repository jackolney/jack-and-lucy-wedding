# Jack & Lucy — 5th June 2027

The wedding website. Plain HTML and CSS, no build step, no framework. Open
`index.html` in a browser and it works.

```
index.html     all the words — this is the only file you need to edit
styles.css     colours, type and layout (taken from Lucy's save-the-date)
images/        the barn, the floral frame, our photos
art/           the save-the-date, redrawn as vector art
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

Lucy's original save-the-date was a 1135×1600 JPEG — fine on a phone screen,
too small and too compressed to enlarge or print. `art/build_card.py` redraws
it as vector art, so it's sharp at any size, from a website thumbnail to a
poster.

The barn's geometry was measured off Lucy's drawing (the roof silhouette was
sampled column by column, which is why the left cat-slide sweeps and the right
runs at a steadier pitch). The wildflower frame is generated — petals, buds,
seed pods, ferns and stems drawn from a palette sampled out of her card — so
re-running the script reshuffles the planting. The lettering is real type,
Cormorant Garamond and Italianno, embedded in the file.

```bash
cd art
python3 build_card.py all     # all six SVGs
node render.mjs               # PNGs and print-ready PDFs into art/out/
```

| File | What it's for |
| ---- | ------------- |
| `art/save-the-date.svg` | the whole card, fonts embedded — send this to a printer |
| `art/barn.svg` | just the barn, transparent — used in the site header |
| `art/floral-left.svg`, `floral-right.svg` | the frame's two columns, for the page edges |
| `art/floral-spray.svg` | the coral cluster, used in the site footer |
| `art/card-blank.svg` | card with no lettering, for a different message |
| `art/out/save-the-date-3000.png` | 3000×4242 raster, for anything that won't take an SVG |
| `art/out/save-the-date-a5.pdf` | A5, print ready |
| `art/out/save-the-date-a6.pdf` | A6, standard postcard size |

To change a colour, edit the palette block at the top of `build_card.py` and
re-run. To reshuffle the flowers, change the seed in `random.Random(20270605)`.

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
