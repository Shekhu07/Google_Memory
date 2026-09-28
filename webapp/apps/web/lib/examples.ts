/** Shared by the compose screen and the Search tab's empty state, so the two
 *  surfaces suggest the same memories rather than drifting apart.
 *
 *  Four kinds of memory - an event, a group of people, a document, a pet - and
 *  none from the case brief. Each has a real answer in the demo library. Nothing
 *  sensitive (health, money) is suggested before the user chooses it. */
export const EXAMPLES = [
  "the photo of the handmade cake from my sister’s graduation",
  "the group photo after our college performance",
  "the picture of the handwritten note from my old apartment",
  "the photo of my dog curled up in the suitcase",
];

/** The primary demo task, used as the composer's placeholder. */
export const PRIMARY_EXAMPLE = EXAMPLES[0];
