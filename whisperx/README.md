Running WhisperX offline
========================

* `pip install whisperx` to venv using python 3.11
* Edit *~py3.11-util/lib/python3.11/site-packages/torch/serialization.py* (~1465) to set `weights_only` False
* `~/py3.11-util/bin/whisperx --compute_type int8 ~/Music/data/240915_1706.mp3`
