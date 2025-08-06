from rapidfuzz import process, fuzz

# Paths
aligned_path = "translated_phrases.txt"
unaligned_path = "cleaned_english_output_with_newlines.txt"
output_path = "matched_from_unaligned_to_aligned.txt"

# Load and clean lines
with open(aligned_path, "r", encoding="utf-8") as f:
    aligned_lines = [line.strip() for line in f if line.strip()]

with open(unaligned_path, "r", encoding="utf-8") as f:
    unaligned_lines = [line.strip() for line in f if line.strip()]

used_unaligned_indices = set()
matched_output = []

# Try to find best match in unaligned for each aligned
for i, aline in enumerate(aligned_lines):
    result = process.extractOne(
        aline,
        unaligned_lines,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=75  # Adjust as needed
    )

    if result is not None:
        match_text, match_score, match_index = result

        if match_index not in used_unaligned_indices:
            matched_output.append(match_text)
            used_unaligned_indices.add(match_index)
            print(f"[{i}] MATCHED: \"{aline}\" -> \"{match_text}\" (score={match_score})")
            continue
        else:
            print(f"[{i}] DUPLICATE SKIPPED: \"{aline}\"")
    else:
        print(f"[{i}] NO MATCH: \"{aline}\"")

    matched_output.append("")  # Placeholder for no match

# Save output
with open(output_path, "w", encoding="utf-8") as f:
    for line in matched_output:
        f.write(line + "\n")

print(f"\nDone. Output written to {output_path}")
