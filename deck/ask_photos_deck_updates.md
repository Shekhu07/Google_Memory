# Proposed Deck Updates: Positioning Memory Trails Inside Ask Photos

> **Status:** Draft recommendations for your review.  
> **Instructions:** No changes have been made to `deck/build_deck.py` or `deck/index.html`. Review the proposed copy diffs below and apply the ones you like directly into `deck/build_deck.py`.

---

## Executive Summary: The Core Message

**Memory Trails is not a standalone competitor or detached parallel search.**  
It is the **episodic memory re-entry and recovery surface integrated directly inside Google Photos’ Ask Photos feature**.

- **Ask Photos (Gemini)** handles **expression / intake** — letting users type or speak natural-language memories.
- **Memory Trails** handles **surfacing, recognition, and recovery** — decomposing conversational queries into editable clue chips, clustering photos into coherent moments/episodes, providing explainable match evidence, and offering the *"What was off?"* repair loop when the initial answer is only "related."

---

## Slide-by-Slide Proposed Diffs for `deck/build_deck.py`

### 1. Slide 6: Problem & Solution Rationale (Lines ~774–788)

#### Context
Slide 6 contrasts existing solutions (Classic Search, Ask Photos, Apple Photos) against Memory Trails. It is the perfect place to establish that Memory Trails is **part of** Ask Photos rather than an external tool.

#### Current Code in `deck/build_deck.py`
```html
          <table class="data-table" style="margin-bottom: 6px;">
            <thead><tr><th style="width: 24%;">Option</th><th style="width: 34%;">Good at</th><th>Gap for a vague memory</th></tr></thead>
            <tbody>
              <tr><td>Photos search</td><td>People, places, things, dates</td><td>Memory must become search terms</td></tr>
              <tr><td>Ask Photos</td><td>Plain-language questions</td><td>All 7 who tried: "related, not the one"</td></tr>
              <tr><td>Apple Photos</td><td>Describing the photo</td><td>Describes items, not when it was</td></tr>
              <tr class="highlight"><td>Memory Trails</td><td>Rough time → moments</td><td>Recognise, then recover the moment</td></tr>
            </tbody>
          </table>
          <p style="margin: 0 0 4px 0;"><strong>Ask Photos</strong> helps people ask; we help them spot the right moment when its answer is only related.</p>
```

#### Proposed Update
```html
          <table class="data-table" style="margin-bottom: 6px;">
            <thead><tr><th style="width: 24%;">Option</th><th style="width: 34%;">Good at</th><th>Role &amp; Gap for a vague memory</th></tr></thead>
            <tbody>
              <tr><td>Photos search</td><td>People, places, things, dates</td><td>Requires exact terms; fails when words or dates are forgotten</td></tr>
              <tr><td>Ask Photos (alone)</td><td>Conversational questions</td><td>Good intake; returns flat photos (all 7 tested: "related, not mine")</td></tr>
              <tr><td>Apple Photos</td><td>Visual scene description</td><td>Matches items; lacks episodic clustering or time-window recovery</td></tr>
              <tr class="highlight"><td>Memory Trails</td><td>Moments &amp; repair inside Ask Photos</td><td>Decomposes vague prompts into editable clues &amp; recognisable moments</td></tr>
            </tbody>
          </table>
          <p style="margin: 0 0 4px 0;"><strong>Integrated Architecture:</strong> Ask Photos handles natural-language intake; Memory Trails provides the recognition and recovery layer inside Ask Photos when answers are only related.</p>
```

---

### 2. Slide 7: The MVP (Memory Trails) (Lines ~821–852)

#### Context
Slide 7 introduces the prototype screenshots and mechanics. Currently, the top card says:  
`"We recommend placing it inside Search, where it fails"`  
Updating this to explicitly name **Ask Photos** reinforces the product hierarchy.

#### Current Code in `deck/build_deck.py`
```html
    <div class="col-1-2">
      <div class="card card-blue" style="margin-bottom: 8px;">
        <div class="card-title" style="color: #1E40AF;">We recommend placing it inside Search, where it fails</div>
        <div class="card-body" style="font-size: 17pt;">
          <p style="margin: 0;">It doesn't ask for a perfect description; it helps you <strong>recognise the right moment from a short trail</strong>. A failed search offers <em>"Can't describe it?"</em> with the words carried over.</p>
        </div>
      </div>
```

#### Proposed Update
```html
    <div class="col-1-2">
      <div class="card card-blue" style="margin-bottom: 8px;">
        <div class="card-title" style="color: #1E40AF;">Placement: Built directly inside Ask Photos as the memory re-entry layer</div>
        <div class="card-body" style="font-size: 17pt;">
          <p style="margin: 0;">When a conversational question in <strong>Ask Photos</strong> describes an episodic memory or returns unconfirmed photos, Ask Photos activates <strong>Memory Trails</strong> with the query carried over—turning "related, not mine" into recognisable moments.</p>
        </div>
      </div>
```

#### Also on Slide 7: Sub-card Title & Bullet Points (Lines ~841–850)

#### Current Code in `deck/build_deck.py`
```html
      <div class="card" style="margin-top: 6px;">
        <div class="card-title">Our MVP: one AI step per failure; the user confirms</div>
        <div class="card-body" style="font-size: 17pt; line-height: 1.3;">
          <strong>Only a rough time</strong> → turns it into a date window<br>
          <strong>Mixed clues</strong> → editable chips, plus "I also heard: + dosa"<br>
          <strong>A flat grid</strong> → moments; full matches rank first<br>
          <strong>Why this one?</strong> → shows matched vs approximate clues<br>
          <strong>Wrong moment</strong> → nearby moments; undo a rule-out<br>
          <em>It never confirms for you, and can't always find the photo.</em>
        </div>
      </div>
```

#### Proposed Update
```html
      <div class="card" style="margin-top: 6px;">
        <div class="card-title">The MVP inside Ask Photos: one inspection step per failure; user confirms</div>
        <div class="card-body" style="font-size: 17pt; line-height: 1.3;">
          <strong>Vague memory prompt</strong> → decomposes into editable clue chips + staged suggestions<br>
          <strong>Approximate time</strong> → resolves into an active, centered calendar window<br>
          <strong>Flat photo response</strong> → clusters into coherent visual episodes; full matches rank #1<br>
          <strong>"Why this photo?"</strong> → transparent evidence panel showing matched vs approximate cues<br>
          <strong>"Related, not mine"</strong> → "What was off?" single-clue repair loop without starting over<br>
          <em>Runs within the Ask Photos shell; never auto-confirms without user verification.</em>
        </div>
      </div>
```

---

### 3. Slide 8: User Testing (Lines ~925–930 & Card Commentary)

#### Context
Slide 8 displays the 6 test users. Highlight that testers tested Ask Photos on their own libraries first, illustrating the gap Memory Trails solves.

#### Current Table Column Header:
`Own Photos search → result`

#### Proposed Table Column Header or Subtitle Note:
`Own Ask Photos / Search query → result`  
And in the takeaway box (right column, lines ~980–990):
```html
<p style="margin: 0 0 6px 0;"><strong>Ask Photos alone vs with Memory Trails:</strong> On their own devices, 3 of 3 Ask Photos queries returned "related photos, not mine". Inside the prototype, 5 of 6 found the exact moment by inspecting clue chips and episode cards.</p>
```

---

### 4. Slide 10: Risks & Limitations (Lines ~1139–1141)

#### Context
Risk R5 currently addresses whether Ask Photos alone already solves this.

#### Current Code in `deck/build_deck.py`
```html
<tr><td><strong>R5. Ask Photos may already suffice</strong></td><td>4 of 4 survey and 3 of 3 test users got "related photos, not the one".</td></tr>
```

#### Proposed Update
```html
<tr><td><strong>R5. Ask Photos may already suffice</strong></td><td>Ask Photos solves conversational intake, not visual recognition. In testing, 7 of 7 got "related, not mine". Memory Trails completes Ask Photos by adding episodic clustering and the repair loop.</td></tr>
```

---

## NextLeap Blind Grading & Compliance Checklist

When you apply these changes to `deck/build_deck.py`, ensure:
1. **No Personal Names:** Do NOT include author names (`Abhishek`, `Pillai`) anywhere in slide text or metadata.
2. **Forbidden Phrase Check:** Do NOT use the exact string `"users find it difficult to search for old photos"`.
3. **Font Size:** Maintain `font-size: 17pt` or greater on all cards and tables.
4. **Slide Count:** Exactly 10 slides (`<section class="slide">` elements).
5. **Re-compilation:** Run `.venv/bin/python deck/build_deck.py` to regenerate `deck/index.html` and `deck/NL_GooglePhotos.pdf`.
