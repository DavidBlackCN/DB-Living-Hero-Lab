"""R7.3B actual-render A/B, continuity, lifecycle and capture audit."""

from __future__ import annotations

import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

from validate_character_coherence import regression as character_regression, continuity

ROOT = Path(__file__).resolve().parents[1]
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"
PHASES = ("Dawn", "Noon", "Dusk", "Night")


def show(page):
    if page.get_by_role("button", name="Debug", exact=True).is_visible():
        page.get_by_role("button", name="Debug", exact=True).click()


def capture(page, destination=None):
    page.get_by_role("button", name="Hide", exact=True).click()
    page.wait_for_timeout(100)
    data = page.screenshot()
    if destination:
        destination.write_bytes(data)
    show(page)
    return Image.open(BytesIO(data)).convert("RGB")


def setup(page, motion=False):
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    if not motion:
        for label in ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off"):
            page.get_by_label(label).uncheck()


def contact(pairs, destination, width=720):
    height = round(pairs[0][1].height / pairs[0][1].width * width)
    image = Image.new("RGB", (width * 2, (height + 26) * ((len(pairs) + 1) // 2)), (22, 24, 29))
    pen = ImageDraw.Draw(image)
    for i, (label, frame) in enumerate(pairs):
        x, y = i % 2 * width, i // 2 * (height + 26)
        pen.text((x + 8, y + 6), label, fill="white")
        image.paste(frame.resize((width, height)), (x, y + 26))
    image.save(destination, quality=92)


def stills(browser, out):
    page = browser.new_page(viewport={"width": 1672, "height": 941}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    setup(page)
    pairs, stats = [], {}
    for phase in PHASES:
        page.get_by_role("button", name=phase, exact=True).click()
        page.get_by_label("Atmosphere on/off").uncheck()
        before = capture(page, out / f"{phase.lower()}-before.png")
        page.get_by_label("Atmosphere on/off").check()
        after = capture(page, out / f"{phase.lower()}.png")
        delta = np.abs(np.asarray(after, dtype=np.int16) - np.asarray(before, dtype=np.int16))
        stats[phase] = {"meanRgbDelta": round(float(delta.mean()), 4), "maxRgbDelta": int(delta.max())}
        if phase == "Noon":
            assert delta.max() == 0, stats
        pairs.extend([(phase + " frozen / OFF", before), (phase + " polish / ON", after)])
        for name, box in (("head", (990, 10, 1370, 335)), ("far-scene", (1360, 80, 1610, 590)),
                          ("lamp", (15, 70, 220, 425))):
            contact([(phase + " OFF", before.crop(box)), (phase + " ON", after.crop(box))],
                    out / f"{phase.lower()}-{name}-ab.jpg", width=500)
        page.get_by_label("Bloom on/off").uncheck()
        capture(page, out / f"{phase.lower()}-bloom-off.png")
        page.get_by_label("Bloom on/off").check()
    contact(pairs, out / "four-phases-ab.jpg")
    contact([(phase, Image.open(out / f"{phase.lower()}.png")) for phase in PHASES], out / "four-phases.jpg")
    slider = page.get_by_role("slider", name="24H Preview")
    frames = []
    for minute in (0, 120, 270, 300, 330, 360, 390, 420, 480, 960, 1020, 1050, 1080, 1110, 1200, 1320, 1440):
        slider.evaluate("(node, value) => { node.value=String(value); node.dispatchEvent(new Event('input', {bubbles:true})); }", minute)
        label = f"{minute//60:02d}:{minute%60:02d}"
        frame = capture(page, out / f"time-{minute:04d}.png")
        frames.append((label, frame))
    contact(frames, out / "time-contact.jpg", width=480)
    first = np.asarray(frames[0][1], dtype=np.int16)
    last = np.asarray(frames[-1][1], dtype=np.int16)
    assert np.array_equal(first, last), "Midnight mismatch"
    for view in ("bright", "bloom", "grade", "final"):
        page.get_by_label("Post preview").select_option(view)
        capture(page, out / f"night-post-{view}.png")
    assert not errors, errors
    page.close()
    stats["midnightMaxRgbDelta"] = int(np.abs(first - last).max())
    return stats


def motion(browser, out, phase, seconds=25):
    # Screenshot frames capture actual WebGL, avoiding stale canvas frames from
    # the browser video recorder. Playback is resampled onto a fixed 30fps grid.
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
    setup(page, motion=True)
    page.get_by_role("button", name=phase, exact=True).click()
    page.get_by_role("button", name="Hide", exact=True).click()
    writer = cv2.VideoWriter(str(out / f"{phase.lower()}-25s.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 30, (1280, 720))
    assert writer.isOpened()
    start = time.monotonic()
    count, samples = 0, []
    while time.monotonic() - start < seconds:
        elapsed = time.monotonic() - start
        frame = cv2.imdecode(np.frombuffer(page.screenshot(), np.uint8), cv2.IMREAD_COLOR)
        target = min(seconds * 30, int(elapsed * 30) + 1)
        while count < target:
            writer.write(frame)
            count += 1
        if len(samples) < 5 and elapsed >= len(samples) * seconds / 5:
            samples.append((f"{phase} {elapsed:.1f}s", Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))))
    while count < seconds * 30:
        writer.write(frame)
        count += 1
    writer.release()
    contact(samples, out / f"{phase.lower()}-motion-contact.jpg", width=640)
    page.close()
    return {"seconds": seconds, "encodedFps": 30, "note": "actual screenshot frames, resampled; not native 30fps capture"}


def lifecycle(browser, out):
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
    setup(page)
    page.get_by_role("button", name="Night", exact=True).click()
    canvas = page.locator("canvas.hero-canvas")
    page.evaluate("() => { window.testGl = document.querySelector('.hero-canvas').getContext('webgl2'); window.testLose=window.testGl.getExtension('WEBGL_lose_context'); window.testLose.loseContext(); }")
    page.wait_for_timeout(250)
    assert "fallback" in page.locator(".debug-panel footer").inner_text().lower()
    page.evaluate("() => window.testLose.restoreContext()")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    assert canvas.evaluate("node=>node.getContext('webgl2').getError()") == 0
    sizes = []
    for width, height in ((1920, 1080), (2560, 1440), (3840, 2160), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_timeout(250)
        sizes.append(canvas.evaluate("node=>[node.width,node.height,node.getContext('webgl2').getError()]"))
        capture(page, out / f"night-{width}x{height}.png")
    assert all(size[2] == 0 for size in sizes), sizes
    page.get_by_label("Quality").select_option("static")
    assert page.locator("canvas.hero-canvas").count() == 0
    page.get_by_label("Quality").select_option("auto")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.close()
    context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, reduced_motion="reduce")
    page = context.new_page()
    setup(page, motion=True)
    page.get_by_role("button", name="Night", exact=True).click()
    assert page.locator(".leaves-canvas").count() == 0
    assert not page.locator("canvas.hero-canvas").evaluate("node=>node.__vueParentComponent.props.hair.enabled")
    assert not page.locator("canvas.hero-canvas").evaluate("node=>node.__vueParentComponent.props.breathing.enabled")
    dpr_size = page.locator("canvas.hero-canvas").evaluate("node=>[node.width,node.height]")
    capture(page, out / "night-mobile-dpr3-reduced.png")
    context.close()
    return {"contextRestore": True, "staticQuality": True, "resizeBuffers": sizes, "mobileDpr3Buffers": dpr_size, "reducedMotion": True}


def long_run(browser, out):
    context = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
    context.add_init_script("""(() => {
      window.audit = {draws:0,leafDraws:0,raf:0};
      const draw=WebGL2RenderingContext.prototype.drawArrays;
      WebGL2RenderingContext.prototype.drawArrays=function(...args){window.audit.draws++;return draw.apply(this,args)};
      const leaf=CanvasRenderingContext2D.prototype.drawImage;
      CanvasRenderingContext2D.prototype.drawImage=function(...args){window.audit.leafDraws++;return leaf.apply(this,args)};
      const raf=window.requestAnimationFrame;
      window.requestAnimationFrame=function(cb){window.audit.raf++;return raf.call(window,cb)};
    })()""")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    setup(page, motion=True)
    page.get_by_role("button", name="Night", exact=True).click()
    page.get_by_role("button", name="Play", exact=True).click()
    page.get_by_role("button", name="Hide", exact=True).click()
    started = time.monotonic()
    samples = []
    while time.monotonic() - started < 610:
        page.wait_for_timeout(10000)
        sample = page.evaluate("() => ({...window.audit,time:document.querySelector('.time-control input').value,heap:performance.memory?.usedJSHeapSize,gl:document.querySelector('.hero-canvas').getContext('webgl2').getError()})")
        sample["elapsed"] = round(time.monotonic() - started, 1)
        samples.append(sample)
        assert sample["gl"] == 0 and not errors, (sample, errors)
        if len(samples) % 6 == 0:
            print(f"Long run {sample['elapsed']}s / 610s: {sample['draws']} draws, no errors", flush=True)
    show(page)
    page.get_by_role("button", name="Pause", exact=True).click()
    page.get_by_role("button", name="Night", exact=True).click()
    capture(page, out / "night-after-10min.png")
    result = {"elapsedSeconds": round(time.monotonic()-started, 1), "errors": errors, "samples": samples}
    (out / "long-run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    context.close()
    return result


def performance_audit(browser):
    # Optional GPU timing. CPU submission time alone is not GPU frame time.
    context = browser.new_context(device_scale_factor=1)
    context.add_init_script("""(() => {
      window.perfAudit={cpu:[],gpu:[],timestamps:[],drawCounts:[]};
      const original=WebGL2RenderingContext.prototype.drawArrays;
      const state=new WeakMap();
      WebGL2RenderingContext.prototype.drawArrays=function(...args){
        let s=state.get(this);
        if(!s){s={ext:this.getExtension('EXT_disjoint_timer_query_webgl2'),pending:[],query:null,draws:0};state.set(this,s)}
        if(!s.draws){
          s.start=performance.now();
          if(s.ext){s.query=this.createQuery();this.beginQuery(s.ext.TIME_ELAPSED_EXT,s.query)}
        }
        s.draws++;
        const result=original.apply(this,args);
        if(!this.getParameter(this.FRAMEBUFFER_BINDING)){
          window.perfAudit.cpu.push(performance.now()-s.start);
          window.perfAudit.timestamps.push(performance.now());
          window.perfAudit.drawCounts.push(s.draws);s.draws=0;
          if(s.query){this.endQuery(s.ext.TIME_ELAPSED_EXT);s.pending.push(s.query);s.query=null}
          while(s.pending.length && this.getQueryParameter(s.pending[0],this.QUERY_RESULT_AVAILABLE)){
            const q=s.pending.shift();
            if(!this.getParameter(s.ext.GPU_DISJOINT_EXT))window.perfAudit.gpu.push(this.getQueryParameter(q,this.QUERY_RESULT)/1e6);
            this.deleteQuery(q);
          }
        }
        return result;
      }
    })()""")
    page = context.new_page()
    setup(page, motion=True)
    page.get_by_label('Leaves').uncheck()
    page.get_by_label('Blink on/off').uncheck()
    page.get_by_role('button', name='Night', exact=True).click()
    results = []
    info = page.locator('.hero-canvas').evaluate("node=>{const gl=node.getContext('webgl2'),ext=gl.getExtension('WEBGL_debug_renderer_info');return {renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),maxSamplers:gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS),gpuTimer:!!gl.getExtension('EXT_disjoint_timer_query_webgl2')}}")
    for width, height in ((1920,1080),(2560,1440),(3840,2160)):
        page.set_viewport_size({'width':width,'height':height})
        has_atmosphere = page.get_by_label('Atmosphere on/off').count() != 0
        for enabled in ((False, True) if has_atmosphere else (False,)):
            if has_atmosphere:
                page.get_by_label('Atmosphere on/off').set_checked(enabled)
            page.wait_for_timeout(1000)
            page.evaluate('window.perfAudit={cpu:[],gpu:[],timestamps:[],drawCounts:[]}')
            page.wait_for_timeout(4500)
            data=page.evaluate('window.perfAudit')
            times=data['timestamps']
            gpu=data['gpu']
            results.append({'size':[width,height], 'atmosphere':enabled,
                'frameSamples':len(times), 'drawsPerFrame':sorted(set(data['drawCounts'])),
                'observedFps':round((len(times)-1)*1000/(times[-1]-times[0]),2),
                'cpuSubmissionMedianMs':round(float(np.median(data['cpu'])),3),
                'gpuMedianMs':round(float(np.median(gpu)),3) if gpu else None,
                'gpuP95Ms':round(float(np.percentile(gpu,95)),3) if gpu else None})
    context.close()
    return {'environment':info,'measurements':results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("stills", "regression", "motion", "long", "performance"), default="stills")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=d3d11"])
        if args.mode == "stills":
            result = stills(browser, args.output)
        elif args.mode == "motion":
            result = {phase: motion(browser, args.output, phase) for phase in ("Dawn", "Dusk", "Night")}
        elif args.mode == "regression":
            result = lifecycle(browser, args.output)
            result["character"] = character_regression(browser, args.output)
            result["continuity"] = continuity(browser)
        elif args.mode == 'performance':
            result = performance_audit(browser)
        else:
            result = long_run(browser, args.output)
        browser.close()
    if args.mode != "long":
        (args.output / f"{args.mode}-stats.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
