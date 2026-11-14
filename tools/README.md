# Report and screenshot authoring

Model reproduction uses the project's virtual environment and `src/` scripts. Document authoring uses the Codex bundled Python runtime with `python-docx` and the bundled LibreOffice renderer. To build the Word report in a normal local environment, install `python-docx==1.2.0` and run `python tools/build_report.py` after figures and screenshots exist.

The report's PDF is exported from the rendered Word document so the two versions share their layout. The authoring environment's bundled dependencies are separate from the experiment environment captured in `requirements-lock.txt`.

To reproduce browser screenshots with Playwright and Chrome:

```bash
npm install --prefix /tmp/acv-browser playwright
PLAYWRIGHT_MODULE=/tmp/acv-browser/node_modules/playwright node src/capture_evidence.cjs
```

Use `CHROME_PATH` if Chrome is installed elsewhere. The generated screenshots show real, static evidence HTML files built from actual outputs. No personal browser profile is used.

`tools/package_submission.py` creates the submission ZIP and records SHA256 values for all included files. It excludes `.git`, virtual environments, downloaded data, caches and document QA intermediates.
