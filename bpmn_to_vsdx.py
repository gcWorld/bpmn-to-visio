"""
Fix for bpmn_to_vsdx.py — background fill colours not exported correctly.

ROOT CAUSE
==========
The original `_fill_xml()` only emits `<Cell N="FillForegnd" …/>`, which is the
*foreground* layer used by patterned fills.  For a solid fill Visio also needs:

  FillPattern  = 1     → solid fill  (0 = no fill / fully transparent in many
                                       Visio versions, which is the default)
  FillBkgnd    = <hex> → the VISIBLE background colour that gets painted
  FillBkgndTrans = 0   → background fully opaque

Without these cells Visio renders the shape as if it has no fill (pattern=0),
so the shape appears white / transparent even though the border colour is
correct (LineColor is a completely separate property and works fine).

HOW TO APPLY
============
In bpmn_to_vsdx.py, find the function `_fill_xml` (around line 870–885) and
replace the entire function body with the version below.

REPLACEMENT FUNCTION
====================
"""


def _fill_xml(category, fill_color=None):
    """Return fill color cells based on element category or per-shape BPMN color.

    Visio solid fills require ALL of:
      FillPattern=1    → solid fill (0 means no fill / transparent)
      FillBkgnd        → the VISIBLE background colour (what gets painted)
      FillBkgndTrans   → background transparency  (0 = fully opaque)
      FillForegnd      → foreground used for patterned fills (= BkGnd for solid)
      FillForegndTrans → foreground transparency

    The original code only set FillForegnd, leaving FillBkgnd unset (defaults
    to white) and FillPattern unset (defaults to 0 = no fill in many Visio
    versions).  That is why only the border colour was correct while the box
    background appeared white/transparent regardless of bioc:fill.
    """
    if fill_color:
        # Both BkGnd and ForeGnd must carry the colour for a solid fill.
        return (
            f'<Cell N="FillPattern" V="1"/>'
            f'<Cell N="FillBkgnd" V="{fill_color}"/>'
            f'<Cell N="FillBkgndTrans" V="0"/>'
            f'<Cell N="FillForegnd" V="{fill_color}"/>'
            f'<Cell N="FillForegndTrans" V="0"/>'
        )

    # Default BPMN colours: white fill for all shapes, matching bpmn.io defaults.
    if category == 'annotation':
        # Annotations have no background in BPMN — use FillPattern=0 (transparent).
        return (
            '<Cell N="FillPattern" V="0"/>'
            '<Cell N="FillForegnd" V="#FFFFFF"/>'
            '<Cell N="FillForegndTrans" V="1"/>'
        )
    else:  # tasks, events, gateways, pools, lanes — solid white
        return (
            '<Cell N="FillPattern" V="1"/>'
            '<Cell N="FillBkgnd" V="#FFFFFF"/>'
            '<Cell N="FillBkgndTrans" V="0"/>'
            '<Cell N="FillForegnd" V="#FFFFFF"/>'
            '<Cell N="FillForegndTrans" V="0"/>'
        )


# ─── QUICK SELF-TEST ────────────────────────────────────────────────────────
if __name__ == '__main__':
    tests = [
        ('task with orange fill',  'task',        '#FF9900'),
        ('task with blue fill',    'task',        '#0080FF'),
        ('task default (white)',   'task',        None),
        ('annotation (no fill)',   'annotation',  None),
        ('pool default (white)',   'participant', None),
    ]
    for label, cat, color in tests:
        result = _fill_xml(cat, color)
        print(f'{label}:\n  {result}\n')
