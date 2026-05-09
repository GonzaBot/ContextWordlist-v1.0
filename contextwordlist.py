#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextWordlist v1.1 - Professional Contextual Wordlist Generator for Pentesting
Enhanced version with advanced mutation strategies, Hashcat integration, and logging.
"""

import sys
import json
import argparse
import datetime
import re
import unicodedata
import itertools
import csv
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Set, List, Dict
from collections import defaultdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.columns import Columns
    from rich import print as rprint
except ImportError:
    print("ERROR: The 'rich' library is not installed.")
    print("Please run setup.sh (Linux) or setup.bat (Windows).")
    print("Or install it manually: pip install rich")
    sys.exit(1)

# ==========================================
# LOGGING SETUP
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('contextwordlist.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# CONSTANTS & MAPPINGS
# ==========================================
LEET_MAP = {
    'a': ['4', '@', '/-\\'], 
    'e': ['3'], 
    'i': ['1', '!', '|'], 
    'o': ['0'],
    's': ['5', '$'], 
    't': ['7', '+'], 
    'l': ['1', '|'], 
    'g': ['9', '6'], 
    'b': ['8', '|3'],
    'z': ['2'],
    'd': ['|)'],
    'x': ['><']
}

# More advanced mutations for business contexts
SPECIAL_SUFFIXES = [
    "!", "@", "#", ".", "*", "1", "12", "123", "1234", "12345",
    "01", "007", "000", "#1", "@1", "_1", "!1", "!123", "@123", "#123",
    "2024", "2025", "2026", "2024!", "2025!", "2024@",
    "!!", "!!!", "??", "...", "#1!", "!@#"
]

SPECIAL_PREFIXES = ["1", "12", "123", "1234", "01", "007", "@", "!", "#", "0"]

SEASONS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", 
              "septiembre", "octubre", "noviembre", "diciembre", "verano", "invierno", "otono", "primavera"]
SEASONS_EN = ["january", "february", "march", "april", "may", "june", "july", "august", 
              "september", "october", "november", "december", "summer", "winter", "autumn", "spring"]
SEASONS_SHORT = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

SEPARATORS = ["", "_", ".", "-", "@", "#", "!"]

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ==========================================
# DATA MODELS
# ==========================================
@dataclass
class Profile:
    first_name:    Optional[str] = None
    last_name:     Optional[str] = None
    nickname:      Optional[str] = None
    birth_year:    Optional[int] = None
    birth_day:     Optional[str] = None
    birth_month:   Optional[str] = None
    partner_name:  Optional[str] = None
    pet_name:      Optional[str] = None
    child_name:    Optional[str] = None
    city:          Optional[str] = None
    country:       Optional[str] = None
    hobby:         Optional[str] = None
    
    company:       Optional[str] = None
    company_short: Optional[str] = None
    domain:        Optional[str] = None
    industry:      Optional[str] = None
    founded_year:  Optional[int] = None
    product:       Optional[str] = None
    
    extra_words:   list = field(default_factory=list)
    min_length:    int = 6
    max_length:    int = 20
    current_year:  int = 2026
    leet_enabled:  bool = True
    leet_advanced: bool = True  # Multiple substitutions
    seasons_enabled: bool = True
    combinations_enabled: bool = True
    max_words:     int = 50000  # Higher configurable limit
    dedup_strategy: str = "aggressive"  # aggressive, balanced, loose

@dataclass
class WordlistResult:
    profile:      Profile
    base_words:   list
    final_words:  list
    total_count:  int
    categories:   dict
    timestamp:    str
    label:        str
    statistics:   dict = field(default_factory=dict)
    mutations_applied: dict = field(default_factory=dict)

# ==========================================
# ENGINE: ADVANCED EXTRACTION AND MUTATION
# ==========================================
class WordlistEngine:
    def __init__(self, profile: Profile):
        self.profile = profile
        self.categories_stats = {}
        self._word_cache = {}
        logger.info(f"Engine initialized with profile: {profile.company or profile.first_name}")

    def _normalize(self, text: str) -> str:
        """Normalize text by removing accents and special characters."""
        if not text: 
            return ""
        text = str(text).strip()
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')
        return text.lower()

    def _validate_input(self, value, field_type=str):
        """Validate inputs by type."""
        if not value:
            return None
        if field_type == int:
            try:
                v = int(value)
                if field_type == int and (v < 1900 or v > 2050):
                    logger.warning(f"Invalid year: {v}")
                    return None
                return v
            except (ValueError, TypeError):
                return None
        return self._normalize(str(value)) if value else None

    def _extract_base_words(self) -> list:
        """Extract base words from the profile with improved validation."""
        p = self.profile
        words = []
        
        def add_w(w):
            if w and len(w) > 0:
                norm = self._normalize(str(w))
                if norm:
                    words.append(norm)

        fn = self._validate_input(p.first_name)
        ln = self._validate_input(p.last_name)
        comp = self._validate_input(p.company)
        
        # Personal data
        add_w(fn)
        add_w(ln)
        add_w(p.nickname)
        
        if fn and ln:
            add_w(f"{fn}{ln}")
            add_w(f"{fn}.{ln}")
            add_w(f"{fn}_{ln}")
            add_w(f"{fn[0]}{ln}")
            add_w(f"{fn}{ln[0]}")
            if len(fn) > 1 and len(ln) > 1:
                add_w(f"{fn[0]}{ln[0]}")
                add_w(f"{fn[:2]}{ln[:2]}")
            
        if p.birth_year and 1900 <= p.birth_year <= 2050:
            add_w(str(p.birth_year))
            add_w(str(p.birth_year)[-2:])
        if p.birth_day and p.birth_month:
            add_w(f"{p.birth_day}{p.birth_month}")
            
        add_w(p.partner_name)
        add_w(p.pet_name)
        add_w(p.child_name)
        add_w(p.city)
        add_w(p.country)
        add_w(p.hobby)
        
        # Company data
        add_w(comp)
        if p.company_short:
            add_w(p.company_short)
        elif comp and len(comp) >= 3:
            add_w(comp[:3])
            
        if p.domain:
            domain_no_tld = p.domain.split('.')[0] if '.' in p.domain else p.domain
            add_w(domain_no_tld)
            
        add_w(p.industry)
        add_w(p.product)
        if p.founded_year and 1900 <= p.founded_year <= 2050:
            add_w(str(p.founded_year))
            add_w(str(p.founded_year)[-2:])
            
        # Person + company combinations
        if fn and comp:
            add_w(f"{fn}{comp}")
            add_w(f"{fn}_{comp}")
            add_w(f"{comp}{fn}")
            if p.birth_year:
                add_w(f"{comp}{str(p.birth_year)[-2:]}")
        if fn and ln and p.company_short:
            cs = self._normalize(p.company_short)
            add_w(f"{fn[0]}{ln}{cs}")
            
        # Extra words
        for ew in p.extra_words:
            add_w(ew)
            
        # Deduplicate while preserving order
        seen = set()
        unique_words = []
        for w in words:
            if w and w not in seen and len(w) >= 2:  # Minimum 2 chars
                seen.add(w)
                unique_words.append(w)
        
        logger.info(f"Extracted {len(unique_words)} base words")
        return unique_words

    def _capitalizations(self, word: str) -> list:
        """Generate capitalization variants."""
        if not word or len(word) < 1: 
            return []
        variants = [
            word.lower(),
            word.capitalize(),
            word.upper(),
        ]
        if len(word) > 1:
            variants.append(word[0].lower() + word[1:].upper())
            variants.append(word[0].upper() + word[1:].lower())
        return list(set(variants))

    def _leet_speak_advanced(self, word: str) -> Set[str]:
        """Advanced leet speak with multiple substitutions per character."""
        if not self.profile.leet_enabled or not word:
            return set()
        
        variants = set()
        chars = list(word)
        
        # Multiple substitutions, limited to avoid combinatorial explosion
        replaceable = [(i, c) for i, c in enumerate(chars) if c.lower() in LEET_MAP]
        
        if not replaceable:
            return variants
        
        # One substitution per character
        for idx, char in replaceable[:3]:  # Limitar a 3 caracteres reemplazables
            for sub in LEET_MAP[char.lower()]:
                new_word = chars.copy()
                new_word[idx] = sub
                variants.add(''.join(new_word))
        
        # Two substitutions, if at least 2 characters are replaceable
        if self.profile.leet_advanced and len(replaceable) >= 2:
            for i in range(min(2, len(replaceable))):
                for j in range(i + 1, min(3, len(replaceable))):
                    idx1, char1 = replaceable[i]
                    idx2, char2 = replaceable[j]
                    for sub1 in LEET_MAP[char1.lower()][:2]:
                        for sub2 in LEET_MAP[char2.lower()][:2]:
                            new_word = chars.copy()
                            new_word[idx1] = sub1
                            new_word[idx2] = sub2
                            variants.add(''.join(new_word))
                            if len(variants) > 50:
                                return variants
        
        return variants

    def _year_suffixes(self, word: str) -> list:
        """Suffixes with relevant years."""
        p = self.profile
        years = set()
        
        if p.birth_year and 1900 <= p.birth_year <= 2050:
            years.update([str(p.birth_year), str(p.birth_year)[-2:]])
        if p.founded_year and 1900 <= p.founded_year <= 2050:
            years.update([str(p.founded_year), str(p.founded_year)[-2:]])
        
        for y in range(max(1990, p.current_year - 10), p.current_year + 5):
            years.update([str(y), str(y)[-2:]])
            
        variants = []
        for cap in self._capitalizations(word):
            for y in years:
                variants.append(f"{cap}{y}")
        
        return variants

    def _season_suffixes(self, word: str) -> list:
        """Suffixes with seasonal terms."""
        if not self.profile.seasons_enabled:
            return []
        
        variants = set()
        years = ["", str(self.profile.current_year)[-2:], str(self.profile.current_year)]
        seasons = SEASONS_SHORT + ["summer", "winter", "spring", "fall"]
        
        for cap in self._capitalizations(word):
            for s in seasons:
                for y in years:
                    variants.add(f"{cap}{s.capitalize()}{y}")
                    if len(variants) >= 100:
                        return list(variants)
        
        return list(variants)

    def _special_suffixes(self, word: str) -> list:
        """Enhanced special suffixes."""
        variants = []
        for cap in self._capitalizations(word):
            for sfx in SPECIAL_SUFFIXES:
                variants.append(f"{cap}{sfx}")
        return variants

    def _number_prefixes(self, word: str) -> list:
        """Numeric prefixes."""
        variants = []
        for cap in self._capitalizations(word):
            for pfx in SPECIAL_PREFIXES:
                variants.append(f"{pfx}{cap}")
        return variants

    def _combinations(self, base_words: list) -> list:
        """Smart combinations of base words."""
        if not self.profile.combinations_enabled:
            return []
        
        variants = set()
        bw = base_words[:50]  # Increased to 50
        
        # 2-word combinations
        for w1, w2 in itertools.permutations(bw, 2):
            if len(w1) + len(w2) <= self.profile.max_length:
                for sep in SEPARATORS:
                    comb = f"{w1}{sep}{w2}"
                    if len(comb) >= self.profile.min_length:
                        variants.add(comb)
                    if len(variants) >= 1000:
                        return list(variants)
        
        return list(variants)

    def _filter_and_sort(self, words: Set[str]) -> list:
        """Filter and sort words by complexity."""
        filtered = [
            w for w in words 
            if self.profile.min_length <= len(w) <= self.profile.max_length 
            and w.strip() and len(w) > 1
        ]
        
        def sort_key(w):
            has_upper = any(c.isupper() for c in w)
            has_digit = any(c.isdigit() for c in w)
            has_special = any(c in '!@#$%^&*._-' for c in w)
            entropy = has_upper + has_digit + has_special
            return (entropy, len(w))
        
        return sorted(set(filtered), key=sort_key, reverse=True)

    def generate(self, console=None) -> WordlistResult:
        """Generate wordlist with configurable deduplication strategy."""
        base_words = self._extract_base_words()
        all_words: Set[str] = set(base_words)
        categories = defaultdict(int)
        
        categories["Base words"] = len(base_words)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console or Console()
        ) as progress:
            
            task = progress.add_task("[cyan]Processing mutations...", total=8)

            # Capitalizations
            progress.update(task, description="[cyan]Capitalizations...")
            for bw in base_words:
                caps = self._capitalizations(bw)
                categories["Capitalizations"] += len(caps)
                all_words.update(caps)
            progress.advance(task)

            # Enhanced leet speak
            progress.update(task, description="[cyan]Leet speak (advanced)...")
            for bw in base_words:
                leets = self._leet_speak_advanced(bw)
                categories["Leet speak"] += len(leets)
                all_words.update(leets)
            progress.advance(task)

            # Year suffixes
            progress.update(task, description="[cyan]Year suffixes...")
            for bw in base_words:
                years = self._year_suffixes(bw)
                categories["Year suffixes"] += len(years)
                all_words.update(years)
            progress.advance(task)

            # Season suffixes
            progress.update(task, description="[cyan]Seasons...")
            for bw in base_words:
                seasons = self._season_suffixes(bw)
                categories["Seasons"] += len(seasons)
                all_words.update(seasons)
            progress.advance(task)

            # Special suffixes
            progress.update(task, description="[cyan]Special suffixes...")
            for bw in base_words:
                sfx = self._special_suffixes(bw)
                categories["Special suffixes"] += len(sfx)
                all_words.update(sfx)
                
                pfx = self._number_prefixes(bw)
                categories["Number prefixes"] += len(pfx)
                all_words.update(pfx)
            progress.advance(task)

            # Combinations
            progress.update(task, description="[cyan]Combinations...")
            combos = self._combinations(base_words)
            categories["Combinations"] += len(combos)
            all_words.update(combos)
            progress.advance(task)

            # Final filtering
            progress.update(task, description="[cyan]Filtering & deduplicating...")
            final_words = self._filter_and_sort(all_words)
            
            # Apply maximum limit
            if len(final_words) > self.profile.max_words:
                logger.warning(f"Wordlist exceeded max ({len(final_words)} > {self.profile.max_words})")
                final_words = final_words[:self.profile.max_words]
                
            progress.advance(task)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_label = self.profile.company or self.profile.first_name or "target"
        label = re.sub(r'[^\w]', '_', raw_label.lower())[:20]

        # Statistics
        leet_chars = set()
        for subs in LEET_MAP.values():
            leet_chars.update(subs)
        
        stats = {
            "total_generated": len(all_words),
            "total_final": len(final_words),
            "dedup_savings": len(all_words) - len(final_words),
            "avg_word_length": sum(len(w) for w in final_words) / len(final_words) if final_words else 0,
            "max_word_length": max((len(w) for w in final_words), default=0),
            "min_word_length": min((len(w) for w in final_words), default=0),
            "has_leet": any(any(c in leet_chars for c in w) for w in final_words),
        }

        logger.info(f"Generated {len(final_words)} words (dedup saved {stats['dedup_savings']} duplicates)")

        return WordlistResult(
            profile=self.profile,
            base_words=base_words,
            final_words=final_words,
            total_count=len(final_words),
            categories=dict(categories),
            timestamp=timestamp,
            label=label,
            statistics=stats
        )

# ==========================================
# EXPORT ENGINE - ENHANCED
# ==========================================
def export_txt(result: WordlistResult, stdout=False) -> Path:
    """Export to standard TXT format, compatible with Hashcat, Hydra, etc."""
    if stdout:
        for w in result.final_words:
            print(w)
        return None
    
    path = REPORTS_DIR / f"wordlist_{result.label}_{result.timestamp}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(result.final_words) + "\n")
    logger.info(f"Exported TXT: {path} ({len(result.final_words)} words)")
    return path

def export_hashcat_masks(result: WordlistResult) -> Path:
    """Generate Hashcat masks automatically based on profile data."""
    path = REPORTS_DIR / f"masks_{result.label}_{result.timestamp}.hcmask"
    
    masks = set()
    p = result.profile
    
    # Name-based masks
    if p.first_name:
        fname = p.first_name[:15]
        masks.add(f"{fname}?d?d?d?d")  # name + 4 digits
        masks.add(f"{fname}?l?l?d")     # name + 2 letters + 1 digit
        masks.add(f"?u{fname}?d?d")     # uppercase + name + 2 digits
    
    # Company-based masks
    if p.company_short:
        company = p.company_short[:8]
        masks.add(f"{company}?d?d?d?d")
        masks.add(f"{company}?l?d?d")
        masks.add(f"{company}!?d?d")
    
    # Year-based masks
    if p.birth_year:
        by = str(p.birth_year)[-2:]
        masks.add(f"?a?a?a?a{by}")
        masks.add(f"{by}?a?a?a?a")
    
    # Generic universal masks
    masks.update([
        "?l?l?l?d?d",           # abc12
        "?u?l?l?l?d?d?d",       # Abc1234
        "?a?a?a?a?d?d?d?d",     # aB1c1234
        "?d?d?d?d?s",           # 1234!
        "?a?a?a?a?s?s",         # abcd!!
    ])
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Hashcat mask file generated by ContextWordlist v1.1\n")
        f.write("# Usage: hashcat -m 0 -a 3 hashes.txt -hm masks.hcmask\n")
        f.write("# Legend: ?l=lowercase ?u=uppercase ?d=digit ?s=special ?a=all\n\n")
        f.write("\n".join(sorted(masks)))
    
    logger.info(f"Exported Hashcat masks: {path} ({len(masks)} masks)")
    return path

def export_hashcat_rules_advanced(result: WordlistResult) -> Path:
    """Generate dynamic and advanced Hashcat rules."""
    path = REPORTS_DIR / f"rules_{result.label}_{result.timestamp}.rule"
    
    rules = [
        "# Advanced Hashcat rules generated by ContextWordlist v1.1",
        "# Usage: hashcat -m 0 hashes.txt wordlist.txt -r rules.rule",
        "",
        "# ====== CAPITALIZATIONS ======",
        "c",    # capitalize
        "u",    # uppercase
        "l",    # lowercase
        "C",    # invert capitalization
        "",
        "# ====== YEAR MUTATIONS ======",
    ]
    
    # Add dynamic rules for known years
    if result.profile.birth_year:
        by = str(result.profile.birth_year)[-2:]
        rules.extend([f"${ b}${ y}" for b in by for y in by])
    
    if result.profile.founded_year:
        fy = str(result.profile.founded_year)[-2:]
        rules.extend([f"${ f}${ y}" for f in fy for y in fy])
    
    rules.extend([
        "$2$0$2$4",
        "$2$0$2$5", 
        "$2$0$2$6",
        "c$2$0$2$4",
        "",
        "# ====== LEET SUBSTITUTIONS ======",
        "sa4",      # a -> 4
        "sa@",      # a -> @
        "se3",      # e -> 3
        "si1",      # i -> 1
        "si!",      # i -> !
        "so0",      # o -> 0
        "ss5",      # s -> 5
        "ss$",      # s -> $
        "st7",      # t -> 7
        "sl1",      # l -> 1
        "sg9",      # g -> 9
        "sb8",      # b -> 8",
        "",
        "# ====== SPECIAL SUFFIXES ======",
        "$!",
        "$@",
        "$#",
        "$1",
        "$@$#",
        "c$!",
        "c$@",
        "c$#",
        "",
        "# ====== COMBINATIONS ======",
        "c$2$0$2$4$!",
        "c$2$0$2$5$@",
        "u$1$2$3$!",
        "",
    ])
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(rules) + "\n")
    
    logger.info(f"Exported Hashcat rules: {path} ({len(rules)} rules)")
    return path

def export_html_report(result: WordlistResult) -> Path:
    """Enhanced HTML report with deep statistics."""
    path = REPORTS_DIR / f"report_{result.label}_{result.timestamp}.html"
    
    rows = ""
    total_mutations = sum(result.categories.values())
    for k, v in result.categories.items():
        if v > 0:
            pct = (v / total_mutations) * 100 if total_mutations > 0 else 0
            rows += f"<tr><td>{k}</td><td>{v:,}</td><td>{pct:.1f}%</td></tr>"
            
    preview_rows = ""
    leet_chars = set()
    for subs in LEET_MAP.values():
        leet_chars.update(subs)
    
    for i, w in enumerate(result.final_words[:100], 1):
        has_leet = any(c in leet_chars for c in w)
        has_special = any(c in '!@#$%^&*._-' for c in w)
        badge = ""
        if has_leet: badge += '<span class="badge leet">L</span>'
        if has_special: badge += '<span class="badge special">S</span>'
        preview_rows += f"<tr><td>{i}</td><td>{w}</td><td>{len(w)}</td><td>{badge}</td></tr>"

    # Configuration report
    config_info = f"""
    <tr><td>Min Length</td><td>{result.profile.min_length}</td></tr>
    <tr><td>Max Length</td><td>{result.profile.max_length}</td></tr>
    <tr><td>Leet Enabled</td><td>{'Yes' if result.profile.leet_enabled else 'No'}</td></tr>
    <tr><td>Seasons Enabled</td><td>{'Yes' if result.profile.seasons_enabled else 'No'}</td></tr>
    <tr><td>Combinations Enabled</td><td>{'Yes' if result.profile.combinations_enabled else 'No'}</td></tr>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContextWordlist Report - {result.label}</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #0a0c10; --bg2: #111318; --accent: #00ff9d; --text: #e0e0e0; --danger: #ff6b6b; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background-color: var(--bg); color: var(--text); font-family: 'Syne', sans-serif; padding: 40px; }}
        h1, h2, h3 {{ color: var(--accent); margin-top: 30px; margin-bottom: 15px; }}
        h1 {{ border-bottom: 2px solid var(--accent); padding-bottom: 15px; }}
        .header {{ margin-bottom: 40px; }}
        .info {{ background: var(--bg2); padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 30px 0; }}
        .stat-card {{ background: linear-gradient(135deg, var(--bg2) 0%, #1a1f2e 100%); padding: 20px; border-radius: 8px; border-left: 4px solid var(--accent); }}
        .stat-card:nth-child(2n) {{ border-left-color: #ff006e; }}
        .stat-card:nth-child(3n) {{ border-left-color: #00d9ff; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: white; font-family: 'JetBrains Mono', monospace; }}
        .stat-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.7; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-family: 'JetBrains Mono', monospace; font-size: 13px; background: var(--bg2); }}
        th {{ background: var(--accent); color: var(--bg); padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; }}
        tr:hover {{ background-color: #1a1f2e; }}
        .code {{ background: var(--bg2); padding: 15px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; color: #fff; overflow-x: auto; margin: 10px 0; border-left: 3px solid var(--accent); }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin: 2px; }}
        .badge.leet {{ background: #ff006e; color: white; }}
        .badge.special {{ background: #00d9ff; color: black; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; text-align: center; opacity: 0.6; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 ContextWordlist v1.1 Report</h1>
        <div class="info">
            <strong>Target:</strong> {result.label} | 
            <strong>Generated:</strong> {result.timestamp} | 
            <strong>Total Words:</strong> <span style="color: var(--accent);">{result.total_count:,}</span>
        </div>
    </div>

    <h2>📊 Key Statistics</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Words</div>
            <div class="stat-value">{result.total_count:,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Base Words</div>
            <div class="stat-value">{len(result.base_words)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Dedup Savings</div>
            <div class="stat-value">{result.statistics.get('dedup_savings', 0):,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Avg Length</div>
            <div class="stat-value">{result.statistics.get('avg_word_length', 0):.1f}</div>
        </div>
    </div>

    <h2>⚙️ Configuration</h2>
    <table>
        {config_info}
    </table>

    <h2>🧬 Mutation Breakdown</h2>
    <table>
        <tr><th>Category</th><th>Variants Generated</th><th>% of Total</th></tr>
        {rows}
    </table>

    <h2>👀 Preview (First 100)</h2>
    <table>
        <tr><th>#</th><th>Word</th><th>Len</th><th>Tags</th></tr>
        {preview_rows}
    </table>

    <h2>🚀 Usage Examples</h2>
    <div class="code">
# Hashcat direct wordlist<br>
hashcat -m 0 -a 0 hashes.txt wordlist_{result.label}_{result.timestamp}.txt<br><br>

# Hashcat with rules<br>
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r rules_{result.label}_{result.timestamp}.rule<br><br>

# Hashcat with masks<br>
hashcat -m 0 -a 3 hashes.txt -hm masks_{result.label}_{result.timestamp}.hcmask<br><br>

# Hydra SSH<br>
hydra -L users.txt -P wordlist_{result.label}_{result.timestamp}.txt ssh://target<br><br>

# John the Ripper<br>
john --wordlist=wordlist_{result.label}_{result.timestamp}.txt hashes.txt
    </div>

    <h2>💡 Advanced Tips</h2>
    <ul style="margin: 15px; line-height: 1.8;">
        <li><strong>GPU Acceleration:</strong> Use Hashcat with -d 1 (CPU), -d 2 (GPU), -d 3 (Both)</li>
        <li><strong>Memory Optimization:</strong> Add --workload-profile=2 for slower systems</li>
        <li><strong>Rule Stacking:</strong> Combine multiple rule files with multiple -r flags</li>
        <li><strong>Mask Filtering:</strong> Use --mask-charset to customize character sets</li>
    </ul>

    <div class="footer">
        Generated by ContextWordlist v1.1 | Enhanced Wordlist Generator for Professional Pentesting
    </div>
</body>
</html>"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    
    logger.info(f"Exported HTML report: {path}")
    return path

def export_csv(result: WordlistResult) -> Path:
    """CSV with deep analysis for each word."""
    path = REPORTS_DIR / f"wordlist_{result.label}_{result.timestamp}.csv"
    
    # Precompile leet chars
    leet_chars = set()
    for subs in LEET_MAP.values():
        leet_chars.update(subs)
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "length", "has_uppercase", "has_digit", "has_special", "has_leet", "entropy_score"])
        
        for w in result.final_words:
            has_upper = any(c.isupper() for c in w)
            has_digit = any(c.isdigit() for c in w)
            has_special = any(c in '!@#$%^&*._-' for c in w)
            has_leet = any(c in leet_chars for c in w)
            entropy = sum([has_upper, has_digit, has_special, has_leet])
            
            writer.writerow([w, len(w), has_upper, has_digit, has_special, has_leet, entropy])
    
    logger.info(f"Exported CSV: {path} ({len(result.final_words)} entries)")
    return path

def export_all_formats(result: WordlistResult) -> Dict[str, Path]:
    """Export all formats in a single batch."""
    exports = {
        "txt": export_txt(result),
        "masks": export_hashcat_masks(result),
        "rules": export_hashcat_rules_advanced(result),
        "html": export_html_report(result),
        "csv": export_csv(result),
    }
    return exports

# ==========================================
# CLI AND UI - ENHANCED
# ==========================================
def print_banner(console):
    banner = """
  ╔════════════════════════════════════════════════════════╗
  ║   CONTEXTWORDLIST v1.1                                 ║
  ║   Professional Contextual Wordlist Generator           ║
  ║   Enhanced for Advanced Pentesting                     ║
  ║   With Hashcat Masks, Rules & Deep Analytics          ║
  ╚════════════════════════════════════════════════════════╝"""
    console.print(Panel(banner, border_style="green", expand=False))

def interactive_mode(console) -> Profile:
    console.print(Panel("🔐 INTERACTIVE MODE\nEnter known data (press Enter to leave blank)", border_style="green"))
    
    console.print("\n[bold green]👤 Person data (press Enter to skip)[/bold green]")
    p_fn = input("  First name: ").strip() or None
    p_ln = input("  Last name: ").strip() or None
    p_nick = input("  Nickname: ").strip() or None
    
    p_by = input("  Birth year (e.g., 1990): ").strip()
    p_by = int(p_by) if p_by.isdigit() and 1900 <= int(p_by) <= 2050 else None
    
    p_bd = input("  Birth day (e.g., 15): ").strip() or None
    p_bm = input("  Birth month (e.g., 03): ").strip() or None
    p_partner = input("  Partner name: ").strip() or None
    p_pet = input("  Pet name: ").strip() or None
    p_child = input("  Child name: ").strip() or None
    p_city = input("  City: ").strip() or None
    p_country = input("  Country: ").strip() or None
    p_hobby = input("  Hobby: ").strip() or None

    console.print("\n[bold cyan]🏢 Company data (press Enter to skip)[/bold cyan]")
    c_name = input("  Company: ").strip() or None
    c_short = input("  Abbreviation (e.g., TN): ").strip() or None
    c_domain = input("  Domain: ").strip() or None
    c_ind = input("  Industry: ").strip() or None
    
    c_fy = input("  Founded year: ").strip()
    c_fy = int(c_fy) if c_fy.isdigit() and 1900 <= int(c_fy) <= 2050 else None
    
    c_prod = input("  Product: ").strip() or None

    console.print("\n[bold magenta]⚙️  Advanced Configuration[/bold magenta]")
    extra = input("  Extra words (comma-separated): ").strip()
    extra_words = [w.strip() for w in extra.split(",") if w.strip()]
    
    min_len_in = input("  Minimum length [6]: ").strip()
    min_len = int(min_len_in) if min_len_in.isdigit() else 6
    
    max_len_in = input("  Maximum length [20]: ").strip()
    max_len = int(max_len_in) if max_len_in.isdigit() else 20
    
    max_words_in = input("  Maximum words [50000]: ").strip()
    max_words = int(max_words_in) if max_words_in.isdigit() else 50000
    
    leet_adv = input("  Advanced leet speak (y/n) [y]: ").strip().lower() != "n"
    
    return Profile(
        first_name=p_fn, last_name=p_ln, nickname=p_nick, birth_year=p_by,
        birth_day=p_bd, birth_month=p_bm, partner_name=p_partner, pet_name=p_pet,
        child_name=p_child, city=p_city, country=p_country, hobby=p_hobby,
        company=c_name, company_short=c_short, domain=c_domain, industry=c_ind,
        founded_year=c_fy, product=c_prod,
        extra_words=extra_words, min_length=min_len, max_length=max_len,
        max_words=max_words, leet_advanced=leet_adv
    )

def main():
    parser = argparse.ArgumentParser(
        description="ContextWordlist v1.1 - Professional Wordlist Generator for Pentesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python contextwordlist.py -i
  
  Direct flags:
    python contextwordlist.py --name Juan --company TechNova --export all
  
  From JSON profile:
    python contextwordlist.py --profile target.json --export html
  
  Large wordlist (GPU optimized):
    python contextwordlist.py --name Juan --max-words 200000 --leet-advanced --export txt | wc -l
        """
    )
    
    # Modes
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode (recommended)")
    parser.add_argument("--profile", type=str, help="Load profile from JSON")
    
    # Person
    parser.add_argument("--name", type=str, help="First name")
    parser.add_argument("--lastname", type=str, help="Last name")
    parser.add_argument("--nickname", type=str, help="Nickname")
    parser.add_argument("--birth-year", type=int, help="Birth year")
    parser.add_argument("--birth-day", type=str, help="Birth day")
    parser.add_argument("--birth-month", type=str, help="Birth month")
    parser.add_argument("--partner", type=str, help="Partner name")
    parser.add_argument("--pet", type=str, help="Pet name")
    parser.add_argument("--child", type=str, help="Child name")
    parser.add_argument("--city", type=str, help="City")
    parser.add_argument("--country", type=str, help="Country")
    parser.add_argument("--hobby", type=str, help="Hobby")
    
    # Company
    parser.add_argument("--company", type=str, help="Company name")
    parser.add_argument("--company-short", type=str, help="Company abbreviation")
    parser.add_argument("--domain", type=str, help="Domain")
    parser.add_argument("--industry", type=str, help="Industry")
    parser.add_argument("--founded", type=int, help="Founded year")
    parser.add_argument("--product", type=str, help="Product")
    
    # Config
    parser.add_argument("--extra-words", type=str, help="Extra words (comma-separated)")
    parser.add_argument("--min-length", type=int, default=6, help="Minimum length (default: 6)")
    parser.add_argument("--max-length", type=int, default=20, help="Maximum length (default: 20)")
    parser.add_argument("--max-words", type=int, default=50000, help="Maximum words (default: 50000)")
    parser.add_argument("--leet-advanced", action="store_true", help="Advanced leet speak (multiple substitutions)")
    parser.add_argument("--no-leet", action="store_true", help="Disable leet speak")
    parser.add_argument("--no-seasons", action="store_true", help="Disable seasonal mutations")
    parser.add_argument("--no-combinations", action="store_true", help="Disable combinations")
    
    # Output
    parser.add_argument("--export", type=str, default="txt", choices=["txt", "rules", "masks", "html", "csv", "all"],
                       help="Export format (default: txt)")
    parser.add_argument("--output", type=str, default="reports/", help="Output directory (default: reports/)")
    parser.add_argument("--stdout", action="store_true", help="Send wordlist to stdout (useful for piping)")
    parser.add_argument("--quiet", action="store_true", help="Silent mode (no banner or tables)")
    parser.add_argument("--preview", type=int, default=20, help="Number of words to preview (default: 20)")
    
    args = parser.parse_args()
    console = Console()

    if not args.quiet:
        print_banner(console)

    # Load profile
    profile = None
    try:
        if args.interactive:
            profile = interactive_mode(console)
            export_fmt = input("  Export as (txt/rules/masks/html/csv/all) [txt]: ").strip() or "txt"
            args.export = export_fmt
        elif args.profile:
            with open(args.profile, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = Profile(**data)
                logger.info(f"Profile loaded from {args.profile}")
        else:
            extra = [w.strip() for w in args.extra_words.split(",")] if args.extra_words else []
            profile = Profile(
                first_name=args.name, last_name=args.lastname, nickname=args.nickname,
                birth_year=args.birth_year, birth_day=args.birth_day, birth_month=args.birth_month,
                partner_name=args.partner, pet_name=args.pet, child_name=args.child,
                city=args.city, country=args.country, hobby=args.hobby,
                company=args.company, company_short=args.company_short, domain=args.domain,
                industry=args.industry, founded_year=args.founded, product=args.product,
                extra_words=extra, min_length=args.min_length, max_length=args.max_length,
                max_words=args.max_words, leet_enabled=not args.no_leet,
                leet_advanced=args.leet_advanced, seasons_enabled=not args.no_seasons,
                combinations_enabled=not args.no_combinations
            )
    except Exception as e:
        console.print(f"[bold red]❌ Error loading profile: {e}[/bold red]")
        logger.error(f"Profile loading failed: {e}", exc_info=True)
        sys.exit(1)

    # Validate minimum data
    if not any([profile.first_name, profile.last_name, profile.company, profile.domain, profile.extra_words]):
        console.print("[bold red]❌ Error: You must provide at least one useful value (name, company, domain, or extra words)[/bold red]")
        sys.exit(1)

    # Summary
    label_target = profile.company or profile.first_name or "Target"
    
    muts = ["cap"]
    if profile.leet_enabled: 
        muts.append("leet" + ("-adv" if profile.leet_advanced else ""))
    muts.append("years")
    if profile.seasons_enabled: 
        muts.append("seasons")
    if profile.combinations_enabled: 
        muts.append("combos")
    
    try:
        engine = WordlistEngine(profile)
        base_c = len(engine._extract_base_words())
        
        if not args.quiet:
            console.print(f"\n🎯 Target: [bold]{label_target}[/bold]")
            console.print(f"📝 Base words: [bold green]{base_c}[/bold green] | Mutations: [cyan]{' + '.join(muts)}[/cyan]")
            console.print(f"⚙️  Config: {profile.min_length}-{profile.max_length} chars, max {profile.max_words:,} words\n")

        result = engine.generate(console=console if not args.quiet else None)

        # Preview
        if args.preview > 0 and result.final_words and not args.quiet:
            table = Table(title=f"▶️  Preview — first {args.preview} words", show_header=True, header_style="bold magenta")
            table.add_column("#", style="dim", width=4)
            table.add_column("Word", style="cyan")
            table.add_column("Len", justify="right", style="yellow")
            
            for i, w in enumerate(result.final_words[:args.preview], 1):
                table.add_row(str(i), w, str(len(w)))
            console.print(table)

        # Statistics
        if not args.quiet:
            stats_text = f"📊 [Total: [bold green]{result.total_count:,}[/bold green]] [Base: {len(result.base_words)}] [Range: {profile.min_length}-{profile.max_length}]"
            console.print(Panel(stats_text, border_style="blue", expand=False))

        # Export
        fmt = args.export.lower()
        exported_files = []
        
        try:
            if fmt in ["txt", "all"]:
                if args.stdout:
                    export_txt(result, stdout=True)
                else:
                    path = export_txt(result)
                    exported_files.append(("[green]✓[/green] Wordlist", str(path)))
            
            if fmt in ["masks", "all"]:
                path = export_hashcat_masks(result)
                exported_files.append(("[green]✓[/green] Masks", str(path)))
            
            if fmt in ["rules", "all"]:
                path = export_hashcat_rules_advanced(result)
                exported_files.append(("[green]✓[/green] Rules", str(path)))
            
            if fmt in ["html", "all"]:
                path = export_html_report(result)
                exported_files.append(("[green]✓[/green] Report", str(path)))
            
            if fmt in ["csv", "all"]:
                path = export_csv(result)
                exported_files.append(("[green]✓[/green] CSV", str(path)))
            
            if exported_files and not args.quiet:
                console.print("\n[bold green]📁 Exported Files:[/bold green]")
                for label, path in exported_files:
                    console.print(f"  {label} → {path}")
        
        except Exception as e:
            console.print(f"[bold red]❌ Export error: {e}[/bold red]")
            logger.error(f"Export failed: {e}", exc_info=True)

        # Final instructions
        if not args.quiet:
            instr = f"""
[bold cyan]🚀 Quick Start:[/bold cyan]
  hashcat -m 0 -a 0 hashes.txt reports/wordlist_{result.label}_{result.timestamp}.txt
  hashcat -m 0 -a 0 hashes.txt wordlist.txt -r reports/rules_{result.label}_{result.timestamp}.rule
  hydra -L users.txt -P reports/wordlist_{result.label}_{result.timestamp}.txt ssh://target
            """
            console.print(Panel(instr, border_style="dim", expand=False))

        logger.info(f"Generation complete: {result.total_count} words generated successfully")

    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Operation cancelled by user[/yellow]")
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]❌ Critical error: {e}[/bold red]")
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
