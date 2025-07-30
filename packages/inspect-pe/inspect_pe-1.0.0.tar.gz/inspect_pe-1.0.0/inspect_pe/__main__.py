#!/usr/bin/env python3
"""
inspect_pe.py — Portable Executable Swiss‑Army‑Knife
===================================================
• Cross‑platform: works on Linux, macOS (arm64/x64, via brew), Windows, WSL, VMs, sand‑boxes—anywhere Python ≥ 3.9 runs.
• Hard dependency:   pefile  (pip install pefile)
• Soft dependencies: ssdeep, rich, yara‑python, lief, capstone  ➜ auto‑detected / optional.

Main tricks
-----------
1. Header / section / import / export / resource / TLS parsing.
2. Hashes  (md5/sha1/sha256/ssdeep) + imphash + richhash.
3. Entropy & simple packer heuristics.
4. Entry‑point disassembly (capstone)  — `--disasm 128`.
5. Digital‑signature metadata  (lief)  — `--sign`.
6. YARA scanning  — `--yara rules.yar`.
7. Section dumping       — `--dump-sections dir`.
8. Resource dumping      — `--dump-resources dir`.
9. JSON report           — `--json`  (machine‑readable output).
10. Pretty colour output (rich) with graceful fallback.

Example‑fu
~~~~~~~~~~
  ## Minimal summary
  ./inspect_pe.py evil.exe

  ## Everything (and save artefacts)
  ./inspect_pe.py evil.exe --entropy --hashes --imports --exports \
       --resources --tls --disasm 256 \
       --yara amazing_rules.yar --sign \
       --dump-sections ./dump/sections --dump-resources ./dump/res --json > full_report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# ----------------------------------------------------------------------------
# Mandatory dependency
# ----------------------------------------------------------------------------
try:
    import pefile
except ImportError:
    sys.exit("[!] pefile missing —  install with:  pip install pefile")

# ----------------------------------------------------------------------------
# Optional deps
# ----------------------------------------------------------------------------


def _optmod(name: str):
    try:
        return __import__(name)
    except ImportError:
        return None

rich = _optmod("rich")
ssdeep = _optmod("ssdeep")
yara = _optmod("yara")
lief = _optmod("lief")
capstone = _optmod("capstone")

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def cprint(msg: str, style: str | None = None):
    if rich:
        from rich import print as rprint
        rprint(msg if style is None else f"[{style}]{msg}[/{style}]")
    else:
        print(msg)


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    probs = [data.count(b) / len(data) for b in set(data)]
    return -sum(p * math.log2(p) for p in probs)


# ----------------------------------------------------------------------------
# PE‑related extraction helpers
# ----------------------------------------------------------------------------


def gather_sections(pe: pefile.PE, want_entropy: bool) -> List[Dict[str, Any]]:
    out = []
    for s in pe.sections:
        d = {
            "name": s.Name.rstrip(b"\x00").decode(errors="ignore"),
            "vaddr": f"0x{s.VirtualAddress:08X}",
            "vsize": hex(s.Misc_VirtualSize),
            "raw_size": hex(s.SizeOfRawData),
            "chars": hex(s.Characteristics),
        }
        if want_entropy:
            d["entropy"] = round(shannon_entropy(s.get_data()), 2)
        out.append(d)
    return out


def gather_imports(pe: pefile.PE) -> List[Dict[str, Any]]:
    result = []
    for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []) or []:
        dll = entry.dll.decode(errors="ignore")
        for imp in entry.imports:
            result.append({
                "dll": dll,
                "name": imp.name.decode(errors="ignore") if imp.name else None,
                "ordinal": imp.ordinal,
                "addr": hex(imp.address)
            })
    return result


def gather_exports(pe: pefile.PE) -> List[Dict[str, Any]]:
    out = []
    base = pe.OPTIONAL_HEADER.ImageBase
    for exp in getattr(pe, "DIRECTORY_ENTRY_EXPORT", []).symbols if hasattr(pe, "DIRECTORY_ENTRY_EXPORT") else []:
        out.append({
            "name": exp.name.decode(errors="ignore") if exp.name else None,
            "ordinal": exp.ordinal,
            "addr": hex(base + exp.address)
        })
    return out


def gather_resources(pe: pefile.PE) -> List[Dict[str, Any]]:
    out = []
    for top in getattr(pe, "DIRECTORY_ENTRY_RESOURCE", []).entries if hasattr(pe, "DIRECTORY_ENTRY_RESOURCE") else []:
        rtype = pefile.RESOURCE_TYPE.get(top.struct.Id) or str(top.struct.Id)
        if not hasattr(top, "directory"):
            continue
        for entry in top.directory.entries:
            for lang in entry.directory.entries:
                out.append({
                    "type": rtype,
                    "lang": hex(lang.data.lang),
                    "sublang": hex(lang.data.sublang),
                    "rva": hex(lang.data.struct.OffsetToData),
                    "size": lang.data.struct.Size
                })
    return out


def gather_tls_callbacks(pe: pefile.PE) -> List[str]:
    callbacks = []
    tls = getattr(pe, "DIRECTORY_ENTRY_TLS", None)
    if not tls:
        return callbacks
    va_array = tls.struct.AddressOfCallBacks
    while True:
        off = pe.get_offset_from_rva(va_array - pe.OPTIONAL_HEADER.ImageBase)
        val = int.from_bytes(pe.__data__[off:off + 4], "little")
        if val == 0:
            break
        callbacks.append(hex(val))
        va_array += 4
    return callbacks


# ----------------------------------------------------------------------------
# Misc helpers
# ----------------------------------------------------------------------------


def file_hash_dict(path: str) -> Dict[str, str]:
    md5, sha1, sha256 = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk); sha1.update(chunk); sha256.update(chunk)
    out = {"md5": md5.hexdigest(), "sha1": sha1.hexdigest(), "sha256": sha256.hexdigest()}
    if ssdeep:
        out["ssdeep"] = ssdeep.hash_from_file(path)
    return out


def calc_rich_hash(pe: pefile.PE):
    try:
        rich = pe.parse_rich_header()
        if not rich or "values" not in rich:
            return None
        import zlib
        comp = zlib.compress(bytes(rich["values"]))
        return hashlib.sha256(comp).hexdigest()
    except Exception:
        return None


def packer_guess(sections: List[Dict[str, Any]]):
    names = {s["name"].lower() for s in sections}
    if {"upx0", "upx1"} <= names:
        return "UPX"
    if {"pec1", "pec2"} & names:
        return "PECompact"
    if any("mpress" in n for n in names):
        return "MPRESS"
    return None


# ----------------------------------------------------------------------------
# Capstone disassembly
# ----------------------------------------------------------------------------


def disasm_entrypoint(pe: pefile.PE, path: str, nbytes: int) -> List[str]:
    if not capstone:
        return []
    mode = capstone.CS_MODE_64 if pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_AMD64'] else capstone.CS_MODE_32
    md = capstone.Cs(capstone.CS_ARCH_X86, mode)
    rva = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    offset = pe.get_offset_from_rva(rva)
    with open(path, "rb") as fp:
        fp.seek(offset)
        code = fp.read(nbytes)
    lines = []
    for ins in md.disasm(code, pe.OPTIONAL_HEADER.ImageBase + rva):
        lines.append(f"0x{ins.address:08X}: {ins.mnemonic} {ins.op_str}")
        if len(lines) >= 64:  # reasonable cap
            break
    return lines


# ----------------------------------------------------------------------------
# LIEF digital‑signature info
# ----------------------------------------------------------------------------


def signature_info(path: str):
    if not lief:
        return None
    try:
        binary = lief.parse(path)
        if not binary.has_signatures:
            return None
        out = []
        for sig in binary.signatures:
            out.append({
                "version": sig.version,
                "sign_time": str(sig.sign_time),
                "issuer": sig.signer_info.issuer,
                "subject": sig.signer_info.subject
            })
        return out
    except Exception:
        return None


# ----------------------------------------------------------------------------
# YARA
# ----------------------------------------------------------------------------


def yara_rules_scan(path: str, rules: str):
    if not yara:
        raise RuntimeError("yara-python missing; install with: pip install yara-python")
    compiled = yara.compile(filepath=rules)
    return [m.rule for m in compiled.match(path)]


# ----------------------------------------------------------------------------
# Dumping helpers
# ----------------------------------------------------------------------------


def dump_blob(blob: bytes, outfile: Path):
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with open(outfile, "wb") as fp:
        fp.write(blob)


def dump_all_sections(pe: pefile.PE, outdir: Path):
    dumped = []
    for s in pe.sections:
        name = s.Name.rstrip(b"\x00").decode(errors="ignore") or "SECTION"
        filename = f"{name}_{s.VirtualAddress:08X}.bin"
        dump_blob(s.get_data(), outdir / filename)
        dumped.append(str(outdir / filename))
    return dumped


def dump_all_resources(pe: pefile.PE, outdir: Path):
    dumped = []
    if not hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
        return dumped
    base = outdir
    for top in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        rtype = pefile.RESOURCE_TYPE.get(top.struct.Id) or str(top.struct.Id)
        for entry in top.directory.entries:
            for lang in entry.directory.entries:
                data = pe.get_data(lang.data.struct.OffsetToData, lang.data.struct.Size)
                filename = f"{rtype}_{lang.data.lang}_{lang.data.sublang}_{lang.data.struct.OffsetToData:08X}.bin"
                dump_blob(data, base / filename)
                dumped.append(str(base / filename))
    return dumped


# ----------------------------------------------------------------------------
# Report generator
# ----------------------------------------------------------------------------


def build_report(path: str, args) -> Dict[str, Any]:
    pe = pefile.PE(path, fast_load=False)
    rep: Dict[str, Any] = {
        "file": os.path.basename(path),
        "size": os.path.getsize(path),
        "compile_time": datetime.utcfromtimestamp(pe.FILE_HEADER.TimeDateStamp).isoformat() + "Z",
        "arch": "64" if pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_AMD64'] else "32",
        "image_base": hex(pe.OPTIONAL_HEADER.ImageBase),
        "entry_point": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
        "imphash": pe.get_imphash(),
        "richhash": calc_rich_hash(pe),
    }

    # Sections & heuristics
    rep["sections"] = gather_sections(pe, args.entropy)
    rep["packer_guess"] = packer_guess(rep["sections"])

    if args.hashes:
        rep["hashes"] = file_hash_dict(path)
    if args.imports:
        rep["imports"] = gather_imports(pe)
    if args.exports:
        rep["exports"] = gather_exports(pe)
    if args.resources:
        rep["resources"] = gather_resources(pe)
    if args.tls:
        rep["tls_callbacks"] = gather_tls_callbacks(pe)
    if args.disasm:
        rep["disasm"] = disasm_entrypoint(pe, path, args.disasm)
    if args.sign:
        rep["signatures"] = signature_info(path)
    if args.yara:
        rep["yara_matches"] = yara_rules_scan(path, args.yara)
    if args.dump_sections:
        rep["dumped_sections"] = dump_all_sections(pe, Path(args.dump_sections))
    if args.dump_resources:
        rep["dumped_resources"] = dump_all_resources(pe, Path(args.dump_resources))
    return rep


# ----------------------------------------------------------------------------
# Pretty print / JSON
# ----------------------------------------------------------------------------


def echo_pretty(rep: Dict[str, Any]):
    cprint(f"
[bold cyan]=== {rep['file']} ===[/]" if rich else f"=== {rep['file']} ===")
    cprint(f"Size: {rep['size']} bytes   Arch: {rep['arch']}-bit   EP: {rep['entry_point']}  Base: {rep['image_base']}")
    cprint(f"Compiled: {rep['compile_time']}   imphash: {rep['imphash']}   richhash: {rep['richhash']}")
    if rep.get("packer_guess"):
        cprint(f"[red]Packer guess:[/] {rep['packer_guess']}" if rich else f"Packer guess: {rep['packer_guess']}")

    cprint("
[bold green]Sections:[/]
" if rich else "
Sections:")
    for s in rep['sections']:
        line = f"{s['name']:<10} VA {s['vaddr']} RSZ {s['raw_size']} VSZ {s['vsize']}"
        if 'entropy' in s:
            line += f"  ENT {s['entropy']:.2f}"
        cprint(line)

    # optional blocks
    if rep.get("hashes"):
        cprint("
[bold yellow]Hashes:[/]") if rich else cprint("
Hashes:")
        for h, v in rep['hashes'].items():
            cprint(f"{h.upper():6}: {v}")

    def dump_list(title, key):
        if rep.get(key):
            cprint(f"
[bold magenta]{title}:[/]") if rich else cprint(f"
{title}:")
            for item in rep[key]:
                cprint(str(item))
    dump_list("TLS Callbacks", "tls_callbacks")
    dump_list("Imports", "imports")
    dump_list("Exports", "exports")
    dump_list("Resources", "resources")
    dump_list("YARA Matches", "yara_matches")
    dump_list("Signatures", "signatures")
    dump_list("Disassembly", "disasm")
    dump_list("Dumped Sections", "dumped_sections")
    dump_list("Dumped Resources", "dumped_resources")


# ----------------------------------------------------------------------------
# CLI / main
# ----------------------------------------------------------------------------


def build_parser():
    p = argparse.ArgumentParser(description="Advanced PE inspector — parses & dumps rich metadata")
    p.add_argument("pe", help="Target PE file (.exe/.dll)")
    p.add_argument("--entropy", action="store_true", help="Calculate section entropy")
    p.add_argument("--hashes", action="store_true", help="Output file hashes & ssdeep (if available)")
    p.add_argument("--imports", action="store_true", help="List imported APIs")
    p.add_argument("--exports", action="store_true", help="List exported symbols")
    p.add_argument("--resources", action="store_true", help="List resources")
    p.add_argument("--tls", action="store_true", help="List TLS callbacks")
    p.add_argument("--disasm", type=int, metavar="N", help="Disassemble N bytes at entry‑point (needs capstone)")
    p.add_argument("--sign", action="store_true", help="Dump Authenticode signature info (needs lief)")
    p.add_argument("--yara", metavar="RULES", help="Scan with YARA rule file (needs yara-python)")
    p.add_argument("--dump-sections", metavar="DIR", help="Dump each section to DIR")
    p.add_argument("--dump-resources", metavar="DIR", help="Dump each raw resource to DIR")
    p.add_argument("--json", action="store_true", help="Print JSON instead of pretty text")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.pe):
        parser.error("File not found → " + args.pe)

    report = build_report(args.pe, args)

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        echo_pretty(report)


if __name__ == "__main__":
    main()
