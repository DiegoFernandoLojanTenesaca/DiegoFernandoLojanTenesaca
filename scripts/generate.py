#!/usr/bin/env python3
"""Genera el perfil: los SVG (banner, whoami, actividad, radares) en claro y oscuro, y el README.

Desde la raíz del repo:
    pip install -r scripts/requirements.txt
    python scripts/generate.py            # paleta por defecto (DEFAULT_PALETTE)
    python scripts/generate.py mono       # otra: cian, ecuador, mono, rojo, verde, naranja, azul

La actividad sale de GitHub (GITHUB_TOKEN o `gh auth token`) y del calendario público de GitLab.
Sin red, se conservan los SVG de actividad que ya haya.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import subprocess
import sys
import urllib.request
from html import escape
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "assets/source/foto.jpg"
OUT = ROOT / "assets"
TEMPLATE = ROOT / "scripts/README.tpl.md"
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SEED = 2026
DEFAULT_PALETTE = "mono"
GITHUB_USER = "DiegoFernandoLojanTenesaca"
GITLAB_USER = "fernando.lojan10"
MESES = "ene feb mar abr may jun jul ago sep oct nov dic".split()

PALETTES = {
    "cian": {
        "dark": dict(bg="#06100F", panel="#0A1817", panel2="#0D1F1E", line="#1D3836", muted="#7C9A97",
                     text="#E4F2F0", accent="#2DD4BF", accent2="#38BDF8", warm="#FBBF24", hot="#FB7185"),
        "light": dict(bg="#EFF8F7", panel="#FFFFFF", panel2="#E3F2EF", line="#BCDCD7", muted="#5B7A77",
                      text="#0F2A28", accent="#0D9488", accent2="#0284C7", warm="#B45309", hot="#E11D48"),
    },
    "ecuador": {
        "dark": dict(bg="#0B0D12", panel="#11141B", panel2="#151923", line="#2A303D", muted="#8A91A2",
                     text="#F2EEE4", accent="#F5B83D", accent2="#5AA2E8", warm="#EF5350", hot="#7DD3A8"),
        "light": dict(bg="#FBF7EE", panel="#FFFFFF", panel2="#F6EEDC", line="#E6D7B5", muted="#7D7362",
                      text="#24201A", accent="#B7791F", accent2="#1D5FA8", warm="#C62828", hot="#2E7D5B"),
    },
    "mono": {
        "dark": dict(bg="#0A0A0A", panel="#111111", panel2="#161616", line="#2B2B2B", muted="#8C8C8C",
                     text="#F5F5F5", accent="#FFFFFF", accent2="#A3A3A3", warm="#D9D9D9", hot="#737373"),
        "light": dict(bg="#F6F6F6", panel="#FFFFFF", panel2="#EFEFEF", line="#D4D4D4", muted="#6E6E6E",
                      text="#111111", accent="#111111", accent2="#6B6B6B", warm="#3A3A3A", hot="#9A9A9A"),
    },
    "rojo": {
        "dark": dict(bg="#0C0708", panel="#140B0D", panel2="#1A0F12", line="#3A1D23", muted="#A38C90",
                     text="#F7EAEC", accent="#FF3B4E", accent2="#FF8A5B", warm="#FFC857", hot="#E8E8E8"),
        "light": dict(bg="#FBF1F2", panel="#FFFFFF", panel2="#F8E4E6", line="#EBC3C8", muted="#85636A",
                      text="#2A1216", accent="#D7263D", accent2="#E0611F", warm="#B7791F", hot="#4A4A4A"),
    },
    "verde": {
        "dark": dict(bg="#050B07", panel="#09140D", panel2="#0C1A11", line="#1B3524", muted="#7FA38A",
                     text="#E1F5E6", accent="#4ADE80", accent2="#A3E635", warm="#FACC15", hot="#22D3EE"),
        "light": dict(bg="#F0F8F2", panel="#FFFFFF", panel2="#E2F1E6", line="#BFDCC7", muted="#5C7A64",
                      text="#10261A", accent="#15803D", accent2="#4D7C0F", warm="#A16207", hot="#0E7490"),
    },
    "naranja": {
        "dark": dict(bg="#0D0906", panel="#160F0A", panel2="#1C140D", line="#3A2A1D", muted="#A8957F",
                     text="#F8EFE4", accent="#FF8A3D", accent2="#FFD166", warm="#EF476F", hot="#06D6A0"),
        "light": dict(bg="#FCF5EE", panel="#FFFFFF", panel2="#F9EADB", line="#EED3B8", muted="#85705A",
                      text="#2B1D10", accent="#D9620B", accent2="#B7791F", warm="#C81E4E", hot="#047857"),
    },
    "azul": {
        "dark": dict(bg="#060A14", panel="#0B1220", panel2="#0F1828", line="#1F2E48", muted="#8393AE",
                     text="#E6EDF8", accent="#60A5FA", accent2="#22D3EE", warm="#FBBF24", hot="#F472B6"),
        "light": dict(bg="#EFF4FB", panel="#FFFFFF", panel2="#E2EBF8", line="#C2D3EC", muted="#5D6F8C",
                      text="#0F1D33", accent="#1D4ED8", accent2="#0E7490", warm="#B45309", hot="#BE185D"),
    },
}

YAML = [
    (0, "profile", ""),
    (1, "name", "Diego Fernando Lojan Tenesaca"),
    (1, "role", "Data & AI Engineer"),
    (1, "origin", "Ecuador"),
    (1, "degree", "Ing. Ciencias de la Computación · UNL"),
    (1, "research", "Springer Nature · CIT 2026"),
    (0, "stack", ""),
    (1, "ai", "LangGraph · RAG · pgvector · ONNX · Ollama"),
    (1, "data", "Python · SQL · Kafka · DuckDB · dbt"),
    (1, "backend", "FastAPI · PostgreSQL · Redis · Docker"),
    (1, "apps", "Next.js · Svelte · Tauri · Rust · Kotlin"),
    (0, "shipping", ""),
    (1, "xyra", "companion de LoL · PC + Android"),
    (1, "ordo", "Gmail ordenado con IA"),
    (1, "riksi", "visión offline en el navegador"),
    (0, "contact", ""),
    (1, "linkedin", "/in/diego-fernando-lojan"),
    (1, "orcid", "0009-0003-3882-3889"),
]

CLUSTERS = [  # (centro relativo, dispersión, peso, etiqueta)
    ((0.30, 0.28), 0.085, 0.30, "ia"),
    ((0.72, 0.33), 0.075, 0.25, "datos"),
    ((0.32, 0.72), 0.080, 0.25, "backend"),
    ((0.71, 0.73), 0.070, 0.20, "apps"),
]

SKILLS = {"LLMs y agentes": 85, "RAG y vectores": 85, "Datos / ETL": 75, "Machine learning": 75,
          "Backend": 85, "Frontend": 70, "Móvil": 55, "DevOps": 60}
LANGS = {"Python": 92, "TypeScript": 78, "SQL": 80, "Rust": 55, "Kotlin": 45, "Java": 45, "Bash": 55}


def text(x, y, s, fill, size=13, weight=None, anchor=None, extra=""):
    attrs = f' font-weight="{weight}"' if weight else ""
    attrs += f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{MONO}" '
            f'font-size="{size}"{attrs}{extra}>{escape(s)}</text>')


# ---------- retrato ----------

def portrait_fields(size):
    img = cv2.imread(str(PHOTO))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sat = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 1]
    whiteish = ((gray > 222) & (sat < 35)).astype(np.uint8)
    _, lab = cv2.connectedComponents(whiteish, connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[:, 0], lab[:, -1]]))) - {0}
    fg = (~np.isin(lab, list(border))).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    eq = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(gray)
    lum = cv2.resize(eq, size, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    mask = cv2.resize(fg, size, interpolation=cv2.INTER_AREA) > 127
    blur = cv2.GaussianBlur(lum, (0, 0), 1.1)
    edge = np.hypot(cv2.Sobel(blur, cv2.CV_32F, 1, 0), cv2.Sobel(blur, cv2.CV_32F, 0, 1))
    edge = np.clip(edge / np.percentile(edge[mask], 97), 0, 1)
    return lum, edge, mask


def dither(tone):
    t = tone.copy()
    h, w = t.shape
    out = np.zeros_like(t, dtype=bool)
    for y in range(h):
        for x in range(w):
            old = t[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y, x] = new > 0
            err = old - new
            if x + 1 < w:
                t[y, x + 1] += err * 7 / 16
            if y + 1 < h:
                if x > 0:
                    t[y + 1, x - 1] += err * 3 / 16
                t[y + 1, x] += err * 5 / 16
                if x + 1 < w:
                    t[y + 1, x + 1] += err / 16
    return out


def portrait_points(mode, grid, cell, origin):
    lum, edge, mask = portrait_fields(grid)
    if mode == "dark":
        tone = np.clip(0.02 + 0.62 * lum ** 1.9 + 0.55 * edge, 0, 0.72)
    else:
        tone = np.clip(0.02 + 0.42 * (1 - lum) ** 1.6 + 0.5 * edge, 0, 0.6)
    tone[~mask] = 0
    ys, xs = np.nonzero(dither(tone))
    return np.stack([origin[0] + xs * cell, origin[1] + ys * cell], axis=1)


def cluster_targets(n, box, rng):
    x0, y0, w, h = box
    weights = np.array([c[2] for c in CLUSTERS])
    counts = np.floor(weights / weights.sum() * n).astype(int)
    counts[0] += n - counts.sum()
    pts, ids = [], []
    for k, ((cx, cy), sd, _, _) in enumerate(CLUSTERS):
        p = rng.normal([cx * w, cy * h], sd * w, size=(counts[k], 2))
        p[:, 0] = np.clip(p[:, 0], 0.06 * w, 0.94 * w)
        p[:, 1] = np.clip(p[:, 1], 0.06 * h, 0.90 * h)
        pts.append(p + [x0, y0])
        ids += [k] * counts[k]
    return np.concatenate(pts), np.array(ids)


# ---------- banner ----------

def banner(c, mode):
    W, H = 1180, 610
    rng = np.random.default_rng(SEED)
    cluster_colors = [c["accent"], c["accent2"], c["warm"], c["hot"]]

    vis = (48, 124, 392, 414)
    cell, grid = 1.5, (204, 272)
    origin = (vis[0] + (vis[2] - grid[0] * cell) / 2, vis[1] + (vis[3] - grid[1] * cell) / 2)
    pts = portrait_points(mode, grid, cell, origin)

    n_move = min(1400, len(pts))
    movers = pts[rng.choice(len(pts), n_move, replace=False)]
    targets, ids = cluster_targets(n_move, vis, rng)
    r, col = linear_sum_assignment(((movers[:, None, :] - targets[None, :, :]) ** 2).sum(-1))
    delta = targets[col] - movers[r]
    groups = ids[col]

    css = f"""
@keyframes go {{ 0%,30% {{ transform: translate(0,0); animation-timing-function: cubic-bezier(.65,0,.35,1) }}
  40%,68% {{ transform: translate(var(--x),var(--y)); animation-timing-function: cubic-bezier(.65,0,.35,1) }}
  78%,100% {{ transform: translate(0,0) }} }}
@keyframes fade {{ 0%,29% {{ opacity: 1 }} 35%,73% {{ opacity: 0 }} 79%,100% {{ opacity: 1 }} }}
@keyframes show {{ 0%,38% {{ opacity: 0 }} 43%,66% {{ opacity: 1 }} 70%,100% {{ opacity: 0 }} }}
@keyframes blink {{ 0%,49% {{ opacity: 1 }} 50%,100% {{ opacity: 0 }} }}
@keyframes line {{ from {{ opacity: 0; transform: translateX(-6px) }} to {{ opacity: 1; transform: none }} }}
.m circle {{ animation: go 16s calc(var(--d) * 1s) infinite both }}
.static {{ animation: fade 16s infinite }}
.overlay {{ animation: show 16s infinite; opacity: 0 }}
.cursor {{ animation: blink 1.1s steps(1) infinite }}
.ln {{ animation: line .45s ease-out both }}
""" + "".join(
        f"@keyframes k{k} {{ 0%,30% {{ fill: {c['accent']} }} 40%,68% {{ fill: {col_} }} 78%,100% {{ fill: {c['accent']} }} }}\n"
        f".k{k} {{ animation: k{k} 16s infinite }}\n" for k, col_ in enumerate(cluster_colors))

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t d"><title id="t">Diego Fernando Lojan Tenesaca, Data &amp; AI Engineer</title>'
         f'<desc id="d">Retrato hecho de puntos que se agrupa en clusters, junto a un perfil en YAML.</desc>',
         f"<style>{css}</style>",
         f'<rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>',
         f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="13" fill="{c["panel"]}" stroke="{c["line"]}"/>',
         f'<path d="M12 62H{W-12}" stroke="{c["line"]}"/>']
    for i, dot in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        o.append(f'<circle cx="{38 + i * 21}" cy="37" r="6" fill="{dot}"/>')
    o.append(text(W / 2, 42, "nvim ~/profile.yml", c["muted"], 13, anchor="middle"))

    # panel izquierdo
    o.append(f'<rect x="32" y="84" width="424" height="478" rx="7" fill="{c["panel2"]}" stroke="{c["line"]}"/>')
    o.append(f'<path d="M32 112H456" stroke="{c["line"]}"/>')
    o.append(text(48, 103, "EMBEDDING.MAP", c["accent2"], 12, 700, extra=' letter-spacing="1.2"'))
    o.append(text(440, 103, "1-BIT · k=4", c["muted"], 11, anchor="end"))
    corner = 12
    x1, y1, x2, y2 = vis[0], vis[1], vis[0] + vis[2], vis[1] + vis[3]
    o.append(f'<path d="M{x1} {y1+corner}V{y1}H{x1+corner}M{x2-corner} {y1}H{x2}V{y1+corner}'
             f'M{x1} {y2-corner}V{y2}H{x1+corner}M{x2-corner} {y2}H{x2}V{y2-corner}" fill="none" '
             f'stroke="{c["accent"]}" opacity=".5"/>')
    o.append(text(48, 553, f"pts {len(pts)} · proj: t-SNE(diego)", c["muted"], 10))

    d = "".join(f"M{x:.1f} {y:.1f}h1.1" for x, y in pts)
    o.append(f'<path class="static" d="{d}" stroke="{c["accent"]}" stroke-width="1.1" opacity=".9"/>')

    o.append('<g class="m">')
    for k in range(len(CLUSTERS)):
        o.append(f'<g class="k{k}">')
        for (x, y), (dx, dy) in zip(movers[r][groups == k], delta[groups == k]):
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1" style="--x:{dx:.0f}px;--y:{dy:.0f}px;'
                     f'--d:{rng.uniform(0, .5):.2f}"/>')
        o.append("</g>")
    o.append("</g>")

    o.append('<g class="overlay">')
    o.append(f'<path d="M{x1+14} {y1+10}V{y2-30}H{x2-10}" fill="none" stroke="{c["muted"]}" stroke-width=".8" opacity=".6"/>')
    o.append(text(x2 - 12, y2 - 16, "x: datos", c["muted"], 10, anchor="end"))
    o.append(text(x1 + 20, y1 + 20, "y: modelos", c["muted"], 10))
    for k, ((cx, cy), sd, _, label) in enumerate(CLUSTERS):
        lx, ly = x1 + cx * vis[2], y1 + cy * vis[3] - sd * vis[2] * 2.3 - 4
        o.append(text(lx, ly, f"c{k} · {label}", cluster_colors[k], 11, 700, anchor="middle"))
    o.append("</g>")


    # panel derecho: YAML en vim
    px, pw = 472, W - 472 - 32
    o.append(f'<rect x="{px}" y="84" width="{pw}" height="478" rx="7" fill="{c["panel2"]}" stroke="{c["line"]}"/>')
    o.append(f'<path d="M{px} 112H{px+pw}" stroke="{c["line"]}"/>')
    o.append(text(px + 16, 103, "profile.yml", c["text"], 12, 700))
    o.append(text(px + 104, 103, "[YAML]", c["muted"], 11))
    pill = "@DiegoFernandoLojanTenesaca"
    pwid = len(pill) * 7.2 + 24
    o.append(f'<rect x="{px+pw-16-pwid:.1f}" y="89" width="{pwid:.1f}" height="19" rx="9.5" fill="{c["line"]}"/>')
    o.append(text(px + pw - 16 - pwid / 2, 102.5, pill, c["accent"], 11, 700, anchor="middle"))

    lh, top = 22, 138
    for i, (lvl, key, val) in enumerate(YAML):
        y = top + i * lh
        line = [text(px + 30, y, str(i + 1), c["muted"], 11, anchor="end"),
                f'<text x="{px + 46 + lvl * 18}" y="{y}" font-family="{MONO}" font-size="13">'
                f'<tspan fill="{c["accent"] if lvl == 0 else c["accent2"]}" font-weight="{700 if lvl == 0 else 400}">'
                f'{escape(key)}</tspan><tspan fill="{c["muted"]}">:</tspan>'
                + (f'<tspan fill="{c["text"]}"> {escape(val)}</tspan>' if val else "") + "</text>"]
        o.append(f'<g class="ln" style="animation-delay:{0.25 + i * 0.07:.2f}s">{"".join(line)}</g>')
    last_y = top + (len(YAML) - 1) * lh
    last = YAML[-1]
    cur_x = px + 46 + last[0] * 18 + (len(last[1]) + 2 + len(last[2])) * 7.8 + 4
    o.append(f'<rect class="cursor" x="{cur_x:.1f}" y="{last_y - 12}" width="8" height="15" fill="{c["accent"]}" opacity=".85"/>')

    sb = 536
    o.append(f'<path d="M{px} {sb-14}H{px+pw}" stroke="{c["line"]}"/>')
    o.append(f'<rect x="{px+10}" y="{sb-9}" width="62" height="19" rx="3" fill="{c["accent"]}"/>')
    o.append(text(px + 41, sb + 5, "NORMAL", c["bg"], 11, 700, anchor="middle"))
    o.append(text(px + 84, sb + 5, "profile.yml", c["text"], 11, 700))
    o.append(text(px + 190, sb + 5, "[utf-8]", c["muted"], 11))
    o.append(text(px + pw - 14, sb + 5, f"{len(YAML)}L · 100% · {len(YAML)}:1", c["muted"], 11, anchor="end"))
    o.append("</svg>")
    return "\n".join(o)


# ---------- whoami ----------

def terrain_paths(w, h, levels):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w * 0.5, h * 0.55
    rr = np.hypot((xx - cx) / (w * 0.42), (yy - cy) / (h * 0.42))
    z = np.exp(-rr ** 2 * 2.2)
    z += 0.05 * np.sin(xx / 9.0 + yy / 23.0) + 0.04 * np.cos(yy / 7.0 - xx / 31.0)
    z += 0.25 * np.exp(-(((xx - w * 0.2) / (w * 0.16)) ** 2 + ((yy - h * 0.8) / (h * 0.2)) ** 2))
    paths = []
    for lv in levels:
        cs, _ = cv2.findContours((z > lv).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cs:
            if len(cnt) < 8:
                continue
            p = cv2.approxPolyDP(cnt, 0.8, True)[:, 0, :]
            paths.append((lv, "M" + "L".join(f"{a} {b}" for a, b in p) + "Z"))
    return paths


def whoami(c, mode):
    W, H = 960, 390
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t d"><title id="t">whoami: Diego Lojan, Data &amp; AI Engineer</title>'
         f'<desc id="d">Tarjeta de terminal con el perfil de Diego y un mapa topográfico de un volcán.</desc>',
         "<style>@keyframes glow { 0%,100% { opacity: .45 } 50% { opacity: 1 } } .peak { animation: glow 4s ease-in-out infinite }"
         "@keyframes blink { 0%,49% { opacity: 1 } 50%,100% { opacity: 0 } } .cursor { animation: blink 1.1s steps(1) infinite }</style>",
         f'<rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>',
         f'<rect x="9" y="9" width="{W-18}" height="{H-18}" rx="13" fill="{c["panel"]}" stroke="{c["accent"]}" stroke-opacity=".55" stroke-width="1.5"/>']
    for i, dot in enumerate((c["hot"], c["warm"], c["accent"])):
        o.append(f'<circle cx="{35 + i * 19}" cy="35" r="5" fill="{dot}"/>')
    o.append(text(98, 40, "diego@ecuador:~  ·  profile shell  ·  online", c["muted"], 14))
    o.append(f'<path d="M29 58H{W-29}" stroke="{c["line"]}"/>')

    o.append(f'<rect x="29" y="78" width="594" height="271" rx="9" fill="{c["panel2"]}" stroke="{c["line"]}"/>')
    o.append(text(48, 111, "❯ whoami", c["accent"], 19, 700))
    o.append(f'<text x="48" y="144" font-family="{MONO}" font-size="17"><tspan fill="{c["text"]}">diego_lojan</tspan>'
             f'<tspan fill="{c["muted"]}">   ·   </tspan><tspan fill="{c["warm"]}">Data &amp; AI Engineer</tspan></text>')
    o.append(f'<path d="M48 164H604" stroke="{c["line"]}"/>')
    rows = [("origin:", "Ecuador", c["accent2"]),
            ("mission:", "llevar modelos de IA a producción y mantenerlos ahí", c["accent"])]
    for i, (k, v, col_) in enumerate(rows):
        o.append(text(48, 193 + i * 27, k, c["muted"], 14))
        o.append(text(160, 193 + i * 27, v, col_, 14))
    o.append(text(48, 262, "❯ ls expertise/", c["accent"], 17, 700))
    exp = [("ai-engineering/", "LLMs · RAG · agentes · MCP"),
           ("data-science/", "ML · NLP · series temporales"),
           ("full-stack/", "FastAPI · Next.js · Tauri")]
    for i, (k, v) in enumerate(exp):
        o.append(text(48, 290 + i * 22, k, c["hot"], 13))
        o.append(text(214, 290 + i * 22, v, c["text"], 13))
    o.append(f'<rect class="cursor" x="420" y="{290 + 2 * 22 - 12}" width="8" height="15" fill="{c["accent"]}"/>')

    bx, by, bw, bh = 651, 78, 280, 271
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9" fill="{c["panel2"]}" stroke="{c["line"]}"/>')
    o.append(text(bx + 22, by + 33, "andes.map", c["warm"], 15, 700))
    o.append(text(bx + bw - 20, by + 33, "curvas c/100 m", c["muted"], 10, anchor="end"))
    tw, th = 236, 170
    levels = [0.18, 0.28, 0.38, 0.48, 0.58, 0.68, 0.78, 0.88]
    ramp = [c["accent2"], c["accent2"], c["accent"], c["accent"], c["accent"], c["warm"], c["warm"], c["text"]]
    o.append(f'<g transform="translate({bx + 22} {by + 48})" fill="none" stroke-width="1.2" stroke-linejoin="round">')
    for lv, d in terrain_paths(tw, th, levels):
        i = levels.index(lv)
        cls = ' class="peak"' if i >= 6 else ""
        o.append(f'<path{cls} d="{d}" stroke="{ramp[i]}" opacity="{0.45 + i * 0.07:.2f}"/>')
    o.append("</g>")
    o.append(f'<circle class="peak" cx="{bx + 22 + tw * 0.5}" cy="{by + 48 + th * 0.55}" r="2.5" fill="{c["hot"]}"/>')
    o.append(text(bx + 22, by + bh - 18, "status: siempre construyendo", c["muted"], 12))
    o.append("</svg>")
    return "\n".join(o)


# ---------- radares ----------

def radar(c, data, title, footer):
    W, H, cx, cy, R = 460, 380, 230, 200, 118
    keys, vals = list(data), list(data.values())
    n = len(keys)
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    pt = lambda a, r: (cx + r * math.cos(a), cy + r * math.sin(a))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{escape(title)}">',
         "<style>@keyframes grow { from { transform: scale(.55) } to { transform: none } }"
         f" .shape {{ transform-origin: {cx}px {cy}px; animation: grow 1.2s cubic-bezier(.2,.8,.2,1) both }}</style>",
         f'<rect width="{W}" height="{H}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>',
         text(20, 30, title, c["accent"], 13, 700),
         text(W - 20, 30, footer, c["muted"], 10, anchor="end")]
    for ring in (0.25, 0.5, 0.75, 1.0):
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(a, R * ring) for a in ang))
        o.append(f'<polygon points="{poly}" fill="none" stroke="{c["line"]}"/>')
    for a, k in zip(ang, keys):
        x, y = pt(a, R)
        o.append(f'<path d="M{cx} {cy}L{x:.1f} {y:.1f}" stroke="{c["line"]}"/>')
        lx, ly = pt(a, R + 22)
        anchor = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        o.append(text(lx, ly + 4, k, c["text"], 11, anchor=anchor))
    shape = [pt(a, R * v / 100) for a, v in zip(ang, vals)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in shape)
    o.append(f'<g class="shape"><polygon points="{poly}" fill="{c["accent"]}" fill-opacity=".22" '
             f'stroke="{c["accent"]}" stroke-width="2" stroke-linejoin="round"/>')
    o += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{c["warm"]}"/>' for x, y in shape]
    o.append("</g></svg>")
    return "\n".join(o)


# ---------- actividad: datos ----------

def github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch_json(url, payload=None, token=None):
    headers = {"User-Agent": GITHUB_USER, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as r:
        return json.load(r)


def gql(token, query, **variables):
    out = fetch_json("https://api.github.com/graphql", {"query": query, "variables": variables}, token)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]


def fetch_activity():
    token = github_token()
    user = gql(token, """query($u: String!) { user(login: $u) { id contributionsCollection {
        totalCommitContributions totalRepositoriesWithContributedCommits
        contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }""",
               u=GITHUB_USER)["user"]
    col = user["contributionsCollection"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]]
             for w in col["contributionCalendar"]["weeks"]]
    try:
        gitlab = fetch_json(f"https://gitlab.com/users/{GITLAB_USER}/calendar.json")
    except OSError:
        gitlab = {}

    repos = gql(token, """query($u: String!, $id: ID!) { user(login: $u) { repositories(ownerAffiliations: OWNER,
        isFork: false, privacy: PUBLIC, first: 8, orderBy: {field: PUSHED_AT, direction: DESC}) { nodes { name
        defaultBranchRef { target { ... on Commit { history(first: 5, author: {id: $id}) { nodes {
        abbreviatedOid messageHeadline committedDate } } } } } } } } }""", u=GITHUB_USER, id=user["id"])
    commits = []
    for repo in repos["user"]["repositories"]["nodes"]:
        ref = repo["defaultBranchRef"]
        for c in (ref["target"]["history"]["nodes"] if ref else []):
            commits.append((c["committedDate"], repo["name"], c["abbreviatedOid"], c["messageHeadline"]))
    commits.sort(reverse=True)

    return dict(
        weeks=[[(d, gh, int(gitlab.get(d, 0))) for d, gh in w] for w in weeks],
        gh_commits=col["totalCommitContributions"],
        repos=col["totalRepositoriesWithContributedCommits"],
        commits=commits[:8],
        today=dt.date.today().isoformat(),
    )


def activity_summary(a):
    days = [(d, gh, gl) for w in a["weeks"] for d, gh, gl in w]
    totals = [gh + gl for _, gh, gl in days]
    streak = best = 0
    for t in totals:
        streak = streak + 1 if t else 0
        best = max(best, streak)
    months = {}
    for d, gh, gl in days:
        m = months.setdefault(d[:7], [0, 0])
        m[0] += gh
        m[1] += gl
    top = max(months, key=lambda k: sum(months[k]))
    return dict(total=sum(totals), gh=sum(gh for _, gh, _ in days), gl=sum(gl for _, _, gl in days),
                active=sum(1 for t in totals if t), streak=best, months=months, top=top)


def mes(ym):
    y, m = ym.split("-")
    return f"{MESES[int(m) - 1]} {y}"


# ---------- actividad: SVG ----------

def frame(c, W, H, title, right=""):
    return [f'<rect width="{W}" height="{H}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>',
            text(20, 30, title, c["accent"], 13, 700),
            text(W - 20, 30, right, c["muted"], 10, anchor="end") if right else ""]


def heatmap(c, a, s):
    W, H, cell, gap, gx, gy = 960, 250, 13, 3, 62, 82
    step = cell + gap
    nz = sorted(gh + gl for w in a["weeks"] for _, gh, gl in w if gh + gl)
    cuts = [nz[int(len(nz) * q)] for q in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]
    gw = len(a["weeks"]) * step
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Contribuciones del último año en GitHub y GitLab: {s["total"]}">',
         "<defs><linearGradient id='scan' x1='0' x2='1'><stop offset='0' stop-color='" + c["accent"] +
         "' stop-opacity='0'/><stop offset='1' stop-color='" + c["accent"] + "' stop-opacity='.35'/></linearGradient></defs>",
         "<style>@keyframes pop { from { opacity: .25 } to { opacity: 1 } } .col { animation: pop .5s ease-out both }"
         f"@keyframes scan {{ 0% {{ transform: translateX(0) }} 100% {{ transform: translateX({gw}px) }} }}"
         " .scan { animation: scan 7s linear infinite }</style>"]
    o += frame(c, W, H, 'git log --since="1 year" --all',
               f'{s["total"]} contribuciones · {s["active"]} días activos · racha máx. {s["streak"]} días')
    for row, label in ((1, "lun"), (3, "mié"), (5, "vie")):
        o.append(text(gx - 10, gy + row * step + 10, label, c["muted"], 10, anchor="end"))
    last_month, last_col = None, -9
    for i, week in enumerate(a["weeks"]):
        m = week[-1][0][5:7]
        if m != last_month:
            if i - last_col >= 3 and i < len(a["weeks"]) - 2:
                o.append(text(gx + i * step, gy - 10, MESES[int(m) - 1], c["muted"], 10))
                last_col = i
            last_month = m
        o.append(f'<g class="col" style="animation-delay:{i * 0.025:.3f}s">')
        for d, gh, gl in week:
            row = (dt.date.fromisoformat(d).weekday() + 1) % 7
            total = gh + gl
            x, y = gx + i * step, gy + row * step
            if total == 0:
                o.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{c["line"]}"/>')
                continue
            level = sum(total > t for t in cuts)
            color = c["accent"] if gh >= gl else c["accent2"]
            o.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{color}" '
                     f'fill-opacity="{(0.35, 0.55, 0.78, 1)[level]}"><title>{d}: {gh} GitHub, {gl} GitLab</title></rect>')
        o.append("</g>")
    o.append(f'<rect class="scan" x="{gx - 60}" y="{gy - 4}" width="60" height="{7 * step + 4}" fill="url(#scan)"/>')
    ly = gy + 7 * step + 26
    o.append(f'<rect x="{gx}" y="{ly - 10}" width="11" height="11" rx="2" fill="{c["accent"]}"/>')
    o.append(text(gx + 17, ly, f'GitHub {s["gh"]}', c["text"], 11))
    o.append(f'<rect x="{gx + 120}" y="{ly - 10}" width="11" height="11" rx="2" fill="{c["accent2"]}"/>')
    o.append(text(gx + 137, ly, f'GitLab {s["gl"]}', c["text"], 11))
    lx = gx + gw - 5 * 15 - 40
    o.append(text(lx - 8, ly, "menos", c["muted"], 10, anchor="end"))
    for k, op in enumerate((None, 0.35, 0.55, 0.78, 1)):
        fill = f'fill="{c["line"]}"' if op is None else f'fill="{c["accent"]}" fill-opacity="{op}"'
        o.append(f'<rect x="{lx + k * 15}" y="{ly - 10}" width="11" height="11" rx="2" {fill}/>')
    o.append(text(lx + 5 * 15 + 4, ly, "más", c["muted"], 10))
    o.append("</svg>")
    return "\n".join(o)


def monthly(c, s):
    W, H, x0, x1, y0, y1 = 470, 300, 46, 450, 64, 244
    keys = sorted(s["months"])[-12:]
    peak = max(sum(s["months"][k]) for k in keys) or 1
    bw = (x1 - x0) / len(keys)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Contribuciones por mes">',
         "<style>@keyframes grow { from { transform: scaleY(.3) } to { transform: none } }"
         " .bar { transform-box: fill-box; transform-origin: bottom; animation: grow .9s cubic-bezier(.2,.8,.2,1) both }</style>"]
    o += frame(c, W, H, "commits.por_mes", "GitHub + GitLab")
    for f in (0.5, 1.0):
        y = y1 - (y1 - y0) * f
        o.append(f'<path d="M{x0} {y:.1f}H{x1}" stroke="{c["line"]}" stroke-dasharray="3 4"/>')
        o.append(text(x0 - 6, y + 4, str(round(peak * f)), c["muted"], 9, anchor="end"))
    o.append(f'<path d="M{x0} {y1}H{x1}" stroke="{c["line"]}"/>')
    for i, k in enumerate(keys):
        gh, gl = s["months"][k]
        x = x0 + i * bw + bw * 0.2
        w = bw * 0.6
        h_gl = (y1 - y0) * gl / peak
        h_gh = (y1 - y0) * gh / peak
        delay = f'style="animation-delay:{i * 0.05:.2f}s"'
        o.append(f'<g class="bar" {delay}>')
        if gl:
            o.append(f'<rect x="{x:.1f}" y="{y1 - h_gl:.1f}" width="{w:.1f}" height="{h_gl:.1f}" rx="2" fill="{c["accent2"]}"/>')
        if gh:
            o.append(f'<rect x="{x:.1f}" y="{y1 - h_gl - h_gh:.1f}" width="{w:.1f}" height="{h_gh:.1f}" rx="2" fill="{c["accent"]}"/>')
        o.append("</g>")
        if gh + gl:
            o.append(text(x + w / 2, y1 - h_gl - h_gh - 6, str(gh + gl), c["text"], 9, anchor="middle"))
        o.append(text(x + w / 2, y1 + 16, MESES[int(k[5:]) - 1], c["muted"], 10, anchor="middle"))
    o.append("</svg>")
    return "\n".join(o)


def stats_card(c, a, s):
    W, H = 470, 300
    gh, gl = s["months"][s["top"]]
    cells = [(s["total"], "contribuciones · último año", c["accent"]),
             (s["active"], "días con actividad", c["accent2"]),
             (f'{s["streak"]} d', "racha más larga", c["warm"]),
             (a["gh_commits"], "commits en GitHub", c["accent"]),
             (a["repos"], "repos con commits", c["accent2"]),
             (gh + gl, f'{mes(s["top"])} · mes más activo', c["hot"])]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Resumen de actividad">',
         "<style>@keyframes up { from { opacity: .3; transform: translateY(6px) } to { opacity: 1; transform: none } }"
         " .n { animation: up .6s ease-out both }</style>"]
    o += frame(c, W, H, "git shortlog --summary", f'actualizado {a["today"]}')
    for i, (value, label, color) in enumerate(cells):
        x = 24 + (i % 2) * 222
        y = 92 + (i // 2) * 70
        o.append(f'<g class="n" style="animation-delay:{i * 0.08:.2f}s">')
        o.append(text(x, y, str(value), color, 30, 700))
        o.append(text(x, y + 20, label, c["muted"], 11))
        o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


def git_log(c, a):
    rows = a["commits"]
    W, H, lh = 960, 74 + len(rows) * 24 + 16, 24
    kinds = {"feat": c["accent"], "fix": c["hot"], "docs": c["accent2"], "chore": c["muted"],
             "refactor": c["warm"], "perf": c["warm"], "test": c["accent2"], "style": c["muted"]}
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Últimos commits públicos">',
         "<style>@keyframes in { from { opacity: .25 } to { opacity: 1 } } .l { animation: in .4s ease-out both }"
         "@keyframes blink { 0%,49% { opacity: 1 } 50%,100% { opacity: 0 } } .cursor { animation: blink 1.1s steps(1) infinite }</style>"]
    o += frame(c, W, H, "git log --all --oneline --author=diego -8", "últimos commits públicos")
    for i, (date, repo, sha, msg) in enumerate(rows):
        y = 66 + i * lh
        head, sep, rest = msg.partition(":")
        kind = head.split("(")[0].strip().lower()
        msg = msg if len(msg) <= 68 else msg[:67] + "…"
        if sep and kind in kinds:
            head, _, rest = msg.partition(":")
            body = (f'<tspan fill="{kinds[kind]}" font-weight="700">{escape(head)}:</tspan>'
                    f'<tspan fill="{c["text"]}">{escape(rest)}</tspan>')
        else:
            body = f'<tspan fill="{c["text"]}">{escape(msg)}</tspan>'
        o.append(f'<g class="l" style="animation-delay:{0.2 + i * 0.09:.2f}s">')
        o.append(text(24, y, sha, c["warm"], 13))
        label = "perfil" if repo == GITHUB_USER else (repo if len(repo) <= 18 else repo[:17] + "…")
        o.append(text(96, y, f"({label})", c["accent2"], 13))
        o.append(f'<text x="268" y="{y}" font-family="{MONO}" font-size="13">{body}</text>')
        o.append(text(W - 24, y, date[:10], c["muted"], 12, anchor="end"))
        o.append("</g>")
    yc = 66 + len(rows) * lh
    o.append(text(24, yc, "❯", c["accent"], 13, 700))
    o.append(f'<rect class="cursor" x="40" y="{yc - 12}" width="8" height="15" fill="{c["accent"]}"/>')
    o.append("</svg>")
    return "\n".join(o)


# ---------- trayectoria ----------

CAREER = [  # (carril, fecha, tipo, mensaje), de lo más nuevo a lo más viejo. 0 trabajo, 1 proyectos, 2 formación
    (0, "ahora", "HEAD", "Data & AI Engineer · Ecuador"),
    (1, "sep 2026", "feat", "Ordo: Gmail ordenado con IA"),
    (1, "sep 2026", "release", "Xyra 1.2.0 · PC + Android"),
    (1, "ago 2026", "feat", "Riksi: visión offline en el navegador"),
    (2, "ago 2026", "learn", "Escuela de Cómputo Cuántico · UNAM"),
    (0, "jul 2026", "work", "cofundador de Xynitra Devs"),
    (1, "jun 2026", "feat", "Cuadrekit para micronegocios del Ecuador"),
    (1, "may 2026", "feat", "AgentOS: un Android sin Google como agente de IA"),
    (1, "may 2026", "feat", "Wauto Indaga: CRM y mensajería con IA"),
    (2, "2026", "paper", "aceptado en Springer Nature · CIT 2026"),
    (1, "abr 2026", "feat", "anomalías energéticas en 8 países"),
    (0, "feb 2026", "work", "Data & AI en Dataglov"),
    (2, "2025", "learn", "Cisco: ciberseguridad y redes · UTP"),
    (0, "oct 2025", "work", "full stack en Serviestudios"),
    (0, "2025", "init", "Indaga Lab"),
    (0, "2024", "work", "freelance: software e IA"),
    (0, "", "init", "Ing. Ciencias de la Computación · UNL"),
]


def timeline(c):
    import hashlib
    rh, top = 28, 74
    W, H = 960, top + len(CAREER) * rh
    lanes = [36, 60, 84]
    lane_color = [c["accent"], c["accent2"], c["hot"]]
    kinds = {"HEAD": c["accent"], "work": c["accent"], "feat": c["accent2"], "release": c["warm"],
             "learn": c["hot"], "paper": c["warm"], "init": c["muted"]}
    y = [top + i * rh - 4 for i in range(len(CAREER))]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Trayectoria de Diego como un git log --graph">',
         "<style>@keyframes in { from { opacity: .25; transform: translateX(-4px) } to { opacity: 1; transform: none } }"
         " .r { animation: in .45s ease-out both }"
         "@keyframes pulse { 0%,100% { r: 7 } 50% { r: 10 } } .head { animation: pulse 2.4s ease-in-out infinite }</style>"]
    o += frame(c, W, H, "git log --graph --oneline trayectoria")
    lx = W - 20
    for name, color in reversed(list(zip(("main", "proyectos", "formación"), lane_color))):
        o.append(text(lx, 30, name, c["muted"], 10, anchor="end"))
        lx -= len(name) * 6.2 + 8
        o.append(f'<circle cx="{lx}" cy="26.5" r="4" fill="{color}"/>')
        lx -= 16

    def branch(lane):
        rows = [i for i, row in enumerate(CAREER) if row[0] == lane]
        lo, hi = max(rows), min(rows)
        x0, x1, k = lanes[0], lanes[lane], rh * 0.55
        return (f'M{x0} {y[lo + 1]}C{x0} {y[lo + 1] - k} {x1} {y[lo] + k} {x1} {y[lo]}'
                f'V{y[1]}C{x1} {y[1] - k} {x0} {y[0] + k} {x0} {y[0]}')

    o.append(f'<path d="M{lanes[0]} {y[-1]}V{y[0]}" stroke="{lane_color[0]}" stroke-width="2" fill="none"/>')
    for lane in (1, 2):
        o.append(f'<path d="{branch(lane)}" stroke="{lane_color[lane]}" stroke-width="2" fill="none"/>')

    for i, (lane, date, kind, msg) in enumerate(CAREER):
        cx = lanes[lane]
        sha = hashlib.sha1(msg.encode()).hexdigest()[:7]
        o.append(f'<g class="r" style="animation-delay:{0.15 + i * 0.06:.2f}s">')
        if kind == "HEAD":
            o.append(f'<circle class="head" cx="{cx}" cy="{y[i]}" r="7" fill="none" stroke="{c["accent"]}" stroke-width="1.5"/>')
        o.append(f'<circle cx="{cx}" cy="{y[i]}" r="4.5" fill="{lane_color[lane]}" stroke="{c["panel"]}" stroke-width="2"/>')
        o.append(text(112, y[i] + 4.5, sha, c["warm"], 13))
        if kind == "HEAD":
            body = (f'<tspan fill="{c["accent"]}" font-weight="700">(HEAD -&gt; main)</tspan>'
                    f'<tspan fill="{c["text"]}"> {escape(msg)}</tspan>')
        else:
            body = (f'<tspan fill="{kinds[kind]}" font-weight="700">{kind}:</tspan>'
                    f'<tspan fill="{c["text"]}"> {escape(msg)}</tspan>')
        o.append(f'<text x="182" y="{y[i] + 4.5}" font-family="{MONO}" font-size="13">{body}</text>')
        o.append(text(W - 24, y[i] + 4.5, date, c["muted"], 12, anchor="end"))
        o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


# ---------- README ----------

def render_readme(pal):
    out = TEMPLATE.read_text(encoding="utf-8")
    for key, value in pal["light"].items():
        out = out.replace("{{light_" + key + "}}", value.lstrip("#"))
    for key, value in pal["dark"].items():
        out = out.replace("{{" + key + "}}", value.lstrip("#"))
    (ROOT / "README.md").write_text(out, encoding="utf-8")


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PALETTE
    pal = PALETTES[name]
    try:
        act = fetch_activity()
        summary = activity_summary(act)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        act = None
        print(f"sin datos de actividad ({e}); se dejan los SVG que había")
    for mode, c in pal.items():
        (OUT / f"banner-{mode}.svg").write_text(banner(c, mode), encoding="utf-8")
        (OUT / f"whoami-{mode}.svg").write_text(whoami(c, mode), encoding="utf-8")
        (OUT / f"timeline-{mode}.svg").write_text(timeline(c), encoding="utf-8")
        (OUT / f"radar-skills-{mode}.svg").write_text(
            radar(c, SKILLS, "skills.radar", "autoevaluación · 0-100"), encoding="utf-8")
        (OUT / f"radar-langs-{mode}.svg").write_text(
            radar(c, LANGS, "langs.radar", "uso real · 0-100"), encoding="utf-8")
        if act:
            (OUT / f"activity-{mode}.svg").write_text(heatmap(c, act, summary), encoding="utf-8")
            (OUT / f"monthly-{mode}.svg").write_text(monthly(c, summary), encoding="utf-8")
            (OUT / f"stats-{mode}.svg").write_text(stats_card(c, act, summary), encoding="utf-8")
            (OUT / f"gitlog-{mode}.svg").write_text(git_log(c, act), encoding="utf-8")
    render_readme(pal)
    print(f"paleta {name}: listo en {OUT}")


if __name__ == "__main__":
    main()
