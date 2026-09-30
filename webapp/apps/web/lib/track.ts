/**
 * Instrumentation for the events the wireframe §8 requires.
 *
 * Deliberately client-side and in-memory: nothing is sent anywhere, and no event
 * ever carries the text a visitor typed. During a user-testing session a
 * facilitator reads the log from the browser console via `window.memoryTrails`.
 */
export type TrailEvent =
  | "memory_reentry_started"
  | "memory_description_submitted"
  | "memory_recap_edited"
  | "memory_clue_removed"
  | "memory_anchor_selected"
  | "memory_anchor_removed"
  | "memory_clue_undo"
  | "memory_clue_added"
  | "moments_shown"
  | "evidence_viewed"
  | "episode_shifted_earlier"
  | "episode_shifted_later"
  | "confirmed_photo_opened"
  | "confirmed_moment_viewed"
  | "prototype_exited"
  | "memory_question_answered"
  | "memory_question_skipped"
  | "episode_opened"
  | "episode_rejected"
  | "moments_none_matched"
  | "recovery_action_selected"
  | "time_ribbon_shifted"
  | "outside_window_opened"
  | "asset_opened"
  | "retrieval_confirmed"
  | "ledger_viewed"
  | "chip_alternative_taken"
  | "seen_cues_shown"
  | "seen_cue_picked"
  | "seen_cue_removed"
  | "memory_reentry_exited";

type Entry = { event: TrailEvent; at: number; sinceStart: number; detail?: Record<string, unknown> };

const log: Entry[] = [];
let startedAt = 0;

export function track(event: TrailEvent, detail?: Record<string, unknown>) {
  const now = Date.now();
  if (event === "memory_reentry_started" || startedAt === 0) startedAt = now;
  const entry: Entry = { event, at: now, sinceStart: (now - startedAt) / 1000, detail };
  log.push(entry);
  if (typeof window !== "undefined") {
    (window as unknown as { memoryTrails?: unknown }).memoryTrails = {
      events: log,
      secondsToConfirm: secondsToConfirm(),
      summary: summary(),
    };
  }
}

/** The primary success measure: did retrieval complete, and how long did it take. */
export function secondsToConfirm(): number | null {
  const done = log.find((e) => e.event === "retrieval_confirmed");
  return done ? Number(done.sinceStart.toFixed(1)) : null;
}

export function summary() {
  const count = (e: TrailEvent) => log.filter((x) => x.event === e).length;
  return {
    cluesRemoved: count("memory_clue_removed"),
    episodesOpened: count("episode_opened"),
    episodesRejected: count("episode_rejected"),
    noneMatched: count("moments_none_matched"),
    recoveryActions: count("recovery_action_selected"),
    evidenceViewed: count("evidence_viewed"),
    seenCuesShown: count("seen_cues_shown"),
    seenCuesPicked: count("seen_cue_picked"),
    seenCuesRemoved: count("seen_cue_removed"),
    clueEdits: count("memory_clue_removed") + count("memory_clue_added") + count("memory_clue_undo") + count("seen_cue_removed"),
    confirmed: count("retrieval_confirmed") > 0,
    confirmedWithSeen: Boolean(
      ((log.find((e) => e.event === "retrieval_confirmed")?.detail?.seen as string[] | undefined) ?? []).length > 0
    ),
    seenAtConfirmation: (log.find((e) => e.event === "retrieval_confirmed")?.detail?.seen as string[] | undefined) ?? [],
    withinFiveMinutes: (secondsToConfirm() ?? Infinity) <= 300,
  };
}

let studyParticipant: string | null = null;

export function setStudyParticipant(id: string | null) {
  studyParticipant = id;
}

export function getStudyParticipant(): string | null {
  return studyParticipant;
}

export function copySessionLog(): string {
  const data = {
    studyId: studyParticipant,
    startedAt: startedAt ? new Date(startedAt).toISOString() : null,
    secondsToConfirm: secondsToConfirm(),
    summary: summary(),
    events: log,
  };
  return JSON.stringify(data, null, 2);
}

export function reset() {
  log.length = 0;
  startedAt = 0;
}

