# Graph Report - frig-zone-web  (2026-10-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 161 nodes · 256 edges · 8 communities (6 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `64556c16`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- system_tools.py
- tts_engine.py
- main.py
- env
- jarvis.py
- calibrador.py
- JarvisBrain
- initFrigZoneApp

## God Nodes (most connected - your core abstractions)
1. `run_jarvis()` - 15 edges
2. `TTSEngine` - 13 edges
3. `JarvisBrain` - 12 edges
4. `main()` - 11 edges
5. `STTEngine` - 10 edges
6. `render_banner()` - 9 edges
7. `env` - 9 edges
8. `get_dbx_client()` - 8 edges
9. `steps` - 6 edges
10. `archive_published_image()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `render_banner()` --uses--> `TTSEngine`  [INFERRED]
  jarvis/jarvis.py → jarvis/tts_engine.py
- `render_banner()` --uses--> `JarvisBrain`  [INFERRED]
  jarvis/jarvis.py → jarvis/brain.py
- `run_jarvis()` --calls--> `TTSEngine`  [EXTRACTED]
  jarvis/jarvis.py → jarvis/tts_engine.py
- `render_banner()` --uses--> `STTEngine`  [INFERRED]
  jarvis/jarvis.py → jarvis/stt_engine.py
- `run_jarvis()` --calls--> `JarvisBrain`  [EXTRACTED]
  jarvis/jarvis.py → jarvis/brain.py

## Import Cycles
- None detected.

## Communities (8 total, 2 thin omitted)

### Community 0 - "system_tools.py"
Cohesion: 0.08
Nodes (6): control_volume(), delegate_to_openclaw(), get_system_status(), get_time_and_date(), open_application(), search_web()

### Community 1 - "tts_engine.py"
Cohesion: 0.10
Nodes (5): clean_text_for_speech(), get_real_output_devices(), get_sapi_engine(), split_into_sentences(), TTSEngine

### Community 2 - "main.py"
Cohesion: 0.18
Nodes (11): create_fallback_image(), generate_ai_image(), generate_post_content(), archive_published_image(), archive_published_video(), get_dbx_client(), get_next_image_from_dropbox(), get_next_video_from_dropbox() (+3 more)

### Community 3 - "env"
Cohesion: 0.08
Nodes (23): DROPBOX_ACCESS_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN, GEMINI_API_KEY, META_ACCESS_TOKEN, META_IG_ACCOUNT_ID, META_PAGE_ID (+15 more)

### Community 4 - "jarvis.py"
Cohesion: 0.13
Nodes (6): clean_wake_word(), contains_wake_word(), render_banner(), run_jarvis(), get_real_microphones(), STTEngine

### Community 5 - "calibrador.py"
Cohesion: 0.15
Nodes (3): main(), test_microphone_meter(), test_output_voice()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TTSEngine` connect `tts_engine.py` to `jarvis.py`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `run_jarvis()` (e.g. with `.get_current_model_info()` and `.process_command()`) actually correct?**
  _`run_jarvis()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `system_tools.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08465608465608465 - nodes in this community are weakly interconnected._
- **Why does `JarvisBrain` connect `JarvisBrain` to `system_tools.py`, `jarvis.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `JarvisBrain` (e.g. with `render_banner()` and `select_model_interactive()`) actually correct?**
  _`JarvisBrain` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `tts_engine.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09846153846153846 - nodes in this community are weakly interconnected._
- **Why does `run_jarvis()` connect `jarvis.py` to `tts_engine.py`, `main.py`, `JarvisBrain`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._