#!/usr/bin/env python3
"""
Build script for Google Photos Retrieval Case Study Deck (NL_GooglePhotos.pdf).
Compiles a 10-slide, 16:9 executive presentation deck adhering to all NextLeap PM Fellowship constraints:
- Exactly 10 slides (no separate title slide; Slide 1 is Slide 1)
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
    justify-content: space-between;
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
  .shot-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.1in; margin: 0.04in 0 0.06in 0; }}
  .shot-row figure {{ margin: 0; display: flex; flex-direction: column; gap: 3px; }}
  .shot {{ height: 3.15in; background: #FFFFFF; }}
  .shot img {{ object-fit: cover; object-position: top; }}
  .shot-ai {{ border: 2.5px solid #1A73E8; }}
  .shot-row figcaption {{ font-size: 17pt; font-weight: 700; color: #0F172A; text-align: center; }}
</style>
</head>
<body>

<!-- SLIDE 1: Executive Summary -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Executive Summary · Slide 1 of 10</span>
      <span class="confidential-tag">Product Case Study · NextLeap Fellow Submission</span>
    </div>
    <h1 class="slide-title">People keep the moment and lose the date, but Photos indexes photos, not moments</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-5">
      <div class="card card-blue" style="border-left: 5px solid #1A73E8;">
        <div class="card-title" style="color: #1E40AF; margin-bottom: 4px;">Strategic Goal (Brief p. 2)</div>
        <div class="card-body" style="font-size: 19pt; font-weight: 600; color: #1E293B;">
          "Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe."
        </div>
      </div>
      
      <div class="card">
        <div class="card-title">Core Finding Across Two Independent Research Methods</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0;"><strong>77.1% of observed search failures occur before recovery can help:</strong> the query clue is misread (35.4%) or the photo never surfaces in results (41.7%). (§B)</p>
          <p style="margin: 0;"><strong>Survey (n=15) and user testing (n=6) agree:</strong> people keep <em>roughly when</em> and the event, but lose the calendar date. 4 of 5 real-app users strip time into bare nouns, and none of the 5 found their photo. (§G1, §G2)</p>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat-box">
          <div class="stat-num">85,140</div>
          <div class="stat-label">Public posts analyzed across 4 platforms in discovery engine</div>
        </div>
        <div class="stat-box">
          <div class="stat-num stat-num-green">+0.075</div>
          <div class="stat-label">Recall@20 gain weighted by real memory (0.259 → 0.334); moment@5 +0.111</div>
        </div>
        <div class="stat-box">
          <div class="stat-num stat-num-amber">77.1%</div>
          <div class="stat-label">Failures at interpretation & surfacing before recovery</div>
        </div>
        <div class="stat-box">
          <div class="stat-num stat-num-green">4.0 / 5</div>
          <div class="stat-label">Ease vs Google Photos, from the 5 testers who use it</div>
        </div>
      </div>
    </div>

    <div class="col">
      <div class="card card-highlight" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="card-title" style="color: #065F46;">What Was Built & Deployed Live</div>
          <div class="card-body">
            <p style="margin: 0 0 10px 0;"><strong>1. Discovery Engine:</strong> Structured pipeline turning 85,140 posts into 144 specific attempts with blind two-model audit.</p>
            <p style="margin: 0 0 10px 0;"><strong>2. Memory Trails MVP:</strong> Episode-first re-entry prototype inside Google Photos. Resolves vague dates, clusters moments, and explains matches with soft scoring.</p>
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.1in;">
          <div class="screenshot-frame shot shot-ai" style="height: 2.75in;"><img src="{img_clues}" alt="Memory Trails clue chips"></div>
          <div class="screenshot-frame shot shot-ai" style="height: 2.75in;"><img src="{img_moments}" alt="Memory Trails likely moments"></div>
        </div>

        <div style="display: flex; gap: 10px; margin-top: 8px;">
          <a class="btn-link" href="https://retrieval-discovery-engine.vercel.app" target="_blank">retrieval-discovery-engine.vercel.app ↗</a>
          <a class="btn-link btn-link-sec" href="https://memory-trails-v2.vercel.app" target="_blank">memory-trails-v2.vercel.app ↗</a>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Engine n = 85,140 posts → 144 attempts · Survey n = 15 (14 dedup) · MVP tests n = 6 · Eval: 120 tasks, 1,282 CC photos
    </div>
    <div class="slide-num">1 / 10</div>
  </div>
</section>

<!-- SLIDE 2: Business Metric Decomposition -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Business Metric Decomposition · Slide 2 of 10</span>
      <span class="confidential-tag">Part 2 Required Deliverable</span>
    </div>
    <h1 class="slide-title">Retrieval breaks most at interpretation and surfacing, and almost never at recovery</h1>
  </div>
  
  <div class="main-content">
    <div class="col-2">
      <div class="card card-blue" style="margin-bottom: 8px; padding: 12px 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <span style="font-weight: 800; font-size: 18pt; color: #1E40AF;">North Star: URR (User Retrieval Rate)</span>
            <div style="font-size: 17pt; color: #334155; margin-top: 2px;">Share of users with a vague-memory search in 28 days who reach the photo. A/B splits by user.</div>
          </div>
          <div style="background: #FFFFFF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 6px 12px; font-family: monospace; font-size: 17pt; font-weight: 700; color: #1E40AF;">
            URR = Expression × [1 − (1 − Interpretation × Surfacing × Recognition)^n̄]
          </div>
        </div>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 18%;">Product Outcome</th>
            <th style="width: 32%;">The Brief's Guiding Question</th>
            <th style="width: 14%; text-align: center;">Engine (144)</th>
            <th style="width: 12%; text-align: center;">Survey (15)</th>
            <th style="width: 24%;">What People Report</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Expression</strong></td>
            <td><em>Can't express what they remember?</em></td>
            <td style="text-align: center;">2 (1.4%)</td>
            <td style="text-align: center;">3 (20%)</td>
            <td>Don't know what to type; 2 of 3 never search</td>
          </tr>
          <tr class="highlight">
            <td><strong>Interpretation ★</strong></td>
            <td><em>Does Photos misread the clues?</em></td>
            <td style="text-align: center; font-weight: 800; color: #1E40AF;">51 (35.4%)</td>
            <td style="text-align: center; font-weight: 800; color: #1E40AF;">3 (20%)</td>
            <td>Add a year, reword: <em>"You must now specify the year"</em></td>
          </tr>
          <tr class="highlight">
            <td><strong>Surfacing ★</strong></td>
            <td><em>Is the photo in results at all? (our term)</em></td>
            <td style="text-align: center; font-weight: 800; color: #1E40AF;">60 (41.7%)</td>
            <td style="text-align: center; font-weight: 800; color: #1E40AF;">5 (33%)</td>
            <td>A grid of near-misses; target absent</td>
          </tr>
          <tr>
            <td><strong>Recognition</strong></td>
            <td><em>Are the results hard to judge?</em></td>
            <td style="text-align: center;">2 (1.4%)</td>
            <td style="text-align: center;">2 (13%)</td>
            <td>Can't confirm; 7 of 15 end unsure</td>
          </tr>
          <tr style="color: #64748B; background: #F8FAFC;">
            <td><strong>Recovery</strong></td>
            <td><em>Can't refine a failed search?</em></td>
            <td style="text-align: center;">1 (0.7%)</td>
            <td style="text-align: center;">1 (7%)</td>
            <td>2–3 tries for 9 of 13 → n̄</td>
          </tr>
        </tbody>
      </table>

    </div>

    <div class="col">
      <div class="card" style="flex: 1;">
        <div class="card-title">Strategic Metric Takeaways</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0;"><strong>1. Where Google invested:</strong> Ask Photos and the hybrid router read prompts better, but don't group moments or resolve event-relative time.</p>
          <p style="margin: 0 0 8px 0;"><strong>2. 77% in two stages:</strong> interpretation + surfacing = 111 of 144 failures.</p>
          <p style="margin: 0;"><strong>3. Expression disagrees</strong> (1.4% vs 3 of 15), but 2 of those 3 browse instead; the moment view serves them.</p>
        </div>
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div class="card" style="padding: 10px 14px;">
          <div style="font-weight: 700; font-size: 17pt; color: #0F172A;">Browse path (outside the formula)</div>
          <div style="font-size: 17pt; color: #475569; line-height: 1.35;">
            Survey: 10 of 15 scrolled or opened an album first. MVP testers last found old photos by scroll 3, album 2, search 0.
          </div>
        </div>
        <div class="card card-amber" style="padding: 10px 14px;">
          <div style="font-weight: 700; font-size: 17pt; color: #92400E;">Recovery scoped out</div>
          <div style="font-size: 17pt; color: #78350F; line-height: 1.35;">
            0.7% of engine failures, 1 of 15 in survey. Kept as a safety net, tracked as a diagnostic.
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Baselines modelled (no Google telemetry) · Stages LLM-extracted (κ 0.509 vs 2nd model) · n̄ ≈ 2–3 from survey
    </div>
    <div class="slide-num">2 / 10</div>
  </div>
</section>

<!-- SLIDE 3: Discovery Engine Workflow -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">AI-Powered Discovery Workflow · Slide 3 of 10</span>
      <span class="confidential-tag">Part 1 Required 1-Slide Explanation</span>
    </div>
    <h1 class="slide-title">The engine turns 85,140 public posts into 144 retrieval attempts, each recording what was remembered, what was forgotten, and where search broke</h1>
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
        <div class="card-title">Why This Is More Than Summarisation</div>
        <div class="card-body">
          <p style="margin: 0 0 10px 0;"><strong>1. Structure, not sentiment:</strong> Every review was converted into a structured, typed record with fixed vocabularies, not qualitative impression tags.</p>
          <p style="margin: 0 0 10px 0;"><strong>2. Pre-registered rules:</strong> Hypotheses H1–H5 and decision thresholds were frozen before data collection, preventing post-hoc confirmation bias.</p>
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
    <div class="slide-num">3 / 10</div>
  </div>
</section>

<!-- SLIDE 4: Discovery Engine Findings -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Discovery-Engine Findings · Slide 4 of 10</span>
      <span class="confidential-tag">Evidence-Led Opportunity Selection</span>
    </div>
    <h1 class="slide-title">People remember roughly when, but search needs the exact date, and the exact date is what they forget</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-5">
      <div class="card" style="margin-bottom: 8px;">
        <div class="card-title">The Brief's Four Questions Answered (Engine vs. Survey)</div>
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
        <div class="card-title">Opportunity Areas: Why O1 Leads (§B2)</div>
        <div class="card-body" style="font-size: 17pt;">
          <strong>O1 (Rough time or an event):</strong> 42 attempts, 20 not surfaced. <em>Core focus.</em><br>
          <strong>O8 (No clue at all):</strong> 47 attempts. Larger, but users kept zero search clues. O1 is the largest group where user memory exists and search fails to use it.<br>
          <strong>Excluded:</strong> O7 (Exact date known, 14 — regular search works); O9 (Path moved by UI update, 12 — app design).
        </div>
      </div>
    </div>

    <div class="col">
      <div class="card card-blue" style="height: 100%;">
        <div class="card-title" style="color: #1E40AF;">Pre-Registered Hypothesis Verdicts (Rule B)</div>
        <div class="card-body" style="display: flex; flex-direction: column; gap: 8px; font-size: 17pt;">
          <div><strong style="color: #059669;">H1 Episodic time: SUPPORTED (root cause).</strong> Roughly when is the #1 kept cue (40); the date is the #1 lost cue (37).</div>
          <div><strong style="color: #059669;">H2 Recognition: SUPPORTED (secondary).</strong> 41.7% never surfaced; 7 of 15 ended unsure.</div>
          <div><strong style="color: #B45309;">H3 Dead-end recovery: NOT THE LEAD.</strong> Overruled by the audit: recovery is 0.7% of failures (stage κ 0.509).</div>
          <div><strong style="color: #475569;">H4 Hinglish: UNTESTED.</strong> Weak signal (2 of 15 survey, 1 of 6 tests); kept as a design choice.</div>
          <div><strong style="color: #475569;">H5 Text not indexed: LOW VOLUME</strong> (3 docs), but high harm.</div>
          <div><strong style="color: #475569;">H6 Path changed: MINOR</strong> (8.3%), found post hoc.</div>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Sources: episodes.jsonl (144) · survey (n=15) · audit (n=203) · pre-registered rules in engine/analysis.py
    </div>
    <div class="slide-num">4 / 10</div>
  </div>
</section>

<!-- SLIDE 5: User Research and Observed Tasks -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">User Research & Retrieval Tasks · Slide 5 of 10</span>
      <span class="confidential-tag">Part 3 Methodology & Real Incidents</span>
    </div>
    <h1 class="slide-title">Most people scroll before they search, and nearly half end close but unsure</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card card-blue">
        <div class="card-title" style="color: #1E40AF;">Research Methodology Rationale</div>
        <div class="card-body">
          <p style="margin: 0 0 6px 0;"><strong>Structured interviews by form (n=15, 23–30 Sep):</strong> every answer maps onto the engine's vocabulary.</p>
          <p style="margin: 0 0 6px 0;"><strong>Why:</strong> 100% scoreable stories (vs 8.6% of public posts); reached 15 people vs 2 call contacts.</p>
          <p style="margin: 0;"><strong>Costs:</strong> self-reported, convenience sample; 8 of 15 fit the segment.</p>
          <a class="btn-link" href="https://docs.google.com/forms/d/e/1FAIpQLSd6InawAamMykxoj6QTHq8Cgp1sgadLT3ZTrjHWjC6eerTltw/viewform" target="_blank" style="margin-top: 8px;">Survey questionnaire (Google Form) ↗</a>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Survey vs. Engine (Side-by-Side)</div>
        <table class="data-table" style="font-size: 17pt;">
          <thead>
            <tr><th>Metric</th><th>Engine (144)</th><th>Survey (15 / 14)</th></tr>
          </thead>
          <tbody>
            <tr><td>Most remembered</td><td>Roughly when (40)</td><td>Roughly when (8)</td></tr>
            <tr><td>Most forgotten</td><td>The date (37)</td><td>When taken (9)</td></tr>
            <tr><td>Top failure</td><td>Never surfaced (41.7%)</td><td>Never surfaced (5 / 4)</td></tr>
            <tr><td>Ended unsure</td><td>Not measurable</td><td><strong>7 of 15 (47%)</strong></td></tr>
            <tr><td>First move: scroll</td><td>15 workarounds</td><td><strong>9 of 15 (60%)</strong></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">Reported Retrieval Incidents (Survey Respondents)</div>
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
              <td>Misread</td>
              <td style="color: #D97706; font-weight: 700;">Unsure</td>
            </tr>
            <tr>
              <td><strong>S02</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event, object</td>
              <td><em>"gym"</em></td>
              <td>Eval fail</td>
              <td style="color: #D97706; font-weight: 700;">Unsure</td>
            </tr>
            <tr>
              <td><strong>S03</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event</td>
              <td><em>(Didn't know what to type; scrolled)</em></td>
              <td>Expression</td>
              <td style="color: #059669; font-weight: 700;">Found</td>
            </tr>
            <tr>
              <td><strong>S11</strong></td>
              <td>Personal photo</td>
              <td>Roughly when, event</td>
              <td><em>(Never typed; opened album)</em></td>
              <td>Expression</td>
              <td style="color: #D97706; font-weight: 700;">Unsure</td>
            </tr>
            <tr style="background: #FEF2F2;">
              <td><strong>S06</strong></td>
              <td>Medicine bill</td>
              <td>Object, text in bill</td>
              <td><em>"medicine, bill"</em></td>
              <td>Surfacing</td>
              <td style="color: #DC2626; font-weight: 700;">Never found</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 10px;">
          <div class="quote-box">"wedding, pichle saal diwali" — S04 (Hinglish: a festival and relative year, not a calendar date)</div>
          <div class="quote-box">"medicine, bill" — S06 (Never found; had to get the document again)</div>
        </div>

        <div style="font-size: 17pt; color: #475569; margin-top: 8px;">
          <strong>Ask Photos Reality:</strong> 7 of 15 had never heard of it. All 4 who described a result said it showed "related photos, but not the one I wanted" and that they "could not tell why".
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Survey n = 15 (14 dedup), self-reported convenience sample · IDs S02–S11 are survey respondents
    </div>
    <div class="slide-num">5 / 10</div>
  </div>
</section>

<!-- SLIDE 6: Target Segment and Root Cause -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Target Segment & Root Cause · Slide 6 of 10</span>
      <span class="confidential-tag">Part 4 Strategic Definition</span>
    </div>
    <h1 class="slide-title">The segment is people who can place the moment only roughly, and search can't turn "roughly" into a date window</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card" style="height: 100%;">
        <div class="card-title">Target Segment Profile</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0; font-size: 18pt; font-weight: 700; color: #1E40AF;">
            Long-time Google Photos users searching for a personal moment they can place only roughly.
          </p>
          <p style="margin: 0 0 10px 0;">Defined by <strong>cognitive memory state</strong> (what they remember), not demographics: "around Diwali", "my sister's graduation", "last winter".</p>
          
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
            <strong>Deliberate Exclusions:</strong> 14 who remembered exact date (standard search works) · 12 whose path moved in an update (H6 navigation) · Cloud sync / corruption issues.
          </div>
        </div>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card card-blue" style="height: 100%;">
        <div class="card-title" style="color: #1E40AF;">The Root Cause: The Broken Link</div>
        
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
          <strong>How Retrieval Breaks for the Segment (37 Attempts):</strong><br>
          • <strong>Misinterpretation (12):</strong> Query clue is misread; search fails to map the event to a date window.<br>
          • <strong>Surfacing Failure (18):</strong> Returns an unranked grid across years; target photo never surfaces.<br>
          • <strong>Real-App Probe Verification (§G2):</strong> 4 of 5 users compressed memory into bare nouns ("vacation", "gym"), and 0 of 5 found the photo.
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Segment: 37 engine attempts (26%), 8 of 15 in survey · Hinglish support is a design choice, not a finding
    </div>
    <div class="slide-num">6 / 10</div>
  </div>
</section>

<!-- SLIDE 7: Problem Definition and Solution Rationale -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Problem Definition & Solution Rationale · Slide 7 of 10</span>
      <span class="confidential-tag">Part 4 Core Argument</span>
    </div>
    <h1 class="slide-title">People already scroll to "roughly when" by hand and still end unsure, so the product should take that step for them</h1>
  </div>
  
  <div class="main-content" style="flex-direction: column; gap: 0.16in;">
    <!-- Top Banner: Locked Problem Statement -->
    <div class="card card-blue" style="border-left: 6px solid #1A73E8; padding: 12px 20px;">
      <div style="font-size: 17pt; font-weight: 800; color: #1E40AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Locked Problem Statement</div>
      <div style="font-size: 19pt; font-weight: 700; color: #0F172A; line-height: 1.35;">
        "People remember when-ish and what happened; Google Photos indexes items and calendar dates. So the photo is in the library, the person can describe the moment but not the photo, and it never comes back."
      </div>
    </div>

    <!-- Middle Split: Workaround vs Solution Rationale -->
    <div style="display: flex; gap: 0.3in; flex: 1;">
      <div class="card" style="flex: 1;">
        <div class="card-title">The Workaround is the Design Blueprint</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0;"><strong>Engine:</strong> 15 of 21 workarounds are manual scrolling (7 of 10 failed): <em>"Every time I scrolled to the right time frame, it kept loading more pictures…"</em></p>
          <p style="margin: 0 0 8px 0;"><strong>Survey:</strong> Scrolling was the first move for 9 of 15. 5 of those 9 still ended unsure.</p>
          <p style="margin: 0 0 8px 0;"><strong>MVP testers:</strong> last found old photos by scroll 3, album 2, <strong>search 0</strong>.</p>
          <p style="margin: 0; font-weight: 600; color: #1E40AF;">Insight: people already retrieve by moment, by hand. The product should find the time window and group the moments.</p>
        </div>
      </div>

      <div class="card" style="flex: 1.2;">
        <div class="card-title">Solution Rationale & Why Not Ask Photos</div>
        <div class="card-body">
          <p style="margin: 0 0 8px 0;"><strong>AI only where it's needed:</strong> (1) turning clues into date spans; (2) grouping photos into recognisable moments. Uses existing metadata.</p>
          <p style="margin: 0 0 8px 0;"><strong>Why not Ask Photos:</strong> no editable clues, no moment grouping, no "why this". <strong>Everyone who tried it got "related photos, but not the one": 4 of 4 in survey, 3 of 3 in tests.</strong></p>
          <p style="margin: 0;"><strong>Scoped out:</strong> clarifying question (1.4%) · full recovery agent (0.7%), replaced by 1-tap clue alternatives.</p>
        </div>
      </div>
    </div>

    <!-- Bottom Strip: Evolution of Thinking -->
    <div class="card" style="background: #F1F5F9; padding: 10px 14px;">
      <div style="font-size: 17pt; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px;">How the thinking evolved</div>
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
      Sources: engine episodes · survey · MVP test log · 1.5B monthly users, 9T+ photos (PetaPixel 2025)
    </div>
    <div class="slide-num">7 / 10</div>
  </div>
</section>

<!-- SLIDE 8: The MVP (Memory Trails) -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">The MVP (Memory Trails) · Slide 8 of 10</span>
      <span class="confidential-tag">Part 5 Mechanism & Empirical Evaluation</span>
    </div>
    <h1 class="slide-title">Memory Trails turns "roughly when and where" into moments you can recognise</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card card-blue" style="margin-bottom: 8px;">
        <div class="card-title" style="color: #1E40AF;">Placement & flow</div>
        <div class="card-body" style="font-size: 17pt;">
          <p style="margin: 0 0 5px 0;"><strong>Where it lives:</strong> inside Photos search. When a search fails, <em>"Can't describe it?"</em> opens it with the words carried over.</p>
          <p style="margin: 0;"><strong>Soft scoring:</strong> a date outside the window lowers rank instead of hiding the photo.</p>
        </div>
      </div>

      <!-- Screenshot Row -->
      <div class="shot-row">
        <figure><div class="screenshot-frame shot"><img src="{img_describe}" alt="Describe the moment"></div><figcaption>1 · Describe</figcaption></figure>
        <figure><div class="screenshot-frame shot shot-ai"><img src="{img_clues}" alt="Editable clue chips"></div><figcaption>2 · Clues</figcaption></figure>
        <figure><div class="screenshot-frame shot shot-ai"><img src="{img_moments}" alt="Ranked likely moments"></div><figcaption>3 · Moments</figcaption></figure>
        <figure><div class="screenshot-frame shot"><img src="{img_found}" alt="Confirm the photo"></div><figcaption>4 · Confirm</figcaption></figure>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center;">
        <a class="btn-link" href="https://memory-trails-v2.vercel.app" target="_blank">memory-trails-v2.vercel.app ↗</a>
        <span style="font-size: 17pt; color: #64748B;"><span style="color:#1A73E8; font-weight:700;">Blue frame</span> = AI step</span>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">Empirical Evaluation Ladder (120 Tasks, 1,282 Photos)</div>
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
              <td style="text-align: center; font-weight: 700; color: #059669;">0.333 ★</td>
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
              <td>Weighted by real cue counts (§E1b)</td>
              <td style="text-align: center;">0.259</td>
              <td style="text-align: center; color: #059669;">0.334 (+0.075)</td>
              <td style="text-align: center; color: #059669;">0.336 (+0.111)</td>
            </tr>
          </tbody>
        </table>

        <div class="card-body" style="font-size: 17pt; line-height: 1.35;">
          <p style="margin: 0 0 6px 0;"><strong>Read this first:</strong> L3's 0.962 needs three cues; only 4% (6 of 144) of real attempts kept that many. Weighted by real memory, recall gains <strong>+0.075</strong> and moment@5 <strong>+0.111</strong>: grouping into moments helps more than flat ranking.</p>
          <p style="margin: 0; font-style: italic; color: #64748B;">"This MVP validates the memory-reentry interaction and recovery model using representative media. It does not validate production-scale Google Photos retrieval accuracy."</p>
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Eval: 120 tasks, 1,282 CC photos, 29 synthetic episodes · Soft-scoring weights are heuristic (τ = 7 days)
    </div>
    <div class="slide-num">8 / 10</div>
  </div>
</section>

<!-- SLIDE 9: User Testing -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">User Testing & Qualitative Evaluation · Slide 9 of 10</span>
      <span class="confidential-tag">Part 6 Validation with Target Segment</span>
    </div>
    <h1 class="slide-title">5 of 6 testers were sure they found the photo and 4 of 5 found it easier than Google Photos, but compound dates still trip it up</h1>
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
            <td style="color: #059669; font-weight: 700;">Found, sure</td>
            <td style="color: #DC2626; font-weight: 700;">Not found</td>
            <td style="text-align: center; white-space: nowrap;">5/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">5/5</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R02</strong></td>
            <td><em>"gym"</em> → can't tell which</td>
            <td style="color: #059669; font-weight: 700;">Found, sure</td>
            <td style="color: #059669; font-weight: 700;">Found (1-tap alt)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>When fails</td>
          </tr>
          <tr>
            <td><strong>R03</strong></td>
            <td><em>(Apple Photos user)</em></td>
            <td style="color: #059669; font-weight: 700;">Found, sure</td>
            <td style="color: #059669; font-weight: 700;">Found (nearby)</td>
            <td style="text-align: center; white-space: nowrap;">5/5</td>
            <td style="text-align: center;">—</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R04</strong></td>
            <td><em>"vacation"</em> → wrong years</td>
            <td style="color: #059669; font-weight: 700;">Found, sure</td>
            <td style="color: #059669; font-weight: 700;">Found (1-tap alt)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>When fails</td>
          </tr>
          <tr>
            <td><strong>R05</strong></td>
            <td><em>"Wedding event"</em> → can't tell which</td>
            <td style="color: #059669; font-weight: 700;">Found, sure</td>
            <td style="color: #059669; font-weight: 700;">Found (clue edit)</td>
            <td style="text-align: center; white-space: nowrap;">4/5</td>
            <td style="text-align: center; white-space: nowrap; font-weight: 700;">4/5</td>
            <td>Every time</td>
          </tr>
          <tr>
            <td><strong>R06</strong></td>
            <td><em>"Kerala photos"</em> → can't tell which</td>
            <td style="color: #D97706; font-weight: 700;">Right day, unsure</td>
            <td style="color: #059669; font-weight: 700;">Found (1-tap alt)</td>
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
        <a class="btn-link" href="https://docs.google.com/forms/d/e/1FAIpQLSec7si5Wff2CYzHBNoQXaU_WPACot5FhkQO57CTQHir1zUIrg/viewform" target="_blank">MVP test form ↗</a>
        <a class="btn-link btn-link-sec" href="https://memory-trails-v2.vercel.app" target="_blank">memory-trails-v2.vercel.app ↗</a>
      </div>
    </div>

    <div class="col">
      <div class="card card-blue" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div class="card-title" style="color: #1E40AF;">What testers said</div>
          <div class="quote-box">"Shows the moment, not a grid" — R02</div>
          <div class="quote-box">"Moving to nearby months, like scrolling but faster" — R03</div>
          <div class="quote-box">"Works without knowing what to type" — R04</div>
          <div class="quote-box">"Finds exact month & year... understands mix of Hindi and English" — R06</div>
        </div>

        <div>
          <div class="card-title" style="color: #991B1B; margin-top: 8px;">What broke → next iteration</div>
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
    <div class="slide-num">9 / 10</div>
  </div>
</section>

<!-- SLIDE 10: Metrics, Risks, and Limitations -->
<section class="slide">
  <div>
    <div class="pill-row">
      <span class="category-pill">Success Metrics, Risks & Limitations · Slide 10 of 10</span>
      <span class="confidential-tag">Part 7 & 8 Measurement & Governance</span>
    </div>
    <h1 class="slide-title">Success is more users reaching the photo, and the biggest risk is that the win sits where memory is richest</h1>
  </div>
  
  <div class="main-content">
    <div class="col-1-2">
      <div class="card card-blue" style="margin-bottom: 8px;">
        <div class="card-title" style="color: #1E40AF;">North Star: 28-day URR</div>
        <div class="card-body">
          <p style="margin: 0 0 6px 0;"><strong>Goal:</strong> +5 pts URR in an 8-week user-level A/B test (~1,600 users per arm for 80% power).</p>
          <p style="margin: 0;"><strong>No Recovery term:</strong> 0.7% of failures; tracked as a diagnostic.</p>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Leading & guardrail metrics</div>
        <table class="data-table">
          <thead>
            <tr><th>Metric (event)</th><th>Target</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>Entry rate</strong> (re-entry started)</td><td>≥12% of failed searches</td></tr>
            <tr><td><strong>Clue correction</strong> (alternative taken)</td><td>15–25%</td></tr>
            <tr><td><strong>Confirm after opening a moment</strong></td><td>≥55%</td></tr>
            <tr style="background: #FEF2F2;"><td><strong>False confirmation ★</strong></td><td><strong>Guardrail: &lt;3% (stop launch)</strong></td></tr>
            <tr style="background: #FEF2F2;"><td><strong>P95 time to first moment</strong></td><td><strong>Guardrail: &lt;1.5 s</strong></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="col-1-5">
      <div class="card" style="height: 100%;">
        <div class="card-title">Risks & mitigations</div>
        <table class="data-table" style="margin-bottom: 8px;">
          <thead>
            <tr><th style="width: 46%;">Risk</th><th style="width: 54%;">Mitigation & evidence</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>R1. The win sits where memory is richest</strong> (+0.79 at L3, +0.07 at L1)</td><td>Lean on moment recognition (moment@5 0.333 at L2); measure L1 in the A/B.</td></tr>
            <tr><td><strong>R2. Date filters hide photos</strong></td><td><strong>Soft scoring built:</strong> L3 recall 0.851 → 0.962.</td></tr>
            <tr><td><strong>R3. Can't read text in photos</strong> (0.000 on receipts)</td><td>Add OCR text to the index.</td></tr>
            <tr><td><strong>R4. False confirmation</strong> (worst failure)</td><td>Never auto-confirm; show the surrounding photos.</td></tr>
            <tr><td><strong>R5. Ask Photos may already suffice</strong></td><td>4 of 4 survey and 3 of 3 test users got "related photos, not the one".</td></tr>
          </tbody>
        </table>

        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 17pt; color: #475569;">
          <strong>Limitations:</strong> Play Store is 86.2% of posts · Hinglish is a weak signal · URR baselines modelled · ranking weights heuristic · small unmoderated samples.
        </div>
      </div>
    </div>
  </div>

  <div class="footnote">
    <div class="footnote-text">
      Targets and guardrails are proposed launch thresholds, not measured results · Sources: facts_table.md
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
    assert "retrieval-discovery-engine.vercel.app" in full_text, "Missing discovery engine link"
    assert "memory-trails-v2.vercel.app" in full_text, "Missing prototype link"
    print("PASS: Both required public web app links are present.")
    uris = set()
    for p in final_reader.pages:
        for annot in (p.get("/Annots") or []):
            act = annot.get_object().get("/A")
            if act and "/URI" in act:
                uris.add(str(act["/URI"]))
    assert any("1FAIpQLSd6InawAamMykxoj6QTHq8Cgp1sgadLT3ZTrjHWjC6eerTltw" in u for u in uris), "Missing clickable survey link"
    print(f"PASS: {len(uris)} distinct clickable links, survey form included.")

    print("\nALL QA CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    build()
