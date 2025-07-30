# file: projects/web/site.py

import os
from docutils.core import publish_parts
from gway import gw, __
import markdown as mdlib

def view_reader(
    *,
    title=__('[README]', 'README'),
    ext=None,
    origin="root",
    **kwargs,
):
    """
    Render a resource file (.rst or .md) as HTML.
    If origin='root', only files in the resource root (no subfolders).
    Never serves files starting with dot or underscore.
    """
    gw.verbose(f"[reader] Called with title={title!r}, ext={ext!r}, origin={origin!r}")
    fname = _sanitize_filename(title)
    gw.verbose(f"[reader] Sanitized filename: {fname}")

    ext = (str(ext).strip().lower() if ext else None)
    if ext and ext.startswith('.'):
        ext = ext[1:]
    gw.verbose(f"[reader] Normalized ext: {ext}")

    # Security: Never allow files starting with dot/underscore
    if _is_hidden_or_private(fname):
        gw.verbose(f"[reader] Access denied due to hidden/private filename: {fname}")
        return "<b>Access denied.</b>"

    def file_variants(base):
        if ext in {'rst', 'md'}:
            variants = [f"{base}.{ext}"]
        else:
            base_, ext_ = os.path.splitext(base)
            if ext_ in {'.rst', '.md'}:
                variants = [base]
            else:
                variants = [f"{base}.rst", f"{base}.md"]
        gw.verbose(f"[reader] Candidate variants for base {base}: {variants}")
        return variants

    if origin == "root":
        resource_dir = os.path.dirname(gw.resource('README.rst'))  # This IS the resource root
        gw.verbose(f"[reader] Resource root directory: {resource_dir}")
        for candidate in file_variants(fname):
            gw.verbose(f"[reader] Checking candidate: {candidate}")
            if _is_hidden_or_private(candidate):
                gw.verbose(f"[reader] Skipped hidden/private candidate: {candidate}")
                continue
            try:
                resource_path = gw.resource(candidate)
                gw.verbose(f"[reader] Resolved resource path: {resource_path}")
            except Exception as e:
                gw.verbose(f"[reader] gw.resource({candidate}) exception: {e}")
                continue
            # Only allow files in the resource root
            if not os.path.isfile(resource_path):
                gw.verbose(f"[reader] Not a file: {resource_path}")
                continue
            if os.path.dirname(resource_path) != resource_dir:
                gw.verbose(f"[reader] File not in resource root: {resource_path}")
                continue
            if _is_hidden_or_private(os.path.basename(resource_path)):
                gw.verbose(f"[reader] File rejected (hidden/private): {resource_path}")
                continue
            gw.verbose(f"[reader] Will open file: {resource_path}")
            try:
                with open(resource_path, encoding="utf-8") as f:
                    content = f.read()
                if candidate.lower().endswith(".rst"):
                    html = publish_parts(source=content, writer_name="html")["html_body"]
                elif candidate.lower().endswith(".md"):
                    html = mdlib.markdown(content)
                else:
                    gw.verbose(f"[reader] Unsupported file type for {candidate}")
                    html = "<b>Unsupported file type.</b>"
                gw.verbose(f"[reader] Successfully rendered {candidate}")
                return html
            except Exception as e:
                gw.verbose(f"[reader] Exception reading or rendering {resource_path}: {e}")
                continue
        exts = ' or '.join(['.rst', '.md']) if not ext else f".{ext}"
        gw.verbose(f"[reader] File not found or not allowed: {fname}{exts}")
        return f"<b>File not found or not allowed: {fname}{exts}</b>"

    # Fallback for other origins (not fully implemented here)
    gw.verbose(f"[view_reader] Non-root origin {origin} not implemented in this snippet.")
    return "<b>Invalid or unsupported origin.</b>"

def _sanitize_filename(fname):
    """
    Sanitize the filename: only allow dots and alphanumerics. No slashes, no backslashes, no "..".
    """
    fname = str(fname)
    fname = fname.replace('/', '').replace('\\', '').replace('..', '')
    fname = ''.join(c for c in fname if c.isalnum() or c in '._-')
    return fname

def _is_hidden_or_private(fname):
    """
    Returns True if filename (or its extension) starts with a dot or underscore.
    """
    fname = os.path.basename(fname)
    if not fname:
        return True
    if fname[0] in {'.', '_'}:
        return True
    name, ext = os.path.splitext(fname)
    if ext and ext[1:2] in {'.', '_'}:
        return True
    if name.startswith('.') or name.startswith('_'):
        return True
    return False

def view_help(topic="", *args, **kwargs):
    """
    Render dynamic help based on GWAY introspection and search-style links.
    If there is an exact match in the search, show it at the top (highlighted).
    """

    # TODO: Change how the help system works: Instead of just using the results of
    # gw.gelp at all times, compliment this result with other information. 

    topic_in = topic or ""
    topic = topic.replace(" ", "/").replace(".", "/").replace("-", "_") if topic else ""
    parts = [p for p in topic.strip("/").split("/") if p]

    if not parts:
        help_info = gw.help()
        title = "Available Projects"
        content = "<ul>"
        for project in help_info["Available Projects"]:
            content += f'<li><a href="?topic={project}">{project}</a></li>'
        content += "</ul>"
        return f"<h1>{title}</h1>{content}"

    elif len(parts) == 1:
        project = parts[0]
        help_info = gw.help(project)
        title = f"Help Topics for <code>{project}</code>"

    else:
        *project_path, maybe_function = parts
        obj = gw
        for segment in project_path:
            obj = getattr(obj, segment, None)
            if obj is None:
                return f"<h2>Not Found</h2><p>Project path invalid at <code>{segment}</code>.</p>"
        project_str = ".".join(project_path)
        if hasattr(obj, maybe_function):
            function = maybe_function
            help_info = gw.help(project_str, function, full=True)
            full_name = f"{project_str}.{function}"
            title = f"Help for <code>{full_name}</code>"
        else:
            help_info = gw.help(project_str)
            full_name = f"{project_str}.{maybe_function}"
            title = f"Help Topics for <code>{full_name}</code>"

    if help_info is None:
        return "<h2>Not Found</h2><p>No help found for the given input.</p>"

    highlight_js = '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
      window.addEventListener('DOMContentLoaded',function(){
        if(window.hljs){
          document.querySelectorAll('pre code.python').forEach(el => { hljs.highlightElement(el); });
        }
      });
    </script>
    '''

    # --- Exact match highlighting logic ---
    # Only applies if help_info contains "Matches"
    if "Matches" in help_info:
        matches = help_info["Matches"]
        exact_key = (topic_in.replace(" ", "/").replace(".", "/").replace("-", "_")).strip("/")
        # Try to find an exact match (project, or project/function) in matches
        def canonical_str(m):
            p, f = m.get("Project", ""), m.get("Function", "")
            return (f"{p}/{f}" if f else p).replace(".", "/").replace("-", "_")
        exact = None
        exact_idx = -1
        for idx, m in enumerate(matches):
            if canonical_str(m).lower() == exact_key.lower():
                exact = m
                exact_idx = idx
                break

        sections = []
        # If found, show exact at top with highlight
        if exact is not None:
            sections.append('<div class="help-exact">' + _render_help_section(exact, use_query_links=True, highlight=True) + '</div>')
            # Add separator if there are more matches
            if len(matches) > 1:
                sections.append('<hr class="help-sep">')
            # Remove exact match from below
            rest = [m for i, m in enumerate(matches) if i != exact_idx]
        else:
            rest = matches

        for idx, match in enumerate(rest):
            section_html = _render_help_section(match, use_query_links=True)
            if idx < len(rest) - 1:
                section_html += '<hr class="help-sep">'
            sections.append(section_html)

        multi = f"<div class='help-multi'>{''.join(sections)}</div>"
        if "Full Code" in str(help_info):
            multi += highlight_js
        return f"<h1>{title}</h1>{multi}"

    # Not a multi-match result: just render normally
    body = _render_help_section(help_info, use_query_links=True)
    if "Full Code" in str(help_info):
        body += highlight_js
    return f"<h1>{title}</h1>{body}"

def _render_help_section(info, use_query_links=False, highlight=False, *args, **kwargs):
    import html
    proj = info.get("Project")
    func = info.get("Function")
    header = ""
    if proj and func:
        if use_query_links:
            proj_link = f'<a href="?topic={proj}">{proj}</a>'
            func_link = f'<a href="?topic={proj}/{func}">{func}</a>'
        else:
            proj_link = html.escape(proj)
            func_link = html.escape(func)
        header = f"""
        <div class="projfunc-row">
            <span class="project">{proj_link}</span>
            <span class="dot">·</span>
            <span class="function">{func_link}</span>
        </div>
        """

    rows = []
    skip_keys = {"Project", "Function"}
    for key, value in info.items():
        if key in skip_keys:
            continue

        # 1. Only autolink References (and plain text fields).
        # 2. Don't autolink Sample CLI, Signature, Full Code, etc.

        if use_query_links and key == "References" and isinstance(value, (list, tuple)):
            refs = [
                f'<a href="?topic={ref}">{html.escape(str(ref))}</a>' for ref in value
            ]
            value = ', '.join(refs)
            value = f"<div class='refs'>{value}</div>"

        # Improvement 4: Copy to clipboard button for Full Code
        elif key == "Full Code":
            code_id = f"code_{abs(hash(value))}"
            value = (
                f"<div class='full-code-block'>"
                f"<button class='copy-btn' onclick=\"copyToClipboard('{code_id}')\">Copy to clipboard</button>"
                f"<pre><code id='{code_id}' class='python'>{html.escape(str(value))}</code></pre>"
                f"</div>"
                "<script>"
                "function copyToClipboard(codeId) {"
                "  var text = document.getElementById(codeId).innerText;"
                "  navigator.clipboard.writeText(text).then(()=>{"
                "    alert('Copied!');"
                "  });"
                "}"
                "</script>"
            )

        # Code fields: no autolinking, just escape & highlight
        elif key in ("Signature", "Example CLI", "Example Code", "Sample CLI"):
            value = f"<pre><code class='python'>{html.escape(str(value))}</code></pre>"

        elif key in ("Docstring", "TODOs"):
            value = f"<div class='doc'>{html.escape(str(value))}</div>"

        # Only for regular text fields, run _autolink_refs
        elif use_query_links and isinstance(value, str):
            value = _autolink_refs(value)
            value = f"<p>{value}</p>"

        else:
            value = f"<p>{html.escape(str(value))}</p>"

        rows.append(f"<section><h3>{key}</h3>{value}</section>")

    # Highlight exact matches with a CSS class
    article_class = 'help-entry'
    if highlight:
        article_class += ' help-entry-exact'
    return f"<article class='{article_class}'>{header}{''.join(rows)}</article>"

def _autolink_refs(text):
    import re
    return re.sub(r'\b([a-zA-Z0-9_]+)(?:\.([a-zA-Z0-9_]+))?\b', 
        lambda m: (
            f'<a href="?topic={m.group(1)}">{m.group(1)}</a>' if not m.group(2) 
            else f'<a href="?topic={m.group(1)}/{m.group(2)}">{m.group(1)}.{m.group(2)}</a>'
        ), text)

def view_qr_code(*args, value=None, **kwargs):
    """Generate a QR code for a given value and serve it from cache if available."""
    if not value:
        return '''
            <h1>QR Code Generator</h1>
            <form method="post">
                <input type="text" name="value" placeholder="Enter text or URL" required class="main" />
                <button type="submit" class="submit">Generate QR</button>
            </form>
        '''
    qr_url = gw.qr.generate_url(value)
    back_link = gw.web.app_url("qr-code")
    return f"""
        <h1>QR Code for:</h1>
        <h2><code>{value}</code></h2>
        <img src="{qr_url}" alt="QR Code" class="qr" />
        <p><a href="{back_link}">Generate another</a></p>
    """

