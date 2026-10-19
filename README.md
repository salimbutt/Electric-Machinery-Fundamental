# Electric Machinery Fundamentals — Interactive Course

A fully client-side course website built around Chapman's *Electric Machinery Fundamentals* (4th ed.):
eight chapters of live simulations, animated phasor diagrams, step-by-step derivations and worked examples.

**Author:** Dr. Muhammad Salim Butt · University of Engineering & Technology · salimbutt@uet.edu.pk

## Live site

Deployed with GitHub Pages — the homepage is `index.html` at the repository root.

## Project structure

```
index.html            ← clean course homepage and chapter selection (generated)
chapters.html         ← dedicated chapter-selection page (generated)
video-lectures.html   ← teacher weekly-plan video library (generated)
video-lectures.json   ← verified topic mappings and explicitly unresolved links
chapter-pages/
  chapterN.html       ← chapter overviews and topic cards (generated)
  viewN.html          ← outer wrappers for original topic and full-chapter views (generated)
chapters/
  chapter0.html       ← Introduction: AC systems & reactive components
  chapter1.html       ← Chapter 1: Introduction to machinery principles
  chapter2.html       ← Chapter 2: Transformers
  chapter3.html       ← Chapter 3: AC machinery fundamentals
  chapter4.html       ← Chapter 4: Synchronous machines
  chapter5.html       ← Chapter 5: Induction motors
  chapter6.html       ← Chapter 6: DC machines
  chapter7.html       ← Chapter 7: Single-phase & special motors
build.py              ← regenerates index.html from chapters/
.nojekyll             ← tells GitHub Pages to serve the files exactly as they are
```

Each file in `chapters/` is a complete, self-contained interactive app (its own styles, scripts and
section navigation) and is treated as protected source. Generated `chapter-pages/viewN.html`
wrappers load these original apps for both direct-to-topic links and the full-chapter view, and
provide fullscreen and chapter-overview navigation outside the lesson content.

## How the site is assembled

`build.py` generates the homepage, chapter-selection page, chapter overviews, and outer lesson
wrappers. Generated pages reuse the homepage navigation header; lesson wrappers keep it outside
the lesson shell so fullscreen mode can continue to take over the viewport. The homepage contains
course introduction and chapter cards only. Topic cards use the registered topic IDs as URL hashes
and load the corresponding original chapter application inside an outer wrapper. The full-chapter
action loads that same original application without a topic hash.
This keeps the independent chapter apps separate and preserves their behavior. The site adds:

- a course homepage and responsive Explore Chapters selection grid,
- smooth, navbar-aware homepage section navigation and subtle page/topic transitions that
  respect reduced-motion preferences,
- a dedicated chapter overview page using topic cards as the single topic-browsing interface,
- outer lesson wrappers with direct topic loading, fullscreen controls, and a context-correct
  return to the chapter overview; interactive lessons retain a collapsible topic sidebar and
  show previous/next topic navigation and progress in the main content area,
- a generated Video Lectures page. It groups the preserved teacher-plan topic and week associations
  from `video-lectures.json`, independently of the textbook chapter registry, and creates an
  embedded player only after the student selects a video. Uncertain links remain recorded as
  unresolved and are not shown as topic cards,
- optimized WebP versions of the homepage imagery, viewport-triggered loading for below-the-fold
  images, and on-demand loading and parsing of the shared topic search index.

## Editing content

1. Edit the relevant source file or data file. The original chapter applications in `chapters/`
   remain teacher-created course content; video assignments belong in `video-lectures.json`.
2. Run `python build.py` (Python 3, no dependencies).
3. Review the regenerated navigation pages and wrappers.

## Deploying to GitHub Pages

1. Push the repository to GitHub.
2. *Settings → Pages → Build and deployment*: Source **Deploy from a branch**, branch **main**, folder **/ (root)**.
3. The site appears at `https://<user>.github.io/<repo>/`. No build step is required on GitHub.

## Licence

Teaching material © Dr. Muhammad Salim Butt. Figures, derivations and simulations are original;
equation numbers follow Chapman's text for ease of cross-reference.
