# Media Capture & Upload

Run this only where `PRODUCT.md` marks a media capability "now". Skipped, every screen that needs a photo grows its own picker, its own size limit and its own idea of what "uploaded" means.

Prereqs: `native-permissions.md` for camera, photo library and microphone; `secure-backend.md` if the storage provider issues signed URLs — the signing key never ships in the app. Physical device: simulators have no camera and lie about cellular.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build capture, picking, and upload for the media `PRODUCT.md` requires.

### Grill

- **Which media kinds, and where is each one used?** Photo, video, audio, document — each against the screen and entity that consumes it. A picker built for a feature that does not exist is dead code, and video drags in transcoding, thumbnails and a size problem that photos do not have.
- **Capture, pick, or both?** Recommended default: both, unless the feature is inherently live (proof-of-delivery photo, voice note) — a capture-only flow forces the user to re-take something already on their phone.
- **What is the size ceiling, and who enforces it?** **A:** the app measures and refuses before uploading. **B:** the server rejects after the bytes arrive. Recommended default: A, with B as the backstop — rejecting a 200 MB video after the upload finished on cellular is the failure users remember and the one that makes them uninstall.
- **Where do the bytes live?** The managed provider already in the stack (`supabase.md`), an S3-compatible bucket with server-signed URLs, or the API itself. Recommended default: the provider already in the stack; a second storage vendor is a second set of credentials, policies and bills.
- **Is each file public or private per user?** A public bucket URL is public forever, guessable, and outside every auth check the rest of the app enforces. Recommended default: private with signed reads for anything a user produced; public only for assets that are already public, like avatars the product says are public.
- **Does anything need a thumbnail or a transcode, and where does it happen?** On device saves server cost and burns battery and time on the user's phone; on server needs a worker and a "still processing" state the UI must render.
- **Must an upload survive leaving the screen or backgrounding the app?** Recommended default: survives navigation, not process death — a 30 MB video on a train needs it, an avatar does not. This answer decides whether the upload lives in a screen or in a queue (`offline.md`).

### Build

**Capture and pick**

- Both paths read permission state from the module `native-permissions.md` owns; no screen calls the OS API directly
- Handle the iOS limited-library grant as a working state, not a denial: show the selection the user allowed plus an affordance to allow more. Treating it as denied hides files the user explicitly granted
- Cancelling the picker or camera is a normal outcome and returns the screen exactly as it was

**Before the bytes leave**

- Compress and resize on device, with the target dimensions written down and justified against how the image is actually displayed. A phone camera photo is several megabytes; most screens render it at 400 px, so uploading the original wastes the user's data allowance and your storage bill
- State whether the original resolution is kept at all. If the product needs the full-size file (documents, evidence, print), say so and accept the cost deliberately
- **EXIF is a decision, not a default.** GPS coordinates inside a shared photo are a location leak the user never agreed to. Strip metadata, or keep specific fields for a stated reason, and record which in `privacy-consent.md`'s inventory
- Enforce the size ceiling here, with a message naming the limit and what to do about it

**The upload**

- The signed URL or upload ticket is requested from the server per file, scoped to this user; a storage secret in the app is the failure `secure-backend.md` exists to prevent
- Real byte-level progress surfaced to the UI. A fake indeterminate spinner on a two-minute cellular upload is indistinguishable from a hang
- Cancellation that aborts the transfer, not one that hides the UI while the bytes keep flowing and the bill keeps running
- Network loss: resume where supported, otherwise restart with the retry count and the give-up point defined. Silent infinite retry drains the battery of a phone in a lift
- **Pending is a domain state.** A record whose media is still uploading is a real state `domain-model.md` must model, with its own rendering — not an optimistic row with a spinner painted over it. Failed-upload is a state too, and it needs a retry the user can reach
- Orphan cleanup on both sides: a successful upload followed by a failed record creation leaves a file nobody references and everybody pays for; a deleted record leaves a file to delete. Decide whether cleanup is immediate or a sweep, and make deletion of the record delete the file

**Serving**

- Signed read URLs with an expiry that outlives the screen showing them, and a refresh path — a URL that expires while a detail screen is open renders a broken image with no explanation
- Cache fetched media on device so a list does not re-download every thumbnail on every scroll (`performance.md`)
- A placeholder for missing, deleted, or still-processing files. A missing file is normal, not an error dialog
- Content type validated server-side from the bytes, never trusted from the filename or the client-supplied header. Where uploaded media is shown to other users, `content-moderation.md` owns what happens next

### Done when

- [ ] A captured photo and a picked existing file both upload from a physical device on cellular, not just on wifi
- [ ] A file over the ceiling is refused before any bytes are sent, with a message naming the limit
- [ ] Backgrounding mid-upload behaves as decided — survives, or fails visibly with a retry
- [ ] Cancelling stops the transfer, verified by watching it stop rather than by the UI closing
- [ ] A private file's URL, requested unauthenticated from another client, is refused — verified by trying it
- [ ] EXIF handled as decided, verified by inspecting the metadata of an uploaded file
- [ ] A forced failure after upload and before record creation leaves no orphan file, and a forced record deletion leaves no orphan file
- [ ] A record in the pending state renders as pending on a cold app launch, not as broken or complete
