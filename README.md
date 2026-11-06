# MobSys — 5G NR course material

Lecture notes and a hands-on lab for the EURECOM *Mobile Communication Systems*
course. The lab uses real 5G traces captured with a commercial phone and converted
to pcap with [**scat**](https://github.com/RaymondKnopp/scat) (our fork of
[fgsect/scat](https://github.com/fgsect/scat), branch `mobsys`).

```
mobsys/
├── lectures/
│   ├── 01_phy_basics_and_initial_access.md   numerology, grid, OFDM, BWP, SSB, PBCH, SI, PDCCH, SIB1
│   └── 02_dl_ul_procedures.md                PDSCH, HARQ, PRACH/RA, TA, PUSCH, PUCCH, CSI, TDD
├── lab/
│   ├── cell_search_lab.ipynb                 the lab (Questions 1–22)
│   └── nrlab.py                              small scat/tshark helpers used by the notebook
├── data/
│   ├── cell_search.hdf                       raw Qualcomm trace (QXDM), NR cell search, Mouans-Sartoux, Galaxy S23 Ultra
│   ├── cell_search.pcap                      the same trace converted by scat
│   ├── cell_search_051124.hdf                second capture, same place
│   └── cell_search_051124.pcap
└── figures/
    ├── make_figures.py                       generates every figure (matplotlib)
    └── *.svg
```

## Reading the lectures

The lectures are Markdown files. GitHub renders them directly. To get slides, use
[Marp](https://marp.app/) (the *Marp for VS Code* extension, or its command line
through `npx`, which needs Node.js). Write the HTML next to the Markdown so that
the figures (`../figures/*.svg`) are found:

```bash
cd lectures
# to present: one slide at a time, in a web browser
npx @marp-team/marp-cli 01_phy_basics_and_initial_access.md --html -o 01.html
# to read or scroll through (also works inside JupyterLab)
npx @marp-team/marp-cli 01_phy_basics_and_initial_access.md --html --template bare -o 01_scroll.html
```

The default (presentation) HTML is driven by JavaScript: in a browser, use the arrow
keys or click, `f` for full screen, `p` for the presenter view. **JupyterLab's HTML
viewer blocks scripts**, so that version stays stuck on the first slide there; use the
`--template bare` version (slides stacked vertically, no script), or click
*Trust HTML* in the viewer's toolbar.

To regenerate the figures after editing `figures/make_figures.py`:
`cd figures && python3 make_figures.py`.

## Setting up for the lab

You need Python ≥ 3.10, Wireshark (≥ 4.2; ≥ 4.4 recommended) with `tshark`, and Jupyter.
Check out this repository and scat **next to each other**:

```bash
mkdir mobsys-course && cd mobsys-course
git clone https://github.com/RaymondKnopp/mobsys.git
git clone -b mobsys https://github.com/RaymondKnopp/scat.git
python3 -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ./scat jupyter pandas matplotlib
scat -V                                           # should print "SCAT 2.1.2" (or later)
```

* scat is pure Python: `pip install -e ./scat` installs it (and its dependencies)
  from your checkout, nothing to compile. `-e` means that `git pull` in `scat/`
  is enough to get later fixes, without reinstalling.
* Install it **from this fork** (branch `mobsys`), not with `pip install signalcat`
  from PyPI: the course needs changes that are not in the upstream release
  (e.g. the UE RRC release shown with each NR RRC message, Question 2).
* Always work inside the virtual environment (`. .venv/bin/activate` in every new
  terminal). Recent Linux distributions refuse `pip install` outside one
  ("externally-managed-environment").
* Optional: `pip install -e "./scat[fastcrc]"` adds a faster CRC library; it needs a
  C compiler and is not needed for the lab.

**Wireshark plugin.** 5G NR messages from scat are encapsulated in GSMTAPv3, which
Wireshark only decodes with the scat Lua plugin. Copy `scat/wireshark/scat.lua` into
your personal Wireshark plugin folder (*Help → About Wireshark → Folders → Personal
Lua Plugins*, typically `~/.local/lib/wireshark/plugins/` on Linux,
`%APPDATA%\Wireshark\plugins\` on Windows) and restart Wireshark. The notebook finds
the plugin in `../scat` by itself (or set `SCAT_LUA` to its path).

Wireshark < 4.4 prints *"Cannot find dissector nr-rrc.sibN"* when loading the
plugin: harmless for this lab.

Then:

```bash
cd mobsys/lab
jupyter lab cell_search_lab.ipynb
```

The notebook converts the raw trace `data/cell_search.hdf` with scat (into
`lab/cell_search.pcap`); if scat is not installed it uses the provided
`data/cell_search.pcap`, which is the same conversion.

## Handing in your work

Answer the questions directly in `cell_search_lab.ipynb` (code cells and the
*Your answer* cells) and hand it in through a **private** repository.

**Don't use GitHub's *Fork* button:** a fork of a public repository is always
public, so your answers would be visible to everyone. Make a private copy instead:

1. On GitHub, create a new **private** repository, e.g. `mobsys-<yourname>`,
   without a README.
2. Point your clone of this repository at it:
   ```bash
   cd mobsys
   git remote rename origin course
   git remote add origin https://github.com/<you>/mobsys-<yourname>.git
   git push -u origin main
   ```
3. Work, commit and push to `origin` as usual. To get later updates of the course
   material: `git pull course main`.
4. In your repository, go to *Settings → Collaborators* and add the instructor's
   GitHub account (given in class) before the deadline.

## Converting a trace yourself

```bash
scat -t qc -d my_trace.hdf -F my_trace.pcap        # Qualcomm .qmdl / .dlf / .hdf
scat -t sec -d my_trace.sdm -F my_trace.pcap       # Samsung (Shannon) SDM
```

Only messages logged in clear by the modem can be decoded. Recent Qualcomm modems
encrypt most diagnostic logs ("Secure DIAG"); for the traces of this lab, only the
NR RRC MIB and SIB1 are readable by scat. For example:

```bash
scat -t qc -d data/cell_search_051124.hdf -F /tmp/second.pcap
```

## Instructors

Solutions are generated together with the student notebook by
`lab/solutions/build_notebooks.py`. That directory is listed in `.gitignore` and
must never be committed. Edit the questions there, then run it to regenerate both
notebooks.
