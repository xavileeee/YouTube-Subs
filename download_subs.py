#!/usr/bin/env python3
"""CLI y utilidades para descargar subtítulos (incluidos autogenerados) de YouTube.

Ejemplo: python download_subs.py "https://www.youtube.com/watch?v=..." --lang es
"""
import argparse
import os
import re
from typing import Optional, Tuple

import requests
import yt_dlp

SUBS_DIR = os.path.join(os.path.dirname(__file__), "subs")
os.makedirs(SUBS_DIR, exist_ok=True)


def get_subtitle_url(info: dict, lang: str) -> Optional[Tuple[str, str]]:
    # Revisa subtítulos subidos y, si no hay, revisa autogenerados
    subs = info.get("subtitles", {}) or {}
    auto = info.get("automatic_captions", {}) or {}

    for source in (subs, auto):
        if lang in source:
            entries = source[lang]
            # Prefer vtt
            for e in entries:
                if e.get("ext") == "vtt":
                    return e.get("url"), "vtt"
            return entries[0].get("url"), entries[0].get("ext")
    return None


def download_text_from_url(url: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def vtt_to_text(vtt: str) -> str:
    # Normaliza VTT: elimina encabezados, marcas de tiempo (incluidas etiquetas inline
    # como <00:00:02.320>), tags <c>...</c> y cualquier tag entre <>
    lines = []
    for line in vtt.splitlines():
        line = line.strip()
        if not line:
            continue
        # Ignore common headers (only when they appear as whole header lines)
        if re.match(r"^(WEBVTT\b.*|Kind:\s*\w+(?:\s+Language:\s*\w+)?|Language:\s*\w+)\s*$", line, re.IGNORECASE):
            continue
        # Cue timestamps on their own lines
        if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3} -->", line) or ("-->" in line and re.match(r"^\d{2}:\d{2}", line)):
            continue
        if re.match(r"^\d+$", line):
            continue
        # Remove inline timestamp tags like <00:00:02.320>
        line = re.sub(r"<\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*>", " ", line)
        # Remove simple <c> tags but keep text
        line = re.sub(r"</?c>", "", line)
        # Remove any other leftover tags
        line = re.sub(r"<[^>]+>", " ", line)
        if line:
            lines.append(line)
    # Join lines preserving cue breaks and normalize spaces inside each line (keep newlines)
    text = "\n".join(lines)
    # Normalize spaces inside each line and remove empty lines, keep paragraph breaks
    nl_lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    nl_lines = [ln for ln in nl_lines if ln]
    text = "\n\n".join(nl_lines)
    return text


def srt_to_text(srt: str) -> str:
    lines = []
    for line in srt.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} -->", line):
            continue
        # clean inline tags similar to VTT
        line = re.sub(r"<\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*>", " ", line)
        line = re.sub(r"</?c>", "", line)
        line = re.sub(r"<[^>]+>", " ", line)
        lines.append(line)
    return "\n".join(lines)
def _dedupe_repeated_sequences(text: str, max_window: int = 20) -> str:
    """Elimina repeticiones contiguas de n-gramas (ventanas) en el texto.
    Busca patrones donde una secuencia de palabras se repite inmediatamente y elimina la segunda
    aparición. Esto ayuda a limpiar las repeticiones que aparecen en subtítulos autogenerados.
    """
    words = text.split()
    i = 0
    while i < len(words):
        removed = False
        max_w = min(max_window, (len(words) - i) // 2)
        for w in range(max_w, 2, -1):
            if words[i:i + w] == words[i + w:i + 2 * w]:
                del words[i + w:i + 2 * w]
                removed = True
                break
        if not removed:
            i += 1
    return " ".join(words)


def clean_text(text: str) -> str:
    # Elimina corchetes y marcas como [música], [risas], timestamps y tags, normaliza y des-duplica
    t = re.sub(r"\[.*?\]", "", text)
    # Elimina timestamps inline y marcas tipo <00:00:00.000>
    t = re.sub(r"<\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*>", " ", t)
    t = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}", " ", t)
    t = re.sub(r"</?c>", "", t)
    t = re.sub(r"<[^>]+>", " ", t)

    # Split into cue-paragraphs (preserve empty cue separators)
    paras = [p for p in t.split('\n\n') if p and p.strip()]

    # Process each cue-group into a cleaned paragraph text (remove duplicate lines and n-gram repeats)
    paras_texts = []
    for p in paras:
        p_lines = [re.sub(r"\s+", " ", ln).strip() for ln in p.splitlines()]
        p_lines = [ln for ln in p_lines if ln]
        if not p_lines:
            continue
        dedup_lines = []
        prev = None
        for ln in p_lines:
            if ln != prev:
                dedup_lines.append(ln)
            prev = ln
        paragraph_text = ' '.join(dedup_lines)
        paragraph_text = _dedupe_repeated_sequences(paragraph_text, max_window=40)
        paras_texts.append(paragraph_text.strip())

    # Merge consecutive cue-paragraphs until a sentence terminator (., !, ?) is found.
    # This preserves logical paragraph breaks unless the sentence continues across cue blocks.
    processed_paras = []
    i = 0
    while i < len(paras_texts):
        if re.search(r"[\.\!\?]$", paras_texts[i]):
            processed_paras.append(paras_texts[i])
            i += 1
            continue
        # lookahead for a paragraph that ends with a terminator
        j = i + 1
        found = False
        while j < len(paras_texts):
            if re.search(r"[\.\!\?]$", paras_texts[j]):
                found = True
                break
            j += 1
        if found:
            merged = ' '.join(paras_texts[i:j + 1])
            merged = _dedupe_repeated_sequences(merged, max_window=40)
            processed_paras.append(merged.strip())
            i = j + 1
        else:
            # no terminator ahead: keep as-is
            processed_paras.append(paras_texts[i])
            i += 1

    # Remove adjacent duplicate paragraphs
    final_pars = []
    prev = None
    for p in processed_paras:
        if p != prev:
            final_pars.append(p)
        prev = p

    # Remove overlapping repeated phrases between adjacent paragraphs.
    connectors = re.compile(r'^(Sin embargo,|Además,|Pero,|No obstante,)\s*', re.IGNORECASE)
    cleaned_pars = []
    for i, p in enumerate(final_pars):
        if not cleaned_pars:
            cleaned_pars.append(p)
            continue
        prev_p = cleaned_pars[-1]
        # candidate prefix in current p after removing connectors
        lead = connectors.sub('', p)
        a_words = re.findall(r"\w+", prev_p.lower())
        b_words = re.findall(r"\w+", lead.lower())
        max_overlap = min(len(a_words), len(b_words), 20)
        overlap = 0
        # find largest overlap (>=3 words)
        for k in range(max_overlap, 2, -1):
            if a_words[-k:] == b_words[:k]:
                overlap = k
                break
        if overlap >= 3:
            # Prefer keeping the repeated phrase in the *later* paragraph and remove it from the previous one.
            prev_words = re.findall(r"\S+", prev_p)
            if len(prev_words) > overlap:
                new_prev = ' '.join(prev_words[:-overlap]).strip()
                cleaned_pars[-1] = new_prev
                cleaned_pars.append(p)
            else:
                lead_words = re.findall(r"\S+", lead)
                new_lead = ' '.join(lead_words[overlap:]).lstrip()
                m = connectors.match(p)
                conn = m.group(0) if m else ''
                new_p = (conn + new_lead).strip()
                if not new_p:
                    continue
                cleaned_pars.append(new_p)
        else:
            cleaned_pars.append(p)

    # Remove duplicate leading connectors in consecutive paragraphs (e.g., "Sin embargo,")
    dedup_connectors = []
    for i, p in enumerate(cleaned_pars):
        if i > 0:
            m1 = connectors.match(cleaned_pars[i - 1])
            m2 = connectors.match(p)
            if m1 and m2 and m1.group(1).lower() == m2.group(1).lower():
                p = connectors.sub('', p)
        dedup_connectors.append(p)

    # Collapse very short standalone paragraphs (e.g., single words or short numerics) into previous paragraph
    normalized_pars = []
    for i, p in enumerate(dedup_connectors):
        if i > 0 and (len(p.split()) <= 3 or len(p) < 25):
            # if p is contained at end of previous, skip it
            prev = normalized_pars[-1]
            if p.strip().strip('.') in prev.split()[-len(p.split()):]:
                # skip duplicate short fragment
                continue
            # otherwise, merge short paragraph into previous
            normalized_pars[-1] = (prev + ' ' + p).strip()
        else:
            normalized_pars.append(p)

    # Merge continuation paragraphs: if a paragraph does NOT end with a sentence terminator
    # and the next paragraph starts with a lowercase letter, it's likely a continuation and should be merged
    # Merge continuation paragraphs only when the next paragraph starts with a short
    # continuation token (e.g., 'es', 'y', 'de', 'con') indicating it's likely the
    # continuation of the previous sentence rather than a new idea.
    continuation_tokens = set(["es","y","que","de","con","por","para","como","se","su","si","al","lo","la","el","los","las","pero","aunque","entre"])
    merged = []
    for p in normalized_pars:
        if merged:
            prev = merged[-1]
            # prev ends with terminator?
            if not re.search(r'[\.\!\?]"?$', prev):
                m = re.match(r"^[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)", p)
                first = m.group(1).lower() if m else ''
                # merge only if first word is explicitly recognized as a continuation token
                if first in continuation_tokens and re.match(r'^[^A-ZÁÉÍÓÚÜÑ]*[a-záéíóúüñ]', p, re.UNICODE):
                    merged[-1] = (prev + ' ' + p).strip()
                else:
                    merged.append(p)
            else:
                merged.append(p)
        else:
            merged.append(p)
    normalized_pars = merged

    # Final pass: collapse repeated adjacent sentences and repeated words/phrases inside paragraphs
    final_pars = []
    for p in normalized_pars:
        # collapse exact adjacent repeated sentences
        sents = re.split(r'(?<=[\.\!\?])\s+', p)
        seen_sents = []
        seen_norm = set()
        for s in sents:
            if not s:
                continue
            norm = re.sub(r"\s+", " ", s.strip()).lower()
            if norm in seen_norm:
                # skip duplicate sentence
                continue
            seen_sents.append(s)
            seen_norm.add(norm)
        p2 = ' '.join(seen_sents)
        # collapse repeated words/phrases more aggressively
        p2 = _dedupe_repeated_sequences(p2, max_window=60)
        # collapse exact repeated tokens
        p2 = re.sub(r'\b(\w+)(?:\W+\1\b){1,}', r'\1', p2, flags=re.IGNORECASE)
        final_pars.append(p2.strip())

    # Final strict paragraph merge: only allow paragraph breaks when the paragraph
    # ends with a sentence terminator. Merge otherwise to avoid spurious short paragraphs.
    strict_pars = []
    for p in final_pars:
        if strict_pars and not re.search(r'[\.\!\?]"?$', strict_pars[-1]):
            strict_pars[-1] = (strict_pars[-1] + ' ' + p).strip()
        else:
            strict_pars.append(p)

    t = '\n\n'.join(strict_pars)

    # Normaliza espaciado con signos de puntuación (respetando saltos de línea)
    t = re.sub(r"\s+([,.;:?!])", r"\1", t)
    t = re.sub(r"([,.;:?!])([^\s\n])", r"\1 \2", t)

    return t.strip()


def fetch_subs(url: str, lang: str = "es") -> Tuple[str, str, Optional[str]]:
    """Devuelve (raw_text, cleaned_text, saved_path)
    si no hay subtítulos, lanza ValueError
    """
    ydl = yt_dlp.YoutubeDL({"quiet": True})
    info = ydl.extract_info(url, download=False)
    sub = get_subtitle_url(info, lang)
    if not sub:
        raise ValueError(f"No hay subtítulos ni autogenerados en '{lang}' para este vídeo")
    sub_url, ext = sub
    raw = download_text_from_url(sub_url)
    # Keep `raw` exactly as downloaded (what Google provides)
    if ext == "vtt":
        processed_text = vtt_to_text(raw)
    elif ext == "srt":
        processed_text = srt_to_text(raw)
    else:
        processed_text = raw

    cleaned = clean_text(processed_text)

    # Guardar en subs/
    video_id = info.get("id") or re.sub(r"[^0-9A-Za-z]+", "_", info.get("title", "video"))
    filename = f"{video_id}.{lang}.{ext}"
    saved_path = os.path.join(SUBS_DIR, filename)
    with open(saved_path, "w", encoding="utf-8") as f:
        f.write(raw)

    # Return raw (unmodified download), cleaned (processed & strict)
    return raw, cleaned, saved_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL del vídeo de YouTube")
    parser.add_argument("--lang", default="es", choices=["es", "en", "fr", "de"], help="Idioma de los subtítulos")
    args = parser.parse_args()

    try:
        raw, cleaned, path = fetch_subs(args.url, args.lang)
    except Exception as e:
        print("Error:", e)
        raise SystemExit(1)

    print("Guardado:", path)
    print("\n--- Transcripción (raw) ---\n")
    print(raw)
    print("\n--- Transcripción (limpia) ---\n")
    print(cleaned)


if __name__ == "__main__":
    main()
