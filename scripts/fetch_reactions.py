#!/usr/bin/env python3
"""
Fetch international reactions to TP4 using Gemini with Google Search grounding.
Reads batches from entities.json, queries Gemini per batch, updates international_reactions.json.

Usage:
    source .venv/bin/activate
    python scripts/fetch_reactions.py [--batch BATCH_NAME] [--dry-run]
"""

import argparse
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTITIES_PATH = os.path.join(REPO, 'data', 'reference', 'entities.json')
REACTIONS_PATH = os.path.join(REPO, 'data', 'tp4-2026', 'international_reactions.json')
REACTION_TYPES_PATH = os.path.join(REPO, 'data', 'reference', 'reaction_types.json')

VALID_STANCES = [
    'active_participant_pro_iran', 'supports_iran', 'condemns_israel',
    'calls_for_deescalation', 'neutral_acknowledgement', 'silent',
    'condemns_iran', 'supports_israel', 'active_participant_coalition',
]

PROMPT_TEMPLATE = """You are researching international reactions to Iran's "Operation True Promise 4" —
a series of missile and drone attacks against Israel and US/coalition military bases in the Gulf,
which began on February 28, 2026.

For each entity listed below, find:
1. **Head of state** statement (president, monarch, supreme leader) — who said it, when, what they said, any URL
2. **Head of government** statement (prime minister, chancellor) — same details
3. **Foreign ministry** statement — same details
4. **Overall stance** — classify as exactly one of: {stances}

If a country has no head of government separate from head of state (e.g. US president), leave head_of_government as made:false.

Entities to research:
{entity_list}

Respond with ONLY a JSON array. Each element must be:
{{
  "code": "XX",
  "overall_stance": "one_of_the_stances_above",
  "head_of_state": {{
    "made": true/false,
    "date": "YYYY-MM-DD or null",
    "speaker": "name or null",
    "speaker_title": "title or null",
    "summary": "brief summary or null",
    "statement_text": "direct quote if available or null",
    "statement_url": "URL or null",
    "category": "stance or null"
  }},
  "head_of_government": {{ same structure }},
  "foreign_ministry": {{ same structure }},
  "notes": "brief context"
}}

Use "silent" for countries with no public reaction found. Return ONLY the JSON array, no other text.
"""


def load_entities():
    with open(ENTITIES_PATH) as f:
        return json.load(f)


def load_reactions():
    with open(REACTIONS_PATH) as f:
        return json.load(f)


def save_reactions(data):
    with open(REACTIONS_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def get_batches(entities):
    from collections import defaultdict
    batches = defaultdict(list)
    for e in entities:
        batches[e['search_batch']].append(e)
    return dict(batches)


def query_gemini(prompt, retries=3):
    from google import genai
    from google.genai import types

    client = genai.Client()

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.2,
                ),
            )

            text = response.text or ''
            if not text:
                raise ValueError("Gemini returned empty response")
            sources = []
            if response.candidates[0].grounding_metadata:
                gm = response.candidates[0].grounding_metadata
                for chunk in (gm.grounding_chunks or []):
                    if chunk.web:
                        sources.append({'title': chunk.web.title, 'uri': chunk.web.uri})

            return text, sources

        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def parse_json_response(text):
    """Extract JSON array from Gemini response, handling markdown fences."""
    text = text.strip()
    if text.startswith('```'):
        # Strip markdown code fences
        lines = text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        text = '\n'.join(lines)
    # Find the JSON array
    start = text.find('[')
    end = text.rfind(']')
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in response: {text[:200]}")
    return json.loads(text[start:end + 1])


def build_statement(data):
    """Convert a parsed statement dict into the canonical format."""
    if not data or not isinstance(data, dict):
        return {"made": False, "date": None, "speaker": None, "speaker_title": None,
                "summary": None, "statement_text": None, "statement_url": None, "category": None}
    cat = data.get('category')
    if cat and cat not in VALID_STANCES:
        cat = None
    return {
        "made": bool(data.get('made', False)),
        "date": data.get('date'),
        "speaker": data.get('speaker'),
        "speaker_title": data.get('speaker_title'),
        "summary": data.get('summary'),
        "statement_text": data.get('statement_text'),
        "statement_url": data.get('statement_url'),
        "category": cat,
    }


def apply_results(reactions_data, parsed_results):
    """Merge parsed Gemini results into the reactions data structure."""
    lookup = {r['iso_3166_1_alpha2']: r for r in reactions_data['reactions']}
    applied = 0

    for result in parsed_results:
        code = result.get('code')
        if not code or code not in lookup:
            print(f"  Warning: code '{code}' not found in reactions, skipping", file=sys.stderr)
            continue

        entry = lookup[code]
        stance = result.get('overall_stance')
        if stance in VALID_STANCES:
            entry['overall_stance'] = stance
        elif stance:
            print(f"  Warning: invalid stance '{stance}' for {code}, keeping existing", file=sys.stderr)

        entry['head_of_state_statement'] = build_statement(result.get('head_of_state'))
        entry['head_of_government_statement'] = build_statement(result.get('head_of_government'))
        entry['foreign_ministry_statement'] = build_statement(result.get('foreign_ministry'))

        if result.get('notes'):
            entry['notes'] = result['notes']

        applied += 1

    return applied


def main():
    parser = argparse.ArgumentParser(description='Fetch international reactions via Gemini')
    parser.add_argument('--batch', type=str, help='Only process this batch (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Print prompts without querying')
    parser.add_argument('--delay', type=float, default=2.0, help='Seconds between batch queries')
    args = parser.parse_args()

    if not os.environ.get('GOOGLE_API_KEY'):
        # Try loading from .env
        env_path = os.path.join(REPO, '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        os.environ['GOOGLE_API_KEY'] = line.strip().split('=', 1)[1]

    if not os.environ.get('GOOGLE_API_KEY'):
        print("Error: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    entities = load_entities()
    batches = get_batches(entities)
    reactions_data = load_reactions()

    stances_str = ', '.join(VALID_STANCES)
    target_batches = [args.batch] if args.batch else sorted(batches.keys())

    total_applied = 0
    total_batches = len(target_batches)

    for i, batch_name in enumerate(target_batches, 1):
        if batch_name not in batches:
            print(f"Unknown batch: {batch_name}", file=sys.stderr)
            continue

        batch_entities = batches[batch_name]
        entity_list = '\n'.join(
            f"- {e['alpha2']}: {e['name']} (type: {e['type']})"
            for e in batch_entities
        )

        prompt = PROMPT_TEMPLATE.format(
            stances=stances_str,
            entity_list=entity_list,
        )

        print(f"[{i}/{total_batches}] {batch_name} ({len(batch_entities)} entities)...", flush=True)

        if args.dry_run:
            print(f"  Would query {len(batch_entities)} entities")
            continue

        try:
            text, sources = query_gemini(prompt)
            parsed = parse_json_response(text)
            applied = apply_results(reactions_data, parsed)
            total_applied += applied
            print(f"  Applied {applied}/{len(batch_entities)} results, {len(sources)} sources")
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        if i < total_batches:
            time.sleep(args.delay)

    if not args.dry_run and total_applied > 0:
        reactions_data['metadata']['last_updated'] = '2026-03-08'
        save_reactions(reactions_data)
        print(f"\nDone. Updated {total_applied} entities across {total_batches} batches.")

        # Print stance summary
        from collections import Counter
        stances = Counter(r['overall_stance'] for r in reactions_data['reactions'])
        print("\nStance distribution:")
        for stance, count in sorted(stances.items(), key=lambda x: -x[1]):
            print(f"  {stance}: {count}")
    elif args.dry_run:
        print(f"\nDry run complete. Would process {total_batches} batches.")
    else:
        print("\nNo updates applied.")


if __name__ == '__main__':
    main()
