// ═══════════════════════════════════════════════════════════════════════════
//  Pauline Network — rebuilt from Gill (2025)
//  "The Complete Social Network of Paul"
//  Source: Figure 2 — all 61 active nodes across 7 Undisputed Pauline Letters
// ═══════════════════════════════════════════════════════════════════════════

// ── NODE DATA ────────────────────────────────────────────────────────────────
// role:    'apostle' | 'companion' | 'inner' | 'outer'
// severed: true  →  dashed border, ghost fill (broken tie)
// capital: 'church' | 'economic' | 'both'  →  affects border colour

const PN_NODES = [

  // ── Jerusalem ───────────────────────────────
  { id: 'paul', name: 'Paul', lon: 35.22, lat: 31.78, city: 'Hierosolyma', letters: 'All Undisputed Letters', role: 'apostle' },
  { id: 'cephas', name: 'Cephas', lon: 34.995, lat: 31.4421, city: 'Hierosolyma', letters: 'Galatians, 1 Corinthians', role: 'inner', severed: true },
  { id: 'james', name: 'James', lon: 35.445, lat: 31.4421, city: 'Hierosolyma', letters: 'Galatians, 1 Corinthians', role: 'inner', severed: true },
  { id: 'john', name: 'John', lon: 34.995, lat: 32.1179, city: 'Hierosolyma', letters: 'Galatians', role: 'inner', severed: true },

  // ── Antioch ───────────────────────────────
  { id: 'barnabas', name: 'Barnabas', lon: 36.14, lat: 36.22, city: 'Antiocheia', letters: 'Galatians, 1 Corinthians', role: 'inner', severed: true },

  // ── Ephesus ───────────────────────────────
  { id: 'timothy', name: 'Timothy', lon: 27.0, lat: 38.0, city: 'Ephesos', letters: 'Romans, 2 Cor, Phil, 1 Thess, Phm', role: 'companion', capital: 'church' },
  { id: 'sosthenes', name: 'Sosthenes', lon: 26.675, lat: 37.5119, city: 'Ephesos', letters: '1 Corinthians', role: 'companion', capital: 'church' },
  { id: 'apollos', name: 'Apollos', lon: 27.325, lat: 37.5119, city: 'Ephesos', letters: '1 Corinthians', role: 'inner' },
  { id: 'prisca', name: 'Prisca', lon: 26.675, lat: 38.4881, city: 'Ephesos', letters: 'Romans', role: 'outer', capital: 'both' },
  { id: 'aquila', name: 'Aquila', lon: 27.325, lat: 38.4881, city: 'Ephesos', letters: 'Romans', role: 'outer', capital: 'both' },
  { id: 'epaenetus', name: 'Epaenetus', lon: 26.35, lat: 38.0, city: 'Ephesos', letters: 'Romans', role: 'outer' },
  { id: 'andronicus', name: 'Andronicus', lon: 27.65, lat: 38.0, city: 'Ephesos', letters: 'Romans', role: 'outer', capital: 'church' },
  { id: 'junia', name: 'Junia', lon: 27.0, lat: 37.0238, city: 'Ephesos', letters: 'Romans', role: 'outer', capital: 'church' },
  { id: 'onesimus', name: 'Onesimus', lon: 27.0, lat: 38.9762, city: 'Ephesos', letters: 'Philemon', role: 'outer' },
  { id: 'epaphras', name: 'Epaphras', lon: 26.025, lat: 37.5119, city: 'Ephesos', letters: 'Philemon', role: 'outer' },
  { id: 'mark', name: 'Mark', lon: 27.975, lat: 37.5119, city: 'Ephesos', letters: 'Philemon', role: 'outer' },
  { id: 'aristarchus', name: 'Aristarchus', lon: 26.025, lat: 38.4881, city: 'Ephesos', letters: 'Philemon', role: 'outer' },
  { id: 'demas', name: 'Demas', lon: 27.975, lat: 38.4881, city: 'Ephesos', letters: 'Philemon', role: 'outer' },
  { id: 'luke', name: 'Luke', lon: 26.35, lat: 37.0238, city: 'Ephesos', letters: 'Philemon', role: 'outer' },

  // ── Macedonia ───────────────────────────────
  { id: 'titus', name: 'Titus', lon: 21.5, lat: 41.0, city: 'Macedonia', letters: '2 Corinthians, Galatians', role: 'companion', capital: 'church' },

  // ── Philippi ───────────────────────────────
  { id: 'epaphroditus', name: 'Epaphroditus', lon: 24.28, lat: 41.01, city: 'Philippi', letters: 'Philippians', role: 'outer' },
  { id: 'euodia', name: 'Euodia', lon: 24.055, lat: 40.6721, city: 'Philippi', letters: 'Philippians', role: 'outer', capital: 'church' },
  { id: 'syntyche', name: 'Syntyche', lon: 24.505, lat: 40.6721, city: 'Philippi', letters: 'Philippians', role: 'outer', capital: 'church' },
  { id: 'clement', name: 'Clement', lon: 24.055, lat: 41.3479, city: 'Philippi', letters: 'Philippians', role: 'outer', capital: 'church' },

  // ── Corinth ───────────────────────────────
  { id: 'silvanus', name: 'Silvanus', lon: 22.6, lat: 37.95, city: 'Corinthus', letters: '1 Thessalonians', role: 'companion', capital: 'church' },
  { id: 'crispus', name: 'Crispus', lon: 22.31, lat: 37.5145, city: 'Corinthus', letters: '1 Corinthians', role: 'outer', capital: 'church' },
  { id: 'gaius_cor', name: 'Gaius', lon: 22.89, lat: 37.5145, city: 'Corinthus', letters: '1 Corinthians', role: 'outer' },
  { id: 'stephanas', name: 'Stephanas', lon: 22.31, lat: 38.3855, city: 'Corinthus', letters: '1 Corinthians', role: 'outer', capital: 'church' },
  { id: 'fortunatus', name: 'Fortunatus', lon: 22.89, lat: 38.3855, city: 'Corinthus', letters: '1 Corinthians', role: 'outer', capital: 'church' },
  { id: 'achaicus', name: 'Achaicus', lon: 22.02, lat: 37.95, city: 'Corinthus', letters: '1 Corinthians', role: 'outer', capital: 'church' },
  { id: 'chloe', name: 'Chloe', lon: 23.18, lat: 37.95, city: 'Corinthus', letters: '1 Corinthians', role: 'outer' },
  { id: 'erastus', name: 'Erastus', lon: 22.6, lat: 37.0789, city: 'Corinthus', letters: 'Romans', role: 'outer', capital: 'economic' },
  { id: 'mary', name: 'Mary', lon: 22.6, lat: 38.8211, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'ampliatus', name: 'Ampliatus', lon: 21.73, lat: 37.5145, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'urbanus', name: 'Urbanus', lon: 23.47, lat: 37.5145, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'stachys', name: 'Stachys', lon: 21.73, lat: 38.3855, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'apelles', name: 'Apelles', lon: 23.47, lat: 38.3855, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'herodion', name: 'Herodion', lon: 22.02, lat: 37.0789, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'tryphena', name: 'Tryphena', lon: 23.18, lat: 37.0789, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'tryphosa', name: 'Tryphosa', lon: 22.02, lat: 38.8211, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'persis', name: 'Persis', lon: 23.18, lat: 38.8211, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'rufus', name: 'Rufus', lon: 21.44, lat: 37.95, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'rufus_mother', name: 'Mother of Rufus', lon: 23.76, lat: 37.95, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'asyncritus', name: 'Asyncritus', lon: 22.31, lat: 36.6434, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'phlegon', name: 'Phlegon', lon: 22.89, lat: 36.6434, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'hermes', name: 'Hermes', lon: 22.31, lat: 39.2566, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'patrobas', name: 'Patrobas', lon: 22.89, lat: 39.2566, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'philologus', name: 'Philologus', lon: 21.44, lat: 37.0789, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'julia', name: 'Julia', lon: 23.76, lat: 37.0789, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'nereus', name: 'Nereus', lon: 21.44, lat: 38.8211, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'nereus_sister', name: 'Sister of Nereus', lon: 23.76, lat: 38.8211, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'olympas', name: 'Olympas', lon: 21.15, lat: 37.5145, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'gaius_rom', name: 'Gaius (Roman)', lon: 24.05, lat: 37.5145, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'quartus', name: 'Quartus', lon: 21.15, lat: 38.3855, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'tertius', name: 'Tertius', lon: 24.05, lat: 38.3855, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'lucius', name: 'Lucius', lon: 21.73, lat: 36.6434, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'jason', name: 'Jason', lon: 23.47, lat: 36.6434, city: 'Corinthus', letters: 'Romans', role: 'outer' },
  { id: 'sosipater', name: 'Sosipater', lon: 21.73, lat: 39.2566, city: 'Corinthus', letters: 'Romans', role: 'outer' },

  // ── Cenchreae ───────────────────────────────
  { id: 'phoebe', name: 'Phoebe', lon: 22.99, lat: 37.89, city: 'Cenchreae', letters: 'Romans', role: 'outer', capital: 'church' },

  // ── Lycus Valley ───────────────────────────────
  { id: 'philemon', name: 'Philemon', lon: 28.72, lat: 37.83, city: 'Lycus Valley', letters: 'Philemon', role: 'outer', capital: 'both' },
  { id: 'apphia', name: 'Apphia', lon: 28.495, lat: 37.4921, city: 'Lycus Valley', letters: 'Philemon', role: 'outer' },
  { id: 'archippus', name: 'Archippus', lon: 28.945, lat: 37.4921, city: 'Lycus Valley', letters: 'Philemon', role: 'outer' },

];



// ── EDGE DATA ─────────────────────────────────────────────────────────────────
// type: 'companion' | 'inner' | 'severed' | 'direct' | 'indirect'

const PN_EDGES = [

  // ── Paul to Core Companions ───────────────────────────────────────────────
  { s: 'paul', t: 'timothy',   type: 'companion', label: 'co-author, closest partner'   },
  { s: 'paul', t: 'titus',     type: 'companion', label: 'trusted delegate'              },
  { s: 'paul', t: 'silvanus',  type: 'companion', label: 'co-author, fellow missionary'  },
  { s: 'paul', t: 'sosthenes', type: 'companion', label: 'co-author of 1 Corinthians'    },

  // ── Paul to Inner Circle (Apostles) ───────────────────────────────────────
  { s: 'paul', t: 'apollos',   type: 'inner',   label: 'colleague, apostolic peer'    },
  { s: 'paul', t: 'cephas',    type: 'severed', label: 'met Jerusalem & Antioch; tie severed (Gal 2)' },
  { s: 'paul', t: 'james',     type: 'severed', label: 'met Jerusalem; tie severed (Gal 2)'           },
  { s: 'paul', t: 'john',      type: 'severed', label: 'pillar of Jerusalem; tie severed'             },
  { s: 'paul', t: 'barnabas',  type: 'severed', label: 'travel partner; severed (Antioch incident)'   },

  // ── Jerusalem apostle secondary connections ───────────────────────────────
  { s: 'cephas',  t: 'james',    type: 'direct', label: 'Jerusalem pillars, Gal 2:9'      },
  { s: 'cephas',  t: 'john',     type: 'direct', label: 'Jerusalem pillars, Gal 2:9'      },
  { s: 'james',   t: 'john',     type: 'direct', label: 'Jerusalem pillars, Gal 2:9'      },
  { s: 'cephas',  t: 'barnabas', type: 'direct', label: 'Antioch incident, Gal 2:13'      },
  { s: 'cephas',  t: 'apollos',  type: 'direct', label: 'both had Corinthian factions, 1 Cor 1:12' },

  // ── Companion secondary connections ───────────────────────────────────────
  { s: 'timothy',   t: 'silvanus',  type: 'direct', label: 'traveled together, 1 Thess 1:1' },
  { s: 'timothy',   t: 'titus',     type: 'direct', label: "both Paul's delegates"           },
  { s: 'timothy',   t: 'sosthenes', type: 'direct', label: 'both in Ephesus'                 },
  { s: 'silvanus',  t: 'sosthenes', type: 'direct', label: "both Paul's co-workers"          },
  { s: 'apollos',   t: 'sosthenes', type: 'direct', label: 'both in Ephesus, 1 Cor'          },
  { s: 'titus',     t: 'barnabas',  type: 'direct', label: 'Jerusalem visit, Gal 2:1'        },

  // ── Ephesus — Prisca & Aquila household ───────────────────────────────────
  { s: 'prisca',   t: 'aquila',    type: 'direct', label: 'married co-workers'              },
  { s: 'prisca',   t: 'epaenetus', type: 'direct', label: 'church in Asia, 1 Cor 16:19'     },
  { s: 'aquila',   t: 'epaenetus', type: 'direct', label: 'church in Asia, 1 Cor 16:19'     },
  { s: 'prisca',   t: 'andronicus',type: 'direct', label: 'both in Ephesus'                 },
  { s: 'prisca',   t: 'junia',     type: 'direct', label: 'both in Ephesus'                 },
  { s: 'aquila',   t: 'andronicus',type: 'direct', label: 'both in Ephesus'                 },
  { s: 'aquila',   t: 'junia',     type: 'direct', label: 'both in Ephesus'                 },
  { s: 'andronicus',t: 'junia',    type: 'direct', label: 'imprisoned together, Rom 16:7'   },

  // ── Prisca/Aquila → Corinth (INDIRECT — one of the 3 indirect links in Fig 2) ──
  { s: 'prisca', t: 'crispus',   type: 'indirect', label: 'Asia church → Corinth church'  },
  { s: 'prisca', t: 'stephanas', type: 'indirect', label: 'Asia church → Corinth church'  },
  { s: 'aquila', t: 'crispus',   type: 'indirect', label: 'Asia church → Corinth church'  },
  { s: 'aquila', t: 'stephanas', type: 'indirect', label: 'Asia church → Corinth church'  },

  // ── Ephesus — Philemon's co-workers (all imprisoned with Paul) ────────────
  { s: 'onesimus',    t: 'epaphras',    type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'onesimus',    t: 'mark',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'onesimus',    t: 'aristarchus', type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'onesimus',    t: 'demas',       type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'onesimus',    t: 'luke',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'epaphras',    t: 'mark',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'epaphras',    t: 'aristarchus', type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'epaphras',    t: 'demas',       type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'epaphras',    t: 'luke',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'mark',        t: 'aristarchus', type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'mark',        t: 'demas',       type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'mark',        t: 'luke',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'aristarchus', t: 'demas',       type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'aristarchus', t: 'luke',        type: 'direct', label: 'both with Paul in Ephesus prison' },
  { s: 'demas',       t: 'luke',        type: 'direct', label: 'both with Paul in Ephesus prison' },

  // ── Ephesus co-workers → Lycus Valley (mutual familiarity, Phm v. 23-24) ──
  { s: 'epaphras',    t: 'philemon',  type: 'direct', label: 'greet Philemon, Phm v. 23'   },
  { s: 'epaphras',    t: 'apphia',    type: 'direct', label: 'greet Apphia, Phm v. 23'     },
  { s: 'epaphras',    t: 'archippus', type: 'direct', label: 'greet Archippus, Phm v. 23'  },
  { s: 'mark',        t: 'philemon',  type: 'direct', label: 'greet Philemon, Phm v. 24'   },
  { s: 'mark',        t: 'apphia',    type: 'direct', label: 'Phm v. 24'                   },
  { s: 'mark',        t: 'archippus', type: 'direct', label: 'Phm v. 24'                   },
  { s: 'aristarchus', t: 'philemon',  type: 'direct', label: 'greet Philemon, Phm v. 24'   },
  { s: 'demas',       t: 'philemon',  type: 'direct', label: 'greet Philemon, Phm v. 24'   },
  { s: 'luke',        t: 'philemon',  type: 'direct', label: 'greet Philemon, Phm v. 24'   },

  // ── Lycus Valley household ────────────────────────────────────────────────
  { s: 'philemon', t: 'onesimus',  type: 'direct',   label: 'enslaved person, Phm v. 16'  },
  { s: 'philemon', t: 'apphia',    type: 'direct',   label: 'household, Phm v. 2'         },
  { s: 'philemon', t: 'archippus', type: 'direct',   label: 'fellow soldier, Phm v. 2'    },
  { s: 'apphia',   t: 'archippus', type: 'direct',   label: 'household'                   },

  // ── Timothy → Lycus Valley (INDIRECT — one of the 3 indirect links in Fig 2)
  { s: 'timothy', t: 'philemon',  type: 'indirect', label: 'co-sender of Philemon (letter)' },
  { s: 'timothy', t: 'apphia',    type: 'indirect', label: 'co-sender of Philemon (letter)' },
  { s: 'timothy', t: 'archippus', type: 'indirect', label: 'co-sender of Philemon (letter)' },

  // ── Philippi group ────────────────────────────────────────────────────────
  { s: 'epaphroditus', t: 'euodia',   type: 'direct', label: 'Philippi church, Phil 4:2-3' },
  { s: 'epaphroditus', t: 'syntyche', type: 'direct', label: 'Philippi church, Phil 4:2-3' },
  { s: 'epaphroditus', t: 'clement',  type: 'direct', label: 'Philippi church, Phil 4:2-3' },
  { s: 'euodia',       t: 'syntyche', type: 'direct', label: 'quarrel, Phil 4:2'           },
  { s: 'euodia',       t: 'clement',  type: 'direct', label: 'Philippi church, Phil 4:3'   },
  { s: 'syntyche',     t: 'clement',  type: 'direct', label: 'Philippi church, Phil 4:3'   },

  // Timothy → Philippians (direct — co-sender, physically traveled there)
  { s: 'timothy', t: 'epaphroditus', type: 'direct', label: 'co-sender Phil; both messengers' },
  { s: 'timothy', t: 'euodia',       type: 'direct', label: 'co-sender of Philippians'        },
  { s: 'timothy', t: 'syntyche',     type: 'direct', label: 'co-sender of Philippians'        },
  { s: 'timothy', t: 'clement',      type: 'direct', label: 'co-sender of Philippians'        },

  // ── Corinth group ─────────────────────────────────────────────────────────
  { s: 'crispus',   t: 'gaius_cor',  type: 'direct', label: 'Corinth church, 1 Cor 1:14'  },
  { s: 'crispus',   t: 'stephanas',  type: 'direct', label: 'Corinth church'               },
  { s: 'gaius_cor', t: 'stephanas',  type: 'direct', label: 'Corinth church'               },
  { s: 'gaius_cor', t: 'erastus',    type: 'direct', label: 'Corinth church'               },
  { s: 'stephanas', t: 'fortunatus', type: 'direct', label: 'household, 1 Cor 16:17'       },
  { s: 'stephanas', t: 'achaicus',   type: 'direct', label: 'household, 1 Cor 16:17'       },
  { s: 'fortunatus',t: 'achaicus',   type: 'direct', label: 'household, 1 Cor 16:17'       },
  { s: 'chloe',     t: 'crispus',    type: 'direct', label: 'Corinth church, 1 Cor 1:11'   },
  { s: 'chloe',     t: 'gaius_cor',  type: 'direct', label: 'Corinth church, 1 Cor 1:11'   },
  { s: 'chloe',     t: 'stephanas',  type: 'direct', label: 'Corinth church, 1 Cor 1:11'   },

  // Chloe's people traveled to Paul in Ephesus
  { s: 'chloe', t: 'apollos',   type: 'direct', label: "Chloe's people reached Ephesus, 1 Cor 1:11" },
  { s: 'chloe', t: 'sosthenes', type: 'direct', label: "Chloe's people reached Ephesus"             },

  // Companions who spread the gospel in Corinth
  { s: 'silvanus', t: 'crispus',   type: 'direct', label: 'spread gospel in Corinth, 2 Cor 1:19' },
  { s: 'silvanus', t: 'stephanas', type: 'direct', label: 'spread gospel in Corinth'              },
  { s: 'silvanus', t: 'gaius_cor', type: 'direct', label: 'spread gospel in Corinth'              },

  // Titus → Corinth (sent from Macedonia, 2 Cor 8:16)
  { s: 'titus', t: 'stephanas',  type: 'direct', label: "Titus's mission to Corinth, 2 Cor 8:16" },
  { s: 'titus', t: 'fortunatus', type: 'direct', label: "Titus's mission to Corinth"             },
  { s: 'titus', t: 'achaicus',   type: 'direct', label: "Titus's mission to Corinth"             },
  { s: 'titus', t: 'silvanus',   type: 'direct', label: "Titus and Silvanus in Corinth"          },

  // Phoebe → Corinth/Achaia area
  { s: 'phoebe', t: 'silvanus',  type: 'direct', label: 'deacon of Cenchreae, near Corinth'  },
  { s: 'phoebe', t: 'crispus',   type: 'direct', label: 'deacon of Cenchreae'                },
  { s: 'phoebe', t: 'gaius_cor', type: 'direct', label: 'deacon of Cenchreae'                },
  { s: 'phoebe', t: 'erastus',   type: 'direct', label: 'deacon of Cenchreae, near Corinth'  },
  { s: 'phoebe', t: 'tryphena',  type: 'direct', label: 'Cenchreae ↔ Achaia'                 },
  { s: 'phoebe', t: 'mary',      type: 'direct', label: 'Cenchreae ↔ Achaia'                 },

  // ── Achaia group — key named connections ─────────────────────────────────
  { s: 'tryphena',  t: 'tryphosa', type: 'direct', label: 'sisters, Rom 16:12'      },
  { s: 'rufus',     t: 'rufus_mother', type: 'direct', label: 'son and mother, Rom 16:13' },
  { s: 'nereus',    t: 'nereus_sister', type: 'direct', label: 'siblings, Rom 16:15' },
  { s: 'lucius',    t: 'jason',     type: 'direct', label: 'kinspeople, Rom 16:21'  },
  { s: 'lucius',    t: 'sosipater', type: 'direct', label: 'kinspeople, Rom 16:21'  },
  { s: 'jason',     t: 'sosipater', type: 'direct', label: 'kinspeople, Rom 16:21'  },
  { s: 'erastus',   t: 'quartus',   type: 'direct', label: 'both greet from Corinth, Rom 16:23-24' },
  { s: 'tertius',   t: 'gaius_rom', type: 'direct', label: "both in Paul's circle, Rom 16" },
  { s: 'tertius',   t: 'erastus',   type: 'direct', label: "both in Paul's circle, Rom 16" },
];

// ── CITY CENTRES ──────────────────────────────────────────────────────────────
// One marker per location; people fan out around it in the honeycomb.
const PN_CITIES = [
  { name: 'Hierosolyma',  lon: 35.216, lat: 31.783 },
  { name: 'Antiocheia',   lon: 36.16,  lat: 36.20  },
  { name: 'Ephesos',      lon: 27.342, lat: 37.944 },
  { name: 'Macedonia',    lon: 21.50,  lat: 41.00  },
  { name: 'Philippi',     lon: 24.289, lat: 41.014 },
  { name: 'Corinthus',    lon: 22.93,  lat: 37.936 },
  { name: 'Cenchreae',    lon: 22.99,  lat: 37.89  },
  { name: 'Lycus Valley', lon: 29.11,  lat: 37.84  },
];

// city name → [node, ...]
const _cityPeopleMap = {};
PN_NODES.forEach(n => {
  if (!_cityPeopleMap[n.city]) _cityPeopleMap[n.city] = [];
  _cityPeopleMap[n.city].push(n);
});

// ═══════════════════════════════════════════════════════════════════════════
//  RENDERING — one blue "orb" per city, styled like the manuscript orbs.
//  People fan-out / connecting lines are intentionally omitted for now;
//  a click-popup listing each city's people will be added next.
// ═══════════════════════════════════════════════════════════════════════════

// city name → [node, ...]   (rebuilt here so this block is self-contained)
const _pnCityPeople = {};
PN_NODES.forEach(n => {
    (_pnCityPeople[n.city] = _pnCityPeople[n.city] || []).push(n);
});

// ── STATE ─────────────────────────────────────────────────────────────────────
// ── PER-PERSON DETAIL (extracted from Gill, "The Complete Social Network of
//    Paul").  role = church office / how they are described (null if none);
//    refs = where they are named in the corpus (Book chapter:verse).
//    Capital comes from each node's `capital` field. ─────────────────────────
const PN_DETAILS = {
  paul:         { role: "Apostle to the gentiles; author of the corpus", refs: "Sender of all seven undisputed letters" },

  timothy:      { role: "Co-worker; co-sender of 2 Cor, Phil, 1 Thess & Philemon", refs: "Rom 16:21; 1 Cor 4:17; 16:10; 2 Cor 1:1, 19; Phil 1:1; 2:19; 1 Thess 1:1; 3:2, 6; Phlm 1" },
  titus:        { role: "Co-worker & delegate; organised the Jerusalem collection", refs: "2 Cor 2:13; 7:6, 13-14; 8:6, 16, 23; 12:18; Gal 2:1, 3" },
  silvanus:     { role: "Co-sender of 1 Thessalonians; fellow preacher in Corinth", refs: "2 Cor 1:19; 1 Thess 1:1" },
  sosthenes:    { role: "Co-sender of 1 Corinthians", refs: "1 Cor 1:1" },

  apollos:      { role: "Apostolic teacher & preacher", refs: "1 Cor 1:12; 3:4-6, 22; 4:6; 16:12" },
  cephas:       { role: "Apostle; Jerusalem 'pillar'", refs: "1 Cor 1:12; 3:22; 9:5; 15:5; Gal 1:18; 2:9, 11-14" },
  james:        { role: "Apostle; Jerusalem 'pillar'; the Lord's brother", refs: "1 Cor 15:7; Gal 1:19; 2:9, 12" },
  john:         { role: "Apostle; Jerusalem 'pillar'", refs: "Gal 2:9" },
  barnabas:     { role: "Apostle; missionary companion", refs: "1 Cor 9:6; Gal 2:1, 9, 13" },

  prisca:       { role: "Co-worker; host & leader of a house church", refs: "Rom 16:3-5; 1 Cor 16:19" },
  aquila:       { role: "Co-worker; host & leader of a house church", refs: "Rom 16:3-5; 1 Cor 16:19" },
  epaenetus:    { role: "'First convert of Asia'", refs: "Rom 16:5" },
  andronicus:   { role: "'Prominent among the apostles'; fellow prisoner", refs: "Rom 16:7" },
  junia:        { role: "'Prominent among the apostles'; fellow prisoner", refs: "Rom 16:7" },
  onesimus:     { role: "Enslaved man of Philemon; courier of the letter", refs: "Phlm 10 (Col 4:9)" },
  epaphras:     { role: "Fellow prisoner; founder of the Colossian church", refs: "Phlm 23 (Col 1:7; 4:12)" },
  mark:         { role: "Co-worker", refs: "Phlm 24 (Col 4:10)" },
  aristarchus:  { role: "Co-worker; fellow prisoner", refs: "Phlm 24 (Col 4:10)" },
  demas:        { role: "Co-worker", refs: "Phlm 24 (Col 4:14)" },
  luke:         { role: "Co-worker ('the beloved physician')", refs: "Phlm 24 (Col 4:14)" },

  epaphroditus: { role: "Messenger of Philippi; 'fellow soldier'", refs: "Phil 2:25; 4:18" },
  euodia:       { role: "Co-worker who 'struggled beside Paul in the gospel'", refs: "Phil 4:2" },
  syntyche:     { role: "Co-worker in the gospel", refs: "Phil 4:2" },
  clement:      { role: "Co-worker", refs: "Phil 4:3" },

  crispus:      { role: "Baptised by Paul", refs: "1 Cor 1:14" },
  gaius_cor:    { role: "Baptised by Paul", refs: "1 Cor 1:14" },
  stephanas:    { role: "'First fruits of Achaia'; household devoted to the saints; baptised by Paul", refs: "1 Cor 1:16; 16:15-18" },
  fortunatus:   { role: "Of Stephanas' household; 'refreshed Paul's spirit'", refs: "1 Cor 16:17" },
  achaicus:     { role: "Of Stephanas' household; 'refreshed Paul's spirit'", refs: "1 Cor 16:17" },
  chloe:        { role: "Her people reported the Corinthian divisions to Paul", refs: "1 Cor 1:11" },
  erastus:      { role: "City treasurer / market manager (oikonomos)", refs: "Rom 16:23" },

  phoebe:       { role: "Deacon of the church at Cenchreae; benefactor; courier of Romans", refs: "Rom 16:1-2" },

  mary:         { role: "'Worked very hard among you'", refs: "Rom 16:6" },
  ampliatus:    { role: "'My beloved in the Lord'", refs: "Rom 16:8" },
  urbanus:      { role: "'Our co-worker in Christ'", refs: "Rom 16:9" },
  stachys:      { role: "'My beloved'", refs: "Rom 16:9" },
  apelles:      { role: "'Approved in Christ'", refs: "Rom 16:10" },
  herodion:     { role: "Paul's kinsman", refs: "Rom 16:11" },
  tryphena:     { role: "'Worker in the Lord'", refs: "Rom 16:12" },
  tryphosa:     { role: "'Worker in the Lord'", refs: "Rom 16:12" },
  persis:       { role: "'Worked hard in the Lord'", refs: "Rom 16:12" },
  rufus:        { role: "'Chosen in the Lord'", refs: "Rom 16:13" },
  rufus_mother: { role: "'A mother to me also' (Paul)", refs: "Rom 16:13" },
  asyncritus:   { role: "Member of the church in Corinth", refs: "Rom 16:14" },
  phlegon:      { role: "Member of the church in Corinth", refs: "Rom 16:14" },
  hermes:       { role: "Member of the church in Corinth", refs: "Rom 16:14" },
  patrobas:     { role: "Member of the church in Corinth", refs: "Rom 16:14" },
  philologus:   { role: "Member of the church in Corinth", refs: "Rom 16:15" },
  julia:        { role: "Member of the church in Corinth", refs: "Rom 16:15" },
  nereus:       { role: "Member of the church in Corinth", refs: "Rom 16:15" },
  nereus_sister:{ role: "Member of the church in Corinth", refs: "Rom 16:15" },
  olympas:      { role: "Member of the church in Corinth", refs: "Rom 16:15" },
  gaius_rom:    { role: "Host (or guest) of Paul and the whole church", refs: "Rom 16:23" },
  quartus:      { role: "'The brother'", refs: "Rom 16:23" },
  tertius:      { role: "Scribe (amanuensis) who wrote down Romans", refs: "Rom 16:22" },
  lucius:       { role: "Paul's kinsman", refs: "Rom 16:21" },
  jason:        { role: "Paul's kinsman", refs: "Rom 16:21" },
  sosipater:    { role: "Paul's kinsman", refs: "Rom 16:21" },

  philemon:     { role: "Host & leader of a house church; Paul's 'fellow worker'", refs: "Phlm 1" },
  apphia:       { role: "'Our sister'; Philemon's household", refs: "Phlm 2" },
  archippus:    { role: "'Our fellow soldier'", refs: "Phlm 2 (Col 4:17)" },
};

function _pnCapitalLabel(cap) {
    return cap === 'both'     ? 'Ecclesial, Economic'
         : cap === 'church'   ? 'Ecclesial'
         : cap === 'economic' ? 'Economic'
         : null;
}

// Surface important people first: apostles, companions, inner circle, then
// anyone with social/economic capital, then the rest — alphabetical within rank.
function _pnRank(n) {
    if (n.role === 'apostle')   return 0;
    if (n.role === 'companion') return 1;
    if (n.role === 'inner')     return 2;
    if (n.capital)              return 3;
    return 4;
}

// ── LOOKUPS & CONNECTION HELPERS ─────────────────────────────────────────────
const _pnNodeById = {};
PN_NODES.forEach(n => { _pnNodeById[n.id] = n; });
const _pnCityByName = {};
PN_CITIES.forEach(c => { _pnCityByName[c.name] = c; });

let _pnLineLayer = null;   // holds connection polylines + the floating name label

// All of a person's connections (node objects), excluding self and Paul
// (Paul is connected to everyone by proxy, so we never list or draw him in
//  other people's networks).
//
//  • Paul himself → the whole network (every other person).
//  • Everyone else → their explicit edges PLUS fellow members of their own
//    church. The paper treats e.g. all of Romans 16 as "sufficiently
//    interconnected" members of the Corinthian church, so co-membership is
//    itself a connection worth listing by name.
function _pnConnections(personId) {
    if (personId === 'paul') {
        return PN_NODES.filter(n => n.id !== 'paul');
    }
    const ids = new Set();
    PN_EDGES.forEach(e => {
        if (e.s === personId) ids.add(e.t);
        if (e.t === personId) ids.add(e.s);
    });
    const self = _pnNodeById[personId];
    if (self) {
        PN_NODES.forEach(n => { if (n.city === self.city) ids.add(n.id); });
    }
    ids.delete(personId);
    ids.delete('paul');
    return [...ids].map(id => _pnNodeById[id]).filter(Boolean);
}

// Quadratic-bezier curve (in CRS lat/lng space) between two points, so the
// connection stems arc gently instead of running dead straight.
function _pnCurve(a, b) {
    const ax = a.lng, ay = a.lat, bx = b.lng, by = b.lat;
    const mx = (ax + bx) / 2, my = (ay + by) / 2;
    const dx = bx - ax, dy = by - ay;
    const k  = 0.16;
    const cx = mx - dy * k, cy = my + dx * k;
    const pts = [];
    for (let t = 0; t <= 1.0001; t += 0.05) {
        const u = 1 - t;
        pts.push(L.latLng(
            u*u*ay + 2*u*t*cy + t*t*by,
            u*u*ax + 2*u*t*cx + t*t*bx
        ));
    }
    return pts;
}

// Draw the connection stems for one person: a green arc from their city to the
// city of every person they are connected with, plus their name above their city.
function showPersonNetwork(personId) {
    clearPersonNetwork();
    const person = _pnNodeById[personId];
    if (!person || !_pnLineLayer) return;

    const fromCity = _pnCityByName[person.city];
    if (!fromCity) return;
    const fromPt = geoToCRS(fromCity.lon, fromCity.lat);

    // Collapse connections down to the set of cities they sit in (one stem per
    // city — so "connected to the whole church here" is a single line to that node).
    const cities = new Set();
    _pnConnections(personId).forEach(c => {
        if (c.city && c.city !== person.city) cities.add(c.city);
    });

    cities.forEach(cityName => {
        const cc = _pnCityByName[cityName];
        if (!cc) return;
        L.polyline(_pnCurve(fromPt, geoToCRS(cc.lon, cc.lat)), {
            color: '#5ab87a', weight: 2.2, opacity: 0.9,
            pane: 'pnLinePane', interactive: false,
            lineCap: 'round', lineJoin: 'round',
        }).addTo(_pnLineLayer);
    });

    // Floating name label, centred just above the person's city node.
    L.marker(fromPt, {
        icon: L.divIcon({
            className: 'pn-net-label',
            html: `<div class="pn-net-label-inner">${person.name}</div>`,
            iconSize:   [180, 24],
            iconAnchor: [90, 46],
        }),
        interactive: false,
        keyboard: false,
    }).addTo(_pnLineLayer);

    _pnLineLayer.addTo(map);
}

function clearPersonNetwork() {
    if (_pnLineLayer) _pnLineLayer.clearLayers();
}

// ── CLICK POPUP — title + scrollable, expandable list of people ──────────────
function showPnPopup(city) {
    const people = (_pnCityPeople[city.name] || []).slice()
        .sort((a, b) => _pnRank(a) - _pnRank(b) || a.name.localeCompare(b.name));

    const rows = people.map(n => {
        const d   = PN_DETAILS[n.id] || {};
        const cap = _pnCapitalLabel(n.capital);
        let detail = '';
        if (d.role) detail += `<div class="pn-d-line"><span class="pn-d-label">Role</span><span class="pn-d-val">${d.role}</span></div>`;
        if (cap)    detail += `<div class="pn-d-line"><span class="pn-d-label">Capital</span><span class="pn-d-val">${cap}</span></div>`;
        if (d.refs) detail += `<div class="pn-d-line"><span class="pn-d-label">Mentioned</span><span class="pn-d-val">${d.refs}</span></div>`;

        // Connections (people), excluding Paul — he is connected to everyone by proxy.
        const conns = _pnConnections(n.id)
            .map(c => c.name)
            .sort((a, b) => a.localeCompare(b));
        if (conns.length) {
            detail += `<div class="pn-d-line"><span class="pn-d-label">Connections</span><span class="pn-d-val"><span class="pn-conn-count">(${conns.length})</span> ${conns.join(', ')}</span></div>`;
        }
        if (!detail) detail = `<div class="pn-d-line pn-d-empty">No further detail recorded.</div>`;

        return `<div class="pn-person" data-id="${n.id}">` +
                   `<div class="pn-person-head">` +
                       `<button class="pn-person-name"><span class="pn-person-chev">&#9656;</span>${n.name}</button>` +
                       `<button class="pn-see-network" data-id="${n.id}">See Network</button>` +
                   `</div>` +
                   `<div class="pn-person-detail">${detail}</div>` +
               `</div>`;
    }).join('');

    const count = people.length;
    const html =
        `<div class="pn-popup">` +
            `<div class="pn-popup-title">${city.name}</div>` +
            `<div class="pn-popup-count">${count} node${count === 1 ? '' : 's'}</div>` +
            `<div class="pn-popup-list">${rows}</div>` +
        `</div>`;

    const popup = L.popup({ className: 'pn-popup-wrap', maxWidth: 400, minWidth: 340, autoPan: true })
        .setLatLng(geoToCRS(city.lon, city.lat))
        .setContent(html)
        .openOn(map);

    const el = popup.getElement();
    if (el) {
        // Clicking a name toggles its detail dropdown.
        el.querySelectorAll('.pn-person-name').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.pn-person').classList.toggle('open');
            });
        });
        // "See Network" → close the popup, draw this person's connection stems,
        // and float their name above their city.
        el.querySelectorAll('.pn-see-network').forEach(btn => {
            btn.addEventListener('click', (ev) => {
                ev.stopPropagation();
                const id = btn.dataset.id;
                map.closePopup();
                showPersonNetwork(id);
            });
        });
    }
}

let _pnActive    = false;   // is the Pauline layer currently shown?
let _pnOrbLayer  = null;    // L.layerGroup holding the city orbs
let _pnBuilt     = false;   // have the orb markers been created yet?

// ── BLUE ORB GRADIENT ───────────────────────────────────────────────────────
// Mirrors orbGradient() in script.js (the red manuscript orbs) but in blue.
function pnOrbGradient(intensity) {
    const a = (base) => +Math.min(1, intensity * base).toFixed(2);
    return `radial-gradient(circle at center,` +
        `rgba(60,150,240,${a(1.00)}) 0%,` +
        `rgba(30,110,220,${a(0.90)}) 20%,` +
        `rgba(20,90,205,${a(0.50)}) 58%,` +
        `rgba(20,90,205,0) 100%)`;
}

// ── BUILD ONE CITY ORB ──────────────────────────────────────────────────────
function _pnBuildOrb(city) {
    const people = _pnCityPeople[city.name] || [];
    const count  = people.length;

    // Radius grows with sqrt(count) — same shape as the manuscript orbs but
    // a touch smaller so a 34-person city doesn't dominate the map.
    const size      = Math.round(14 + 4.5 * Math.sqrt(count));   // px radius
    const intensity = 0.60 + 0.35 * Math.min(1, count / 20);     // 0.60 → 0.95
    const grad      = pnOrbGradient(intensity);
    const label     = `${count} node${count === 1 ? '' : 's'}`;

    const marker = L.marker(geoToCRS(city.lon, city.lat), {
        icon: L.divIcon({
            className:  'pn-orb-icon',
            iconSize:   [size * 2, size * 2],
            iconAnchor: [size, size],
            html: `<div class="pn-orb-circle" style="width:${size*2}px;height:${size*2}px;background:${grad}">` +
                  `<div class="pn-orb-label">` +
                      `<div class="pn-orb-title">${city.name}</div>` +
                      `<div class="pn-orb-count">${label}</div>` +
                  `</div></div>`,
        }),
        pane:        'orbPane',
        interactive: true,
    });

    // Click → open the city's people popup. Stop propagation so the map
    // doesn't swallow / deselect anything underneath.
    marker.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        showPnPopup(city);
    });

    return marker;
}

// ── TOGGLE ────────────────────────────────────────────────────────────────────
function pnSetActive(on) {
    if (!_pnOrbLayer) return;   // init not finished yet
    _pnActive = on;

    if (on) {
        if (!_pnBuilt) {
            PN_CITIES.forEach(c => _pnOrbLayer.addLayer(_pnBuildOrb(c)));
            _pnBuilt = true;
        }
        _pnOrbLayer.addTo(map);
    } else {
        clearPersonNetwork();
        if (_pnLineLayer) map.removeLayer(_pnLineLayer);
        map.removeLayer(_pnOrbLayer);
    }

    const btn = document.getElementById('sn-pauline-btn');
    if (btn) btn.classList.toggle('active', on);
}

// ── INIT ──────────────────────────────────────────────────────────────────────
function pnInit() {
    // Layer group lives in the same orbPane the manuscript orbs use.
    _pnOrbLayer = L.layerGroup();

    // Connection stems render in their own pane just below the orbs (z 340),
    // so the orbs stay on top and remain clickable.
    if (!map.getPane('pnLinePane')) {
        map.createPane('pnLinePane');
        map.getPane('pnLinePane').style.zIndex = '340';
    }
    _pnLineLayer = L.layerGroup();

    // Sidebar wiring — collapsible section header + the network toggle row.
    const sectionToggle = document.getElementById('sn-section-toggle');
    if (sectionToggle) {
        sectionToggle.addEventListener('click', () => {
            document.getElementById('social-networks-section').classList.toggle('open');
        });
    }
    const paulineBtn = document.getElementById('sn-pauline-btn');
    if (paulineBtn) {
        paulineBtn.addEventListener('click', () => pnSetActive(!_pnActive));
    }
}

// ── BOOTSTRAP ─────────────────────────────────────────────────────────────────
setTimeout(pnInit, 80);
