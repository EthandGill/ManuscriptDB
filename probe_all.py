"""Run probes for all needed manuscripts sequentially and output clean results."""
import subprocess, sys, re
sys.stdout.reconfigure(encoding='utf-8')

manuscripts = [
    (10051, 'P51'),
    (10049, 'P49'),
    (10092, 'P92'),
    (10132, 'P132'),
    (10016, 'P16'),
    (10030, 'P30'),
    (10065, 'P65'),
    (10133, 'P133'),
    (10032, 'P32'),
    (10087, 'P87'),
    (10135, 'P135'),
    (10139, 'P139'),
]

results = {}
for doc_id, label in manuscripts:
    print(f"Probing {label} (docID={doc_id})...", flush=True)
    r = subprocess.run(
        ['python', r'.claude/skills/grab-manuscript/scripts/probe_pages.py',
         str(doc_id), '--max', '60'],
        capture_output=True, text=True, cwd=r'C:\ManuscriptDB'
    )
    output = r.stdout.strip()
    # Extract FOUND_PAGES line
    m = re.search(r'FOUND_PAGES:([\d,]*)', output)
    pages = [int(p) for p in m.group(1).split(',') if p] if m else []
    # Show page details
    for line in output.splitlines():
        if line.startswith('pageID'):
            print(f"  {line}")
    print(f"  => PAGES: {pages}\n", flush=True)
    results[label] = pages

print("=== SUMMARY ===")
for label, pages in results.items():
    print(f"{label}: {pages}")
