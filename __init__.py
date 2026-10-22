"""SaveImage that also embeds a runtime string (e.g. an LLM-generated prompt) into the PNG.

ComfyUI writes the graph into the PNG at queue time, so text produced while the graph runs
(TextGenerate and friends) is otherwise lost. This node stores it in two text chunks:
  final_prompt         - the string itself
  final_prompt_source  - id of the node that produced it, so viewers can put it in place
Everything else (prompt/workflow chunks, file naming) is identical to the stock SaveImage.
"""
import json
import os

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths
from comfy.cli_args import args
from nodes import SaveImage


class SaveImageWithText(SaveImage):
    @classmethod
    def INPUT_TYPES(s):
        types = SaveImage.INPUT_TYPES()
        types["required"]["text"] = ("STRING", {"forceInput": True, "tooltip": "Text to embed as the final_prompt chunk."})
        types["hidden"]["unique_id"] = "UNIQUE_ID"
        return types

    DESCRIPTION = "Saves images like Save Image, and embeds the connected text (e.g. a generated prompt) in the PNG."
    SEARCH_ALIASES = ["save image text", "save final prompt", "embed prompt"]

    def save_images(self, images, filename_prefix="ComfyUI", text="", prompt=None, extra_pnginfo=None, unique_id=None):
        source = None
        try:
            link = prompt[str(unique_id)]["inputs"]["text"]
            if isinstance(link, list):
                source = str(link[0])
        except (KeyError, TypeError):
            pass

        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = []
        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                metadata.add_text("final_prompt", text)  # non-latin text becomes iTXt automatically
                if source is not None:
                    metadata.add_text("final_prompt_source", source)

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({"filename": file, "subfolder": subfolder, "type": self.type})
            counter += 1

        return {"ui": {"images": results}, "result": (images,)}


NODE_CLASS_MAPPINGS = {"SaveImageWithText": SaveImageWithText}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveImageWithText": "Save Image (+ final prompt)"}
