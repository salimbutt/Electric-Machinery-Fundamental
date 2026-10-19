#!/usr/bin/env python3
"""Build index.html (Homepage), a legacy chapters.html redirect, and chapter-pages/
from the chapter sources in chapters/.

Run:  python build.py
"""
import io, os, re, html, json
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "chapters")
OUT_INDEX = os.path.join(ROOT, "index.html")
OUT_LEGACY_CHAPTERS = os.path.join(ROOT, "chapters.html")
OUT_VIDEO_LECTURES = os.path.join(ROOT, "video-lectures.html")
OUT_SEARCH_INDEX = os.path.join(ROOT, "search-index.json")
VIDEO_DATA = os.path.join(ROOT, "video-lectures.json")
CHAPTER_PAGES_DIR = os.path.join(ROOT, "chapter-pages")
CHAPTER_CARD_IMAGES = (
    "assets/chapter-00-ac-systems.png",
    "assets/chapter-01-machinery-principles.png",
    "assets/chapter-02-transformers.png",
    "assets/chapter-03-ac-machinery.png",
    "assets/chapter-04-synchronous-machines.png",
    "assets/chapter-05-induction-motors.png",
    "assets/chapter-06-dc-machines.png",
    "assets/chapter-07-special-motors.png",
)
FONT_STYLESHEET = """<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"></noscript>"""

CHAPTERS = [
    ("chapter0.html", "Introduction", "AC Systems & Reactive Components",
     "Prerequisites for everything that follows: function graphs and calculus refreshers, single-, two- and three-phase voltages, Y and Δ relations, and the behaviour of resistors, inductors and capacitors — including why sudden switching produces current and voltage spikes.",
     "CHAPTER 00", "AC Systems & Reactive Components. Preparatory material.",
     "#2563eb", "#eff6ff",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>"""),

    ("chapter1.html", "Chapter 1", "Machinery Principles",
     "Rotation and power, Ampère's law from a single wire to a toroid, Faraday's law and self-inductance, force on a wire, the moving conductor, the linear DC machine, AC power, and a full treatment of magnetic circuits.",
     "CHAPTER 01", "Basic principles, magnetic fields, Faraday's law and more.",
     "#0284c7", "#f0f9ff",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>"""),

    ("chapter2.html", "Chapter 2", "Transformers",
     "Ideal and real transformers, the equivalent circuit built from the primary side with winding-to-circuit correspondence, voltage regulation and efficiency with live phasor diagrams, taps, autotransformers, three-phase banks, ratings and instrument transformers.",
     "CHAPTER 02", "Construction, operation, equivalent circuits and testing.",
     "#059669", "#ecfdf5",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>"""),

    ("chapter3.html", "Chapter 3", "AC Machinery",
     "The rotating magnetic field from single-, two- and three-phase windings with animated 2-pole winding diagrams, MMF and flux distribution, induced voltage and torque, insulation, power flow and losses.",
     "CHAPTER 03", "Single & three phase induction machines, synchronous machines.",
     "#7c3aed", "#f5f3ff",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""),

    ("chapter4.html", "Chapter 4", "Synchronous Machines",
     "Generators and motors: phasor diagrams, power-angle curves, terminal characteristics, open- and short-circuit tests, droop and capability curves, V-curves, power-factor correction and starting.",
     "CHAPTER 04", "Operation, performance, excitation and power factor.",
     "#d97706", "#fffbeb",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>"""),

    ("chapter5.html", "Chapter 5", "Induction Motors",
     "Slip, the equivalent circuit, power flow, the torque–speed characteristic from the Thévenin model, NEMA designs, starting and parameter tests.",
     "CHAPTER 05", "Principle, torque-speed, starting methods and control.",
     "#db2777", "#fdf2f8",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="3"></circle><path d="M6 12h.01M18 12h.01"></path></svg>"""),

    ("chapter6.html", "Chapter 6", "DC Machines",
     "The parts of a DC machine and how they work together, commutation, E_A = Kφω and τ = KφI_A, armature reaction, motor torque–speed curves, speed control, and generator characteristics and voltage build-up.",
     "CHAPTER 06", "Construction, operation, speed control and applications.",
     "#0d9488", "#f0fdfa",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"></circle><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>"""),

    ("chapter7.html", "Chapter 7", "Special Motors",
     "Universal motors, the double-revolving-field theory, starting methods, reluctance, hysteresis, brushless DC and stepper motors.",
     "CHAPTER 07", "Stepper, servo, linear and other special machines.",
     "#ea580c", "#fff7ed",
     """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>"""),
]

SEC_BLOCK_RE = re.compile(
    r"section\s*\(\s*'([^']+)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*(?:\([^\)]*\)|function\s*\([^\)]*\))\s*=>?\s*\{(.*?)(?=\n\s*(?:section\(|function\s+render|const\s+SECTIONS|window\.addEventListener|\Z))",
    re.DOTALL
)

BRIDGE = """<script>
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var m=(a.getAttribute('href')||'').match(/^chapter(\\d)\\.html$/);if(m){e.preventDefault();try{parent.postMessage({emfGo:+m[1]},'*');}catch(_){}}},true);
window.addEventListener('message',function(e){var d=e.data||{};if(d.emfSection&&typeof render==='function'){try{render(d.emfSection);}catch(_){}}});
</script>
"""

TOPIC_ICONS = [
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>""", "#2563eb", "#eff6ff"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>""", "#059669", "#ecfdf5"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>""", "#0284c7", "#f0f9ff"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"></circle><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg>""", "#7c3aed", "#f5f3ff"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="3"></circle><path d="M6 12h.01M18 12h.01"></path></svg>""", "#d97706", "#fffbeb"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h2c2 0 3-8 5-8s3 16 5 16 3-8 5-8h3"></path></svg>""", "#db2777", "#fdf2f8"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>""", "#0d9488", "#f0fdfa"),
    ("""<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>""", "#ea580c", "#fff7ed")
]

def load():
    out = []
    for i, (fn, num, title, blurb, ch_code, ch_short, ch_color, ch_bg, ch_icon) in enumerate(CHAPTERS):
        filepath = os.path.join(SRC, fn)
        s = io.open(filepath, encoding="utf-8").read()
        assert "</template" not in s, fn

        matches = SEC_BLOCK_RE.findall(s)
        topics = []
        for sid, grp, lab, block in matches:
            lab_clean = html.unescape(lab.replace(r"\'", "'"))
            grp_clean = html.unescape(grp.replace(r"\'", "'"))

            h2_m = re.search(r'<h2[^>]*>(.*?)</h2>', block, re.DOTALL)
            h2 = re.sub(r'<[^>]+>', '', h2_m.group(1)).strip() if h2_m else ""
            h2 = html.unescape(h2)

            sub_m = re.search(r'<p class=["\']subttl["\'][^>]*>(.*?)</p>', block, re.DOTALL)
            if not sub_m:
                sub_m = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
            sub = re.sub(r'<[^>]+>', '', sub_m.group(1)).strip() if sub_m else ""
            sub = html.unescape(sub)

            num_match = re.match(r"^(?:★\s*)?(\d+(?:[.–\-]\d+)?)\s*·\s*(.*)$", lab_clean)
            if num_match:
                topic_num = num_match.group(1)
                topic_short_title = num_match.group(2).strip()
            elif "practice" in sid or "practice" in lab_clean.lower():
                topic_num = f"{i}.P" if i > 0 else "0.P"
                topic_short_title = "Practice Mode"
            elif "summary" in sid or "quiz" in lab_clean.lower():
                topic_num = f"{i}.Q" if i > 0 else "0.Q"
                topic_short_title = "Summary & Self-Test Quiz"
            else:
                topic_num = f"{i}.{len(topics)+1}"
                topic_short_title = lab_clean

            display_title = h2 if h2 else topic_short_title

            desc = sub.strip()
            if not desc or (desc.startswith("§") and len(desc) < 8):
                if "quiz" in sid or "summary" in sid:
                    desc = "Comprehensive review of key formulas, summary notes, and self-test quiz questions."
                elif "practice" in sid:
                    desc = "Interactive problem solver with randomized values and step-by-step worked solutions."
                else:
                    desc = f"Interactive simulation and visual lessons for {display_title}."

            topics.append({
                "id": sid,
                "group": grp_clean,
                "label": lab_clean,
                "num": topic_num,
                "short_title": topic_short_title,
                "title": display_title,
                "desc": desc
            })

        secs = [(t["id"], t["label"]) for t in topics]
        body = re.sub(r"^\s*<!doctype html>\s*", "", s, flags=re.I).replace("<head>", "<head>\n" + BRIDGE, 1)

        out.append(dict(
            i=i, fn=fn, num=num, title=title, blurb=blurb,
            ch_code=ch_code, ch_short=ch_short, ch_color=ch_color, ch_bg=ch_bg, ch_icon=ch_icon,
            ch_image=CHAPTER_CARD_IMAGES[i],
            topics=topics, secs=secs, body=body
        ))
    return out

CSS_COMMON = """
:root {
  --navy-dark: #070e1e;
  --navy-nav: #081226;
  --navy-hero: #070e1e;
  --hero-background: linear-gradient(110deg, #f8fafc 0%, #f8fafc 48%, #eaf3ff 100%);
  --hero-text: #0b1730;
  --hero-lead: #334155;
  --hero-kicker: #0e7490;
  --hero-highlight: radial-gradient(circle at 75% 40%, rgba(37, 99, 235, 0.08) 0%, transparent 65%);
  --hero-art-glow: radial-gradient(ellipse at center, rgba(37, 99, 235, 0.18) 0%, rgba(56, 189, 248, 0.12) 36%, transparent 72%);
  --hero-bottom-glow: radial-gradient(circle at 50% 100%, rgba(56, 189, 248, 0.05) 0%, transparent 70%);
  --hero-secondary-text: #0b1730;
  --hero-secondary-background: rgba(15, 23, 42, 0.025);
  --hero-secondary-border: rgba(15, 23, 42, 0.22);
  --hero-secondary-hover-background: rgba(15, 23, 42, 0.07);
  --hero-secondary-hover-border: rgba(15, 23, 42, 0.38);
  --hero-art-border: linear-gradient(135deg, rgba(56, 189, 248, 0.48), rgba(37, 99, 235, 0.25) 60%, rgba(255, 255, 255, 0.85));
  --hero-art-shadow: 0 18px 40px rgba(11, 23, 48, 0.14), 0 0 30px rgba(37, 99, 235, 0.12);
  --features-section-start: #eef4fc;
  --navy-heading: #0b1730;
  --blue-primary: #2563eb;
  --blue-hover: #1d4ed8;
  --blue-light: #eff6ff;
  --blue-border: #dbeafe;
  --cyan-accent: #38bdf8;
  --cyan-glow: rgba(56, 189, 248, 0.35);
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --line: #e2e8f0;
  --card-shadow: 0 4px 20px rgba(11, 42, 91, 0.05);
  --card-hover-shadow: 0 12px 30px rgba(11, 42, 91, 0.1);
  --chapter-card-shadow: 0 4px 18px rgba(11, 42, 91, 0.08), 0 0 22px rgba(37, 99, 235, 0.22);
  --chapter-card-hover-shadow: 0 12px 28px rgba(11, 42, 91, 0.14), 0 0 30px rgba(37, 99, 235, 0.32), 0 0 52px rgba(37, 99, 235, 0.16);
  --feature-card-shadow: 0 6px 18px rgba(11, 42, 91, 0.06);
  --feature-card-hover-shadow: 0 10px 24px rgba(11, 42, 91, 0.1);
  --feature-glow: rgba(37, 99, 235, 0.08);
  --feature-glow-hover: rgba(37, 99, 235, 0.15);
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
}

body.dark-mode {
  --bg-page: #0b132b;
  --hero-background: linear-gradient(135deg, #0b1730 0%, #0a1733 55%, #0e2759 100%);
  --hero-text: #ffffff;
  --hero-lead: #cbd5e1;
  --hero-kicker: var(--cyan-accent);
  --hero-highlight: radial-gradient(circle at 75% 40%, rgba(37, 99, 235, 0.22) 0%, transparent 65%);
  --hero-art-glow: radial-gradient(ellipse at center, rgba(37, 99, 235, 0.24) 0%, rgba(56, 189, 248, 0.16) 36%, transparent 72%);
  --hero-bottom-glow: radial-gradient(circle at 50% 100%, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
  --hero-secondary-text: #ffffff;
  --hero-secondary-background: rgba(255, 255, 255, 0.035);
  --hero-secondary-border: rgba(255, 255, 255, 0.34);
  --hero-secondary-hover-background: rgba(255, 255, 255, 0.1);
  --hero-secondary-hover-border: rgba(255, 255, 255, 0.56);
  --hero-art-border: linear-gradient(135deg, rgba(56, 189, 248, 0.4), rgba(37, 99, 235, 0.2) 60%, rgba(255, 255, 255, 0.05));
  --hero-art-shadow: 0 24px 50px rgba(0, 0, 0, 0.55), 0 0 40px rgba(37, 99, 235, 0.25);
  --features-section-start: #0b132b;
  --bg-card: #111d3d;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --navy-heading: #f8fafc;
  --line: #1e2c50;
  --blue-light: rgba(37, 99, 235, 0.15);
  --blue-border: rgba(56, 189, 248, 0.25);
  --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  --card-hover-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
  --chapter-card-shadow: 0 4px 20px rgba(0, 0, 0, 0.32), 0 0 20px rgba(56, 189, 248, 0.22);
  --chapter-card-hover-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 32px rgba(56, 189, 248, 0.34), 0 0 52px rgba(37, 99, 235, 0.18);
  --feature-card-shadow: 0 6px 18px rgba(0, 0, 0, 0.32);
  --feature-card-hover-shadow: 0 10px 24px rgba(0, 0, 0, 0.42);
  --feature-glow: rgba(56, 189, 248, 0.14);
  --feature-glow-hover: rgba(56, 189, 248, 0.23);
}

*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}
body {
  margin: 0;
  background: var(--bg-page);
  color: var(--text-main);
  font: 16px/1.6 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  transition: background-color 0.25s ease, color 0.25s ease;
}
@keyframes emf-page-enter {
  from { opacity: 0.92; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
body.emf-page-enter > :not(.nav):not(#top):not(.search-overlay) {
  animation: emf-page-enter 220ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  body.emf-page-enter > :not(.nav):not(#top):not(.search-overlay) { animation: none; }
}

h1, h2, h3, h4 {
  color: var(--navy-heading);
  margin: 0 0 0.4em;
  line-height: 1.25;
  font-weight: 700;
}

a { color: var(--blue-primary); }
a:focus-visible, button:focus-visible { outline: 2px solid var(--blue-primary); outline-offset: 2px; }

.wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px; width: 100%; }
@media (max-width: 480px) { .wrap { padding: 0 16px; } }

/* Navigation */
.nav {
  --nav-height: 60px;
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 1000;
  background: rgba(8, 18, 38, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  height: var(--nav-height);
}
.nav-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  position: relative;
  left: calc((min(100vw, 1200px) - 100vw) / 2);
  min-width: 0;
  gap: 8px;
  text-decoration: none;
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
}
@media (max-width: 420px) {
  .brand { font-size: 15px; }
  .brand .brand-text { max-width: 260px; overflow: hidden; text-overflow: ellipsis; }
}
.brand .mark {
  color: var(--cyan-accent);
  font-size: 22px;
  line-height: 1;
  filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.5));
}
.brand-text { font-weight: 700; }
.nav-menu { display: flex; align-items: center; gap: 20px; margin-left: auto; }
@media (min-width: 1201px) {
  .nav-menu { margin-right: calc(592px - 50vw); }
}
.nav-links { display: flex; align-items: center; gap: 18px; list-style: none; margin: 0; padding: 0; }
.nav-links a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 14.5px;
  font-weight: 500;
  padding: 5px 3px;
  position: relative;
  transition: color 0.15s ease;
}
.nav-links a:hover, .nav-links a.active { color: #ffffff; }
.nav-links a.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0; right: 0;
  height: 2px;
  background: var(--cyan-accent);
  border-radius: 2px;
  box-shadow: 0 0 6px var(--cyan-accent);
}
.nav-actions { display: flex; align-items: center; gap: 12px; }
.icon-btn {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.15s ease;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.25);
}
.burger {
  display: none;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  width: 40px;
  height: 38px;
  padding: 8px;
  cursor: pointer;
  flex-direction: column;
  justify-content: space-around;
}
.burger span {
  display: block;
  width: 100%;
  height: 2px;
  background: #ffffff;
  border-radius: 2px;
  transition: all 0.2s ease;
}

@media (max-width: 860px) {
  .burger { display: flex; }
  .nav-menu {
    display: none;
    position: absolute;
    top: var(--nav-height); left: 0; right: 0;
    background: #081226;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-direction: column;
    align-items: flex-start;
    padding: 16px 24px;
    gap: 16px;
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
  }
  .nav-menu.open { display: flex; }
  .nav-links { flex-direction: column; align-items: stretch; width: 100%; gap: 12px; }
  .nav-links a { font-size: 16px; display: block; padding: 6px 0; }
  .nav-actions { width: 100%; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); }
}
@media (max-width: 480px) {
  .nav-wrap { gap: 12px; }
}

/* Footer */
.site-footer {
  margin-top: 72px;
  background: #070e1e;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  font-size: 14px;
  padding: 36px 0;
}
.footer-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.footer-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 14px; }
.footer-brand { font-weight: 700; color: #ffffff; }
.footer-dot, .footer-sep { color: rgba(255, 255, 255, 0.3); }
.footer-right { display: flex; align-items: center; gap: 8px; font-weight: 500; font-size: 14px; }
.footer-sub { padding-top: 20px; font-size: 13px; color: #64748b; line-height: 1.6; }
.footer-sub p { margin: 0; }
.footer-sub code {
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Back to top button */
#top {
  position: fixed;
  right: 24px; bottom: 24px;
  z-index: 50;
  width: 44px; height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: var(--blue-primary);
  color: #ffffff;
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}
#top svg { width: 22px; height: 22px; stroke-width: 3; }
#top:hover { transform: translateY(-2px); background: var(--blue-hover); box-shadow: 0 8px 18px rgba(37, 99, 235, 0.38); }
#top:focus-visible { outline: 3px solid #7dd3fc; outline-offset: 3px; }
#top.show { opacity: 1; pointer-events: auto; }
@media (prefers-reduced-motion: reduce) {
  #top { transition: none; }
  #top:hover { transform: none; }
}

/* Search Dialog */
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(7, 14, 30, 0.75);
  backdrop-filter: blur(8px);
  display: grid;
  place-items: flex-start center;
  padding: 80px 20px 20px;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.search-modal {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 640px;
  max-height: 75vh;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}
.search-header svg { color: var(--text-muted); flex-shrink: 0; }
.search-header input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  color: var(--text-main);
  font-family: inherit;
}
.search-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 24px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}
.search-results {
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.search-item {
  display: block;
  padding: 10px 14px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 14px;
  transition: background 0.1s;
}
.search-item:hover {
  background: var(--blue-light);
  color: var(--blue-primary);
}
.search-item small {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 2px;
}
.search-empty {
  padding: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}
"""

CSS_INDEX = CSS_COMMON + """
/* Hero Section */
.hero {
  padding: 130px 0 68px;
  background: var(--hero-background);
  position: relative;
  overflow: hidden;
  color: var(--hero-text);
}
.hero::before {
  content: '';
  position: absolute;
  top: 0; right: 0; width: 650px; height: 100%;
  background: var(--hero-highlight);
  pointer-events: none;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: 0; left: 10%; width: 500px; height: 300px;
  background: var(--hero-bottom-glow);
  pointer-events: none;
}
.hero-wrap {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 48px;
  align-items: center;
  position: relative;
  z-index: 2;
}
.hero-kicker {
  color: var(--hero-kicker);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.hero-title {
  color: var(--hero-text);
  font-size: clamp(32px, 4.2vw, 54px);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.02em;
  margin: 0 0 18px;
}
.hero-lead {
  color: var(--hero-lead);
  font-size: clamp(15.5px, 1.8vw, 18px);
  line-height: 1.65;
  max-width: 580px;
  margin: 0 0 32px;
}
.hero-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hero-actions a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
  font-size: 15.5px;
  line-height: 1.25;
  min-height: 48px;
  padding: 12px 20px;
  border-radius: 10px;
  border: 1px solid transparent;
  transition: background-color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}
.hero-action-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 9px;
  background: rgba(37, 99, 235, 0.1);
  color: var(--blue-primary);
  transition: background-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}
.hero-action-icon svg {
  display: block;
  width: 26px;
  height: 26px;
}
.hero-actions .btn-secondary:hover .hero-action-icon {
  background: rgba(37, 99, 235, 0.17);
  color: var(--blue-hover);
  box-shadow: 0 0 12px rgba(37, 99, 235, 0.18);
}
body.dark-mode .hero-action-icon {
  background: rgba(56, 189, 248, 0.12);
  color: #7dd3fc;
}
body.dark-mode .hero-actions .btn-secondary:hover .hero-action-icon {
  background: rgba(56, 189, 248, 0.2);
  color: #bae6fd;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
}
.hero-actions .btn-primary {
  background: var(--blue-primary);
  border-color: rgba(255, 255, 255, 0.16);
}
.hero-actions .btn-primary:hover {
  background: var(--blue-hover);
}
.hero-actions .btn-secondary {
  color: var(--hero-secondary-text);
  background: var(--hero-secondary-background);
  border-color: var(--hero-secondary-border);
  padding-top: 3px;
  padding-bottom: 3px;
}
.hero-actions .btn-secondary:hover {
  background: var(--hero-secondary-hover-background);
  border-color: var(--hero-secondary-hover-border);
}
.hero-actions a:focus-visible {
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.22), 0 6px 16px rgba(37, 99, 235, 0.2);
}
@media (hover: hover) and (pointer: fine) {
  .hero-actions a:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.2);
  }
  .hero-actions .btn-primary:not(.btn-secondary):hover {
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.32);
  }
}
.hero-actions a:focus-visible {
  outline: 3px solid #7dd3fc;
  outline-offset: 3px;
}
@media (max-width: 560px) {
  .hero-actions { align-items: stretch; }
  .hero-actions a { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  .hero-actions a { transition: none; }
  .hero-actions a:hover { transform: none; }
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  isolation: isolate;
}
.hero-visual::before {
  content: '';
  position: absolute;
  inset: -12%;
  z-index: -1;
  background: var(--hero-art-glow);
  pointer-events: none;
}
.hero-img-card {
  position: relative;
  z-index: 1;
  border-radius: 20px;
  padding: 4px;
  background: var(--hero-art-border);
  box-shadow: var(--hero-art-shadow);
  max-width: 440px;
  width: 100%;
}
.motor-img { width: 100%; height: auto; border-radius: 16px; display: block; }

@media (max-width: 960px) {
  .hero-wrap { grid-template-columns: 1fr; gap: 40px; text-align: left; }
  .hero { padding: 110px 0 56px; }
  .hero-visual { max-width: 420px; margin: 0 auto; }
}

/* Features */
.features-section {
  position: relative;
  background: linear-gradient(180deg, var(--features-section-start) 0%, var(--bg-page) 280px);
  padding: 64px 0;
}
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  align-items: stretch;
  gap: 20px;
  margin-top: 0;
  position: relative;
  z-index: 10;
  margin-bottom: 32px;
}
.feature-card {
  min-width: 0;
  height: 100%;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--feature-card-shadow), 0 0 18px var(--feature-glow);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}
@media (hover: hover) and (pointer: fine) {
  .feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--blue-border);
    box-shadow: var(--feature-card-hover-shadow), 0 0 26px var(--feature-glow-hover);
  }
}
@media (prefers-reduced-motion: reduce) {
  .feature-card { transition: none; }
  .feature-card:hover { transform: none; }
}
.feature-icon {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  margin-bottom: 4px;
}
.feature-icon svg { display: none; }
.feature-icon img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: inherit;
}
.icon-blue { background: #eff6ff; color: #2563eb; }
.icon-cyan { background: #f0f9ff; color: #0284c7; }
.icon-indigo { background: #eef2ff; color: #4f46e5; }
body.dark-mode .icon-blue, body.dark-mode .icon-cyan, body.dark-mode .icon-indigo {
  background: rgba(37, 99, 235, 0.2);
  color: var(--cyan-accent);
}
.feature-card h3 { font-size: 19px; margin: 0; font-weight: 700; color: var(--navy-heading); }
.feature-card p { margin: 0; font-size: 14.5px; color: var(--text-muted); line-height: 1.55; }

@media (max-width: 600px) {
  .features-section { padding: 44px 0; }
}

/* About */
.about-section {
  border-top: 1px solid var(--line);
  padding-top: 36px;
  position: relative;
  overflow: hidden;
}
.about-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 44px;
  align-items: center;
  position: relative;
  z-index: 2;
}
.about-info h2 { font-size: 28px; font-weight: 800; margin: 0 0 16px; letter-spacing: -0.01em; }
.about-info p { color: var(--text-muted); font-size: 15.5px; line-height: 1.68; margin: 0 0 24px; }
.btn-learn-more {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--blue-primary);
  color: #ffffff;
  padding: 11px 22px;
  border-radius: 9px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  box-shadow: 0 3px 12px rgba(37, 99, 235, 0.3);
  transition: all 0.15s ease;
}
.btn-learn-more:hover { background: var(--blue-hover); transform: translateY(-1px); }
.btn-learn-more svg { transition: transform 0.15s ease; }
.btn-learn-more:hover svg { transform: translateX(3px); }

.instructor-card {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--card-shadow);
  display: flex;
  align-items: center;
  gap: 20px;
}
.instructor-avatar-wrap { flex-shrink: 0; }
.instructor-avatar {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--blue-primary);
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
  display: block;
}
.instructor-details { display: flex; flex-direction: column; }
.instructor-badge {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--blue-primary);
  background: var(--blue-light);
  padding: 2px 8px;
  border-radius: 6px;
  align-self: flex-start;
  margin-bottom: 6px;
}
body.dark-mode .instructor-badge { color: var(--cyan-accent); }
.instructor-name { font-size: 18px; font-weight: 700; margin: 0 0 2px; color: var(--navy-heading); }
.instructor-title, .instructor-affil { font-size: 13.5px; color: var(--text-muted); margin: 0; line-height: 1.4; }
.instructor-email {
  font-size: 13px;
  color: var(--blue-primary);
  text-decoration: none;
  font-weight: 500;
  margin-top: 6px;
  transition: color 0.15s;
}
.instructor-email:hover { text-decoration: underline; }

.wave-decoration {
  margin-top: 36px;
  height: 60px;
  overflow: hidden;
  position: relative;
  pointer-events: none;
}
.wave-decoration svg { width: 100%; height: 100%; display: block; }

@media (max-width: 860px) {
  .about-grid { grid-template-columns: 1fr; gap: 32px; }
}

/* Chapters Grid */
.chapters-section {
  scroll-margin-top: 72px;
  padding: 64px 0 36px;
  background: var(--bg-page);
  border-top: 1px solid var(--line);
}
.chapters-header { margin-bottom: 32px; }
.section-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--blue-primary);
  display: block;
  margin-bottom: 6px;
}
body.dark-mode .section-kicker { color: var(--cyan-accent); }
.chapters-header h2 { font-size: 32px; font-weight: 800; margin: 0 0 8px; letter-spacing: -0.01em; }
.chapters-header p { color: var(--text-muted); font-size: 16px; margin: 0; }

.home-video-section {
  scroll-margin-top: 72px;
  padding: 64px 0 72px;
  background: linear-gradient(180deg, var(--features-section-start) 0%, var(--bg-page) 280px);
  border-top: 1px solid var(--line);
}
.home-video-heading {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  align-items: start;
  gap: clamp(28px, 5vw, 64px);
  margin-bottom: 28px;
}
.home-video-intro { min-width: 0; }
.home-video-heading h2 { font-size: 32px; font-weight: 800; margin: 0 0 8px; letter-spacing: -0.01em; }
.home-video-heading p { color: var(--text-muted); font-size: 16px; margin: 0; }
.home-video-search {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  min-height: 44px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--bg-card);
  color: var(--text-muted);
}
.home-video-search svg { width: 20px; height: 20px; flex: 0 0 20px; }
.home-video-search input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-main);
  font: inherit;
  font-size: 14px;
}
.home-video-search:focus-within { border-color: var(--blue-primary); box-shadow: 0 0 0 3px var(--feature-glow); }
.home-video-filters {
  display: grid;
  grid-template-columns: minmax(110px, 0.7fr) minmax(0, 1.3fr) auto;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.home-video-filters label { min-width: 0; }
.home-video-filters select, .home-video-reset {
  min-width: 0; width: 100%; min-height: 44px; padding: 8px 12px; border: 1px solid var(--line); border-radius: 9px;
  background: var(--bg-card); color: var(--text-main); font: inherit; font-size: 14px;
}
.home-video-filters select { max-width: 100%; }
.home-video-filters .home-video-search { grid-column: 1 / 3; }
.home-video-reset { width: auto; cursor: pointer; font-weight: 650; white-space: nowrap; }
.home-video-reset:hover { border-color: var(--blue-primary); }
.home-video-heading .home-video-result-count { margin: 18px 0 0; color: var(--text-muted); font-size: 14px; }
.home-video-section input:focus-visible, .home-video-section select:focus-visible, .home-video-section button:focus-visible {
  outline: 3px solid var(--blue-primary); outline-offset: 2px;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.home-video-topic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.home-lecture-topic {
  min-width: 0;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--card-shadow), 0 0 20px var(--feature-glow);
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}
@media (hover: hover) and (pointer: fine) {
  .home-lecture-topic:hover {
    transform: translateY(-3px);
    border-color: var(--blue-border);
    box-shadow: var(--card-hover-shadow), 0 0 24px var(--feature-glow-hover);
  }
}
.home-lecture-topic-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.week-label {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 4px 9px;
  border-radius: 999px;
  background: var(--blue-light);
  color: var(--blue-primary);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.topic-video-count { color: var(--text-muted); font-size: 12px; font-weight: 600; white-space: nowrap; }
.home-lecture-topic h3 { margin: 0 0 16px; color: var(--navy-heading); font-size: 17px; line-height: 1.45; overflow-wrap: anywhere; }
.home-lecture-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.home-lecture-card {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: var(--bg-page);
}
.home-lecture-thumbnail {
  display: block;
  position: relative;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: #0b1730;
}
.home-lecture-thumbnail img { display: block; width: 100%; height: 100%; object-fit: cover; }
.home-lecture-play {
  display: grid;
  place-items: center;
  position: absolute;
  inset: 0;
  color: #fff;
  background: rgba(7, 14, 30, 0.12);
  transition: background-color 0.2s ease;
}
.home-lecture-play svg { width: 42px; height: 42px; filter: drop-shadow(0 2px 5px rgba(0,0,0,.4)); }
.home-lecture-thumbnail:hover .home-lecture-play,
.home-lecture-thumbnail:focus-visible .home-lecture-play { background: rgba(7, 14, 30, 0.35); }
.home-lecture-card h4 { min-height: 60px; margin: 0; padding: 12px 12px 6px; color: var(--text-main); font-size: 13.5px; line-height: 1.45; }
.home-lecture-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 36px;
  margin: 0 12px 12px;
  padding: 7px 10px;
  border-radius: 8px;
  background: var(--blue-primary);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
}
.home-lecture-button:hover { background: var(--blue-hover); }
.home-lecture-button svg { width: 16px; height: 16px; }
.home-video-empty { padding: 18px; border: 1px solid var(--line); border-radius: 10px; color: var(--text-muted); background: var(--bg-card); }
@media (prefers-reduced-motion: reduce) {
  .home-lecture-topic,
  .home-lecture-play { transition: none; }
  .home-lecture-topic:hover { transform: none; }
}
@media (max-width: 760px) {
  .home-video-topic-grid { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 900px) {
  .home-video-heading { grid-template-columns: minmax(0, 1fr); gap: 22px; }
  .home-video-filters { grid-template-columns: minmax(120px, 0.7fr) minmax(0, 1.3fr) auto; }
}
@media (max-width: 600px) {
  .home-video-section { padding: 48px 0 56px; }
  .home-video-heading { gap: 18px; }
  .home-video-filters { grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); gap: 8px; }
  .home-video-filters .home-video-search { grid-column: 1 / 3; }
  .home-video-reset { grid-column: 1 / 3; justify-self: end; }
  .home-lecture-topic { padding: 16px; }
}

.chapter-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: 20px;
  margin-bottom: 40px;
}
.ch-card {
  min-width: 0;
  min-height: 148px;
  height: 100%;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  box-shadow: var(--chapter-card-shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
}
.ch-card:focus-visible {
  outline: 3px solid var(--blue-primary);
  outline-offset: 3px;
}
.ch-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: #07152f;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.ch-icon-wrap img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: inherit;
}
.ch-body { flex: 1; min-width: 0; }
.ch-code {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 3px;
  display: block;
}
.ch-title { font-size: 18px; font-weight: 700; line-height: 1.35; overflow-wrap: anywhere; color: var(--navy-heading); margin: 0 0 6px; }
.ch-desc { font-size: 13.5px; color: var(--text-muted); line-height: 1.5; overflow-wrap: anywhere; margin: 0; }
.ch-arrow {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  color: var(--blue-primary);
  margin-left: 8px;
  align-self: center;
  flex-shrink: 0;
  transition: transform 0.2s ease, filter 0.2s ease;
}
.ch-arrow svg { display: block; width: 22px; height: 22px; }
.ch-card:focus-visible .ch-arrow { filter: brightness(1.2) drop-shadow(0 0 3px currentColor); }
@media (hover: hover) and (pointer: fine) {
  .ch-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--chapter-card-hover-shadow);
    border-color: var(--blue-border);
  }
  .ch-card:hover .ch-arrow { transform: translateX(3px); }
}
@media (prefers-reduced-motion: reduce) {
  .ch-card { transition: none; }
  .ch-arrow { transition: none; }
  .ch-card:hover,
  .ch-card:hover .ch-arrow,
  .ch-card:focus-visible .ch-arrow { transform: none; }
}

/* Shared homepage card hover treatment */
.instructor-card {
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease, filter 0.24s ease;
}
@media (hover: hover) and (pointer: fine) {
  .instructor-card:hover {
    transform: translateY(-3px);
    filter: drop-shadow(0 0 12px var(--feature-glow-hover));
  }
  .instructor-card:hover,
  .ch-card:hover {
    border-color: var(--blue-border);
  }
}
.ch-card:focus-visible,
.instructor-card:focus-within {
  border-color: var(--blue-border);
  filter: drop-shadow(0 0 12px var(--feature-glow-hover));
}
@media (prefers-reduced-motion: reduce) {
  .instructor-card { transition: none; }
  .instructor-card:hover {
    transform: none;
  }
}

@media (max-width: 760px) {
  .chapter-cards-grid { grid-template-columns: 1fr; }
}

.ch-info-note {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--blue-light);
  border: 1px solid var(--blue-border);
  color: var(--blue-primary);
  font-size: 13.5px;
  font-weight: 500;
  padding: 12px 18px;
  border-radius: 10px;
  margin-bottom: 48px;
}
body.dark-mode .ch-info-note { color: var(--cyan-accent); }

/* Table of Contents */
.toc-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--card-shadow);
  margin-bottom: 56px;
}
.toc-header h3 { font-size: 20px; margin: 0 0 4px; }
.toc-header p { color: var(--text-muted); font-size: 14px; margin: 0 0 20px; }
.toc {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.toc details {
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  overflow: hidden;
}
.toc summary {
  cursor: pointer;
  padding: 11px 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
  background: var(--bg-page);
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.toc summary::-webkit-details-marker { display: none; }
.toc summary::after { content: "+"; color: var(--blue-primary); font-weight: 700; font-size: 16px; }
.toc details[open] summary::after { content: "–"; }
.toc ol { margin: 0; padding: 10px 16px 12px 32px; font-size: 13.5px; }
.toc li { padding: 3px 0; }
.toc li a { text-decoration: none; color: var(--text-main); transition: color 0.15s; }
.toc li a:hover { color: var(--blue-primary); text-decoration: underline; }

/* Interactive Chapter Labs */
.chapter {
  scroll-margin-top: 80px;
  padding: 56px 0 24px;
  border-top: 1px solid var(--line);
}
.chapter .head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px 20px;
  margin-bottom: 14px;
}
.chapter .head .num {
  color: var(--blue-primary);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
  display: block;
}
.chapter .head h2 { font-size: 28px; margin: 0; }
.chapter .head .tools { margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }
.chapter .head .tools a, .chapter .head .tools button {
  font: 600 13px 'Inter', system-ui, sans-serif;
  color: var(--blue-primary);
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px 12px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s;
}
.chapter .head .tools a:hover, .chapter .head .tools button:hover {
  background: var(--blue-light);
  border-color: var(--blue-border);
}
.chapter .desc { color: var(--text-muted); max-width: 900px; font-size: 15px; margin: 0 0 18px; }
.lab {
  position: relative;
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
  background: #0f1220;
  height: min(900px, 88vh);
  min-height: 560px;
  box-shadow: 0 12px 32px rgba(11, 42, 91, 0.12);
}
.lab-fullscreen-controls {
  display: none;
}
.lab:fullscreen,
.lab.is-fullscreen {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  height: 100dvh;
  min-height: 0;
  max-height: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}
.lab:fullscreen .lab-fullscreen-controls,
.lab.is-fullscreen .lab-fullscreen-controls {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-height: 60px;
  padding: max(8px, env(safe-area-inset-top, 0px)) max(12px, env(safe-area-inset-right, 0px)) 8px max(12px, env(safe-area-inset-left, 0px));
  background: #070e1e;
  border-bottom: 1px solid rgba(255, 255, 255, 0.16);
}
.lab-fullscreen-controls button,
.lab-fullscreen-controls a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 9px 14px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 9px;
  background: #17243a;
  color: #f8fafc;
  font: 600 14px 'Inter', system-ui, sans-serif;
  text-decoration: none;
  cursor: pointer;
  touch-action: manipulation;
}
.lab-fullscreen-controls button:hover,
.lab-fullscreen-controls a:hover {
  background: #253a5a;
  border-color: rgba(255, 255, 255, 0.45);
}
.lab-fullscreen-controls button:focus-visible,
.lab-fullscreen-controls a:focus-visible {
  outline: 3px solid #38bdf8;
  outline-offset: 2px;
}
.lab iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  background: #0f1220;
}
.lab:fullscreen iframe,
.lab.is-fullscreen iframe {
  position: relative;
  inset: auto;
  flex: 1 1 auto;
  width: 100%;
  height: auto;
  min-height: 0;
}
.lab .ph {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #9aa3c4;
  font-size: 15px;
}
@media (max-width: 700px) {
  .lab { height: 80vh; min-height: 480px; }
  .lab:fullscreen .lab-fullscreen-controls,
  .lab.is-fullscreen .lab-fullscreen-controls {
    justify-content: stretch;
    gap: 8px;
    padding-right: max(8px, env(safe-area-inset-right, 0px));
    padding-left: max(8px, env(safe-area-inset-left, 0px));
  }
  .lab-fullscreen-controls button,
  .lab-fullscreen-controls a {
    flex: 1 1 0;
    padding: 8px 10px;
    font-size: 13px;
  }
}
"""

CSS_EXPLORE = CSS_COMMON + """
.explore-breadcrumbs {
  margin-top: 68px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
  background: var(--bg-card);
}
.explore-breadcrumbs .wrap,
.explore-breadcrumbs nav {
  display: flex;
  align-items: center;
}
.explore-breadcrumbs .wrap {
  justify-content: space-between;
  gap: 14px;
}
.explore-breadcrumbs nav {
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13.5px;
}
.explore-breadcrumbs nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
}
.explore-breadcrumbs nav a:hover { color: var(--blue-primary); }
.explore-breadcrumbs .crumb-sep { color: var(--text-muted); opacity: 0.5; }
.explore-breadcrumbs .crumb-current { color: var(--text-main); font-weight: 600; }
.back-home-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 40px;
  padding: 8px 13px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--bg-page);
  color: var(--text-main);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 600;
  white-space: nowrap;
}
.explore-breadcrumbs a.back-home-btn {
  flex: 0 0 auto;
  visibility: visible;
  opacity: 1;
  position: relative;
  z-index: 1;
}
.back-home-btn:hover,
.back-home-btn:focus-visible {
  color: var(--blue-primary);
  border-color: var(--blue-primary);
  background: var(--blue-light);
}
.back-home-btn:focus-visible {
  outline: 2px solid var(--blue-primary);
  outline-offset: 3px;
}
@media (max-width: 480px) {
  .explore-breadcrumbs .wrap { align-items: flex-start; flex-direction: column; }
  .back-home-btn { align-self: flex-start; }
}
.explore-hero {
  padding: 42px 0 44px;
  background: var(--bg-page);
  position: relative;
  border-bottom: 1px solid var(--line);
}
.explore-hero-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
  position: relative;
}
.explore-hero-content {
  max-width: 700px;
}
.section-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--blue-primary);
  display: block;
  margin-bottom: 6px;
}
body.dark-mode .section-kicker { color: var(--cyan-accent); }
.explore-hero h1 {
  font-size: clamp(32px, 4.2vw, 48px);
  font-weight: 800;
  margin: 0 0 10px;
  letter-spacing: -0.01em;
}
.explore-hero p {
  color: var(--text-muted);
  font-size: 16.5px;
  line-height: 1.6;
  margin: 0;
}
.explore-motor-watermark {
  max-width: 220px;
  opacity: 0.85;
  filter: drop-shadow(0 8px 24px rgba(37,99,235,0.15));
}
@media (max-width: 760px) {
  .explore-motor-watermark { display: none; }
  .explore-hero { padding: 36px 0; }
}

.explore-main {
  padding: 48px 0 72px;
}
.chapter-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
  margin-bottom: 40px;
}
@media (max-width: 760px) {
  .chapter-cards-grid { grid-template-columns: 1fr; }
}
.ch-card {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 18px;
  text-decoration: none;
  box-shadow: var(--card-shadow);
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
}
.ch-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-hover-shadow);
  border-color: #cbd5e1;
}
.ch-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.ch-body { flex: 1; min-width: 0; }
.ch-code {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 3px;
  display: block;
}
.ch-title { font-size: 18px; font-weight: 700; color: var(--navy-heading); margin: 0 0 6px; }
.ch-desc { font-size: 13.5px; color: var(--text-muted); line-height: 1.5; margin: 0; }
.ch-arrow {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  color: var(--blue-primary);
  margin-left: 8px;
  align-self: center;
  flex-shrink: 0;
  transition: transform 0.2s ease, filter 0.2s ease;
}
.ch-arrow svg { display: block; width: 22px; height: 22px; }
.ch-card:hover .ch-arrow,
.ch-card:focus-visible .ch-arrow { transform: translateX(4px); filter: brightness(1.2) drop-shadow(0 0 3px currentColor); }
@media (prefers-reduced-motion: reduce) {
  .ch-arrow { transition: none; }
  .ch-card:hover .ch-arrow,
  .ch-card:focus-visible .ch-arrow { transform: none; }
}

.ch-info-note {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--blue-light);
  border: 1px solid var(--blue-border);
  color: var(--blue-primary);
  font-size: 14px;
  font-weight: 500;
  padding: 14px 20px;
  border-radius: 12px;
  margin-bottom: 56px;
}
body.dark-mode .ch-info-note { color: var(--cyan-accent); }

.toc-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--card-shadow);
}
.toc-header h3 { font-size: 20px; margin: 0 0 4px; }
.toc-header p { color: var(--text-muted); font-size: 14px; margin: 0 0 20px; }
.toc {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.toc details {
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  overflow: hidden;
}
.toc summary {
  cursor: pointer;
  padding: 11px 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
  background: var(--bg-page);
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.toc summary::-webkit-details-marker { display: none; }
.toc summary::after { content: "+"; color: var(--blue-primary); font-weight: 700; font-size: 16px; }
.toc details[open] summary::after { content: "–"; }
.toc ol { margin: 0; padding: 10px 16px 12px 32px; font-size: 13.5px; }
.toc li { padding: 3px 0; }
.toc li a { text-decoration: none; color: var(--text-main); transition: color 0.15s; }
.toc li a:hover { color: var(--blue-primary); text-decoration: underline; }
"""

CSS_CHAPTER_PAGE = CSS_COMMON + """
/* Breadcrumbs */
.breadcrumbs-bar {
  background: var(--bg-card);
  border-bottom: 1px solid var(--line);
  padding: 14px 0;
  font-size: 13.5px;
  margin-top: 68px;
}
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.breadcrumbs a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s;
}
.breadcrumbs a:hover { color: var(--blue-primary); }
.breadcrumbs .crumb-sep { color: var(--text-muted); opacity: 0.5; font-size: 12px; }
.breadcrumbs .crumb-current { color: var(--text-main); font-weight: 600; }

/* Chapter Overview Layout */
.chapter-layout-wrap {
  display: block;
  padding: 36px 0 72px;
}
.chapter-main-content { min-width: 0; width: 100%; }
.ch-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 32px;
}
.ch-overview-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  flex-shrink: 0;
}
.view-full-chapter-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 48px;
  padding: 11px 18px;
  border: 1px solid var(--blue-primary);
  border-radius: 10px;
  background: var(--blue-primary);
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
  transition: background 0.15s, transform 0.15s;
}
.view-full-chapter-btn:hover {
  background: var(--blue-hover);
  transform: translateY(-1px);
}
@media (max-width: 720px) {
  .ch-overview-header { flex-direction: column; }
  .ch-overview-actions { align-items: flex-start; }
}
.ch-overview-info h1 {
  font-size: 34px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.01em;
  overflow-wrap: anywhere;
  margin: 0 0 10px;
}
.ch-overview-info { min-width: 0; flex: 1; }
.ch-overview-lead {
  font-size: 16px;
  line-height: 1.65;
  color: var(--text-muted);
  overflow-wrap: anywhere;
  margin: 0;
}
.topics-count-badge {
  background: var(--blue-light);
  color: var(--blue-primary);
  border: 1px solid var(--blue-border);
  font-size: 13px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
}
body.dark-mode .topics-count-badge { color: var(--cyan-accent); }

/* Responsive Topic Cards Grid */
.topic-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: 20px;
  margin-bottom: 48px;
}
@media (max-width: 720px) {
  .topic-cards-grid { grid-template-columns: minmax(0, 1fr); gap: 16px; }
}

.topic-card {
  min-width: 0;
  min-height: 252px;
  height: 100%;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-decoration: none;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.topic-card:focus-visible {
  outline: 3px solid var(--blue-primary);
  outline-offset: 3px;
  border-color: var(--blue-primary);
}
.topic-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.topic-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: grid;
  place-items: center;
}
.topic-num-pill {
  font-size: 11px;
  font-weight: 700;
  background: var(--bg-page);
  color: var(--text-muted);
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid var(--line);
}
.topic-card-title {
  min-width: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--navy-heading);
  margin: 0;
  line-height: 1.35;
  overflow-wrap: anywhere;
}
.topic-card-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.55;
  overflow-wrap: anywhere;
  margin: 0;
  flex: 1;
}
.topic-card-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--blue-primary);
  margin-top: 6px;
}
.topic-card-action svg { transition: transform 0.2s ease; }
@media (hover: hover) and (pointer: fine) {
  .topic-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--card-hover-shadow);
    border-color: var(--blue-border);
  }
  .topic-card:hover .topic-card-action svg { transform: translateX(3px); }
}
@media (prefers-reduced-motion: reduce) {
  .topic-card, .topic-card-action svg { transition: none; }
  .topic-card:hover, .topic-card:hover .topic-card-action svg { transform: none; }
}
@media (max-width: 480px) {
  .topic-card { padding: 18px; }
}

"""

JS_COMMON = """
(function(){
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    document.body.classList.add('emf-page-enter');
  }

  var deferredImages=document.querySelectorAll('img[data-src]');
  if('IntersectionObserver' in window){
    var imageObserver=new IntersectionObserver(function(entries,observer){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          var image=entry.target;
          image.src=image.dataset.src;
          image.removeAttribute('data-src');
          observer.unobserve(image);
        }
      });
    },{rootMargin:'300px 0px'});
    deferredImages.forEach(function(image){ imageObserver.observe(image); });
  } else {
    deferredImages.forEach(function(image){
      image.src=image.dataset.src;
      image.removeAttribute('data-src');
    });
  }

  // Theme toggle
  var themeBtn=document.getElementById('theme-toggle');
  if(themeBtn){
    var syncThemeIcon=function(){
      var dark=document.body.classList.contains('dark-mode');
      themeBtn.innerHTML=dark
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"></path></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    };
    var savedTheme=localStorage.getItem('emf_theme');
    if(savedTheme==='dark'){
      document.body.classList.add('dark-mode');
    } else if(savedTheme==='light'){
      document.body.classList.remove('dark-mode');
    }
    syncThemeIcon();
    new MutationObserver(syncThemeIcon).observe(document.body,{attributes:true,attributeFilter:['class']});
    themeBtn.onclick=function(){
      var isDark=document.body.classList.toggle('dark-mode');
      localStorage.setItem('emf_theme', isDark ? 'dark' : 'light');
      syncThemeIcon();
    };
  }

  // Mobile menu
  var burger=document.getElementById('burger'), menu=document.getElementById('links');
  if(burger && menu){
    burger.onclick=function(){ menu.classList.toggle('open'); };
    menu.addEventListener('click',function(e){
      if(e.target.tagName==='A') menu.classList.remove('open');
    });
  }

  // Keep the primary navigation indicator in sync with routes and homepage sections.
  var navLinks=Array.prototype.slice.call(document.querySelectorAll('.nav-links a'));
  var navBar=document.querySelector('.nav');
  function normalizedPagePath(path){
    path=path.toLowerCase();
    if(path.endsWith('/index.html')) path=path.slice(0,-10);
    if(!path.endsWith('/')) path+='/';
    return path;
  }
  function setActiveNav(link){
    navLinks.forEach(function(item){ item.classList.toggle('active',item===link); });
  }
  function navLinkFor(label){
    return navLinks.find(function(link){ return link.textContent.trim().toLowerCase()===label; });
  }
  function updateActiveNav(){
    if(!navLinks.length) return;
    var path=window.location.pathname.toLowerCase();
    if(path.endsWith('/video-lectures.html')){
      setActiveNav(navLinkFor('video lectures'));
      return;
    }
    if(path.endsWith('/chapters.html') || path.indexOf('/chapter-pages/')!==-1){
      setActiveNav(navLinkFor('chapters'));
      return;
    }
    if(!(path.endsWith('/index.html') || path.endsWith('/'))){
      return;
    }
    if(window.scrollY<2 && location.hash){
      var initialSection=document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if(initialSection){
        var initialId=initialSection.id;
        if(initialId==='chapters' || initialId==='video-lectures' || initialId==='about' || initialId==='home'){
          setActiveNav(navLinkFor(initialId==='video-lectures' ? 'video lectures' : initialId));
          return;
        }
      }
    }
    var headerHeight=navBar ? navBar.getBoundingClientRect().height : 0;
    var marker=window.scrollY+headerHeight+Math.min(window.innerHeight*0.32,240);
    var activeSection='home';
    ['home','about','chapters','video-lectures'].forEach(function(id){
      var section=document.getElementById(id);
      if(section && section.getBoundingClientRect().top+window.scrollY<=marker){
        activeSection=id;
      }
    });
    setActiveNav(navLinkFor(activeSection==='chapters' ? 'chapters' : activeSection==='video-lectures' ? 'video lectures' : activeSection));
  }
  var navUpdatePending=false;
  function scheduleActiveNavUpdate(){
    if(navUpdatePending) return;
    navUpdatePending=true;
    window.requestAnimationFrame(function(){
      navUpdatePending=false;
      updateActiveNav();
    });
  }
  function scrollToSection(section, instant){
    var headerHeight=navBar ? navBar.getBoundingClientRect().height : 0;
    var sectionTop=window.scrollY+section.getBoundingClientRect().top-headerHeight-8;
    var reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({top:Math.max(0,sectionTop),behavior:instant?'instant':reducedMotion?'auto':'smooth'});
    setActiveNav(navLinkFor(section.id==='video-lectures' ? 'video lectures' : section.id));
  }
  navLinks.forEach(function(link){
    link.addEventListener('click',function(){
      setActiveNav(link);
      window.setTimeout(updateActiveNav,0);
    });
  });
  document.addEventListener('click',function(event){
    var anchor=event.target.closest&&event.target.closest('a[href]');
    if(!anchor) return;
    var targetUrl=new URL(anchor.href,window.location.href);
    if(targetUrl.origin!==window.location.origin ||
       normalizedPagePath(targetUrl.pathname)!==normalizedPagePath(window.location.pathname) ||
       !targetUrl.hash) return;
    var target=document.getElementById(decodeURIComponent(targetUrl.hash.slice(1)));
    if(!target || !['home','about','chapters','video-lectures'].includes(target.id)) return;
    event.preventDefault();
    if(window.location.hash!==targetUrl.hash) history.pushState(null,'',targetUrl.hash);
    scrollToSection(target);
    scheduleActiveNavUpdate();
  });
  function scrollToInitialHash(){
    if(!(window.location.pathname.toLowerCase().endsWith('/index.html') || window.location.pathname.endsWith('/')) || !window.location.hash) return;
    var initialTarget=document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if(initialTarget && ['home','about','chapters','video-lectures'].includes(initialTarget.id)){
      scrollToSection(initialTarget,true);
      updateActiveNav();
    }
  }
  var initialHashScrollTimer=0;
  function scheduleInitialHashScroll(){
    window.clearTimeout(initialHashScrollTimer);
    initialHashScrollTimer=window.setTimeout(function(){
      initialHashScrollTimer=0;
      window.setTimeout(scrollToInitialHash,0);
    },0);
  }
  scheduleInitialHashScroll();
  window.addEventListener('pageshow',scheduleInitialHashScroll);
  window.addEventListener('load',scheduleInitialHashScroll);
  window.addEventListener('hashchange',scheduleInitialHashScroll);
  window.addEventListener('scroll',scheduleActiveNavUpdate,{passive:true});
  window.addEventListener('resize',scheduleActiveNavUpdate);
  window.addEventListener('hashchange',scheduleActiveNavUpdate);
  window.addEventListener('popstate',scheduleActiveNavUpdate);
  window.addEventListener('pageshow',scheduleActiveNavUpdate);
  updateActiveNav();

  // Back to top
  var topBtn=document.getElementById('top');
  if(topBtn){
    window.addEventListener('scroll',function(){
      topBtn.classList.toggle('show', window.scrollY > 400);
    },{passive:true});
    topBtn.onclick=function(){ window.scrollTo({top:0,behavior:'smooth'}); };
  }

  // Search dialog
  var searchOverlay=document.getElementById('search-overlay');
  var searchBtn=document.getElementById('search-toggle');
  var searchInput=document.getElementById('search-input');
  var searchResults=document.getElementById('search-results');
  var searchClose=document.getElementById('search-close');
  var searchIndex=null;
  var searchIndexRequest=null;
  var rootPrefix='%(root_prefix)s';

  function loadSearchIndex(){
    if(searchIndex) return Promise.resolve(searchIndex);
    if(!searchIndexRequest){
      searchIndexRequest=fetch(rootPrefix+'search-index.json').then(function(response){
        if(!response.ok) throw new Error('Search index request failed with HTTP '+response.status);
        return response.json();
      }).then(function(data){
        if(!Array.isArray(data)) throw new TypeError('Search index must contain an array');
        searchIndex=data;
        return searchIndex;
      }).catch(function(error){
        searchIndexRequest=null;
        throw error;
      });
    }
    return searchIndexRequest;
  }

  function showSearchLoadError(error){
    console.error('Topic search could not be loaded.',error);
    searchResults.innerHTML='';
    var message=document.createElement('div');
    message.className='search-empty';
    message.appendChild(document.createTextNode('Could not load topic search. '));
    var retry=document.createElement('button');
    retry.type='button';
    retry.textContent='Retry';
    retry.onclick=loadAndRenderSearch;
    message.appendChild(retry);
    searchResults.appendChild(message);
  }

  function loadAndRenderSearch(){
    if(!searchResults) return;
    searchResults.innerHTML='<div class="search-empty">Loading topics…</div>';
    loadSearchIndex().then(function(){ renderSearchResults(searchInput.value); }).catch(showSearchLoadError);
  }

  function openSearch(){
    if(!searchOverlay) return;
    searchOverlay.style.display='grid';
    searchInput.value='';
    loadAndRenderSearch();
    setTimeout(function(){ searchInput.focus(); }, 50);
  }
  function closeSearch(){
    if(!searchOverlay) return;
    searchOverlay.style.display='none';
  }
  if(searchBtn) searchBtn.onclick=openSearch;
  if(searchClose) searchClose.onclick=closeSearch;
  if(searchOverlay){
    searchOverlay.onclick=function(e){
      if(e.target===searchOverlay) closeSearch();
    };
  }
  if(searchResults){
    searchResults.addEventListener('click',function(e){
      if(e.target.closest && e.target.closest('.search-item')) closeSearch();
    });
  }
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape') closeSearch();
    if((e.metaKey||e.ctrlKey) && e.key==='k'){ e.preventDefault(); openSearch(); }
  });

  function renderSearchResults(q){
    if(!searchResults || !searchIndex) return;
    q=(q||'').trim().toLowerCase();
    var matches = searchIndex.filter(function(item){
      return !q || item.title.toLowerCase().indexOf(q)!==-1 || item.chTitle.toLowerCase().indexOf(q)!==-1 || item.desc.toLowerCase().indexOf(q)!==-1;
    }).slice(0, 20);

    if(!matches.length){
      searchResults.innerHTML='<div class="search-empty">No matching topics found</div>';
      return;
    }
    searchResults.innerHTML=matches.map(function(m){
      var linkUrl = rootPrefix + 'chapter-pages/view' + m.chIndex + '.html#' + encodeURIComponent(m.id);
      return '<a href="' + linkUrl + '" class="search-item">' +
             '<strong>' + m.title + '</strong>' +
             '<small>' + m.chCode + ' · ' + m.chTitle + '</small>' +
             '</a>';
    }).join('');

  }

  if(searchInput){
    searchInput.addEventListener('input',function(){
      if(searchIndex) renderSearchResults(searchInput.value);
    });
  }
})();
"""

JS_INDEX_FRAME_MANAGEMENT = """
(function(){
  var N=%(n)d, frames={}, pending={}, sections=[].slice.call(document.querySelectorAll('section.chapter'));

  function mount(i){
    if(frames[i]) return frames[i];
    var box=document.getElementById('lab'+i);
    if(!box) return null;
    var f=document.createElement('iframe');
    f.title=box.dataset.title || ('Chapter ' + i);
    f.loading='eager';
    f.addEventListener('load',function(){
      var ph=box.querySelector('.ph');
      if(ph) ph.remove();
      if(pending[i]){
        try{ f.contentWindow.postMessage({emfSection:pending[i]},'*'); }catch(_){}
        delete pending[i];
      }
    });
    f.srcdoc=document.getElementById('tpl'+i).innerHTML;
    box.appendChild(f);
    frames[i]=f;
    return f;
  }

  function openSection(i,sid){
    var f=mount(i);
    if(sid){
      pending[i]=sid;
      try{ f.contentWindow.postMessage({emfSection:sid},'*'); }catch(_){}
    }
  }

  function fullscreenError(action,error){
    console.error(action,error);
    window.alert(action + (error&&error.message ? ' ' + error.message : ' Please try again.'));
  }

  function updateFullscreenState(){
    sections.forEach(function(section){
      var box=document.getElementById('lab'+section.dataset.i);
      if(box) box.classList.toggle('is-fullscreen',
        document.fullscreenElement===box || document.webkitFullscreenElement===box);
    });
  }

  document.querySelectorAll('button[data-fullscreen]').forEach(function(button){
    var i=+button.dataset.fullscreen;
    var box=document.getElementById('lab'+i);
    if(!box || !(box.requestFullscreen || box.webkitRequestFullscreen)){
      button.hidden=true;
      return;
    }
    button.addEventListener('click',function(){
      var request=box.requestFullscreen || box.webkitRequestFullscreen;
      try{
        var result=request.call(box);
        if(result&&typeof result.catch==='function'){
          result.catch(function(error){fullscreenError('Could not enter fullscreen.',error);});
        }
      }catch(error){
        fullscreenError('Could not enter fullscreen.',error);
      }
    });
  });

  document.addEventListener('fullscreenchange',updateFullscreenState);
  document.addEventListener('webkitfullscreenchange',updateFullscreenState);

  document.querySelectorAll('[data-exit-fullscreen]').forEach(function(button){
    button.addEventListener('click',function(){
      var exit=document.exitFullscreen || document.webkitExitFullscreen;
      if(!exit) return;
      try{
        var result=exit.call(document);
        if(result&&typeof result.catch==='function'){
          result.catch(function(error){fullscreenError('Could not exit fullscreen.',error);});
        }
      }catch(error){
        fullscreenError('Could not exit fullscreen.',error);
      }
    });
  });

  document.querySelectorAll('[data-back-to-chapter]').forEach(function(link){
    link.addEventListener('click',function(event){
      event.preventDefault();
      var exit=document.exitFullscreen || document.webkitExitFullscreen;
      var isFullscreen=document.fullscreenElement || document.webkitFullscreenElement;
      var result;
      try{
        result=isFullscreen&&exit ? exit.call(document) : Promise.resolve();
      }catch(error){
        fullscreenError('Could not exit fullscreen before returning to the chapter.',error);
        window.location.assign(link.href);
        return;
      }
      Promise.resolve(result).then(function(){
        window.location.assign(link.href);
      },function(error){
        fullscreenError('Could not exit fullscreen before returning to the chapter.',error);
        window.location.assign(link.href);
      });
    });
  });

  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting){
          mount(+e.target.dataset.i);
          io.unobserve(e.target);
        }
      });
    },{rootMargin:'600px 0px'});
    sections.forEach(function(s){ io.observe(s); });
  } else {
    sections.forEach(function(s){ mount(+s.dataset.i); });
  }

  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('[data-ch]');
    if(!a) return;
    var i=+a.dataset.ch, sid=a.dataset.sec;
    openSection(i, sid);
  });

  window.addEventListener('message',function(e){
    var d=e.data||{};
    if(typeof d.emfGo==='number'){
      var s=document.getElementById('chapter'+d.emfGo);
      if(!s) return;
      var f=mount(d.emfGo);
      var go=function(){ s.scrollIntoView({behavior:'smooth',block:'start'}); };
      go();
      if(!f.dataset.loaded) f.addEventListener('load',function(){ setTimeout(go,80); },{once:true});
    }
  });

  document.addEventListener('load',function(e){
    if(e.target&&e.target.tagName==='IFRAME') e.target.dataset.loaded='1';
  },true);

  // "Reload chapter" tool
  document.querySelectorAll('button[data-reload]').forEach(function(b){
    b.onclick=function(){
      var i=+b.dataset.reload;
      if(frames[i]){ frames[i].remove(); delete frames[i]; }
      mount(i);
    };
  });

  if(location.hash){
    var t=document.querySelector(location.hash);
    if(t && t.classList.contains('chapter')) mount(+t.dataset.i);
  }
})();
"""

def generate_favicon_link(root_prefix=""):
    return f'<link rel="icon" type="image/svg+xml" href="{root_prefix}favicon.svg">'


def generate_header(root_prefix, active_page=""):
    home_link = root_prefix + "index.html#home" if root_prefix else "index.html#home"
    chapters_link = root_prefix + "index.html#chapters" if root_prefix else "index.html#chapters"
    about_link = root_prefix + "index.html#about" if root_prefix else "index.html#about"
    video_link = root_prefix + "index.html#video-lectures" if root_prefix else "index.html#video-lectures"

    return f'''<header class="nav" id="top-nav">
  <div class="wrap nav-wrap">
    <a class="brand" href="{home_link}">
      <span class="mark">⚡</span>
      <span class="brand-text">Electric Machinery Fundamentals</span>
    </a>
    <button class="burger" id="burger" aria-label="Toggle navigation" aria-controls="links">
      <span></span><span></span><span></span>
    </button>
    <div class="nav-menu" id="links">
      <ul class="nav-links">
        <li><a href="{home_link}" class="{'active' if active_page=='home' else ''}">Home</a></li>
        <li><a href="{chapters_link}" class="{'active' if active_page=='chapters' else ''}">Chapters</a></li>
        <li><a href="{video_link}" class="{'active' if active_page=='video-lectures' else ''}">Video Lectures</a></li>
        <li><a href="{about_link}" class="{'active' if active_page=='about' else ''}">About</a></li>
      </ul>
      <div class="nav-actions">
        <button class="icon-btn" id="theme-toggle" aria-label="Toggle dark mode" title="Toggle theme">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
        </button>
        <button class="icon-btn" id="search-toggle" aria-label="Search topics" title="Search topics (Ctrl+K)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </button>
      </div>
    </div>
  </div>
</header>'''

def generate_nav_styles():
    start = CSS_COMMON.index("/* Navigation */")
    end = CSS_COMMON.index("/* Footer */", start)
    return CSS_COMMON[start:end]

def generate_search_styles():
    start = CSS_COMMON.index("/* Search Dialog */")
    return CSS_COMMON[start:]

def generate_search_modal():
    return '''<div class="search-overlay" id="search-overlay" style="display:none">
  <div class="search-modal">
    <div class="search-header">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input type="text" id="search-input" placeholder="Search topics, equations, machines..." autocomplete="off">
      <button class="search-close" id="search-close" aria-label="Close search">&times;</button>
    </div>
    <div class="search-results" id="search-results"></div>
  </div>
</div>'''

def generate_footer():
    return '''<footer class="site-footer">
  <div class="wrap footer-wrap">
    <div class="footer-left">
      <span class="footer-brand">Electric Machinery Fundamentals</span>
      <span class="footer-dot">•</span>
      <span>Learn</span>
      <span class="footer-dot">•</span>
      <span>Explore</span>
      <span class="footer-dot">•</span>
      <span>Build Your Future</span>
    </div>
    <div class="footer-right">
      <span>UET</span>
      <span class="footer-sep">|</span>
      <span>Electrical Engineering</span>
    </div>
  </div>
  <div class="wrap footer-sub">
    <p>© Dr. Muhammad Salim Butt · University of Engineering &amp; Technology · Built as a teaching aid for <em>Electric Machinery Fundamentals</em> (S. J. Chapman). Stand-alone chapter modules are in the <code>chapters/</code> directory.</p>
  </div>
</footer>

<button id="top" aria-label="Back to top" title="Scroll to top">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="19" x2="12" y2="6"></line><polyline points="7 11 12 6 17 11"></polyline></svg>
</button>'''

def build_chapter_page(c, ch_list):
    e = html.escape
    idx = c["i"]

    topic_cards = []
    for k, t in enumerate(c["topics"]):
        icon_svg, icon_col, icon_bg = TOPIC_ICONS[k % len(TOPIC_ICONS)]
        topic_cards.append(f'''
      <a href="view{idx}.html#{e(t["id"])}" class="topic-card">
        <div class="topic-card-top">
          <div class="topic-card-icon" style="background:{icon_bg}; color:{icon_col}">
            {icon_svg}
          </div>
          <span class="topic-num-pill">{e(t["num"])}</span>
        </div>
        <h3 class="topic-card-title">{e(t["num"])} {e(t["title"])}</h3>
        <p class="topic-card-desc">{e(t["desc"])}</p>
        <div class="topic-card-action">
          Open topic
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </div>
      </a>''')
    cards_html = "".join(topic_cards)

    page_html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(c["ch_code"])}: {e(c["title"])} — Electric Machinery Fundamentals</title>
<meta name="description" content="{e(c["blurb"])}">
<meta name="theme-color" content="#070e1e">
{generate_favicon_link("../")}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT_STYLESHEET}
<style>{CSS_CHAPTER_PAGE}</style>
</head>
<body>

{generate_header("../", active_page="chapters")}

<!-- Breadcrumbs -->
<div class="breadcrumbs-bar">
  <div class="wrap">
    <nav class="breadcrumbs" aria-label="Breadcrumb">
      <a href="../index.html">Home</a>
      <span class="crumb-sep">›</span>
      <a href="../index.html#chapters">Chapters</a>
      <span class="crumb-sep">›</span>
      <span class="crumb-current">{e(c["title"])}</span>
    </nav>
  </div>
</div>

<!-- Chapter Overview Content -->
<main class="wrap chapter-layout-wrap">
  <section class="chapter-main-content">
    <div class="ch-overview-header">
      <div class="ch-overview-info">
        <h1>{e(c["title"])}</h1>
        <p class="ch-overview-lead">{e(c["blurb"])}</p>
      </div>
      <div class="ch-overview-actions">
        <span class="topics-count-badge">{len(c["topics"])} Topics</span>
        <a href="view{idx}.html?full=1" class="view-full-chapter-btn" aria-label="View full interactive chapter: {e(c["title"])}" title="Open the complete interactive chapter">
          <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M16 3h3a2 2 0 0 1 2 2v3"></path><path d="M8 21H5a2 2 0 0 1-2-2v-3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path></svg>
          View Full Chapter
        </a>
      </div>
    </div>

    <!-- Topic Cards Grid -->
    <div class="topic-cards-grid">
      {cards_html}
    </div>
  </section>
</main>

{generate_footer()}
{generate_search_modal()}

<script>
{JS_COMMON % {"root_prefix": "../"}}
</script>
</body>
</html>
'''
    return page_html

def build_chapter_view_page(c):
    e = html.escape
    idx = c["i"]
    page_html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(c["ch_code"])} — Interactive Chapter | Electric Machinery Fundamentals</title>
<meta name="description" content="Interactive chapter application for {e(c["title"])}.">
<meta name="theme-color" content="#070e1e">
{generate_favicon_link("../")}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT_STYLESHEET}
<style>
* {{ box-sizing: border-box; }}
:root {{ --cyan-accent: #38bdf8; --bg-card: #fff; --line: #e2e8f0; --radius-lg: 16px; --text-muted: #64748b; --text-main: #0f172a; --blue-light: #eff6ff; --blue-primary: #2563eb; }}
html, body {{ width: 100%; min-height: 100%; margin: 0; overflow-x: hidden; }}
body {{ padding-top: 64px; background: #0b132b; color: #f8fafc; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
.wrap {{ max-width: 1200px; width: 100%; margin: 0 auto; padding: 0 24px; }}
a:focus-visible, button:focus-visible {{ outline: 3px solid #38bdf8; outline-offset: 2px; }}
.lesson-shell {{ display: flex; flex-direction: column; width: 100%; height: calc(100vh - 64px); height: calc(100dvh - 64px); background: #0b132b; }}
.lesson-toolbar {{
  display: grid; flex: 0 0 auto; grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center; column-gap: 14px; min-height: 64px; padding: 8px 16px;
  background: #070e1e; border-bottom: 1px solid rgba(255,255,255,.14);
}}
.lesson-breadcrumbs {{ display: flex; align-items: center; gap: 8px; min-width: 0; overflow: hidden; white-space: nowrap; }}
.lesson-breadcrumbs a {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.lesson-breadcrumbs .current {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.lesson-breadcrumbs a {{ color: #cbd5e1; text-decoration: none; font-weight: 600; }}
.lesson-breadcrumbs a:hover {{ color: #7dd3fc; }}
.lesson-breadcrumbs .separator {{ color: #64748b; }}
.lesson-breadcrumbs .current {{ color: #f8fafc; font-weight: 700; }}
.lesson-actions {{ display: flex; flex: 0 0 auto; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }}
.lesson-topic-controls {{ display: none; align-items: center; gap: 8px; }}
.lesson-shell:fullscreen .lesson-topic-controls, .lesson-shell.is-fullscreen .lesson-topic-controls {{ display: flex; }}
.topics-toggle {{
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  min-height: 44px; padding: 9px 12px; border: 1px solid rgba(255,255,255,.22);
  border-radius: 9px; background: #17243a; color: #f8fafc;
  font: 600 14px/1.2 system-ui, -apple-system, "Segoe UI", sans-serif;
  white-space: nowrap; cursor: pointer; touch-action: manipulation;
}}
.topics-toggle:hover {{ background: #253a5a; border-color: rgba(255,255,255,.45); }}
.topics-toggle svg {{ flex: 0 0 auto; }}
.lesson-actions a, .lesson-actions button {{
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  min-height: 44px; padding: 9px 13px; border: 1px solid rgba(255,255,255,.22);
  border-radius: 9px; background: #17243a; color: #f8fafc;
  font: 600 14px/1.2 system-ui, -apple-system, "Segoe UI", sans-serif;
  text-decoration: none; cursor: pointer; touch-action: manipulation; white-space: nowrap;
}}
.lesson-actions a:hover, .lesson-actions button:hover {{ background: #253a5a; border-color: rgba(255,255,255,.45); }}
.lesson-toolbar > .topics-toggle {{ grid-column: 1; grid-row: 1; }}
.lesson-toolbar > .lesson-breadcrumbs {{ grid-column: 2; grid-row: 1; }}
.lesson-toolbar > .lesson-actions {{ grid-column: 3; grid-row: 1; }}
.lesson-shell:fullscreen, .lesson-shell.is-fullscreen {{ width: 100%; height: 100vh; height: 100dvh; margin-top: -64px; }}
.lesson-shell:fullscreen [data-enter-fullscreen], .lesson-shell.is-fullscreen [data-enter-fullscreen] {{ display: none; }}
.lesson-shell:not(:fullscreen):not(.is-fullscreen) [data-exit-fullscreen] {{ display: none; }}
.lesson-frame {{ display: block; flex: 1 1 auto; width: 100%; min-height: 0; border: 0; background: #0f1220; }}
@media (max-width: 720px) {{
  .lesson-toolbar {{ grid-template-columns: auto minmax(0, 1fr); row-gap: 7px; column-gap: 10px; padding: 8px max(10px, env(safe-area-inset-right, 0px)) 8px max(10px, env(safe-area-inset-left, 0px)); }}
  .lesson-toolbar > .topics-toggle {{ grid-column: 1; grid-row: 1; }}
  .lesson-toolbar > .lesson-actions {{ grid-column: 2; grid-row: 1; }}
  .lesson-toolbar > .lesson-breadcrumbs {{ grid-column: 1 / -1; grid-row: 2; min-height: 28px; font-size: 13px; }}
  .topics-toggle {{ width: 44px; padding: 10px; }}
  .topics-toggle span {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }}
  .lesson-actions {{ display: flex; }}
  .lesson-actions a, .lesson-actions button {{ min-width: 0; padding: 8px 6px; font-size: 12px; }}
  .lesson-topic-controls {{ flex-wrap: wrap; justify-content: flex-end; }}
}}
@media (max-width: 860px) {{
  .lesson-toolbar {{ grid-template-columns: auto minmax(0, 1fr); }}
  .lesson-toolbar > .topics-toggle {{ grid-column: 1; grid-row: 1; }}
  .lesson-toolbar > .lesson-actions {{ grid-column: 2; grid-row: 1; }}
  .lesson-toolbar > .lesson-breadcrumbs {{ grid-column: 1 / -1; grid-row: 2; }}
  .lesson-actions {{ min-width: 0; max-width: 100%; }}
  .lesson-actions a, .lesson-actions button {{ min-width: 0; max-width: 100%; white-space: normal; overflow-wrap: anywhere; }}
  .lesson-topic-controls {{ min-width: 0; max-width: 100%; flex-wrap: wrap; }}
}}
@media (max-width: 480px) {{
  .wrap {{ padding: 0 16px; }}
}}
@media (max-width: 380px) {{
  .lesson-breadcrumbs {{ gap: 5px; font-size: 12px; }}
  .lesson-actions {{ display: grid; width: 100%; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .lesson-topic-controls {{ grid-column: 1 / -1; }}
  .lesson-topic-controls button {{ flex: 1 1 0; }}
  .lesson-actions a, .lesson-actions button {{ gap: 5px; padding: 8px 4px; font-size: 11px; }}
  .lesson-actions svg {{ width: 15px; height: 15px; }}
}}
{generate_nav_styles()}
{generate_search_styles()}
</style>
</head>
<body>
{generate_header("../", active_page="chapters")}
<main class="lesson-shell" id="lesson-shell">
  <div class="lesson-toolbar">
    <button type="button" class="topics-toggle" id="toggle-topics" aria-label="Hide topics" aria-expanded="true" title="Hide topics">
      <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"></rect><path d="M9 4v16"></path><path d="m16 9-3 3 3 3"></path></svg>
      <span>Hide topics</span>
    </button>
    <nav class="lesson-breadcrumbs" aria-label="Breadcrumb">
      <a href="../index.html">Home</a><span class="separator" aria-hidden="true">›</span>
      <a href="../index.html#chapters">Chapters</a><span class="separator" aria-hidden="true">›</span>
      <a href="chapter{idx}.html">{e(c["title"])}</a><span class="separator" aria-hidden="true">›</span>
      <span class="current" id="lesson-kind">Interactive Topic</span>
    </nav>
    <div class="lesson-actions" role="toolbar" aria-label="Chapter navigation">
      <div class="lesson-topic-controls" id="fullscreen-topic-navigation" role="group" aria-label="Topic navigation">
        <button type="button" id="fullscreen-previous-topic" disabled>← Previous Topic</button>
        <button type="button" id="fullscreen-next-topic" disabled>Next Topic →</button>
      </div>
      <button type="button" id="enter-fullscreen" data-enter-fullscreen aria-label="Enter fullscreen" title="Enter fullscreen">
        <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 3 5 3 5 8"></polyline><polyline points="16 3 19 3 19 8"></polyline><polyline points="8 21 5 21 5 16"></polyline><polyline points="16 21 19 21 19 16"></polyline></svg>
        Fullscreen
      </button>
      <button type="button" id="exit-fullscreen" data-exit-fullscreen aria-label="Exit fullscreen" title="Exit fullscreen">
        <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 3 8 8 3 8"></polyline><polyline points="16 3 16 8 21 8"></polyline><polyline points="8 21 8 16 3 16"></polyline><polyline points="16 21 16 16 21 16"></polyline></svg>
        Exit Fullscreen
      </button>
      <a href="chapter{idx}.html" id="back-to-chapter" aria-label="Back to {e(c["title"])} chapter overview" title="Return to the chapter overview">
        <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
        <span id="back-label">Back to Chapter</span>
      </a>
    </div>
  </div>
  <iframe class="lesson-frame" id="lesson-frame" title="{e(c["ch_code"])} — {e(c["title"])}"></iframe>
</main>
{generate_search_modal()}
<script>
{JS_COMMON % {"root_prefix": "../"}}
</script>
<script>
(function(){{
  var shell=document.getElementById('lesson-shell');
  var frame=document.getElementById('lesson-frame');
  var fullscreenPreviousTopic=document.getElementById('fullscreen-previous-topic');
  var fullscreenNextTopic=document.getElementById('fullscreen-next-topic');
  var enter=document.getElementById('enter-fullscreen');
  var exitButton=document.getElementById('exit-fullscreen');
  var back=document.getElementById('back-to-chapter');
  var topicsToggle=document.getElementById('toggle-topics');
  var topicsHidden=false;
  var isFullChapter=new URLSearchParams(location.search).get('full')==='1';
  var chapterUrl='../chapters/{e(c["fn"])}';

  function refreshLessonLayout(){{
    var lessonWindow=frame.contentWindow;
    if(lessonWindow) lessonWindow.dispatchEvent(new lessonWindow.Event('resize'));
  }}
  function applyTopicsLayout(lessonDocument){{
    var app=lessonDocument&&lessonDocument.querySelector('.app');
    var sidebar=lessonDocument&&lessonDocument.querySelector('.side');
    var workspace=lessonDocument&&lessonDocument.querySelector('.main');
    if(!app||!sidebar||!workspace||!topicsToggle) return false;
    app.classList.toggle('emf-topics-collapsed',topicsHidden);
    if(topicsHidden){{
      var isMobile=window.matchMedia('(max-width: 860px)').matches;
      app.style.setProperty('grid-template-columns',isMobile?'1fr':'0px 1fr');
      if(isMobile) sidebar.style.setProperty('display','none');
      else sidebar.style.removeProperty('display');
      workspace.style.setProperty('width','100%');
      workspace.style.setProperty('max-width','none');
    }}else{{
      app.style.removeProperty('grid-template-columns');
      sidebar.style.removeProperty('display');
      workspace.style.removeProperty('width');
      workspace.style.removeProperty('max-width');
    }}
    return true;
  }}
  function setTopicsHidden(hidden){{
    topicsHidden=hidden;
    var lessonDocument=frame.contentDocument;
    applyTopicsLayout(lessonDocument);
    if(!topicsToggle)return;
    topicsToggle.setAttribute('aria-expanded',String(!hidden));
    topicsToggle.setAttribute('aria-label',hidden?'Show topics':'Hide topics');
    topicsToggle.title=hidden?'Show topics':'Hide topics';
    topicsToggle.querySelector('span').textContent=hidden?'Show topics':'Hide topics';
    topicsToggle.querySelector('svg').innerHTML=hidden
      ? '<rect x="3" y="4" width="18" height="16" rx="2"></rect><path d="M9 4v16"></path><path d="m12 9 3 3-3 3"></path>'
      : '<rect x="3" y="4" width="18" height="16" rx="2"></rect><path d="M9 4v16"></path><path d="m16 9-3 3 3 3"></path>';
    requestAnimationFrame(function(){{setTimeout(refreshLessonLayout,250);}});
  }}
  document.getElementById('lesson-kind').textContent=isFullChapter?'Full Interactive Chapter':'Interactive Topic';
  document.getElementById('back-label').textContent=isFullChapter?'Back to Chapter Overview':'Back to Chapter';
  frame.src=chapterUrl+location.hash;

  frame.addEventListener('load',function(){{
    var lessonDocument=frame.contentDocument;
    if(!lessonDocument)return;
    if(!lessonDocument.getElementById('emf-topics-collapse-style')){{
      var collapseStyle=lessonDocument.createElement('style');
      collapseStyle.id='emf-topics-collapse-style';
      collapseStyle.textContent='.app{{transition:none}}.app>.side{{transition:opacity .22s ease,transform .22s ease}}.app.emf-topics-collapsed>.side{{min-width:0;padding-left:0;padding-right:0;border-right-width:0;overflow:hidden;opacity:0;transform:translateX(-8px)}}.app.emf-topics-collapsed>.main{{width:100%;max-width:none;min-width:0}}.emf-topic-navigation{{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:12px;margin:0 0 18px;padding:0;border:0}}.emf-topic-navigation>div:first-child{{justify-self:start}}.emf-topic-navigation>div:last-child{{justify-self:end}}.emf-topic-navigation .emf-topic-nav-center{{display:flex;flex-direction:column;align-items:center;gap:4px}}.emf-topic-navigation .emf-nav-btn{{width:auto;max-width:100%;white-space:normal;text-align:center}}.emf-topic-navigation .emf-nav-btn:disabled{{opacity:.35;cursor:not-allowed;pointer-events:none}}.emf-topic-progress{{color:var(--muted);font-size:12px;font-weight:600;white-space:nowrap}}.emf-fullscreen-topic-toolbar #emf-bottom-bar{{display:none!important}}@keyframes emf-topic-enter{{from{{opacity:.92;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}}.sec.emf-topic-transition{{animation:emf-topic-enter 220ms ease-out both}}@media(max-width:640px){{.emf-topic-navigation{{gap:6px}}.emf-topic-navigation .emf-nav-btn{{padding:8px 9px;font-size:12px}}}}@media(max-width:860px){{.app.emf-topics-collapsed>.side{{display:none}}}}@media(prefers-reduced-motion:reduce){{.app,.app>.side{{transition:none!important}}.sec.emf-topic-transition{{animation:none}}}}';
      lessonDocument.head.appendChild(collapseStyle);
    }}
    if(!lessonDocument.querySelector('.app')||!lessonDocument.querySelector('.side')||!lessonDocument.querySelector('.main')){{
      topicsToggle.disabled=true;
      topicsToggle.title='Topics sidebar is unavailable on this page';
      console.error('Cannot collapse topics: expected .app, .side, and .main in the chapter lesson.');
      return;
    }}
    topicsToggle.disabled=false;
    var lessonWindow=frame.contentWindow;
    lessonWindow.eval('window.SECTIONS = SECTIONS;');
    if(!Array.isArray(lessonWindow.SECTIONS)||!lessonWindow.SECTIONS.length||typeof lessonWindow.render!=='function'){{
      console.error('Cannot initialize topic navigation: expected chapter SECTIONS and render().');
    }}else{{
      function updateTopicNavigation(activeId){{
        var sections=lessonWindow.SECTIONS;
        var sectionIndex=sections.findIndex(function(section){{return section.id===activeId;}});
        var main=lessonDocument.querySelector('.main');
        var topicNavigation=main&&main.querySelector('#emf-bottom-bar');
        var activeSection=main&&main.querySelector('.sec.on');
        if(sectionIndex<0||!main||!activeSection){{
          console.error('Cannot update topic navigation: expected an active section in the main content area.');
          return;
        }}
        if(!topicNavigation){{
          topicNavigation=lessonDocument.createElement('div');
          topicNavigation.id='emf-bottom-bar';
          main.appendChild(topicNavigation);
        }}
        main.querySelectorAll('.sec.emf-topic-transition').forEach(function(section){{
          section.classList.remove('emf-topic-transition');
        }});
        activeSection.classList.add('emf-topic-transition');
        var topAction=main.querySelector('#emf-top-bar .emf-btn-next-top');
        if(topAction&&topAction.parentNode) topAction.parentNode.remove();
        topicNavigation.classList.remove('emf-topic-footer-nav');
        topicNavigation.classList.add('emf-topic-navigation');
        var previousSection=sectionIndex>0?sections[sectionIndex-1]:null;
        var nextSection=sectionIndex<sections.length-1?sections[sectionIndex+1]:null;
        var previousButton=lessonDocument.createElement('button');
        previousButton.type='button';
        previousButton.className='emf-nav-btn';
        previousButton.textContent=previousSection?'← Previous: '+previousSection.label:'← Previous Topic';
        previousButton.disabled=!previousSection;
        previousButton.setAttribute('aria-label',previousSection?'Previous topic: '+previousSection.label:'No previous topic');
        previousButton.title=previousSection?'Previous: '+previousSection.label:'No previous topic';
        if(previousSection) previousButton.onclick=function(){{lessonWindow.render(previousSection.id);}};
        var nextButton=lessonDocument.createElement('button');
        nextButton.type='button';
        nextButton.className='emf-nav-btn';
        nextButton.textContent=nextSection?'Next: '+nextSection.label+' →':'Next Topic →';
        nextButton.disabled=!nextSection;
        nextButton.setAttribute('aria-label',nextSection?'Next topic: '+nextSection.label:'No next topic');
        nextButton.title=nextSection?'Next: '+nextSection.label:'No next topic';
        if(nextSection) nextButton.onclick=function(){{lessonWindow.render(nextSection.id);}};
        var previousSlot=lessonDocument.createElement('div');
        previousSlot.appendChild(previousButton);
        var center=lessonDocument.createElement('div');
        center.className='emf-topic-nav-center';
        var progress=lessonDocument.createElement('span');
        progress.className='emf-topic-progress';
        progress.textContent='Topic '+(sectionIndex+1)+' of '+sections.length;
        var overviewLink=lessonDocument.createElement('a');
        overviewLink.href='../chapter-pages/chapter{idx}.html';
        overviewLink.className='emf-overview-link';
        overviewLink.textContent='Back to Chapter Overview';
        center.appendChild(overviewLink);
        center.appendChild(progress);
        var nextSlot=lessonDocument.createElement('div');
        nextSlot.appendChild(nextButton);
        topicNavigation.replaceChildren(previousSlot,center,nextSlot);
        main.insertBefore(topicNavigation,activeSection);
        fullscreenPreviousTopic.disabled=!previousSection;
        fullscreenPreviousTopic.textContent=previousSection?'← Previous: '+previousSection.label:'← Previous Topic';
        fullscreenPreviousTopic.setAttribute('aria-label',previousSection?'Previous topic: '+previousSection.label:'No previous topic');
        fullscreenPreviousTopic.title=previousSection?'Previous: '+previousSection.label:'No previous topic';
        fullscreenPreviousTopic.onclick=previousSection?function(){{lessonWindow.render(previousSection.id);}}:null;
        fullscreenNextTopic.disabled=!nextSection;
        fullscreenNextTopic.textContent=nextSection?'Next: '+nextSection.label+' →':'Next Topic →';
        fullscreenNextTopic.setAttribute('aria-label',nextSection?'Next topic: '+nextSection.label:'No next topic');
        fullscreenNextTopic.title=nextSection?'Next: '+nextSection.label:'No next topic';
        fullscreenNextTopic.onclick=nextSection?function(){{lessonWindow.render(nextSection.id);}}:null;
      }}
      var chapterRender=lessonWindow.render;
      lessonWindow.render=function(id){{
        var topic=lessonWindow.SECTIONS.find(function(section){{return section.id===id;}});
        if(topic){{
          var topicHash='#'+topic.id;
          if(lessonWindow.location.hash!==topicHash) lessonWindow.history.replaceState(null,'',topicHash);
          if(location.hash!==topicHash) history.pushState(null,'',topicHash);
        }}
        var result=chapterRender.apply(this,arguments);
        updateTopicNavigation(id);
        return result;
      }};
      var requestedSection=(lessonWindow.location.hash||'').slice(1);
      var initialSection=lessonWindow.SECTIONS.find(function(section){{return section.id===requestedSection;}});
      lessonWindow.render((initialSection||lessonWindow.SECTIONS[0]).id);
      function syncTopicFromRoute(){{
        var topicId=decodeURIComponent(location.hash.slice(1));
        var topic=lessonWindow.SECTIONS.find(function(section){{return section.id===topicId;}});
        if(topic&&lessonWindow.location.hash!=='#'+topic.id) lessonWindow.render(topic.id);
      }}
      window.addEventListener('popstate',syncTopicFromRoute);
      window.addEventListener('hashchange',syncTopicFromRoute);
    }}
    applyTopicsLayout(lessonDocument);
    updateFullscreenState();
    refreshLessonLayout();
    lessonDocument.addEventListener('click',function(event){{
      var link=event.target.closest&&event.target.closest('a[href]');
      if(!link)return;
      var href=link.getAttribute('href')||'';
      var overview=href.match(/^\\.\\.\\/chapter-pages\\/chapter([0-7])\\.html(?:#.*)?$/);
      if(overview){{
        event.preventDefault();
        location.assign('chapter'+overview[1]+'.html');
        return;
      }}
      var chapter=href.match(/^chapter([0-7])\\.html(?:#.*)?$/);
      if(chapter){{
        event.preventDefault();
        location.assign('view'+chapter[1]+'.html?full=1'+(link.hash||''));
      }}
    }},true);
  }});
  topicsToggle.addEventListener('click',function(){{setTopicsHidden(!topicsHidden);}});

  function fullscreenError(action,error){{
    console.error(action,error);
    window.alert(action+(error&&error.message?' '+error.message:' Please try again.'));
  }}
  function updateFullscreenState(){{
    var active=document.fullscreenElement===shell||document.webkitFullscreenElement===shell;
    shell.classList.toggle('is-fullscreen',active);
    exitButton.hidden=!active;
    var lessonDocument=frame.contentDocument;
    if(lessonDocument&&lessonDocument.body) lessonDocument.body.classList.toggle('emf-fullscreen-topic-toolbar',active);
  }}
  function exitFullscreen(){{
    if(document.fullscreenElement!==shell&&document.webkitFullscreenElement!==shell)return Promise.resolve();
    var method=document.exitFullscreen||document.webkitExitFullscreen;
    if(!method)return Promise.resolve();
    try{{return Promise.resolve(method.call(document));}}
    catch(error){{return Promise.reject(error);}}
  }}

  if(!(shell.requestFullscreen||shell.webkitRequestFullscreen))enter.hidden=true;
  updateFullscreenState();
  enter.addEventListener('click',function(){{
    var method=shell.requestFullscreen||shell.webkitRequestFullscreen;
    if(!method)return;
    try{{
      var request=method.call(shell);
      requestAnimationFrame(updateFullscreenState);
      Promise.resolve(request).then(updateFullscreenState).catch(function(error){{fullscreenError('Could not enter fullscreen.',error);}});
    }}
    catch(error){{fullscreenError('Could not enter fullscreen.',error);}}
  }});
  exitButton.addEventListener('click',function(){{
    exitFullscreen().then(updateFullscreenState).catch(function(error){{fullscreenError('Could not exit fullscreen.',error);}});
  }});
  back.addEventListener('click',function(event){{
    event.preventDefault();
    exitFullscreen().then(function(){{updateFullscreenState();location.assign(back.href);}},function(error){{
      fullscreenError('Could not exit fullscreen before returning to the chapter overview.',error);
      location.assign(back.href);
    }});
  }});
  document.addEventListener('keydown',function(event){{
    if(event.key==='Escape'&&(document.fullscreenElement===shell||document.webkitFullscreenElement===shell)){{
      exitFullscreen().then(updateFullscreenState).catch(function(error){{fullscreenError('Could not exit fullscreen.',error);}});
    }}
  }});
  document.addEventListener('fullscreenchange',updateFullscreenState);
  document.addEventListener('webkitfullscreenchange',updateFullscreenState);
  shell.addEventListener('fullscreenchange',updateFullscreenState);
  shell.addEventListener('webkitfullscreenchange',updateFullscreenState);
  var topicViewport=window.matchMedia('(max-width: 860px)');
  function updateTopicsForViewport(){{
    if(!topicsHidden)return;
    applyTopicsLayout(frame.contentDocument);
    refreshLessonLayout();
  }}
  window.addEventListener('resize',updateTopicsForViewport);
  if(topicViewport.addEventListener) topicViewport.addEventListener('change',updateTopicsForViewport);
  else if(topicViewport.addListener) topicViewport.addListener(updateTopicsForViewport);
}})();
</script>
</body>
</html>
'''
    return page_html

def build_explore_page(ch):
    e = html.escape
    cards = "".join(f'''
      <a class="ch-card" href="chapter-pages/chapter{c["i"]}.html">
        <div class="ch-icon-wrap" style="background:{c["ch_bg"]}; color:{c["ch_color"]}">
          {c["ch_icon"]}
        </div>
        <div class="ch-body">
          <span class="ch-code" style="color:{c["ch_color"]}">{e(c["ch_code"])}</span>
          <h3 class="ch-title">{e(c["title"])}</h3>
          <p class="ch-desc">{e(c["ch_short"])}</p>
        </div>
        <div class="ch-arrow" style="color:{c["ch_color"]}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="12" x2="19" y2="12"></line><polyline points="13 6 19 12 13 18"></polyline></svg></div>
      </a>''' for c in ch)

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Explore Chapters — Electric Machinery Fundamentals</title>
<meta name="description" content="Select a chapter to explore electrical machines topics, interactive labs, and animated simulations.">
<meta name="theme-color" content="#070e1e">
{generate_favicon_link()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT_STYLESHEET}
<style>{CSS_EXPLORE}</style>
</head>
<body>

{generate_header("", active_page="chapters")}

<div class="explore-breadcrumbs">
  <div class="wrap">
    <nav aria-label="Breadcrumb">
      <a href="index.html">Home</a>
      <span class="crumb-sep" aria-hidden="true">›</span>
      <span class="crumb-current">Explore Chapters</span>
    </nav>
    <a href="index.html" class="back-home-btn">
      <span aria-hidden="true">←</span>
      <span>Back to Home</span>
    </a>
  </div>
</div>

<!-- Explore Header Banner with Watermark -->
<section class="explore-hero">
  <div class="wrap explore-hero-wrap">
    <div class="explore-hero-content">
      <span class="section-kicker">EXPLORE CHAPTERS</span>
      <h1>Choose a Chapter</h1>
      <p>Select a chapter to explore its topics, engineering derivations, and interactive simulations.</p>
    </div>
    <div class="explore-motor-watermark">
      <img data-src="assets/motor_hero.webp" alt="Electric Motor Blueprint" width="220" height="220" loading="lazy" decoding="async" style="width:100%; border-radius:16px; border:1px solid rgba(56,189,248,0.3); box-shadow:0 12px 30px rgba(11,42,91,0.1);">
    </div>
  </div>
</section>

<!-- Chapters Cards Grid -->
<main class="wrap explore-main">
  <div class="chapter-cards-grid">
    {cards}
  </div>
</main>

{generate_footer()}
{generate_search_modal()}

<script>
{JS_COMMON % {"root_prefix": ""}}
</script>
</body>
</html>
'''

def extract_youtube_video_id(url):
    if not isinstance(url, str):
        raise ValueError(f"Unsupported or invalid YouTube URL/video ID: {url!r}")

    raw = url.strip()
    if not raw:
        raise ValueError("Empty YouTube URL")

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", raw):
        return raw

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower().replace("www.", "")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in ("youtube.com", "m.youtube.com", "music.youtube.com", "youtube-nocookie.com"):
        if parsed.path in ("/watch", "/watch/"):
            video_id = parse_qs(parsed.query, keep_blank_values=True).get("v", [""])[0]
        else:
            match = re.match(r"^/(?:embed|shorts|live|v)/([^/?#]+)", parsed.path)
            video_id = match.group(1) if match else ""
    else:
        video_id = ""

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Unsupported or invalid YouTube URL/video ID: {url!r}")
    return video_id


def load_video_data():
    with io.open(VIDEO_DATA, "r", encoding="utf-8") as source:
        data = json.load(source)

    seen_ids = set()
    entries = list(data.get("mapped", [])) + list(data.get("unresolved", []))
    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError(f"Invalid lecture record in {VIDEO_DATA}: each entry must be an object")
        raw_url = entry.get("url", "")
        if not raw_url:
            raise ValueError(f"Missing YouTube URL for lecture {entry.get('title', '<untitled>')!r}")
        try:
            video_id = extract_youtube_video_id(raw_url)
        except ValueError as error:
            raise ValueError(
                f"Invalid YouTube URL for lecture {entry.get('title', '<untitled>')!r}: {raw_url!r}"
            ) from error
        if not video_id:
            continue
        if "id" in entry and entry.get("id") not in (None, "") and entry.get("id") != video_id:
            raise ValueError(
                f"Stored YouTube ID {entry.get('id')!r} does not match URL ID {video_id!r}"
            )
        if not isinstance(entry.get("title"), str) or not entry["title"].strip():
            raise ValueError(f"Missing verified video title for {video_id!r}")
        if not isinstance(entry.get("sourceWeek"), int) or not isinstance(entry.get("sourceTopics"), str) or not entry["sourceTopics"].strip():
            raise ValueError(f"Missing weekly-plan topic association for {video_id!r}")
        if video_id in seen_ids:
            continue
        seen_ids.add(video_id)
        entry["id"] = video_id
    if "sourceNotes" in data and not isinstance(data.get("sourceNotes"), list):
        raise ValueError(f"Missing source notes in {VIDEO_DATA}")
    return data


def group_video_topics(video_data):
    topics_by_source = {}
    for video in video_data.get("mapped", []):
        if not isinstance(video, dict):
            continue
        key = (video.get("sourceWeek"), video.get("sourceTopics"))
        if key[0] is None or not key[1]:
            continue
        if key not in topics_by_source:
            topics_by_source[key] = {
                "week": key[0],
                "title": key[1],
                "videos": [],
            }
        topics_by_source[key]["videos"].append({
            "id": video.get("id"),
            "title": video.get("title"),
            "url": video.get("url"),
        })
    return sorted(topics_by_source.values(), key=lambda topic: topic["week"])


def build_legacy_chapters_redirect():
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=index.html#chapters">
<title>Chapters — Electric Machinery Fundamentals</title>
{generate_favicon_link()}
<link rel="canonical" href="index.html#chapters">
<script>window.location.replace("index.html#chapters");</script>
</head>
<body>
<p>Chapter selection has moved to the <a href="index.html#chapters">homepage chapters section</a>.</p>
</body>
</html>'''


def build_home_video_section(video_data):
    topics = group_video_topics(video_data)
    weeks = sorted({topic["week"] for topic in topics})
    topic_options = sorted({topic["title"] for topic in topics}, key=str.casefold)
    week_options_html = "".join(
        f'<option value="{week}">Week {week}</option>' for week in weeks
    )
    topic_options_html = "".join(
        f'<option value="{html.escape(title, quote=True)}">{html.escape(title)}</option>'
        for title in topic_options
    )
    topic_cards = []
    for topic in topics:
        lecture_cards = []
        for video in topic["videos"]:
            player_url = f'video-lectures.html#video/{video["id"]}'
            title = html.escape(video["title"])
            url = html.escape(player_url, quote=True)
            search_text = html.escape(
                f'week {topic["week"]} {topic["title"]} {video["title"]} {video["url"]} {video["id"]}'.lower(),
                quote=True,
            )
            topic_attr = html.escape(topic["title"], quote=True)
            thumbnail = f'https://img.youtube.com/vi/{video["id"]}/hqdefault.jpg'
            lecture_cards.append(f'''
          <article class="home-lecture-card" data-lecture-search="{search_text}" data-lecture-week="{topic["week"]}" data-lecture-topic="{topic_attr}">
            <a class="home-lecture-thumbnail" href="{url}" aria-label="Play {title}">
              <img src="{thumbnail}" alt="" loading="lazy" decoding="async">
              <span class="home-lecture-play" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l10-6.5z"></path></svg></span>
            </a>
            <h4>{title}</h4>
            <a class="home-lecture-button" href="{url}"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l10-6.5z"></path></svg>Play Lecture</a>
          </article>''')
        topic_cards.append(f'''
      <article class="home-lecture-topic">
        <div class="home-lecture-topic-header">
          <span class="week-label">Week {topic["week"]}</span>
          <span class="topic-video-count">{len(topic["videos"])} lecture{"s" if len(topic["videos"]) != 1 else ""}</span>
        </div>
        <h3>{html.escape(topic["title"])}</h3>
        <div class="home-lecture-grid">{"".join(lecture_cards)}</div>
      </article>''')

    return f'''<section class="home-video-section" id="video-lectures" aria-labelledby="home-video-heading">
  <div class="wrap">
    <div class="home-video-heading">
      <div class="home-video-intro">
        <span class="section-kicker">DIGITAL LEARNING RESOURCES</span>
        <h2 id="home-video-heading">Video Lectures</h2>
        <p>Browse topic-wise lectures and watch a lesson on its dedicated page.</p>
        <p class="home-video-result-count" id="home-video-result-count" aria-live="polite"></p>
      </div>
      <div class="home-video-filters" role="group" aria-label="Filter video lectures">
        <label><span class="sr-only">Filter by week</span><select id="home-video-week"><option value="">All weeks</option>{week_options_html}</select></label>
        <label><span class="sr-only">Filter by topic</span><select id="home-video-topic"><option value="">All topics</option>{topic_options_html}</select></label>
        <label class="home-video-search">
          <span class="sr-only">Search video lectures</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>
          <input id="home-video-search" type="search" placeholder="Search lectures, topics or weeks" autocomplete="off" aria-controls="home-video-topic-grid">
        </label>
        <button class="home-video-reset" id="home-video-reset" type="button">Clear filters</button>
      </div>
    </div>
    <p class="home-video-empty" id="home-video-empty" role="status" hidden>No matching lectures found</p>
    <div class="home-video-topic-grid" id="home-video-topic-grid">
      {"".join(topic_cards)}
    </div>
  </div>
</section>
<script>
(function(){{
  var returnKey='emfVideoListReturn';
  var search=document.getElementById('home-video-search');
  var weekFilter=document.getElementById('home-video-week');
  var topicFilter=document.getElementById('home-video-topic');
  var reset=document.getElementById('home-video-reset');
  var resultCount=document.getElementById('home-video-result-count');
  window.addEventListener('pageshow',function(){{
    if(sessionStorage.getItem(returnKey)!=='1') return;
    sessionStorage.removeItem(returnKey);
    var savedQuery=sessionStorage.getItem('emfVideoListSearch')||'';
    var savedWeek=sessionStorage.getItem('emfVideoListWeek')||'';
    var savedTopic=sessionStorage.getItem('emfVideoListTopic')||'';
    var savedScroll=Number(sessionStorage.getItem('emfVideoListScrollY'));
    sessionStorage.removeItem('emfVideoListSearch');
    sessionStorage.removeItem('emfVideoListWeek');
    sessionStorage.removeItem('emfVideoListTopic');
    sessionStorage.removeItem('emfVideoListScrollY');
    search.value=savedQuery;
    weekFilter.value=savedWeek;
    topicFilter.value=savedTopic;
    search.dispatchEvent(new Event('input'));
    if(Number.isFinite(savedScroll)) window.requestAnimationFrame(function(){{window.scrollTo(0,savedScroll);}});
  }});
  document.querySelectorAll('.home-lecture-thumbnail,.home-lecture-button').forEach(function(link){{
    link.addEventListener('click',function(){{
      sessionStorage.setItem(returnKey,'1');
      sessionStorage.setItem('emfVideoListSearch',search.value);
      sessionStorage.setItem('emfVideoListWeek',weekFilter.value);
      sessionStorage.setItem('emfVideoListTopic',topicFilter.value);
      sessionStorage.setItem('emfVideoListScrollY',String(window.scrollY));
    }});
  }});
  var topics=Array.prototype.slice.call(document.querySelectorAll('.home-lecture-topic'));
  var empty=document.getElementById('home-video-empty');
  if(!search) return;
  function updateLectureResults(){{
    var query=search.value.trim().toLowerCase();
    var visibleCount=0;
    topics.forEach(function(topic){{
      var cards=Array.prototype.slice.call(topic.querySelectorAll('.home-lecture-card'));
      var visibleInTopic=0;
      cards.forEach(function(card){{
        var visible=(!query || card.dataset.lectureSearch.indexOf(query)!==-1) &&
          (!weekFilter.value || card.dataset.lectureWeek===weekFilter.value) &&
          (!topicFilter.value || card.dataset.lectureTopic===topicFilter.value);
        card.hidden=!visible;
        if(visible) visibleInTopic++;
      }});
      topic.hidden=visibleInTopic===0;
      visibleCount+=visibleInTopic;
    }});
    empty.hidden=visibleCount!==0;
    resultCount.textContent=visibleCount+' lecture'+(visibleCount===1?'':'s')+' found';
  }}
  search.addEventListener('input',updateLectureResults);
  weekFilter.addEventListener('change',updateLectureResults);
  topicFilter.addEventListener('change',updateLectureResults);
  reset.addEventListener('click',function(){{
    search.value='';
    weekFilter.value='';
    topicFilter.value='';
    updateLectureResults();
    search.focus();
  }});
  updateLectureResults();
}})();
</script>'''


def build_video_lectures_page(video_data):
    weekly_topics = group_video_topics(video_data)
    weeks = sorted({topic["week"] for topic in weekly_topics})
    topic_options = sorted({topic["title"] for topic in weekly_topics}, key=str.casefold)
    week_options_html = "".join(
        f'<option value="{week}">Week {week}</option>' for week in weeks
    )
    topic_options_html = "".join(
        f'<option value="{html.escape(title, quote=True)}">{html.escape(title)}</option>'
        for title in topic_options
    )
    embedded_data = json.dumps(weekly_topics, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    css = r"""
* { box-sizing: border-box; }
:root { --cyan-accent: #38bdf8; --bg-card: #fff; --line: #e2e8f0; --radius-lg: 16px; --text-muted: #64748b; --text-main: #0f172a; --blue-light: #eff6ff; --blue-primary: #2563eb; --video-page-bg: #f4f7fb; --video-surface: #fff; --video-line: #dce4ef; --video-text: #172033; --video-heading: #10213f; --video-muted: #64748b; --video-subtle: #f8fafc; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--video-page-bg); color: var(--video-text); font-family: Inter, system-ui, sans-serif; }
body.dark-mode { --video-page-bg: #0b132b; --video-surface: #111d3d; --video-line: #26385f; --video-text: #e2e8f0; --video-heading: #f8fafc; --video-muted: #a7b4ca; --video-subtle: #0b1730; --blue-light: rgba(37,99,235,.2); }
a { color: inherit; }
.wrap { max-width: 1200px; width: 100%; margin: 0 auto; padding: 0 24px; }
@media(max-width:480px) { .wrap { padding: 0 16px; } }
.video-top-nav-spacer { height: 64px; }
.video-back-home-row { max-width: 1200px; margin: 0 auto; padding: 12px 24px 0; }
.video-back-home { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 42px; padding: 9px 14px; border: 1px solid var(--video-line); border-radius: 9px; background: var(--video-surface); color: var(--video-text); font-size: 14px; font-weight: 650; text-decoration: none; }
.video-back-home:hover { background: var(--video-subtle); }
.video-main { width: min(100%, 1200px); min-height: calc(100vh - 185px); margin: auto; padding: 14px 24px 64px; }
.breadcrumbs { margin: 0 0 18px; color: var(--video-muted); font-size: 14px; }
.breadcrumbs a { color: #2563eb; text-decoration: none; }
.inline-crumb { padding: 0; border: 0; background: transparent; color: #2563eb; font: inherit; cursor: pointer; }
.video-hero { padding: clamp(22px, 3vw, 32px) clamp(22px, 4vw, 42px); margin-bottom: 28px; border: 1px solid var(--video-line); border-radius: 18px; background: linear-gradient(120deg,var(--blue-light),var(--video-surface) 68%); }
.eyebrow { display: block; color: #2563eb; font-size: 12px; font-weight: 800; letter-spacing: .12em; line-height: 1.4; text-transform: uppercase; margin-bottom: 8px; }
h1 { margin: 0 0 10px; color: var(--video-heading); font-size: clamp(28px,3.5vw,40px); line-height: 1.12; }
.video-hero p { max-width: 760px; margin: 0; color: var(--video-muted); font-size: clamp(14px,1.2vw,16px); line-height: 1.6; }
.section-heading { margin: 0 0 14px; color: var(--video-heading); font-size: 22px; }
.lecture-controls { display: grid; grid-template-columns: minmax(220px, 1fr) repeat(2,minmax(150px,.55fr)) auto; gap: 10px; margin: 0 0 12px; }
.lecture-controls > label { display: block; width: 100%; min-width: 0; }
.lecture-controls input, .lecture-controls select, .lecture-reset { width: 100%; min-width: 0; min-height: 44px; padding: 9px 12px; border: 1px solid var(--video-line); border-radius: 9px; background: var(--video-surface); color: var(--video-text); font: inherit; }
.lecture-controls input:focus-visible, .lecture-controls select:focus-visible, .lecture-reset:focus-visible, .back-button:focus-visible, .watch-button:focus-visible, .youtube-link:focus-visible, .topic-video-title:focus-visible { outline: 3px solid #2563eb; outline-offset: 2px; }
.lecture-reset { cursor: pointer; font-weight: 650; }
.lecture-reset:hover { background: var(--video-subtle); }
.lecture-result-count { margin: 0 0 14px; color: var(--video-muted); font-size: 14px; }
.lecture-empty { margin: 0 0 14px; padding: 16px; border: 1px solid var(--video-line); border-radius: 9px; background: var(--video-surface); color: var(--video-muted); }
.week-topic-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); align-items: start; gap: 20px; }
.week-topic-card { min-width: 0; padding: 22px; border: 1px solid var(--video-line); border-radius: 14px; background: var(--video-surface); box-shadow: 0 3px 12px rgba(15,23,42,.035); }
.topic-card-meta { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.week-label { display: inline-flex; align-items: center; min-height: 26px; padding: 4px 9px; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 12px; font-weight: 700; white-space: nowrap; }
.week-topic-card h2 { min-width: 0; margin: 0; color: var(--video-heading); font-size: 17px; line-height: 1.45; overflow-wrap: anywhere; }
.topic-video-count { margin: 0; color: var(--video-muted); font-size: 12px; font-weight: 600; white-space: nowrap; }
.topic-video-list { display: grid; gap: 10px; margin-top: 14px; }
.topic-video { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px; border: 1px solid var(--video-line); border-radius: 10px; background: var(--video-subtle); }
.topic-video-title { min-width: 0; flex: 1 1 auto; color: var(--video-text); font-size: 14px; line-height: 1.45; overflow-wrap: anywhere; text-decoration: none; }
.topic-video-title:hover { color: #2563eb; text-decoration: underline; }
.back-button, .watch-button, .youtube-link { min-height: 42px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 9px 14px; border-radius: 9px; font: inherit; font-size: 14px; font-weight: 650; text-decoration: none; cursor: pointer; }
.back-button { margin: 0 0 22px; border: 1px solid var(--video-line); background: var(--video-surface); color: var(--video-text); }
.back-button:hover { background: var(--video-subtle); }
.watch-button { flex: 0 0 auto; border: 0; background: #2563eb; color: #fff; white-space: nowrap; }
.watch-button:hover { background: #1d4ed8; }
.player-card { padding: 22px; border: 1px solid var(--video-line); border-radius: 14px; background: var(--video-surface); }
.player-card h2 { margin: 0 0 6px; color: var(--video-heading); font-size: 21px; }
.player-card h3 { margin: 0 0 10px; color: var(--video-text); font-size: 16px; }
.player-topic { margin: 0 0 16px; color: var(--video-muted); }
.player-frame { overflow: hidden; width: 100%; aspect-ratio: 16/9; border-radius: 11px; background: #07101f; }
.player-frame iframe { display: block; width: 100%; height: 100%; border: 0; }
.player-fallback { margin: 14px 0 0; padding: 12px 14px; border: 1px solid var(--video-line); border-radius: 9px; background: var(--blue-light); color: var(--video-text); font-size: 14px; line-height: 1.5; }
.player-fallback a { color: #1d4ed8; font-weight: 700; }
.player-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.youtube-link { border: 1px solid var(--video-line); background: var(--video-surface); color: var(--video-text); }
.youtube-link:hover { background: var(--video-subtle); }
.related-lectures { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--video-line); }
.related-lectures h3 { margin: 0 0 10px; color: var(--video-heading); }
.related-list { display: grid; gap: 8px; }
.related-list a { color: #2563eb; overflow-wrap: anywhere; }
.video-footer { padding: 23px 24px; color: #94a3b8; background: #070e1e; text-align: center; font-size: 13px; }
[hidden] { display: none !important; }
@media(max-width:680px) {
  .video-back-home-row { padding: 10px 16px 0; }
  .video-main { padding: 12px 16px 48px; }
  .video-hero { padding: 23px 20px; }
  .week-topic-card { padding: 16px; }
  .topic-video { align-items: flex-start; flex-direction: column; }
  .watch-button { align-self: flex-start; }
  .lecture-controls { grid-template-columns: repeat(2,minmax(0,1fr)); }
  .lecture-controls > label:first-child { grid-column: 1 / -1; }
  .lecture-reset { width: auto; grid-column: 1 / -1; justify-self: end; }
}
@media(max-width:520px) {
  .week-topic-grid { grid-template-columns: minmax(0,1fr); gap: 14px; }
  .video-hero { margin-bottom: 22px; }
  .lecture-controls { grid-template-columns: minmax(0,1fr); }
  .lecture-controls > label:first-child, .lecture-reset { grid-column: 1; }
  .lecture-reset { width: 100%; }
  .player-card { padding: 16px; }
}
"""
    css = generate_nav_styles() + generate_search_styles() + css
    script = r"""
const topics = JSON.parse(document.getElementById('video-data').textContent);
const views = {
  list: document.getElementById('lectures-view'),
  player: document.getElementById('player-view')
};
const state = { view: 'list', videoId: null };
const escapeHtml = value => String(value).replace(/[&<>"']/g, ch =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const topicForVideo = id => topics.find(topic => topic.videos.some(video => video.id === id));
const videoFor = id => topicForVideo(id)?.videos.find(video => video.id === id);
const searchInput = document.getElementById('lecture-search');
const weekFilter = document.getElementById('lecture-week');
const topicFilter = document.getElementById('lecture-topic');
const resultCount = document.getElementById('lecture-result-count');
const emptyState = document.getElementById('lecture-empty');
const routeError = document.getElementById('lecture-route-error');
function routeHash() {
  return state.view === 'player' ? `#video/${state.videoId}` : '#lectures';
}
function navigate(view, videoId = null, push = true) {
  if (view !== 'player') {
    state.view = 'list';
    state.videoId = null;
    routeError.hidden = true;
    if (push && location.hash !== '#lectures') history.pushState(null, '', '#lectures');
  } else {
    if (!videoFor(videoId)) {
      showInvalidLecture();
      return;
    }
    state.view = view;
    state.videoId = videoId;
    const hash = routeHash();
    if (push && location.hash !== hash) history.pushState(null, '', hash);
  }
  render();
  window.scrollTo(0, 0);
}
function renderList() {
  document.title = 'Video Lectures — Electric Machinery Fundamentals';
  document.getElementById('player-frame').replaceChildren();
  document.getElementById('youtube-link').href = '#';
  const grouped = new Map();
  for (const topic of topics) {
    if (!grouped.has(topic.week)) grouped.set(topic.week, []);
    grouped.get(topic.week).push(topic);
  }
  const cards = [...grouped.entries()]
    .sort(([weekA], [weekB]) => weekA - weekB)
    .flatMap(([week, weekTopics]) => weekTopics.map(topic => `<article class="week-topic-card" data-topic-week="${week}" data-topic-title="${escapeHtml(topic.title)}">
        <div class="topic-card-meta"><span class="week-label">Week ${week}</span>${topic.videos.length > 1 ? `<span class="topic-video-count">${topic.videos.length} videos</span>` : ''}</div>
        <h2>${escapeHtml(topic.title)}</h2>
        <div class="topic-video-list">${topic.videos.map(video => `<div class="topic-video">
          <a class="topic-video-title" href="#video/${encodeURIComponent(video.id)}" data-watch="${escapeHtml(video.id)}">${escapeHtml(video.title)}</a>
          <button type="button" class="watch-button" data-watch="${escapeHtml(video.id)}">▶ Play Video</button>
        </div>`).join('')}</div>
      </article>`));
  document.getElementById('weekly-plan-list').innerHTML = `<div class="week-topic-grid">${cards.join('')}</div>`;
  applyLectureFilters();
}
function applyLectureFilters() {
  const query = searchInput.value.trim().toLowerCase();
  let visibleCount = 0;
  document.querySelectorAll('.week-topic-card').forEach(topic => {
    const weekMatches = !weekFilter.value || topic.dataset.topicWeek === weekFilter.value;
    const topicMatches = !topicFilter.value || topic.dataset.topicTitle === topicFilter.value;
    let visibleInTopic = 0;
    topic.querySelectorAll('.topic-video').forEach(card => {
      const video = videoFor(card.querySelector('[data-watch]').dataset.watch);
      const searchable = `${video.title} ${topic.dataset.topicTitle} week ${topic.dataset.topicWeek} ${video.id} ${video.url}`.toLowerCase();
      const visible = weekMatches && topicMatches && (!query || searchable.includes(query));
      card.hidden = !visible;
      if (visible) visibleInTopic++;
    });
    topic.hidden = visibleInTopic === 0;
    visibleCount += visibleInTopic;
  });
  resultCount.textContent = `${visibleCount} lecture${visibleCount === 1 ? '' : 's'} found`;
  emptyState.hidden = visibleCount !== 0;
}
function showInvalidLecture() {
  state.view = 'list';
  state.videoId = null;
  routeError.hidden = false;
  render();
}
function renderPlayer() {
  const topic = topicForVideo(state.videoId);
  const video = videoFor(state.videoId);
  if (!topic || !video) {
    showInvalidLecture();
    return;
  }
  document.getElementById('player-topic-title').textContent = topic.title;
  document.getElementById('player-title').textContent = video.title;
  document.getElementById('player-week').textContent = `Week ${topic.week}`;
  document.title = `${video.title} — Video Lectures`;
  document.getElementById('youtube-link').href = video.url;
  const container = document.getElementById('player-frame');
  const fallback = document.getElementById('player-fallback');
  container.replaceChildren();
  if (location.protocol === 'file:') {
    container.hidden = true;
    fallback.textContent = 'Embedded playback is unavailable when this site is opened directly from disk. Use Watch on YouTube to play the original lecture.';
  } else {
    container.hidden = false;
    fallback.textContent = 'If embedded playback is unavailable or does not start, use Watch on YouTube to play the original lecture.';
    const frame = document.createElement('iframe');
    frame.src = `https://www.youtube.com/embed/${encodeURIComponent(video.id)}`;
    frame.title = `YouTube video: ${video.title}`;
    frame.loading = 'lazy';
    frame.referrerPolicy = 'origin';
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    frame.allowFullscreen = true;
    frame.addEventListener('error', () => {
      fallback.textContent = 'The video could not be embedded here. Use Watch on YouTube to play the original lecture.';
    });
    container.appendChild(frame);
  }
  const relatedSection = document.getElementById('related-lectures');
  const relatedVideos = topic.videos.filter(item => item.id !== video.id);
  relatedSection.hidden = relatedVideos.length === 0;
  document.getElementById('related-list').innerHTML = relatedVideos.map(item =>
    `<a href="#video/${encodeURIComponent(item.id)}" data-watch="${escapeHtml(item.id)}">${escapeHtml(item.title)}</a>`
  ).join('');
}
function render() {
  for (const [name, element] of Object.entries(views)) element.hidden = name !== state.view;
  if (state.view === 'list') renderList();
  if (state.view === 'player') renderPlayer();
}
function restoreRoute(hash) {
  let route;
  try {
    route = decodeURIComponent(hash.replace(/^#/, ''));
  } catch (error) {
    showInvalidLecture();
    return;
  }
  const match = route.match(/^video\/([^/]+)$/);
  if (match) {
    if (videoFor(match[1])) {
      state.view = 'player';
      state.videoId = match[1];
      routeError.hidden = true;
      render();
      return;
    }
    showInvalidLecture();
    return;
  }
  state.view = 'list';
  state.videoId = null;
  routeError.hidden = !!(route && route !== 'lectures');
  render();
}
document.addEventListener('click', event => {
  const watchLink = event.target.closest('[data-watch]');
  if (watchLink) {
    event.preventDefault();
    navigate('player', watchLink.dataset.watch);
  }
});
searchInput.addEventListener('input', applyLectureFilters);
weekFilter.addEventListener('change', applyLectureFilters);
topicFilter.addEventListener('change', applyLectureFilters);
document.getElementById('lecture-reset').addEventListener('click', () => {
  searchInput.value = '';
  weekFilter.value = '';
  topicFilter.value = '';
  applyLectureFilters();
  searchInput.focus();
});
document.getElementById('back-to-list').addEventListener('click', () => navigate('list'));
document.getElementById('back-to-list-crumb').addEventListener('click', () => navigate('list'));
window.addEventListener('popstate', () => restoreRoute(location.hash));
document.getElementById('youtube-link').addEventListener('click', event => {
  if (!videoFor(state.videoId)) event.preventDefault();
});
restoreRoute(location.hash);
"""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Browse the teacher's weekly video lecture plan and watch selected lessons.">
<meta name="theme-color" content="#070e1e">
<title>Video Lectures — Electric Machinery Fundamentals</title>
{generate_favicon_link()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT_STYLESHEET}
<style>{css}</style>
</head>
<body>
{generate_header("", active_page="video-lectures")}
<div class="video-top-nav-spacer" aria-hidden="true"></div>
<div class="video-back-home-row"><a class="video-back-home" href="index.html">← Back to Home</a></div>
<main class="video-main">
  <section id="lectures-view">
    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> <span aria-hidden="true">›</span> Video Lectures</nav>
    <div class="video-hero">
      <span class="eyebrow">DIGITAL LEARNING RESOURCES</span>
      <h1>Video Lectures</h1>
      <p>Explore topic-wise video lectures provided by your teacher to strengthen your understanding of Electric Machinery Fundamentals. Select a lecture to watch it directly on this website, or open it on YouTube.</p>
    </div>
    <div class="lecture-controls" role="group" aria-label="Search and filter lectures">
      <label><span class="sr-only">Search lectures by title, topic, or week</span><input id="lecture-search" type="search" placeholder="Search lectures, topics or weeks" autocomplete="off" aria-controls="weekly-plan-list"></label>
      <label><span class="sr-only">Filter by week</span><select id="lecture-week"><option value="">All weeks</option>{week_options_html}</select></label>
      <label><span class="sr-only">Filter by topic</span><select id="lecture-topic"><option value="">All topics</option>{topic_options_html}</select></label>
      <button class="lecture-reset" id="lecture-reset" type="button">Clear filters</button>
    </div>
    <p class="lecture-result-count" id="lecture-result-count" aria-live="polite"></p>
    <p class="lecture-empty" id="lecture-empty" role="status" hidden>No matching lectures found</p>
    <p class="lecture-empty" id="lecture-route-error" role="status" hidden>This lecture link is invalid or is not available in the current lecture list. No other video was substituted.</p>
    <div id="weekly-plan-list"></div>
  </section>
  <section id="player-view" hidden>
    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> <span aria-hidden="true">›</span> <button type="button" class="inline-crumb" id="back-to-list-crumb">Video Lectures</button></nav>
    <button class="back-button" type="button" id="back-to-list">← Back to Video Lectures</button>
    <div class="player-card">
      <h2 id="player-topic-title"></h2>
      <p class="player-week" id="player-week"></p>
      <h3 id="player-title"></h3>
      <div class="player-frame" id="player-frame"></div>
      <p class="player-fallback" id="player-fallback"></p>
      <div class="player-actions"><a class="youtube-link" id="youtube-link" href="#" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></div>
      <section class="related-lectures" id="related-lectures" hidden>
        <h3>Related lectures</h3>
        <div class="related-list" id="related-list"></div>
      </section>
    </div>
  </section>
</main>
<footer class="video-footer">Electric Machinery Fundamentals · Video Lectures</footer>
{generate_search_modal()}
<script type="application/json" id="video-data">{embedded_data}</script>

<script>{JS_COMMON % {"root_prefix": ""}}</script>
<script>{script}</script>
</body>
</html>
'''

def build():
    ch = load()
    e = html.escape

    os.makedirs(CHAPTER_PAGES_DIR, exist_ok=True)

    search_index = []
    for c in ch:
        for t in c["topics"]:
            search_index.append({
                "chIndex": c["i"],
                "fn": c["fn"],
                "chCode": c["ch_code"],
                "chTitle": c["title"],
                "id": t["id"],
                "num": t["num"],
                "title": t["title"],
                "desc": t["desc"]
            })
    search_index_json = json.dumps(search_index, ensure_ascii=False, separators=(",", ":"))
    with io.open(OUT_SEARCH_INDEX, "w", encoding="utf-8", newline="") as search_index_file:
        search_index_file.write(search_index_json)
    print(f"search-index.json written: {len(search_index_json.encode('utf-8'))/1024:.0f} KB, {len(search_index)} topics")

    # 1. Build each dedicated chapter overview page in chapter-pages/
    for c in ch:
        ch_page_path = os.path.join(CHAPTER_PAGES_DIR, f"chapter{c['i']}.html")
        ch_content = build_chapter_page(c, ch)
        io.open(ch_page_path, "w", encoding="utf-8", newline="").write(ch_content)
        view_path = os.path.join(CHAPTER_PAGES_DIR, f"view{c['i']}.html")
        view_content = build_chapter_view_page(c)
        io.open(view_path, "w", encoding="utf-8", newline="").write(view_content)
    print(f"Generated {len(ch)} chapter overviews and interactive wrappers in chapter-pages/")

    # Preserve old chapters.html links while keeping chapter selection on the homepage.
    legacy_chapters_content = build_legacy_chapters_redirect()
    io.open(OUT_LEGACY_CHAPTERS, "w", encoding="utf-8", newline="").write(legacy_chapters_content)
    print("chapters.html legacy redirect written")

    video_data = load_video_data()
    video_page = build_video_lectures_page(video_data)
    home_video_section = build_home_video_section(video_data)
    io.open(OUT_VIDEO_LECTURES, "w", encoding="utf-8", newline="").write(video_page)
    print(
        f"video-lectures.html written: {len(video_page.encode('utf-8'))/1024:.0f} KB, "
        f"{len(video_data['mapped'])} mapped videos, "
        f"{len(video_data['unresolved'])} unresolved"
    )

    # 3. Modern Chapter Cards on index.html
    cards = "".join(f'''
      <a class="ch-card" href="chapter-pages/chapter{c["i"]}.html">
        <div class="ch-icon-wrap">
          <img src="{c["ch_image"]}" alt="" width="52" height="52" loading="lazy" decoding="async">
        </div>
        <div class="ch-body">
          <span class="ch-code" style="color:{c["ch_color"]}">{e(c["ch_code"])}</span>
          <h3 class="ch-title">{e(c["title"])}</h3>
          <p class="ch-desc">{e(c["ch_short"])}</p>
        </div>
        <div class="ch-arrow" style="color:{c["ch_color"]}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="12" x2="19" y2="12"></line><polyline points="13 6 19 12 13 18"></polyline></svg></div>
      </a>''' for c in ch)

    total_sections = sum(len(c["topics"]) for c in ch)

    # 4. Build index.html
    index_page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Electric Machinery Fundamentals — Interactive Course</title>
<meta name="description" content="Explore the principles, operation and control of electrical machines through interactive simulations, clear explanations and real-world examples. Based on Chapman's Electric Machinery Fundamentals.">
<meta name="theme-color" content="#070e1e">
{generate_favicon_link()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONT_STYLESHEET}
<style>{CSS_INDEX}</style>
</head>
<body>

{generate_header("", active_page="home")}

<!-- Hero Section -->
<section class="hero" id="home">
  <div class="wrap hero-wrap">
    <div class="hero-content">
      <div class="hero-kicker">ELECTRICAL ENGINEERING COURSE</div>
      <h1 class="hero-title">Electric Machinery Fundamentals</h1>
      <p class="hero-lead">Explore the principles, operation and control of electrical machines through interactive simulations, clear explanations and real-world examples.</p>
      <div class="hero-actions">
        <a class="btn-primary" href="#chapters">
          Explore Chapters
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </a>
        <a class="btn-primary btn-secondary" href="https://drive.google.com/file/d/1NZYZV8si5BRyqteX9DAg-fVmUIBETosb/view?usp=sharing" target="_blank" rel="noopener noreferrer" aria-label="Read the Electric Machinery Fundamentals textbook PDF in a new tab">
          <span class="hero-action-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6.5v14"></path><path d="M12 7c-1.4-1.4-3.2-2-5.2-2H5a2 2 0 0 0-2 2v10.5a2 2 0 0 0 2 2h2.5c2 0 3.5.5 4.5 1.5"></path><path d="M12 7c1.4-1.4 3.2-2 5.2-2H19a2 2 0 0 1 2 2v10.5a2 2 0 0 1-2 2h-2.5c-2 0-3.5.5-4.5 1.5"></path></svg></span>
          Read Book
        </a>
        <a class="btn-primary btn-secondary" href="#video-lectures" aria-label="Browse video lectures by chapter and topic">
          <span class="hero-action-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"></rect><polygon points="10 9 15 12 10 15 10 9" fill="currentColor" stroke="none"></polygon></svg></span>
          Video Lectures
        </a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="hero-img-card">
        <img src="assets/motor_hero.webp" alt="Electric Motor Blueprint Illustration" class="motor-img" width="512" height="512" fetchpriority="high" decoding="async">
      </div>
    </div>
  </div>
</section>

<!-- Features & About Section -->
<section class="features-section">
  <div class="wrap">
    <!-- 3 Feature Cards -->
    <div class="feature-cards">
      <div class="feature-card">
        <div class="feature-icon icon-blue">
          <img src="assets/interactive-learning.png" alt="" width="72" height="72" loading="lazy" decoding="async">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        </div>
        <h3>Interactive Learning</h3>
        <p>Simulations, visualizations and hands-on calculations.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon icon-cyan">
          <img src="assets/reference-book-lectures.png" alt="" width="72" height="72" loading="lazy" decoding="async">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        </div>
        <h3>Learning Resources</h3>
        <p>Access reference books, video lectures, and additional materials to support your learning.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon icon-indigo">
          <img src="assets/learn-anytime.png" alt="" width="72" height="72" loading="lazy" decoding="async">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c3 3 9 3 12 0v-5"></path></svg>
        </div>
        <h3>Learn Anytime</h3>
        <p>Access from any device, anywhere in the world.</p>
      </div>
    </div>

    <!-- About Section -->
    <div class="about-section" id="about">
      <div class="about-grid">
        <div class="about-info">
          <h2>About the Course</h2>
          <p>This course provides a comprehensive understanding of electrical machines, including transformers, induction motors, synchronous machines, DC machines and special machines. It is designed for students, engineers and anyone interested in the field of electrical power or machines.</p>
          <a href="#chapters" class="btn-learn-more">
            Learn More
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </a>
        </div>
        <div class="instructor-card">
          <div class="instructor-avatar-wrap">
            <img data-src="assets/instructor_avatar.webp" alt="Prof. Salim Butt" class="instructor-avatar" width="78" height="78" loading="lazy" decoding="async">
          </div>
          <div class="instructor-details">
            <span class="instructor-badge">INSTRUCTOR</span>
            <h4 class="instructor-name">Prof. Salim Butt</h4>
            <p class="instructor-title">Electrical Engineering Department</p>
            <p class="instructor-affil">UET</p>
            <a href="mailto:salimbutt@uet.edu.pk" class="instructor-email">salimbutt@uet.edu.pk</a>
          </div>
        </div>
      </div>

      <div class="wave-decoration" aria-hidden="true">
        <svg viewBox="0 0 1200 60" preserveAspectRatio="none" fill="none">
          <path d="M0,30 C150,55 350,5 500,30 C650,55 850,5 1000,30 C1080,45 1150,20 1200,30" stroke="#93c5fd" stroke-width="2" stroke-dasharray="6 4" opacity="0.6"/>
          <path d="M0,38 C200,60 400,15 600,38 C800,60 1000,15 1200,38" stroke="#38bdf8" stroke-width="1.5" opacity="0.4"/>
        </svg>
      </div>
    </div>
  </div>
</section>

<!-- Choose a Chapter Section on Home -->
<main class="chapters-section" id="chapters">
  <div class="wrap">
    <div class="chapters-header">
      <span class="section-kicker">EXPLORE CHAPTERS</span>
      <h2>Choose a Chapter</h2>
      <p>Select a chapter to view its overview and open an interactive lesson.</p>
    </div>

    <div class="chapter-cards-grid">
      {cards}
    </div>

  </div>
</main>

{home_video_section}

{generate_footer()}
{generate_search_modal()}

<script>
{JS_COMMON % {"root_prefix": ""}}
</script>
</body>
</html>
'''
    io.open(OUT_INDEX, "w", encoding="utf-8", newline="").write(index_page)
    print(f"index.html written: {len(index_page.encode('utf-8'))/1024:.0f} KB, {len(ch)} chapters, {total_sections} topics")

if __name__ == "__main__":
    build()
