"""Where an event happens, as three fields rather than one parsed string.

`event-location` used to hold "HEX Gallery, Lidická 63a, Brno" and the address
was recovered by splitting on commas. That put the whole weight on the *shape*
of one value: "Sono Centrum Brno" without its comma produced a venue with no
address, and nothing said so. To keep the shape safe, the CMS offered a frozen
list of twenty venues — so an event at the twenty-first could not be created at
all.

`event-venue`, `event-street` and `event-locality` carry the same information
with neither problem. Nothing is parsed, so nothing degrades quietly, and
nothing has to be on a list.

Two readers, one function:

  the address    article.html builds a schema.org Place out of `name` and a
                 PostalAddress out of `streetAddress` / `addressLocality`.
                 `addressCountry` is the template's business, not ours.
  the line       the card, the ICS export and the LLM mirror print one human
                 string. It is spelled exactly the way the old single value
                 was, so the migration left the output byte for byte the same.

Not a Pelican plugin despite living here: it registers no signal. `plugins/` is
on sys.path for both pelicanconf.py and the calendarium package, and this is
the one place they both need to agree on.
"""

# In the order they are written and read.
FIELDS = (("event-venue", "name"),
          ("event-street", "streetAddress"),
          ("event-locality", "addressLocality"))


def place(metadata):
    """{name?, streetAddress?, addressLocality?, line} — empty keys left out.

    An absent part is omitted rather than written empty: a schema.org validator
    reads `"streetAddress": ""` as a claim about the address, not as silence.
    Returns `{}` when the event names no place at all, which is what the
    templates test for.
    """
    values = metadata or {}
    parts = []
    address = {}
    for field, key in FIELDS:
        value = str(values.get(field) or "").strip()
        if not value:
            continue
        address[key] = value
        parts.append(value)
    if not parts:
        return {}
    address["line"] = ", ".join(parts)
    return address
