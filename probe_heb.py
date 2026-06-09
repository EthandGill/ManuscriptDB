import subprocess, sys, re
sys.stdout.reconfigure(encoding='utf-8')
manuscripts = [
    (10012,'P12'),(10013,'P13'),(10017,'P17'),(10079,'P79'),
    (10089,'P89'),(10114,'P114'),(10116,'P116'),(10126,'P126'),(10130,'P130'),
]
results = {}
for doc_id, label in manuscripts:
    r = subprocess.run(
        ['python', r'.claude/skills/grab-manuscript/scripts/probe_pages.py',
         str(doc_id), '--max', '300'],
        capture_output=True, text=True, cwd=r'C:\ManuscriptDB'
    )
    m = re.search(r'FOUND_PAGES:([\d,]*)', r.stdout)
    pages = [int(p) for p in m.group(1).split(',') if p] if m else []
    details = [l for l in r.stdout.splitlines() if l.startswith('pageID')]
    results[label] = pages
    print(f"{label} ({doc_id}): {pages}")
    for d in details: print(f"  {d}")
    sys.stdout.flush()
print("\n=== SUMMARY ===")
for k,v in results.items(): print(f"{k}: {v}")
