"""Render AI_USAGE_LOG.md into the dashboard's side rail.

The log is the source of truth. Run this after editing it and the rail in
outputs/payment_explorer.html is rebuilt in place:

    python build_log_rail.py

Markdown tables are NOT rendered as tables. At 360px wide a three-column table
is unreadable, so each row becomes a stacked block with its column headers as
labels. Everything else is a small subset of markdown: headings, bullets with
hanging continuation lines, bold, italic, inline code and rules.
"""
import html
import io
import re

LOG = "AI_USAGE_LOG.md"
PAGE = "outputs/payment_explorer.html"


def inline(t):
    """Escape, then put back the handful of inline marks the log actually uses."""
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<i>\1</i>", t)
    # _[Danny: ]_ is a stub he still has to fill -- make it impossible to miss
    t = re.sub(r"_\[Danny:\s*(.*?)\]_",
               lambda m: '<span class="lgtodo">Danny: '
                         + (m.group(1) or "&nbsp;&nbsp;&nbsp;&nbsp;") + "</span>",
               t)
    t = re.sub(r"(?<![\w_])_([^_]+)_(?![\w_])", r"<i>\1</i>", t)
    return t


def render(md):
    out, i, lines = [], 0, md.split("\n")
    nsec = 0
    while i < len(lines):
        ln = lines[i]

        if not ln.strip():
            i += 1
            continue

        if ln.startswith("---") and set(ln.strip()) == {"-"}:
            out.append('<hr class="lghr">')
            i += 1
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            tag = {1: "h3", 2: "h4", 3: "h5"}[lvl]
            cls = {1: "lgh1", 2: "lgh2", 3: "lgh3"}[lvl]
            aid = ""
            if lvl == 2:                       # only the four numbered sections get anchors
                nsec += 1
                aid = ' id="lgs%d"' % nsec
            out.append('<%s class="%s"%s>%s</%s>' % (tag, cls, aid, inline(m.group(2)), tag))
            i += 1
            continue

        # table: header row, separator, then body rows -> one block per row
        if ln.lstrip().startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            heads = cells(ln)
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                row = cells(lines[i])
                out.append('<div class="lgrow">')
                for h, c in zip(heads, row):
                    if not c:
                        continue
                    lab = ('<span class="lglab">%s</span>' % inline(h)) if h else ""
                    out.append('<div class="lgcell">%s%s</div>' % (lab, inline(c)))
                out.append("</div>")
                i += 1
            continue

        if re.match(r"^\s*[-*]\s+", ln):
            out.append('<ul class="lgul">')
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                buf = [re.sub(r"^\s*[-*]\s+", "", lines[i])]
                i += 1
                # hanging indent: the log wraps its bullets across lines
                while i < len(lines) and lines[i].startswith("  ") \
                        and lines[i].strip() and not re.match(r"^\s*[-*]\s+", lines[i]):
                    buf.append(lines[i].strip())
                    i += 1
                out.append("<li>%s</li>" % inline(" ".join(buf)))
            out.append("</ul>")
            continue

        buf = []
        while i < len(lines) and lines[i].strip() \
                and not lines[i].lstrip().startswith(("|", "#", "-", "*")):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
        else:
            i += 1
    return "\n".join(out)


def main():
    md = io.open(LOG, encoding="utf-8").read()
    body = render(md)
    secs = re.findall(r"^##\s+(\d)\.\s+(.*)$", md, re.M)
    nav = "".join('<button data-lg="%s">%s</button>' % (n, n) for n, _ in secs)

    rail = (
        '<aside id="rail" aria-label="AI usage log">\n'
        '  <div class="lghead"><b>AI-usage log</b>'
        '<span class="lgsub">the required deliverable, live</span>'
        '<button id="lgClose" aria-label="Close">&times;</button></div>\n'
        '  <div class="lgnav">' + nav + '</div>\n'
        '  <div class="lgbody" id="lgBody">\n' + body + "\n  </div>\n"
        "</aside>"
    )

    s = io.open(PAGE, encoding="utf-8").read()
    if 'id="rail"' in s:
        s = re.sub(r'<aside id="rail".*?</aside>', lambda _: rail, s, count=1, flags=re.S)
    else:
        s = s.replace("\n</div>\n", "\n" + rail + "\n</div>\n", 1) \
            if False else s.replace("</section>\n</div>", "</section>\n" + rail + "\n</div>")
    io.open(PAGE, "w", encoding="utf-8", newline="\n").write(s)
    print("rail rebuilt: %d sections, %d chars of log HTML" % (len(secs), len(body)))
    for n, t in secs:
        print("  %s. %s" % (n, t))


if __name__ == "__main__":
    main()
