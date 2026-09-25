# Push Notifications

Skip unless `PRODUCT.md` marks notifications "now" **and** answered what would actually trigger one. Notifications without a trigger are permission prompts users deny.

Prereqs: physical device; Apple Developer account (iOS); FCM configured (Android).

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up notifications with `expo-notifications`.

**Check the installed `expo-notifications` version and the Expo SDK version, then follow the current docs** (https://docs.expo.dev/push-notifications/overview/). Two things that trip up copied snippets:

- The notification-handler result fields were renamed — the old single "show alert" flag was split into separate banner and list flags. Use what the installed version's types expect; TypeScript will tell you.
- **Remote push does not work in Expo Go on recent SDKs.** A development build is required. Confirm the developer has one before debugging "notifications don't arrive".

### Grill

- **Local, remote, or both?** Local (reminders scheduled on-device) needs no server and no push token. If `PRODUCT.md`'s trigger is a reminder, stop after local — it is a fraction of the work.
- What event on the server sends a push, and does that server exist yet?
- Where should tapping a notification land? Deep links need route data in the payload.
- When is permission requested? Recommended: after the user has seen value, not on first launch — a denied iOS permission is expensive to recover.

### Build

- Install `expo-notifications`, plus device and constants helpers as needed
- A notification handler configured with the installed version's field names
- Permission request at the chosen moment, with the denied path handled gracefully — never block the app or loop the prompt
- Registration guarded by a physical-device check; the EAS project id must come from the app config, not be hard-coded
- Android notification channels created before any notification is delivered, or importance and sound are ignored
- **Remote only:** obtain the push token, send it to the backend keyed to the user, and refresh it when it rotates. Handle multiple devices per user and stale tokens
- Listeners for foreground receipt and for taps, with tap-handling routing from payload data; clean up on unmount
- **Local only:** scheduling and cancelling helpers, and cancel-on-change so a rescheduled reminder does not stack duplicates
- Notification content: no sensitive data — lock-screen previews are visible without unlocking

### Done when

- [ ] Verified on a physical device with a development build (not Expo Go)
- [ ] Permission denial leaves the app fully usable
- [ ] Tapping a notification lands on the right screen from cold start, background, and foreground
- [ ] Android: channel set before first delivery
- [ ] Remote: token stored server-side and refreshed; local: no duplicate schedules
