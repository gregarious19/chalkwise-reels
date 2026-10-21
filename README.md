# Chalkwise reels

Daily 30–50 second Instagram reels for Chalkwise, made and posted automatically.

```
Claude (daily, ~09:00 IST)                GitHub Actions
  read data/insights.json  ─────────┐       render.yml   on new spec → MP4 + voice → release reel-<id> (preview link)
  update LEARNINGS.md               │       post.yml     19:00 IST → posts the oldest APPROVED due reel → moves spec to scripts/posted/
  write scripts/queue/<id>.json ────┼──▶    insights.yml 08:00 IST → metrics for every posted reel → data/insights.json
  push, send you a preview          └────── (and refreshes the Instagram token every Monday)
```

**Nothing posts without your approval.** Each reel is queued with `"approved": false`. Watch the preview, then tell Claude "approve" (or set `"approved": true` in the spec on GitHub). Approved reels post at the next 19:00 IST slot after their `post_after` time; unapproved ones wait in the queue.

## Pausing or stopping a reel

- **Approve a reel:** tell Claude "approve", or edit its spec on GitHub and set `"approved": true`.
- **One reel:** tell Claude "hold tomorrow's reel", or edit its spec on GitHub and add `"hold": true`.
- **Everything:** create an empty file named `PAUSED` at the repo root (GitHub app → Add file). Delete it to resume.
- **Post one now:** Actions → Post reel to Instagram → Run workflow, optionally giving a spec path.

## One-time setup

### 1. Instagram account
In the Instagram app: Settings → *Account type and tools* → switch to a **Creator** or **Business** account. The account must be public.

### 2. Meta developer app
1. Go to [developers.facebook.com](https://developers.facebook.com), log in with the Facebook account you want to own the app, and register as a developer if asked.
2. **My Apps → Create App.** Use case: **Other** → app type: **Business** → name it "Chalkwise Reels" and add your email.
3. On the app dashboard, find the **Instagram** product and click **Set up**. "API setup with Instagram login" is added automatically.
4. Under **Generate access tokens**, click **Add account** and log in to the Chalkwise Instagram account. Keep these permissions ticked: `instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_insights`.
5. Click **Generate token** next to the account and copy it. Also note the Instagram **user ID** shown next to the account.

The app can stay in development mode: it only ever posts to your own account, which already has a role on the app.

### 3. GitHub secrets
Repo → Settings → *Secrets and variables* → Actions → **New repository secret**:

| Secret | Value | Needed for |
| --- | --- | --- |
| `IG_ACCESS_TOKEN` | the token from step 2.5 | posting, insights |
| `IG_USER_ID` | the Instagram user ID | posting, insights (optional, looked up if missing) |
| `DEEPGRAM_API_KEY` | a Deepgram API key ([console.deepgram.com](https://console.deepgram.com)) | voiceover (optional; without it reels have no voice) |
| `GH_PAT` | a fine-grained GitHub token with **Secrets: read and write** on this repo | saving the refreshed Instagram token every Monday |

Optional *variables* (same page, Variables tab): `DEEPGRAM_VOICE` (default `aura-2-thalia-en`), `IG_API_VERSION` (default `v24.0`).

### 4. Test
Actions → **Pull Instagram insights** → Run workflow. A green run means the token works.

## Files

| Path | What |
| --- | --- |
| `render.py` | Spec → MP4 (self-drawing whiteboard, captions, marker sounds, pad, voice) |
| `tts.py` | Spec voiceover lines → voice track (Deepgram Aura) |
| `ig.py` | Instagram API: check, publish, insights, token refresh |
| `scripts/queue/` | Reels waiting to post |
| `scripts/posted/` | Posted reels, with media ID and permalink |
| `data/insights.json` | Daily metric snapshots per reel |
| `CONTENT_PLAYBOOK.md` | Audience, hooks, structure, rules, how performance is judged |
| `SPEC_FORMAT.md` | The reel JSON format |
| `DAILY_RUN.md` | What Claude does each day |
| `LEARNINGS.md` | What the data has taught so far |
| `FEEDBACK.md` | Your notes for Claude (anything goes) |
