import textwrap

def wrap_text(text, indent, width):
    text = text.replace("\"", "'")
    wrapped_lines = []
    for l in text.strip().splitlines():
        wrapped_lines.append(textwrap.fill(l, width=width,
                             subsequent_indent='    ',
                             replace_whitespace=False))
    text = "\n".join(wrapped_lines)
    lines = ["u\"%s\"" % (i.strip(),) for i in text.splitlines()]
    text = ("\n%s" % (" " * indent,)).join(lines)
    if "\n" in text:
        text = "(%s)" % (text,)
    return text
