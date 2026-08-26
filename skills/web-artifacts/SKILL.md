---
name: web-artifacts
description: Builds a small interactive web page or app — a tool, calculator, form, mini-dashboard, game, or visualization — and publishes it so it renders live for the user, the same way a generated spreadsheet or chart image appears as a file. Use whenever the user wants something they can click, type into, or watch run: "build me a...", "make a tool that...", "a page where I can...", "an interactive version of...". Two project kinds: `html` for a single self-contained page, `react` for anything with real state or multiple views. Do NOT use for a document to read (PDF → base-report, slides → pptx-deck, workbook → spreadsheet) or for a static chart (see generate_chart_config) — those aren't rendered as a live page.
---

# Web artifacts

An artifact is a page, not a report. Nobody scrolls it top to bottom — they
click something and expect it to respond. If what's actually being asked for
is "explain this" or "show me this number," it doesn't belong here — say it in
chat, or hand off to base-report / generate_chart_config.

## How to use this skill

### 1. Pick html vs react

| Signal | Kind |
|---|---|
| One screen, a form, a calculator, a visualization, a handful of buttons | `html` |
| Multiple views/tabs, non-trivial state, a list that grows/reorders, anything you'd reach for `useState`/`useEffect` to build | `react` |

When unsure, start with `html` — no build step, so the first working version
comes back faster. Reach for `react` only when the plain-JS version would
fight you.

### 2. Scaffold

```
scaffold_web_artifact({ title: "...", kind: "html" | "react" })
```

Returns a project path under `projects/<slug>/` and does not publish anything
yet. For `html`, it seeds `index.html` / `style.css` / `script.js` with an
error-reporting snippet already wired into `script.js` — leave those lines in
place, they're what turns a runtime crash into a visible message instead of a
blank frame. For `react`, it copies a React + TypeScript + Vite starter with
the same reporting wired into an `ErrorBoundary` in `src/App.tsx`.

Before writing any markup, do the design pass — load
[web-design](../web-design/SKILL.md). A working page with the default look is
not the deliverable; five minutes deciding a palette, a type scale, and one
deliberate visual choice is what separates this from a template.

### 3. Edit with execute_code — that's the only tool available here

There is no `write_file`/`read_file`/`bash` in this context, only
`execute_code`. Write files from inside it:

```python
open("/home/user/projects/my-tool/script.js", "w").write(js_source)
```

or from JS: `fs.writeFileSync(path, source)`. Read a file back the same way
before assuming what's currently in it — don't guess at content you wrote a
few turns ago.

### 4. Validate before you publish — you have a real feedback loop, use it

- **html**: nothing to compile, but re-read the file you just wrote and check
  it against what you intended before moving on.
- **react**: run the actual build from the same tool, and read its output:
  ```python
  import subprocess
  r = subprocess.run(
      "cd /home/user/projects/my-tool && npm run build",
      shell=True, capture_output=True, text=True,
  )
  print(r.returncode, r.stdout, r.stderr)
  ```
  This runs `tsc --noEmit` before the Vite build, so a real type error comes
  back as text you can read and fix — not a broken page the user opens. Fix it
  and run the build again. Don't call `publish_web_artifact` on a hunch that
  it compiles.

Keep the `ErrorBoundary`/`window.onerror` wiring already in the template — the
build can't catch a *runtime* failure, one that only shows up once the code is
actually executing in the viewer's frame. That wiring is the only thing that
makes such a failure visible instead of a silent blank page.

### 5. Publish

```
publish_web_artifact({ path: "<project path from scaffold>", title: "..." })
```

This re-validates — a `react` project that fails to build comes back here as
an unpublished error, not a broken page. On success, the artifact attaches to
your reply automatically, the same way a generated file does: it appears as a
file the user can open, and in the side files panel alongside anything else
produced this session. **Don't paste a URL, don't describe the file layout** —
you don't get one back, and there's nothing to link to. Just say in one short
line what you built.

## Guidelines

- **One project per artifact.** Never scaffold a second artifact into an
  existing project's directory.
- **Self-contained.** No external network calls, no CDN scripts, no fonts
  fetched at runtime that you haven't actually verified load — the published
  page has to work standalone. Ship the 5MB you're given, not a page that
  depends on something outside it.
- **The build is the safety net, not a formality.** Don't skip `npm run build`
  to save a turn — a compile error that reaches the user as a blank frame is
  worse than one more validate-and-fix loop.
- **Never publish something you haven't validated at least once.** "It should
  work" is not a reason to call `publish_web_artifact`.
- **A revision edits the same project** — it doesn't scaffold a new one. Keep
  the path from your first `scaffold_web_artifact` call for the rest of the
  conversation and reuse it.
