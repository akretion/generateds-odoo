import textwrap

def wrap_text(text, indent, width=79, initial_indent=4, multi=False):
    text = text.strip()
    if not multi:
        if len(text) + initial_indent + 8 > width or "\n" in text or '"' in text:
            quote = '"""'
        else:
            quote = '"'
        if text[0] == '"':
            text = '%s %s' % (quote, text)
        else:
            text = '%s%s' % (quote, text)
        if text[-1] == '"':
            text = '%s %s' % (text, quote)
        else:
            text = '%s%s' % (text, quote)
    else:
        width -= 3

    wrapped_lines = []
    first = True
    for l in text.splitlines():
        if first:
            w = width - initial_indent
            first = False
        else:
            if multi:
                w = width - indent
            else:
                w = width
        lines = textwrap.fill(' '.join(l.strip().split()), width=w,
                              subsequent_indent=' ' * indent,
                              replace_whitespace=False).splitlines()
        wrapped_lines += [i.strip() for i in lines]
    text = ("\n" + " " * indent).join(wrapped_lines)

    if not multi:
        return text
    else:
        lines = ["\"%s\"" % (i.strip().replace('"', "'"),) for i in text.splitlines()]
        lines2 = []
        first = True
        for l in lines:
            if not first:
                l = "\"\\n%s" % (l[1:100],)
            else:
                first = False
            lines2.append(l)
        text = ("\n%s" % (" " * indent,)).join(lines2)
        if "\n" in text:
            text = "%s" % (text,)
        return text
