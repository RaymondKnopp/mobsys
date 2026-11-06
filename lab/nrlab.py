"""Small helpers for the MobSys 5G NR lab.

They only wrap scat and tshark so that the notebook can stay focused on the
protocol questions. Everything 3GPP-related (ARFCN, RIV, SLIV, CORESET#0...)
is left to you to compute in the notebook.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent                       # the mobsys repository
SCAT_REPO = REPO.parent / 'scat'         # scat checked out next to it


def find_scat_lua() -> Path:
    """Locate the scat Wireshark plugin (needed to dissect GSMTAPv3 / NR RRC):
    $SCAT_LUA, then ../scat/wireshark/scat.lua, then the personal plugin folders."""
    candidates = [os.environ.get('SCAT_LUA', ''),
                  SCAT_REPO / 'wireshark' / 'scat.lua',
                  Path.home() / '.local/lib/wireshark/plugins/scat.lua',
                  Path.home() / '.config/wireshark/plugins/scat.lua']
    for c in candidates:
        if c and Path(c).is_file():
            return Path(c)
    raise FileNotFoundError('scat.lua not found: set the SCAT_LUA environment variable')


def check_tools() -> None:
    """Print the versions of the tools used in the lab."""
    for tool, arg in (('scat', '-V'), ('tshark', '--version')):
        path = shutil.which(tool)
        if path is None:
            print(f'{tool:7s}: NOT FOUND in PATH')
            continue
        out = subprocess.run([tool, arg], capture_output=True, text=True).stdout.splitlines()
        print(f'{tool:7s}: {out[0] if out else "?"} ({path})')
    print(f'scat.lua: {find_scat_lua()}')


def run_scat(dump: str | Path, pcap: str | Path) -> Path:
    """Convert a Qualcomm baseband dump (.qmdl/.dlf/.hdf) into a pcap with scat."""
    pcap = Path(pcap)
    subprocess.run(['scat', '-t', 'qc', '-d', str(dump), '-F', str(pcap)],
                   check=True, stdout=subprocess.DEVNULL)
    return pcap


def _tshark(pcap, extra):
    cmd = ['tshark', '-X', f'lua_script:{find_scat_lua()}', '-r', str(pcap)] + extra
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    # scat.lua prints a warning on stdout for each NR RRC dissector missing in
    # older Wireshark versions (e.g. nr-rrc.sib2); these are harmless, drop them.
    return '\n'.join(l for l in res.stdout.splitlines()
                     if not l.startswith('Cannot find dissector'))


# Columns every packet has: time, NR-ARFCN and PCI from the scat (GSMTAPv3) header,
# the UE information comment, and the RRC message name.
BASE_FIELDS = {
    'frame': 'frame.number',
    'time': 'frame.time_relative',
    'arfcn': 'gsmtapv3.channel_number',
    'pci': 'gsmtapv3.multiplex',
    'comment': 'gsmtapv3.packet_comment',
    'message': '_ws.col.Info',
}


def packets(pcap, **extra_fields) -> pd.DataFrame:
    """One row per packet. Add Wireshark fields as keyword arguments, e.g.
    packets(pcap, barred='nr-rrc.cellBarred'). Repeated fields come back as
    comma-separated strings."""
    fields = {**BASE_FIELDS, **extra_fields}
    args = ['-T', 'fields', '-E', 'separator=\t', '-E', 'occurrence=a', '-E', 'aggregator=,']
    for f in fields.values():
        args += ['-e', f]
    rows = [line.split('\t') for line in _tshark(pcap, args).splitlines() if line]
    df = pd.DataFrame(rows, columns=list(fields.keys()))
    for col in ('frame', 'arfcn', 'pci'):
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    df['time'] = pd.to_numeric(df['time'], errors='coerce')
    return df


def show(pcap, frame: int, grep: str | None = None) -> None:
    """Print the decoded RRC message of one frame, like Wireshark's packet details.
    With grep, only lines containing that string (case-insensitive) are printed."""
    text = _tshark(pcap, ['-Y', f'frame.number=={frame}', '-O', 'nr-rrc'])
    start = text.find('NR Radio Resource Control')
    text = text[start:] if start >= 0 else text
    for line in text.splitlines():
        if grep is None or grep.lower() in line.lower():
            print(line)


def field(pcap, frame: int, name: str) -> list[str]:
    """All values of one Wireshark field (e.g. 'nr-rrc.k2') in one frame, in order."""
    out = _tshark(pcap, ['-Y', f'frame.number=={frame}', '-T', 'json', '-e', name])
    data = json.loads(out)
    if not data:
        return []
    return data[0]['_source']['layers'].get(name, [])
