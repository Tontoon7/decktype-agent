# Text block alignment (format 0.19.0)

Four choices: left, center, right, justified. To justify, write
`align: "left"` and `justify: true` together. For the other three choices,
write the desired `align` and `justify: false`. On a linked element, set both
properties as overrides in the same patch without changing other edits.

Never write `align: "justify"`: older readers reject this value.
They accept the unknown boolean and render according to `align`, but rewriting
may lose justification. The corresponding template schema is 0.13.0;
`justify` has the same meaning there as on materialized text.

Paragraph endings are not stretched; do not insert spaces into content to
simulate alignment. Table cells retain their three historical alignments.
Native, inline and web rendering use the same paragraph choice.
PowerPoint uses `algn="just"`.
