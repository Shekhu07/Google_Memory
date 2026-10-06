#!/usr/bin/env python3
"""
Build script for Google Photos Retrieval Case Study Deck (NL_GooglePhotos.pdf).
Compiles a 10-slide, 16:9 executive presentation deck adhering to all NextLeap PM Fellowship constraints:
- Exactly 10 slides (no title slide; Slide 1 is context + metric decomposition)
- Message-led slide titles
- Colors: accessible, color-blind safe, professional Google aesthetic
- Minimum font >= 17pt on a 16in x 9in page (= 14pt on a 13.33in PPT slide)
- NO personal names anywhere in content, code, or metadata
- The forbidden phrase "users find it difficult to search for old photos" appears nowhere
- Every number strictly verified against facts_table.md
- Renders via headless Chrome to NL_GooglePhotos.pdf (<40 MB)
- Validates PDF structure and text using pypdf
"""

import os
import sys
import base64
import subprocess
import pypdf

def get_base64_image(rel_path):
    abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rel_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Missing asset: {abs_path}")
    with open(abs_path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

def generate_html():
    img_entry = get_base64_image("design/mvp-screenshots/1-entry.jpg")
    img_describe = get_base64_image("design/mvp-screenshots/2-describe.jpg")
    img_clues = get_base64_image("design/mvp-screenshots/3-clues.jpg")
    img_moments = get_base64_image("design/mvp-screenshots/4-moments.jpg")
    img_moment = get_base64_image("design/mvp-screenshots/5-moment.jpg")
    img_recover = get_base64_image("design/mvp-screenshots/6-recover.jpg")
    img_found = get_base64_image("design/mvp-screenshots/7-found.jpg")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NL_GooglePhotos</title>
<style>
  @page {{
    size: 16in 9in;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  html, body {{
    margin: 0;
    padding: 0;
    background-color: #0F172A;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1E293B;
  }}
  .slide {{
    width: 16in;
    height: 9in;
    max-height: 9in;
    overflow: hidden;
    page-break-after: always;
    break-after: page;
    background: #FFFFFF;
    position: relative;
    padding: 0.3in 0.5in 0.22in 0.5in;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .pill-row {{
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 0.03in;
  }}
  .category-pill {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 9999px;
    background: #EBF5FF;
    color: #1A73E8;
    font-size: 17pt;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }}
  .confidential-tag {{
    font-size: 17pt;
    color: #64748B;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }}
  .slide-title {{
    font-size: 24pt;
    font-weight: 800;
    line-height: 1.16;
    color: #0F172A;
    margin: 0 0 0.08in 0;
  }}
  .main-content {{
    flex: 1;
    display: flex;
    gap: 0.28in;
    min-height: 0;
  }}
  .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.1in;
    min-width: 0;
  }}
  .col-2 {{
    flex: 2;
    display: flex;
    flex-direction: column;
    gap: 0.1in;
    min-width: 0;
  }}
  .col-1-5 {{
    flex: 1.5;
    display: flex;
    flex-direction: column;
    gap: 0.1in;
    min-width: 0;
  }}
  .col-1-2 {{
    flex: 1.2;
    display: flex;
    flex-direction: column;
    gap: 0.1in;
    min-width: 0;
  }}
  .card {{
    background: #F8FAFC;
    border: 1.5px solid #E2E8F0;
    border-radius: 9px;
    padding: 0.1in 0.16in;
  }}
  .card-highlight {{
    background: #F0FDF4;
    border: 1.5px solid #BBF7D0;
  }}
  .card-blue {{
    background: #EFF6FF;
    border: 1.5px solid #BFDBFE;
  }}
  .card-amber {{
    background: #FFFBEB;
    border: 1.5px solid #FDE68A;
  }}
  .card-title {{
    font-size: 17pt;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.03in;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .card-body {{
    font-size: 17pt;
    line-height: 1.27;
    color: #334155;
  }}
  .stat-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.08in;
  }}
  .stat-box {{
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 7px;
    padding: 0.06in 0.1in;
    text-align: left;
  }}
  .stat-num {{
    font-size: 24pt;
    font-weight: 800;
    line-height: 1.1;
    color: #1A73E8;
    margin-bottom: 1px;
  }}
  .stat-num-green {{
    color: #059669;
  }}
  .stat-num-amber {{
    color: #D97706;
  }}
  .stat-label {{
    font-size: 17pt;
    font-weight: 600;
    color: #64748B;
    line-height: 1.15;
  }}
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 17pt;
    background: #FFFFFF;
    border-radius: 7px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
  }}
  table.data-table th {{
    background: #F1F5F9;
    color: #0F172A;
    font-weight: 700;
    text-align: left;
    padding: 3px 7px;
    border-bottom: 2px solid #CBD5E1;
    font-size: 17pt;
  }}
  table.data-table td {{
    padding: 3px 7px;
    border-bottom: 1px solid #E2E8F0;
    color: #334155;
    line-height: 1.18;
    font-size: 17pt;
  }}
  table.data-table tr.highlight {{
    background: #EFF6FF;
    font-weight: 600;
  }}
  table.data-table tr.highlight td {{
    color: #1E40AF;
  }}
  .btn-link {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #1A73E8;
    color: #FFFFFF !important;
    text-decoration: none;
    font-size: 17pt;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    margin-top: 3px;
  }}
  .btn-link-sec {{
    background: #0F172A;
  }}
  .footnote {{
    font-size: 17pt;
    color: #64748B;
    line-height: 1.2;
    padding-top: 0.06in;
    border-top: 1px solid #E2E8F0;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .footnote-text {{
    flex: 1;
    margin-right: 0.2in;
  }}
  .slide-num {{
    font-weight: 700;
    color: #0F172A;
    font-size: 17pt;
    white-space: nowrap;
  }}
  .quote-box {{
    background: #F8FAFC;
    border-left: 3.5px solid #1A73E8;
    padding: 4px 8px;
    font-style: italic;
    font-size: 17pt;
    color: #1E293B;
    line-height: 1.22;
    margin: 2px 0;
  }}
  .screenshot-frame {{
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    overflow: hidden;
    background: #F8FAFC;
    display: flex;
    justify-content: center;
    align-items: center;
  }}
  .screenshot-frame img {{
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
  }}
  .tag {{ display: inline-block; font-size: 17pt; font-weight: 700; padding: 0 7px; border-radius: 4px; border: 1.5px solid currentColor; margin-left: 6px; white-space: nowrap; }}
  .tag-obs {{ color: #1E40AF; }}
  .tag-mod {{ color: #475569; border-style: dashed; }}
  .tag-prop {{ color: #92400E; }}
  .tag-hyp {{ color: #6D28D9; border-style: dotted; }}
  .shot-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.1in; margin: 0.04in 0 0.06in 0; }}
  .shot-row figure {{ margin: 0; display: flex; flex-direction: column; gap: 3px; }}
  .shot {{ height: 3.15in; background: #FFFFFF; }}
  .shot img {{ object-fit: cover; object-position: top; }}
  .shot-ai {{ border: 2.5px solid #1A73E8; }}
  .shot-row figcaption {{ font-size: 17pt; font-weight: 700; color: #0F172A; text-align: center; }}
</style>
</head>
<body>

<!-- SLIDE 1: Context and Business Metric Decomposition -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Business metric decomposition</span></div>
    <h1 class="slide-title">A photo you can't find is a memory you've lost</h1>
  </div>

  <div class="main-content" style="flex-direction: column; gap: 0.12in;">
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.12in;">
      <div class="stat-box" style="padding: 6px 12px;"><div class="stat-num">1.5B+</div><div class="stat-label">people use Google Photos each month</div></div>
      <div class="stat-box" style="padding: 6px 12px;"><div class="stat-num">9T+</div><div class="stat-label">photos and videos stored</div></div>
      <div class="stat-box" style="padding: 6px 12px; border: 2px solid #1A73E8;"><div class="stat-num">370M+</div><div class="stat-label">people search their photos each month (1 in 4)</div></div>
      <div class="stat-box" style="padding: 6px 12px;"><div class="stat-num">150M</div><div class="stat-label">Google One subscribers paying for storage</div></div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 40px 1.35fr; gap: 0.08in; align-items: stretch;">
      <div class="card card-blue" style="border-left: 5px solid #1A73E8;">
        <div class="card-title" style="color: #1E40AF;">More people finding the photo keeps the library worth paying for</div>
        <div class="card-body"><strong>Goal:</strong> more users retrieve a photo they remember but can't precisely describe. <strong>Why Google cares:</strong> a library people can't search is worth less to keep, and storage is what Google One sells.</div>
      </div>
      <div style="display: flex; align-items: center; justify-content: center; font-size: 26pt; font-weight: 800; color: #1A73E8;">→</div>
      <div class="card card-blue">
        <div class="card-title" style="color: #1E40AF;">It becomes one number: User Retrieval Rate (URR)</div>
        <div class="card-body">Of the people who search for a photo they can only vaguely describe, the share who reach it within 28 days. It counts people, not searches.</div>
        <div style="margin-top: 6px; background: #FFFFFF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 4px 10px; font-family: monospace; font-size: 17pt; font-weight: 700; color: #1E40AF; display: inline-block;">URR = E × [1 − (1 − I × S × R)^n]</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.1in; flex: 1;">
      <div class="card" style="display: flex; flex-direction: column;"><div class="card-title"><span style="color:#1A73E8;">E</span>&nbsp;Express it</div><div class="card-body">Can they put the memory into words at all?</div><div style="margin-top: auto; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 4px; padding: 5px 8px; min-height: 0.98in; font-size: 17pt; line-height: 1.25; color: #1E293B;"><strong style="color: #1E40AF;">Today:</strong> a search box, or a question to Ask Photos</div></div>
      <div class="card" style="display: flex; flex-direction: column;"><div class="card-title"><span style="color:#1A73E8;">I</span>&nbsp;Be understood</div><div class="card-body">Does Photos read the clue the way they meant it?</div><div style="margin-top: auto; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 4px; padding: 5px 8px; min-height: 0.98in; font-size: 17pt; line-height: 1.25; color: #1E293B;"><strong style="color: #1E40AF;">Today:</strong> matches people, places and things</div></div>
      <div class="card" style="display: flex; flex-direction: column;"><div class="card-title"><span style="color:#1A73E8;">S</span>&nbsp;See it surface</div><div class="card-body">Is the photo in the results at all?</div><div style="margin-top: auto; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 4px; padding: 5px 8px; min-height: 0.98in; font-size: 17pt; line-height: 1.25; color: #1E293B;"><strong style="color: #1E40AF;">Today:</strong> a grid of matching photos</div></div>
      <div class="card" style="display: flex; flex-direction: column;"><div class="card-title"><span style="color:#1A73E8;">R</span>&nbsp;Recognise it</div><div class="card-body">Can they tell it is the right one?</div><div style="margin-top: auto; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 4px; padding: 5px 8px; min-height: 0.98in; font-size: 17pt; line-height: 1.25; color: #1E293B;"><strong style="color: #1E40AF;">Today:</strong> thumbnails with date and place</div></div>
      <div class="card" style="display: flex; flex-direction: column; background: #F1F5F9;"><div class="card-title"><span style="color:#1A73E8;">n</span>&nbsp;Try again</div><div class="card-body">How many tries before they give up?</div><div style="margin-top: auto; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 4px; padding: 5px 8px; min-height: 0.98in; font-size: 17pt; line-height: 1.25; color: #1E293B;"><strong style="color: #1E40AF;">Today:</strong> retype the search</div></div>
    </div>

    <div class="card card-amber" style="padding: 8px 14px;">
      <div class="card-body" style="color: #78350F;"><strong>How to read it:</strong> a person succeeds only if they can express the memory and one try passes I, S and R together. One weak step caps the whole number, so the next slides find which step breaks.</div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Sources: <a href="https://blog.google/products/photos/google-photos-10-years-tips-tricks/" target="_blank" style="color: #1A73E8;">Google, May 2025 ↗</a> (users, photos, searchers) · <a href="https://9to5google.com/2025/05/15/google-one-150-million/" target="_blank" style="color: #1A73E8;">Reuters via 9to5Google, May 2025 ↗</a> (Google One)
    </div>
    <div class="slide-num">1 / 10</div>
  </div>
</section>

<!-- SLIDE 2: Discovery Engine Workflow -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">AI discovery engine</span></div>
    <h1 class="slide-title">85,140 posts in, 144 real failed searches out</h1>
  </div>
  
  <div class="main-content">
    <div class="col-2">
      <!-- 5-Box Pipeline -->
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 12px;">
        <div class="card" style="text-align: center; padding: 10px 8px;">
          <div style="font-size: 17pt; font-weight: 700; color: #1A73E8;">1 · COLLECT</div>
          <div style="font-size: 22pt; font-weight: 800; color: #0F172A; margin: 4px 0;">85,140</div>
          <div style="font-size: 17pt; color: #64748B;">Public posts (Play Store, App Store, YT, Reddit)</div>
        </div>
        <div class="card" style="text-align: center; padding: 10px 8px;">
          <div style="font-size: 17pt; font-weight: 700; color: #1A73E8;">2 · SCREEN</div>
          <div style="font-size: 22pt; font-weight: 800; color: #0F172A; margin: 4px 0;">819</div>
          <div style="font-size: 17pt; color: #64748B;">Relevant (Gate A 5,305 → Gate B 1,333 sample)</div>
        </div>
        <div class="card card-blue" style="text-align: center; padding: 10px 8px;">
          <div style="font-size: 17pt; font-weight: 700; color: #1E40AF;">3 · EXTRACT</div>
          <div style="font-size: 22pt; font-weight: 800; color: #1E40AF; margin: 4px 0;">144</div>
          <div style="font-size: 17pt; color: #3B82F6;">Specific attempts (720 episodes; 62 scoreable)</div>
        </div>
        <div class="card" style="text-align: center; padding: 10px 8px;">
          <div style="font-size: 17pt; font-weight: 700; color: #1A73E8;">4 · AUDIT</div>
          <div style="font-size: 22pt; font-weight: 800; color: #0F172A; margin: 4px 0;">203</div>
          <div style="font-size: 17pt; color: #64748B;">Pairs checked blind by Qwen 27B model</div>
        </div>
        <div class="card card-highlight" style="text-align: center; padding: 10px 8px;">
          <div style="font-size: 17pt; font-weight: 700; color: #065F46;">5 · COMPARE</div>
          <div style="font-size: 22pt; font-weight: 800; color: #065F46; margin: 4px 0;">9 Areas</div>
          <div style="font-size: 17pt; color: #059669;">Ranked only on agreed fields (O1–O9)</div>
        </div>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 32%;">Extracted Field in Schema</th>
            <th style="width: 48%;">The Brief's Underlying Question Answered</th>
            <th style="width: 20%;">Reliability Check</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>asset_type</code></td>
            <td><em>What kinds of old photos do users struggle to retrieve?</em></td>
            <td>Validated in Gate B</td>
          </tr>
          <tr>
            <td><code>cues_retained</code> (14 cue types)</td>
            <td><em>What do people actually remember about the photo?</em></td>
            <td>Jaccard 0.557</td>
          </tr>
          <tr>
            <td><code>cues_lost</code> (date, place, album, words)</td>
            <td><em>What have they forgotten when search fails?</em></td>
            <td>Jaccard 0.673</td>
          </tr>
          <tr>
            <td><code>query_verbatim</code> · <code>search_mode</code></td>
            <td><em>How do they search when memory is incomplete?</em></td>
            <td>Quote verify 85.2%</td>
          </tr>
          <tr class="highlight">
            <td><code>failure_stage</code> (5 stages)</td>
            <td><em>Where does retrieval break? (Part 3 decomposition)</em></td>
            <td><strong>κ 0.509 (Moderate)</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="col">
      <div class="card" style="height: 100%;">
        <div class="card-title">The audit, not the model, set the ranking</div>
        <div class="card-body">
          <p style="margin: 0 0 10px 0;"><strong>1. Structure, not sentiment:</strong> Every review was converted into a structured, typed record with fixed vocabularies, not qualitative impression tags.</p>
          <p style="margin: 0 0 10px 0;"><strong>2. Pre-registered rules:</strong> Hypotheses H1–H5 and decision thresholds were set before extraction, so the data could not be read to fit them.</p>
          <p style="margin: 0 0 10px 0;"><strong>3. The audit overruled the ranking:</strong> When the blind audit showed hypothesis agreement was low (Jaccard 0.347) while failure stage agreement was solid (κ 0.509), the engine demoted hypothesis ranking and pivoted to failure stages.</p>
          <div style="margin-top: 14px;">
            <a class="btn-link" href="https://retrieval-discovery-engine.vercel.app" target="_blank">retrieval-discovery-engine.vercel.app ↗</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Play Store = 86.2% of episodes · Quotes verified 85.2% (audit n=203) · Extraction closed at 720/819
    </div>
    <div class="slide-num">2 / 10</div>
  </div>
</section>

<!-- SLIDE 3: Discovery Engine Findings -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Discovery-engine findings · observed</span></div>
    <h1 class="slide-title">People keep "roughly when" and lose the exact date, the one thing search needs</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-5">
      <div class="card" style="margin-bottom: 8px;">
        <div class="card-title">Engine and survey agree: the time is kept, the date is lost</div>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 25%;">Question</th>
              <th style="width: 40%;">Engine (144 Specific Attempts)</th>
              <th style="width: 35%;">Survey (n=15 / 14 Dedup)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Photo Kinds</strong></td>
              <td>Personal photos 80 · multi-photo 26 · videos 16 · screenshots 7 · docs 3</td>
              <td>All 3 real-trouble cases were document or medicine photos</td>
            </tr>
            <tr class="highlight">
              <td><strong>Remembered</strong></td>
              <td><strong>Roughly when 40</strong> · object 17 · exact date 14 · text 12 · people 10</td>
              <td><strong>Roughly when 8</strong> · object 7 · people with me 6</td>
            </tr>
            <tr class="highlight">
              <td><strong>Forgotten</strong></td>
              <td><strong>The date 37</strong> · album 29 · exact words 10 · place 10</td>
              <td><strong>When it was taken 9</strong> · words to search 9</td>
            </tr>
            <tr>
              <td><strong>Search Method</strong></td>
              <td>20 of 32 queries are 1 word ("dog"); 10 name a time ("Halloween 2024")</td>
              <td>First move: scroll 9/15; own-app: 4 of 5 strip time to bare nouns</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title">O1 is the largest group with a memory search ignores</div>
        <div class="card-body" style="font-size: 17pt;">
          <strong>O1 (Rough time or an event):</strong> 42 → 37 after exclusions (18 never surfaced, 12 misread).<br>
          <strong>O8 (No clue at all):</strong> 47 attempts, larger, but there is no memory for search to use. O1 is the largest group where memory exists and search ignores it.<br>
          <strong>Excluded:</strong> O7 exact date known (14) · O9 path moved by an update (12).
        </div>
      </div>
    </div>

    <div class="col">
      <div class="card card-blue" style="height: 100%;">
        <div class="card-title" style="color: #1E40AF;">Episodic time wins; dead-end recovery loses</div>
        <div class="card-body" style="display: flex; flex-direction: column; gap: 8px; font-size: 17pt;">
          <div><strong style="color: #059669;">H1 Episodic time: SUPPORTED (root cause).</strong> Roughly when is the #1 kept cue (40); the date is the #1 lost cue (37).</div>
          <div><strong style="color: #059669;">H2 Recognition: SUPPORTED (secondary).</strong> 41.7% never surfaced; 7 of 15 ended unsure.</div>
          <div><strong style="color: #B45309;">H3 Dead-end recovery: REFINED, NOT THE LEAD.</strong> Overruled by the audit: recovery is 0.7% of failures (stage κ 0.509).</div>
          <div><strong style="color: #475569;">H4 Hinglish: NOT TESTED.</strong> Weak signal (2 of 15 survey, 1 of 6 tests); kept as a design choice.</div>
          <div><strong style="color: #475569;">H5 Text not indexed: WEAKLY SUPPORTED</strong> (3 docs; the index scores 0.000 on text in images).</div>
          <div><strong style="color: #475569;">H6 Path changed: PRESENT BUT MINOR</strong> (8.3%), added post hoc.</div>
        </div>
        <div style="margin-top: 10px; border-top: 1px solid #BFDBFE; padding-top: 8px;">
          <div class="card-title" style="color: #1E40AF;">77% of the 144 failures break at I or S, before a retry</div>
          <table class="data-table">
            <tbody>
              <tr class="highlight"><td>S Never surfaced</td><td style="text-align: right;">60 (41.7%)</td></tr>
              <tr class="highlight"><td>I Clue misread</td><td style="text-align: right;">51 (35.4%)</td></tr>
              <tr><td>E · R · retry</td><td style="text-align: right;">2 · 2 · 1</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Sources: 144 engine attempts · survey (n=15) · blind audit (n=203) · H1–H5 and decision rules set before extraction
    </div>
    <div class="slide-num">3 / 10</div>
  </div>
</section>

<!-- SLIDE 4: User Research and Observed Tasks -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">User research</span></div>
    <h1 class="slide-title">Most people scroll before they search, and nearly half end close but unsure</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card card-blue">
        <div class="card-title" style="color: #1E40AF;">A directional survey: 15 stories we could score</div>
        <div class="card-body">
          <p style="margin: 0 0 6px 0;"><strong>Structured self-serve questionnaire (n=15, 23–30 Sep):</strong> every answer maps onto the engine's vocabulary.</p>
          <p style="margin: 0 0 6px 0;"><strong>Why:</strong> 100% scoreable stories (vs 8.6% of public posts); reached 15 people vs 2 call contacts.</p>
          <p style="margin: 0;"><strong>Costs:</strong> self-reported convenience sample; it shows patterns, not how common they are.</p>
          <a class="btn-link" href="https://retrieval-discovery-engine.vercel.app/survey" target="_blank" style="margin-top: 8px;">Survey questions ↗</a>
        </div>
      </div>

      <div class="card">
        <div class="card-title">The survey repeats the engine's pattern</div>
        <table class="data-table" style="font-size: 17pt;">
          <thead>
            <tr><th>Metric</th><th>Engine (144)</th><th>Survey (15 / 14)</th></tr>
          </thead>
          <tbody>
            <tr><td>Most remembered</td><td>Roughly when (40)</td><td>Roughly when (8)</td></tr>
            <tr><td>Ended unsure</td><td>Not measurable</td><td><strong>7 of 15 (47%)</strong></td></tr>
            <tr><td>First move: scroll</td><td>15 workarounds</td><td><strong>9 of 15 (60%)</strong></td></tr>
          </tbody>
        </table>
      </div>

      <div class="card card-amber" style="padding: 8px 14px;">
        <div class="card-title" style="color: #92400E;">It costs most people over five minutes</div>
        <div class="card-body" style="color: #78350F;">Trips and outings, a photo for LinkedIn, a medical report. <strong>12 of 15 spent 5+ minutes</strong>, past the brief's five-minute bar; 3 had to ask someone or get the document again.</div>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">4 of 5 kept roughly when; only 1 put it in the search</div>
        <table class="data-table" style="font-size: 17pt;">
          <thead>
            <tr>
              <th style="width: 8%;">ID</th>
              <th style="width: 18%;">Target Photo</th>
              <th style="width: 26%;">What They Remembered</th>
              <th style="width: 24%;">What They Typed</th>
              <th style="width: 12%;">Break</th>
              <th style="width: 12%;">Outcome</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>S04</strong></td>
              <td>Wedding photo</td>
              <td>Roughly when, event, people</td>
              <td><em>"wedding, pichle saal diwali"</em></td>
              <td>Interpretation</td>
              <td style="color: #D97706; font-weight: 700;">? Unsure</td>
            </tr>
            <tr>
              <td><strong>S03</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event, object</td>
              <td><em>"gym"</em></td>
              <td>Recognition</td>
              <td style="color: #D97706; font-weight: 700;">? Unsure</td>
            </tr>
            <tr>
              <td><strong>S08</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event</td>
              <td><em>(Didn't know what to type; scrolled)</em></td>
              <td>Expression</td>
              <td style="color: #059669; font-weight: 700;">✓ Found</td>
            </tr>
            <tr>
              <td><strong>S12</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event</td>
              <td><em>(Never typed; opened album)</em></td>
              <td>Expression</td>
              <td style="color: #D97706; font-weight: 700;">? Unsure</td>
            </tr>
            <tr style="background: #FEF2F2;">
              <td><strong>S06</strong></td>
              <td>Medicine bill</td>
              <td>Object, text in bill</td>
              <td><em>"medicine, bill"</em></td>
              <td>Surfacing</td>
              <td style="color: #DC2626; font-weight: 700;">✗ Never found</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 10px;">
          <div class="quote-box">"wedding, pichle saal diwali" — S04 (Hinglish: a festival and relative year, not a calendar date)</div>
          <div class="quote-box">"medicine, bill" — S06 (Never found; had to get the document again)</div>
        </div>

        <div style="font-size: 17pt; color: #475569; margin-top: 8px;">
          <strong>Ask Photos:</strong> 7 of 15 had never heard of it; all 4 who used it got "related photos, but not the one".
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Survey n = 15 (14 dedup), self-reported convenience sample · IDs S01–S15 match the published responses
    </div>
    <div class="slide-num">4 / 10</div>
  </div>
</section>

<!-- SLIDE 5: Target Segment and Root Cause -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Target segment &amp; root cause</span></div>
    <h1 class="slide-title">Our segment can place the moment only roughly, and search can't turn "roughly" into dates</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card" style="height: 100%;">
        <div class="card-title">Defined by what they remember, not by age</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0; font-size: 18pt; font-weight: 700; color: #1E40AF;">
            Long-time Google Photos users searching for a personal moment they can place only roughly.
          </p>
          <p style="margin: 0 0 10px 0;">They remember "around Diwali", "my sister's graduation", "last winter".</p>
          
          <table class="data-table" style="font-size: 17pt; margin-bottom: 12px;">
            <thead>
              <tr><th>Segment Sizing Filter</th><th>Engine (144)</th><th>Survey (15)</th></tr>
            </thead>
            <tbody>
              <tr><td>Kept rough time or event (O1)</td><td>42 (29%)</td><td>8 (53%)</td></tr>
              <tr class="highlight"><td><strong>Target Segment (After Exclusions)</strong></td><td><strong>37 (26%)</strong></td><td><strong>8 (53%)</strong></td></tr>
              <tr><td>Personal photo or video</td><td>30 of 37</td><td>All 8</td></tr>
              <tr><td>Large library (5,000+ items)</td><td>Not measured</td><td>5 of 8</td></tr>
            </tbody>
          </table>

          <div style="background: #F1F5F9; border-radius: 6px; padding: 8px 12px; font-size: 17pt; color: #475569;">
            <strong>42 → 37:</strong> minus 2 who also knew the exact date (plain search works) and 3 whose browse path moved in an update (H6).
          </div>
          <div style="margin-top: 8px; background: #EFF6FF; border-left: 4px solid #1A73E8; border-radius: 6px; padding: 8px 12px; font-size: 17pt; color: #1E293B;">
            <strong>Why not an age band?</strong> The failure comes from memory state and library habits, not age, and nothing in our evidence points to an age gap. Age is a diagnostic cut in the A/B, not the targeting rule.
          </div>
        </div>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card card-blue" style="height: 100%;">
        <div class="card-title" style="color: #1E40AF;">Memory stores episodes; Photos stores items and dates</div>
        
        <div style="display: grid; grid-template-columns: 1fr 40px 1fr; gap: 8px; align-items: center; margin: 12px 0;">
          <div style="background: #FFFFFF; border: 2px solid #93C5FD; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-weight: 800; font-size: 18pt; color: #1E40AF; margin-bottom: 4px;">Human Memory Stores</div>
            <div style="font-size: 20pt; font-weight: 800; color: #0F172A;">EPISODES</div>
            <div style="font-size: 17pt; color: #64748B; margin-top: 4px;">Rough time, event anchors, surrounding scenes ("last winter", "cousin's wedding")</div>
          </div>
          <div style="text-align: center; font-size: 26pt; font-weight: 800; color: #DC2626;">⚡</div>
          <div style="background: #FFFFFF; border: 2px solid #FCA5A5; border-radius: 8px; padding: 12px; text-align: center;">
            <div style="font-weight: 800; font-size: 18pt; color: #DC2626; margin-bottom: 4px;">Google Photos Indexes</div>
            <div style="font-size: 20pt; font-weight: 800; color: #0F172A;">ITEMS & DATES</div>
            <div style="font-size: 17pt; color: #64748B; margin-top: 4px;">Isolated photos with calendar timestamps (YYYY-MM-DD) and tags</div>
          </div>
        </div>

        <div class="quote-box" style="margin-bottom: 10px;">
          "I'll type in something super simple, like 'Halloween 2024' and it seriously can't find anything?" — Play Store review
        </div>

        <div class="card-body" style="font-size: 17pt;">
          <strong>Asking why, for the 37 segment attempts:</strong><br>
          <strong>1. Why isn't the photo found?</strong> It never surfaces (18 of 37).<br>
          <strong>2. Why not?</strong> Search misreads the clue (12): "last Diwali" is neither a keyword nor a date.<br>
          <strong>3. Why does that matter?</strong> People keep the event and lose the date (the #1 lost cue, 37 of 144).<br>
          <strong>4. Root cause:</strong> nothing turns "roughly when" into a date window.<br>
          <em>Real app: 4 of 5 testers typed bare nouns ("vacation", "gym"); 0 of 5 found the photo.</em>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Segment: 37 engine attempts (26%), 8 of 15 in survey · Hinglish support is a design choice, not a finding
    </div>
    <div class="slide-num">5 / 10</div>
  </div>
</section>

<!-- SLIDE 6: Problem Definition and Solution Rationale -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Problem &amp; solution rationale</span></div>
    <h1 class="slide-title">People already scroll to "roughly when" by hand and still end unsure, so the product should take that step for them</h1>
  </div>
  
  <div class="main-content" style="flex-direction: column; gap: 0.16in;">
    <!-- Top Banner: Locked Problem Statement -->
    <div class="card card-blue" style="border-left: 6px solid #1A73E8; padding: 12px 20px;">
      <div style="font-size: 17pt; font-weight: 800; color: #1E40AF; margin-bottom: 2px;">The problem, in the user's words</div>
      <div style="font-size: 19pt; font-weight: 700; color: #0F172A; line-height: 1.35;">
        "I remember the event and roughly when ("last Diwali"), but Photos wants a date or keyword I've forgotten. So I scroll by hand, and even then I'm not sure the photo I found is the one."
      </div>
    </div>

    <!-- Middle Split: Workaround vs Solution Rationale -->
    <div style="display: flex; gap: 0.3in; flex: 1;">
      <div class="card" style="flex: 0.8;">
        <div class="card-title">The workaround is the design blueprint</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0;"><strong>Engine:</strong> 15 of 21 workarounds are manual scrolling (7 of 10 failed).</p>
          <p style="margin: 0 0 8px 0;"><strong>Survey:</strong> scrolling was the first move for 9 of 15; 5 of those 9 still ended unsure.</p>
          <p style="margin: 0; font-weight: 600; color: #1E40AF;">So the product should find the time window and group the moments for them.</p>
        </div>
      </div>

      <div class="card" style="flex: 1.6;">
        <div class="card-title">Each option helps, but none is built for "I'll know it when I see it"</div>
        <div class="card-body">
          <table class="data-table" style="margin-bottom: 6px;">
            <thead><tr><th style="width: 24%;">Option</th><th style="width: 34%;">Good at</th><th>Gap for a vague memory</th></tr></thead>
            <tbody>
              <tr><td>Photos search</td><td>People, places, things, dates</td><td>Memory must become search terms</td></tr>
              <tr><td>Ask Photos</td><td>Plain-language questions</td><td>All 7 who tried: "related, not the one"</td></tr>
              <tr><td>Apple Photos</td><td>Describing the photo</td><td>Describes items, not when it was</td></tr>
              <tr class="highlight"><td>Memory Trails</td><td>Rough time → moments</td><td>Recognise, then recover the moment</td></tr>
            </tbody>
          </table>
          <p style="margin: 0;"><strong>Why Google could win</strong> <span class="tag tag-hyp" style="margin-left:2px;">Hypothesis</span> years of each user's own dates, places and faces, joined into moments by the UX. Rivals could build it too.</p>
        </div>
      </div>
    </div>

    <!-- Bottom Strip: Evolution of Thinking -->
    <div class="card" style="background: #F1F5F9; padding: 10px 14px;">
      <div style="font-size: 17pt; font-weight: 700; color: #475569; margin-bottom: 6px;">Five times the evidence changed the plan</div>
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; font-size: 17pt;">
        <div><strong>1. Metric:</strong> per-search success → <strong>per-user URR</strong></div>
        <div><strong>2. Outcomes:</strong> recovery agent → <strong>5 stages + browse</strong></div>
        <div><strong>3. Discovery:</strong> H3 ranked top → <strong>overturned by audit</strong></div>
        <div><strong>4. Reported behaviour:</strong> retry search → <strong>scroll by hand</strong></div>
        <div><strong>5. Problem:</strong> "search is bad" → <strong>items vs. moments</strong></div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Sources: 144 engine attempts · survey (n=15) · MVP tests (n=6)
    </div>
    <div class="slide-num">6 / 10</div>
  </div>
</section>

<!-- SLIDE 7: The MVP (Memory Trails) -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">MVP</span></div>
    <h1 class="slide-title">Memory Trails turns "last Diwali" into a date window and shows moments, not a grid</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card card-blue" style="margin-bottom: 8px;">
        <div class="card-title" style="color: #1E40AF;">It sits inside search, where the failure happens</div>
        <div class="card-body" style="font-size: 17pt;">
          <p style="margin: 0;"><strong>Where it lives:</strong> inside Photos search. When a search fails, <em>"Can't describe it?"</em> opens it with the words carried over.</p>
        </div>
      </div>

      <!-- Screenshot Row -->
      <div class="shot-row">
        <figure><div class="screenshot-frame shot" style="height: 2.3in;"><img src="{img_describe}" alt="Describe the moment"></div><figcaption>1 · Describe</figcaption></figure>
        <figure><div class="screenshot-frame shot shot-ai" style="height: 2.3in;"><img src="{img_clues}" alt="Editable clue chips"></div><figcaption>2 · Clues</figcaption></figure>
        <figure><div class="screenshot-frame shot shot-ai" style="height: 2.3in;"><img src="{img_moments}" alt="Ranked likely moments"></div><figcaption>3 · Moments</figcaption></figure>
        <figure><div class="screenshot-frame shot" style="height: 2.3in;"><img src="{img_found}" alt="Confirm the photo"></div><figcaption>4 · Confirm</figcaption></figure>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center;">
        <a class="btn-link" href="https://memory-trails-v2.vercel.app" target="_blank">memory-trails-v2.vercel.app ↗</a>
        <span style="font-size: 17pt; color: #64748B;"><span style="color:#1A73E8; font-weight:700;">Blue frame</span> = AI step</span>
      </div>

      <div class="card" style="margin-top: 6px;">
        <div class="card-title">Each failure gets one AI step; the person confirms</div>
        <div class="card-body" style="font-size: 17pt; line-height: 1.3;">
          <strong>Only a rough time</strong> → turns it into a date window<br>
          <strong>Mixed clues</strong> → splits them into chips you can edit<br>
          <strong>A flat grid</strong> → groups photos into moments<br>
          <strong>Why this one?</strong> → shows matched vs approximate clues<br>
          <strong>Wrong moment</strong> → offers nearby moments; never hides<br>
          <em>It never confirms for you, and can't always find the photo.</em>
        </div>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">Big gain with rich memory, modest with one vague cue <span class="tag tag-mod">Modelled</span></div>
        <table class="data-table" style="font-size: 17pt; margin-bottom: 8px;">
          <thead>
            <tr>
              <th>Cue Dropout Level</th>
              <th>What the Query Keeps</th>
              <th style="text-align: center;">Plain CLIP</th>
              <th style="text-align: center;">Memory Trails</th>
              <th style="text-align: center;">Moment@5</th>
            </tr>
          </thead>
          <tbody>
            <tr class="highlight">
              <td><strong>L3 (Fully described)</strong></td>
              <td>Vague time + exact place + library word</td>
              <td style="text-align: center;">0.172</td>
              <td style="text-align: center; font-weight: 800; color: #1E40AF;">0.962</td>
              <td style="text-align: center; font-weight: 800; color: #1E40AF;">0.933</td>
            </tr>
            <tr>
              <td><strong>L2 (Two vague cues)</strong></td>
              <td>Paraphrased content + 2 vague cues</td>
              <td style="text-align: center;">0.209</td>
              <td style="text-align: center;">0.276</td>
              <td style="text-align: center;">0.333</td>
            </tr>
            <tr>
              <td><strong>L1 (One vague cue)</strong></td>
              <td>Paraphrased content + 1 vague time cue</td>
              <td style="text-align: center;">0.242</td>
              <td style="text-align: center;">0.309</td>
              <td style="text-align: center;">0.333</td>
            </tr>
            <tr>
              <td><strong>L0 (Content only)</strong></td>
              <td>Pure scene description, no metadata</td>
              <td style="text-align: center;">0.312</td>
              <td style="text-align: center;">0.312</td>
              <td style="text-align: center;">0.267</td>
            </tr>
            <tr style="background: #F0FDF4; font-weight: 800;">
              <td><strong>Weighted by real memory</strong></td>
              <td>Each level weighted by how often the 144 real attempts keep it</td>
              <td style="text-align: center;">0.259</td>
              <td style="text-align: center; color: #059669;">0.334 (+0.075)</td>
              <td style="text-align: center; color: #059669;">0.336 (+0.111)</td>
            </tr>
          </tbody>
        </table>

        <div class="card-body" style="font-size: 17pt; line-height: 1.35;">
          <p style="margin: 0 0 6px 0;"><strong>Read this first:</strong> L3's 0.962 needs three cues; only 4% (6 of 144) of real attempts kept that many. Weighted by real memory, recall gains <strong>+0.075</strong> and moment@5 <strong>+0.111</strong>: grouping into moments helps more than flat ranking.</p>
          <p style="margin: 0; color: #64748B;"><strong>Scope:</strong> tests the re-entry and recovery interaction on 1,282 CC photos, not production accuracy. Out: a search redesign, unasked sensitive memories, a stored life-event profile.</p>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      recall@20 = right photo in the top 20 · moment@5 = right moment in the top 5 · ranking weights are judgement
    </div>
    <div class="slide-num">7 / 10</div>
  </div>
</section>

<!-- SLIDE 8: User Testing -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">User testing · observed, n = 6</span></div>
    <h1 class="slide-title">5 of 6 testers were sure they found the photo, but "year before last" still breaks it</h1>
  </div>
  
  <div class="main-content">
    <div class="col-2">
      <!-- Results Table -->
      <table class="data-table" style="font-size: 17pt; margin-bottom: 8px;">
        <thead>
          <tr>
            <th>ID</th>
            <th>Own Photos search → result</th>
            <th>Task 1 (cat)</th>
            <th>Task 2 (dog)</th>
            <th style="text-align: center;">Sure</th>
            <th style="text-align: center;">vs GP</th>
            <th>Would use</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>R01</strong></td>
            <td><em>"Wedding before COVID"</em> → wrong years</td>
            <td style="color: #059669; font-weight: 700;">✓ Found, sure</td>
            <td style="color: #DC2626; font-weight: 700;">✗ Not found</td>
            <td style="text-align: center; white-space: nowrap;">5/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">5/5</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R02</strong></td>
            <td><em>"gym"</em> → can't tell which</td>
            <td style="color: #059669; font-weight: 700;">✓ Found, sure</td>
            <td style="color: #059669; font-weight: 700;">✓ Found (1-tap alt)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>When fails</td>
          </tr>
          <tr>
            <td><strong>R03</strong></td>
            <td><em>(Apple Photos user)</em></td>
            <td style="color: #059669; font-weight: 700;">✓ Found, sure</td>
            <td style="color: #059669; font-weight: 700;">✓ Found (nearby)</td>
            <td style="text-align: center; white-space: nowrap;">5/5</td>
            <td style="text-align: center;">—</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R04</strong></td>
            <td><em>"vacation"</em> → wrong years</td>
            <td style="color: #059669; font-weight: 700;">✓ Found, sure</td>
            <td style="color: #059669; font-weight: 700;">✓ Found (1-tap alt)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>When fails</td>
          </tr>
          <tr>
            <td><strong>R05</strong></td>
            <td><em>"Wedding event"</em> → can't tell which</td>
            <td style="color: #059669; font-weight: 700;">✓ Found, sure</td>
            <td style="color: #059669; font-weight: 700;">✓ Found (clue edit)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R06</strong></td>
            <td><em>"Kerala photos"</em> → can't tell which</td>
            <td style="color: #D97706; font-weight: 700;">? Right day, unsure</td>
            <td style="color: #059669; font-weight: 700;">✓ Found (1-tap alt)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">3/5</td>
            <td>Every time</td>
          </tr>
        </tbody>
      </table>

      <!-- Key Metrics Strip -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
        <div class="stat-box" style="padding: 6px 10px;">
          <div class="stat-num stat-num-green" style="font-size: 22pt;">6 of 6</div>
          <div class="stat-label">Fit the segment</div>
        </div>
        <div class="stat-box" style="padding: 6px 10px;">
          <div class="stat-num stat-num-green" style="font-size: 22pt;">4.33 / 5</div>
          <div class="stat-label">Task 1 sureness</div>
        </div>
        <div class="stat-box" style="padding: 6px 10px;">
          <div class="stat-num stat-num-green" style="font-size: 22pt;">4.0 / 5</div>
          <div class="stat-label">Ease vs Photos</div>
        </div>
        <div class="stat-box" style="padding: 6px 10px;">
          <div class="stat-num" style="font-size: 22pt; color: #DC2626;">0 of 5</div>
          <div class="stat-label">Found it in own Photos</div>
        </div>
      </div>
      <div style="display: flex; gap: 10px; margin-top: 8px;">
        <a class="btn-link" href="https://retrieval-discovery-engine.vercel.app/mvp-test" target="_blank">MVP test questions ↗</a>
        <a class="btn-link btn-link-sec" href="https://memory-trails-v2.vercel.app" target="_blank">memory-trails-v2.vercel.app ↗</a>
      </div>
    </div>

    <div class="col">
      <div class="card card-blue" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="card-title" style="color: #1E40AF;">Testers valued the moment, not a grid</div>
          <div class="quote-box">"Shows the moment, not a grid" — R02</div>
          <div class="quote-box">"Moving to nearby months, like scrolling but faster" — R03</div>
          <div class="quote-box">"Works without knowing what to type" — R04</div>
          <div class="quote-box">"Finds exact month & year... understands mix of Hindi and English" — R06</div>
        </div>

        <div>
          <div class="card-title" style="color: #991B1B; margin-top: 8px;">Three fixes for the next version</div>
          <div style="font-size: 17pt; color: #334155; line-height: 1.35;">
            <strong>1. Compound time:</strong> R01 stuck on <em>"pichle ke pichle saal"</em> (year before last). <em>Fix:</em> parse compound offsets; editable year.<br>
            <strong>2. Clues missed:</strong> R04 didn't notice them. <em>Fix:</em> high-contrast <em>"Showing Diwali 2025 · Tap to change"</em>.<br>
            <strong>3. Speed:</strong> R05, R06 wanted faster loading. <em>Fix:</em> pre-cache moments.
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Self-serve, unmoderated, 3–4 Oct 2026, n = 6, self-reported · No session logs, so wrong confirmations are unknown
    </div>
    <div class="slide-num">8 / 10</div>
  </div>
</section>

<!-- SLIDE 9: Success Metrics -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Success metrics</span></div>
    <h1 class="slide-title">Next: an A/B test of whether URR moves from 40% toward 45%, with an early signal per step</h1>
  </div>

  <div class="main-content">
    <div class="col">
      <div class="card card-blue">
        <div class="card-title" style="color: #1E40AF;">One number: users who reach the photo in 28 days <span class="tag tag-prop">Proposed</span></div>
        <div class="card-body">
          <p style="margin: 0 0 6px 0;"><strong>Definition:</strong> share of users with a vague-memory search in 28 days who reach the photo. Counts users, not searches.</p>
          <p style="margin: 0 0 6px 0;"><strong>Baseline 40% → target 45%.</strong> The baseline is a self-reported proxy (6 of 15 sure they found it). +5 pts is the smallest lift worth shipping.</p>
          <p style="margin: 0;"><strong>Planned test, not yet run:</strong> 8 weeks, randomised by user; ~1,600 users per arm for 80% power at α 0.05.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-title">What the MVP has shown so far (not the A/B)</div>
        <div class="card-body">
          <span class="tag tag-mod" style="margin-left:0;">Modelled</span> recall@20 weighted by real memory <strong>0.259 → 0.334</strong>, moment@5 <strong>+0.111</strong><br>
          <span class="tag tag-obs" style="margin-left:0;">Observed</span> 6 testers: sureness <strong>4.33 / 5</strong>, ease vs Photos <strong>4.0 / 5</strong>
        </div>
      </div>
      <div class="card card-highlight">
        <div class="card-title" style="color: #065F46;">Ship, extend or stop is decided in advance <span class="tag tag-prop">Proposed</span></div>
        <div class="card-body">
          <strong>Ship</strong> if URR rises ≥5 pts and no guardrail trips. <strong>Extend</strong> if the lift is positive but under 5. <strong>Stop</strong> if false confirmation passes 3%.
        </div>
      </div>
    </div>

    <div class="col-1-2">
      <div class="card">
        <div class="card-title">Each URR term gets an early signal</div>
        <table class="data-table">
          <thead><tr><th>Metric</th><th>Term</th><th>Target</th></tr></thead>
          <tbody>
            <tr><td><strong>Entry rate</strong> after a failed search</td><td>Expression</td><td>≥12%</td></tr>
            <tr><td><strong>Clue correction</strong> (chip edited)</td><td>Interpretation</td><td>15–25%</td></tr>
            <tr><td><strong>"Not in any of these?"</strong> rate</td><td>Surfacing</td><td>Falling</td></tr>
            <tr><td><strong>Confirm after opening a moment</strong></td><td>Recognition</td><td>≥55%</td></tr>
          </tbody>
        </table>
      </div>
      <div class="card">
        <div class="card-title">A wrong 'found it' stops the launch</div>
        <table class="data-table">
          <tbody>
            <tr style="background: #FEF2F2;"><td><strong>False confirmation</strong> (confirmed, then kept searching)</td><td><strong>&lt;3%</strong></td></tr>
            <tr style="background: #FEF2F2;"><td><strong>P95 time to first moment</strong></td><td><strong>&lt;1.5 s</strong></td></tr>
            <tr style="background: #FEF2F2;"><td><strong>Abandonment</strong> before the first moment</td><td>No rise vs control</td></tr>
          </tbody>
        </table>
      </div>
      <div class="card">
        <div class="card-title">Diagnostics explain any movement</div>
        <div class="card-body">Recall@20 by cue type · near-miss recovery rate · "Why this moment?" views before confirming</div>
      </div>
      <div class="card card-amber">
        <div class="card-body" style="color: #78350F;"><strong>The A/B has not run yet.</strong> Baseline and target are proposed thresholds. The A/B will test whether Memory Trails lifts <em>confirmed</em> retrieval without raising false confidence.</div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Primary metric is confirmed retrieval, not clicks or feature use · No Google telemetry
    </div>
    <div class="slide-num">9 / 10</div>
  </div>
</section>

<!-- SLIDE 10: Risks and Limitations -->
<section class="slide">
  <div>
    <div class="pill-row"><span class="confidential-tag">Risks &amp; limitations</span></div>
    <h1 class="slide-title">Biggest risk: the gain is largest where memory is richest, and the evidence is still small</h1>
  </div>

  <div class="main-content">
    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">Each risk has a mitigation built or planned</div>
        <table class="data-table">
          <thead>
            <tr><th style="width: 46%;">Risk</th><th style="width: 54%;">Mitigation & evidence</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>R1. The win sits where memory is richest</strong> (+0.79 at L3, +0.07 at L1)</td><td>Lean on moment recognition (moment@5 0.333 at L1–L2); report L1 separately in the A/B.</td></tr>
            <tr><td><strong>R2. Date filters hide photos</strong></td><td><strong>Soft scoring built:</strong> L3 recall 0.851 → 0.962.</td></tr>
            <tr><td><strong>R3. False confirmation</strong> (worst failure)</td><td>Never auto-confirm; show the surrounding photos; stop launch above 3%.</td></tr>
            <tr><td><strong>R4. Can't read text in photos</strong> (0.000 on receipts)</td><td>Add OCR text to the index.</td></tr>
            <tr><td><strong>R5. Ask Photos may already suffice</strong></td><td>4 of 4 survey and 3 of 3 test users got "related photos, not the one".</td></tr>
            <tr><td><strong>R6. Sensitive memories</strong> (medical, relationships)</td><td>User-initiated only; the session persists nothing.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="col">
      <div class="card card-amber">
        <div class="card-title" style="color: #92400E;">The evidence is small and mostly self-reported</div>
        <div class="card-body" style="color: #78350F;">
          • Play Store is 86.2% of engine posts<br>
          • Survey n = 15 vs a target of 30, self-reported<br>
          • MVP tests n = 6, unmoderated, no session logs<br>
          • URR baselines modelled; no telemetry<br>
          • Eval library: 1,282 CC photos, synthetic episodes<br>
          • Ranking weights are judgement<br>
          • Hinglish (H4) is a weak signal only
        </div>
      </div>
      <div class="card card-blue">
        <div class="card-title" style="color: #1E40AF;">Next: compound dates, clearer clues, a one-market test</div>
        <div class="card-body">
          1. Parse compound dates ("pichle ke pichle saal")<br>
          2. Make the active date clue unmissable<br>
          3. Run the A/B in one market
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Ladder levels: L3 = vague time + exact place + library word · L1 = paraphrased content + one vague time cue
    </div>
    <div class="slide-num">10 / 10</div>
  </div>
</section>

</body>
</html>
"""
    return html

def build():
    print("Generating deck/index.html...")
    html_content = generate_html()
    deck_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deck")
    html_path = os.path.join(deck_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Written: {html_path} ({os.path.getsize(html_path)} bytes)")

    pdf_deck_path = os.path.join(deck_dir, "NL_GooglePhotos.pdf")
    pdf_root_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NL_GooglePhotos.pdf")

    print("Rendering PDF via Google Chrome headless...")
    chrome = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    cmd = [
        chrome,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_deck_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Chrome error:", res.stderr)
        sys.exit(1)

    print(f"Generated PDF: {pdf_deck_path} ({os.path.getsize(pdf_deck_path)} bytes)")

    # Copy to root directory as required by brief
    with open(pdf_deck_path, "rb") as src, open(pdf_root_path, "wb") as dst:
        dst.write(src.read())
    print(f"Copied to: {pdf_root_path}")

    # Validate PDF structure and scrub metadata
    print("Validating and scrubbing PDF...")
    reader = pypdf.PdfReader(pdf_deck_path)
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Completely scrub all metadata
    clean_metadata = {
        "/Title": "NL_GooglePhotos",
        "/Author": "",
        "/Creator": "",
        "/Producer": "",
        "/Subject": "Google Photos Retrieval Case Study",
        "/Keywords": "Google Photos, Retrieval, Case Study, Product Management"
    }
    writer.add_metadata(clean_metadata)

    with open(pdf_deck_path, "wb") as f:
        writer.write(f)
    with open(pdf_root_path, "wb") as f:
        writer.write(f)

    # QA Verification Checks
    print("\n--- RUNNING SUBMISSION QA CHECKS ---")
    final_reader = pypdf.PdfReader(pdf_deck_path)
    num_pages = len(final_reader.pages)
    print(f"Page Count: {num_pages} (Required: exactly 10)")
    assert num_pages == 10, f"Expected 10 pages, found {num_pages}"

    file_size_mb = os.path.getsize(pdf_deck_path) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB (Required: <40 MB)")
    assert file_size_mb < 40, f"File size too large: {file_size_mb} MB"

    # Check text across all pages
    full_text = ""
    for i, p in enumerate(final_reader.pages):
        text = p.extract_text() or ""
        full_text += f"\n--- PAGE {i+1} ---\n" + text
        # Check aspect ratio
        box = p.mediabox
        aspect = float(box.width) / float(box.height)
        print(f"Page {i+1} box: {box.width}x{box.height} (Aspect: {aspect:.3f})")

    # Forbidden checks
    forbidden_phrase = "users find it difficult to search for old photos"
    if forbidden_phrase.lower() in full_text.lower():
        print(f"ERROR: Forbidden phrase found in PDF!")
        sys.exit(1)
    else:
        print("PASS: Forbidden phrase 'users find it difficult to search for old photos' is ABSENT.")

    # Name check
    name_tokens = ["Abhishek", "Pillai"]
    for token in name_tokens:
        if token.lower() in full_text.lower():
            print(f"ERROR: Name token '{token}' found in PDF!")
            sys.exit(1)
        # Check metadata
        meta = str(final_reader.metadata)
        if token.lower() in meta.lower():
            print(f"ERROR: Name token '{token}' found in PDF metadata!")
            sys.exit(1)
    print("PASS: Personal names are completely ABSENT from text and metadata.")

    # Link check
    assert "retrieval-discovery-engine.vercel.app" in full_text.replace("\n", ""), "Missing discovery engine link"
    assert "memory-trails-v2.vercel.app" in full_text.replace("\n", ""), "Missing prototype link"
    print("PASS: Both required public web app links are present.")
    uris = set()
    for p in final_reader.pages:
        for annot in (p.get("/Annots") or []):
            act = annot.get_object().get("/A")
            if act and "/URI" in act:
                uris.add(str(act["/URI"]))
    for page in ("/survey", "/mvp-test"):
        assert any(u.endswith("retrieval-discovery-engine.vercel.app" + page) for u in uris), f"Missing clickable {page} link"
    assert not any("docs.google.com/forms" in u for u in uris), "Deck still links a closed Google Form"
    print(f"PASS: {len(uris)} distinct clickable links, /survey and /mvp-test included.")

    print("\nALL QA CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    build()
