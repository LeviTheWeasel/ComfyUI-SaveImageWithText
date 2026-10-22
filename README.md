# ComfyUI-SaveImageWithText

A drop-in replacement for ComfyUI's **Save Image** that also embeds a string in the PNG — typically a prompt
that was generated while the graph ran (an LLM node such as TextGenerate, wildcards, random prompt builders).

ComfyUI writes the graph into the PNG when the job is queued, so text produced during execution is otherwise lost:
the saved `prompt`/`workflow` only show the node that *would* generate it.

## Install

Clone or copy this folder into `ComfyUI/custom_nodes/` and restart ComfyUI.

```bash
cd ComfyUI/custom_nodes
git clone <this repo> ComfyUI-SaveImageWithText
```

## Use

Replace **Save Image** with **Save Image (+ final prompt)** (`SaveImageWithText`) and connect the string you want
to keep — e.g. the same output that feeds your CLIP Text Encode — to its `text` input.

Everything else is identical to Save Image (file naming, `prompt` and `workflow` chunks). Two text chunks are added:

| chunk | content |
|---|---|
| `final_prompt` | the connected string (stored as UTF-8 iTXt when it isn't Latin-1) |
| `final_prompt_source` | id of the node that produced it, so viewers can put the text back in its place in the graph |

AIImageViewer reads both and shows the generated prompt in place of the placeholder.
