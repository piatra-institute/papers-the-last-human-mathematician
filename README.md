# 1976–2036: From the Last Human Computer to the Last Human Mathematician

In the 1930s and 1940s a computer was a person who calculated for a living; within two decades the word meant a machine. The paper dates that transfer from English books: writers marked the machine sense of "computer" with a qualifier ("electronic", "digital", "automatic") in 22.7% of uses at the 1955 peak and in a tenth of that share by 1980, and most printed uses referred to machines by 1952, two decades before the four-colour theorem of 1976 and while NASA still employed human computers. In a second case, "typewriter", the operator was renamed "typist". The same measure applied to "mathematician" in October 2026 shows "human mathematician" rising to 1.5% of scholarly works using the noun, almost always beside terms for AI, while machines are rarely called mathematicians: the contrastive marking that preceded the transfer of "computer", without the extension that accompanied it. The paper separates five transitions (capability, operational autonomy, research production, professional jurisdiction, semantic default) and two outcomes (human understanding and control), reads the verified 2026 record of machine mathematics and the professional responses to it against them, and states three claims for 2036 that can be preregistered and can fail. No forecast of a year is made.

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run `papers build the-last-human-mathematician`.

## Corpus analysis

```bash
cd simulation && uv run run_all.py     # reads the frozen data in data/ -> output/results.json and output/figures/*.png, 12 checks
cd simulation && uv run fetch_data.py  # re-retrieves the data (Google Books Ngram Viewer, OpenAlex); results will change as the indexes change
```

The data in `simulation/data/` were retrieved on 8 October 2026: Google Books Ngram Viewer series (English, case-insensitive), OpenAlex yearly counts, and identifiers, titles and computed flags for works matching "human mathematician".

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace docs for the research and writing pipelines.
