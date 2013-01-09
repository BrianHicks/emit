def make_digraph(router, name='router'):
    header = 'digraph %s {\n' % name
    footer = '\n}'

    lines = []
    for origin, destinations in router.routes.items():
        for destination in destinations:
            lines.append('"%s" -> "%s";' % (origin, destination))

    return header + '\n'.join(lines) + footer
