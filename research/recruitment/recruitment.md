# Interview recruitment — Google Photos retrieval study

**Target:** 6 booked, 5 usable · **Interview window:** Sep 29 – Oct 2 · **MVP follow-up:** Oct 1–4 · **Post by:** Sep 28 (re-dated; was Sep 18)
**Quota:** at least 3 of 6 must mix Hindi/English day to day (tests H4)

Funnel maths: expect ~40% of screener responses to qualify, ~70% of invites to book, ~80% of
bookings to show. To land 6 usable interviews, aim for **~25–30 screener responses**. Post to more
than one channel on day one; a single LinkedIn post will not clear this on its own.

---

## 1. Where to post (ranked by yield for this profile)

| Channel | Why | Watch out |
|---|---|---|
| **WhatsApp / personal network** | Fastest bookings, highest show rate, easiest Hinglish quota | Skews to people who know you — fine for a case study, say so in the deck |
| **LinkedIn post** | Good reach among 2+ year, large-library users | Slow burn; post in the morning IST |
| **r/googlephotos, r/india, r/bangalore** | Exactly the right users | **Most subs require mod approval for research recruitment — message mods first or the post gets removed** |
| **College / fellowship Slack + WhatsApp groups** | Peers will actually reply | May over-sample PMs; they make poor "typical user" participants |

---

## 2. The post

### Short version (WhatsApp / Slack)

> Looking for 6 people for a 40-minute video call about **finding old photos on Google Photos**
> — the times you know the photo exists but can't get search to surface it.
>
> You'd fit if you've used Google Photos 2+ years, have a big library (5,000+ photos), and have
> had a search fail or take forever in the last 3 months.
>
> You will **never share or show your photos** — camera stays off for that part, and you just tell
> me what you typed and what came back. It's for a product case study, not for Google.
>
> 2-minute form: [FORM LINK] · Slots Sep 29 – Oct 2.

### LinkedIn version

> Someone wrote online that they searched their own photo library for their cat's name, and not
> one of the results was even an animal. Someone else went looking for a picture of themselves and
> got a photo of Emilia Clarke instead.
>
> **I'm looking for 6 people who have lost a photo inside their own library — and I'd like 40
> minutes of your time.**
>
> Not "search is hard" in the abstract. The specific thing: you *know* the photo exists. You
> remember the trip, or the week you were ill, or who was standing next to you. And you still
> cannot get it to come up.
>
> This is for an independent product case study. It is not affiliated with Google or Apple.
> 40 minutes, video call, sometime between **29 September and 2 October**.
>
> **You'd fit if:**
> · **Google Photos is where you go to find an old photo** — or you use Google and Apple Photos
>   about equally, which is even more useful to me
> · You've been using it **2+ years**, with **5,000+ photos and videos**
> · In the **last 3 months** a search failed, or took far longer than it should have
>
> **Privacy, plainly:** I never see your photos. For the hands-on part your camera stays off and
> you run the searches yourself, on your own phone — you tell me what you typed and what came
> back. No screen share, no names, nothing recorded that identifies you. Your contact details are
> used to send the invite and then deleted.
>
> **2-minute screener:** [FORM LINK]
>
> If you take part I'll share what I find with you. If you don't fit but know someone who fills
> their phone with receipts, prescriptions and whiteboard photos — please send this their way.
> Those are the ones nobody can ever find again.
>
> #productmanagement #userresearch

**Why this version:** it opens with two real failures from public discussion rather than an
abstract claim, because a concrete image is what makes someone stop scrolling. It names Apple
Photos explicitly so "both" users self-identify instead of assuming the study is not for them, and
it ends by asking for a referral of *utility-photo* people — receipts, prescriptions, whiteboards —
who the engine showed are the hardest hit and the least likely to volunteer on their own.

### Reddit version

Same as LinkedIn, minus the last line, plus:
> Mods: happy to remove if this isn't allowed — messaged first / checked the rules.

---

## 3. Screener form (Google Forms)

**Don't build this by hand.** `research/recruitment/screener_form.gs` creates the whole form in about two
minutes: open script.google.com → New project → paste the file → Run → approve the prompt →
View → Logs prints the live link. Paste that link into the three `[FORM LINK]` placeholders above.

The script is the source of truth for wording; the table below is the summary.

Keep it to these 9 questions. Every extra question costs responses.

| # | Question | Type | Qualifies if |
|---|---|---|---|
| **1** | **Which app do you mainly use to look back at your photos?** | **Google Photos** / Apple Photos / **Both** / Something else | **Google Photos or Both** |
| 2 | How long have you been using it? | <1 yr / 1–2 yrs / **2+ yrs** | 2+ yrs |
| 3 | Roughly how many photos and videos are in it? (Settings shows this) | <1,000 / 1,000–5,000 / **5,000–20,000** / **20,000+** | 5,000+ |
| 4 | In the **last 3 months**, have you searched for a specific older photo and failed to find it, or taken far longer than expected? | **Yes** / No / Can't remember | Yes |
| 5 | If yes — what were you looking for, and what did you type? (one or two lines) | Short answer | **Quality signal: a concrete answer here is the single best predictor of a usable interview. Vague answers → deprioritise.** |
| 6 | Day to day, do you mix Hindi and English when you type or talk? | Mostly English / **Mix of both** / Mostly Hindi | Tracks the 3-of-6 quota |
| 7 | Which phone do you use? | Android / iPhone / Both | Balance, not a filter |
| 8 | Which slots work Sep 29 – Oct 2? (pick all) | Checkboxes, 8 slots | — |
| 8b | Open to a 15-min MVP follow-up Oct 1–4? | Yes / Maybe / No | Part 6: pick 3 returners from Yes |
| 9 | Email or WhatsApp number to send the invite | Short answer | — |

**Q1 has to come first.** Asking "how long have you used Google Photos" presupposes that they do.
It is also the cheapest disqualifier — an Apple-Photos-only user is not the brief's segment, and
finding that out in question 1 costs them nothing. **"Both, about equally" qualifies and is the most
valuable answer**: those participants can compare the two directly, which no engine post can.

**Form header text:**
> 2 minutes. I'm looking for people who've had trouble finding an old photo in Google Photos, for a
> 40-minute conversation between Sep 29 and Oct 2, and an optional 15-minute prototype follow-up Oct 1–4. You will never share or show your photos. Independent
> product case study, not affiliated with Google. Your contact details are used only to send the
> invite and are deleted after the study.

**Selection rule:** sort qualified responses by the quality of Q5, then fill so that ≥3 of the 6
answered "Mix of both" on Q6. Invite 8–10 to book 6.

---

## 4. Consent line (read at the start of the call)

> This is for a product case study, independent of Google. I'll take written notes but no recording
> unless you'd like one. Nothing that identifies you goes in the write-up — no name, no employer, no
> photos. For the hands-on part your camera is off and you drive your own phone; I only hear what you
> typed and what came back. You can skip any question or stop at any point. Fine to go ahead?

---

## 5. Open items for you

- [x] **Compensation: none** (decided 28 Sep). Was: decide and add to the post if yes (a ₹300–500 voucher typically doubles
      response rate; unpaid works for personal network). Left blank deliberately. If you decide yes,
      uncomment the line marked `COMPENSATION` in `research/recruitment/screener_form.gs` **before** running it.
- [ ] **Run `research/recruitment/screener_form.gs`** at script.google.com, then paste the live link into the three `[FORM LINK]` placeholders above
- [ ] Message subreddit mods **before** posting there
- [ ] Set up a booking link (Calendly free tier) or just confirm slots by hand from Q7
