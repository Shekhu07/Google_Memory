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
  | "anchor_selected"
  | "anchor_removed"
  | "memory_question_answered"
  | "memory_question_skipped"
  | "episode_opened"
  | "episode_rejected"
  | "recovery_action_selected"
  | "time_ribbon_shifted"
  | "outside_window_opened"
  | "asset_opened"
  | "retrieval_confirmed"
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
    recoveryActions: count("recovery_action_selected"),
    confirmed: count("retrieval_confirmed") > 0,
    withinFiveMinutes: (secondsToConfirm() ?? Infinity) <= 300,
  };
}

export function reset() {
  log.length = 0;
  startedAt = 0;
}
