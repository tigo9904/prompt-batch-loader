import os
import folder_paths

class PromptBatchLoader:
    _execution_state = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upload": ("UPLOAD",),
                "read_mode": (["sequential", "specific_line", "all"], {"default": "sequential"}),
                "line_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                "control_after_generate": (["increment", "fixed", "random", "loop"], {"default": "increment"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset_counter": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("prompt", "current_line", "total_lines", "status")
    FUNCTION = "read_text"
    CATEGORY = "Custom/Text IO"

    def read_text(self, upload, read_mode, line_index, control_after_generate, seed, reset_counter):
        try:
            if upload is None:
                return ("ERROR: Please upload a .txt file using the upload button", 0, 0, "No file uploaded")

            if isinstance(upload, dict) and 'name' in upload:
                file_name = upload['name']
            else:
                file_name = str(upload)

            file_id = f"{file_name}_{hash(str(upload))}"

            if reset_counter:
                self._execution_state[file_id] = {"current_line": 0, "total_executions": 0}

            if file_id not in self._execution_state:
                self._execution_state[file_id] = {"current_line": 0, "total_executions": 0}

            input_dir = folder_paths.get_input_directory()
            file_path = os.path.join(input_dir, file_name)

            if not os.path.exists(file_path):
                return (f"ERROR: Uploaded file not found: {file_name}", 0, 0, "File not found")

            if not file_name.lower().endswith(('.txt', '.text')):
                return (f"ERROR: Please upload a .txt file. Current file: {file_name}", 0, 0, "Wrong file type")

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                file_content = [line.strip() for line in lines if line.strip()]
                total_lines = len(file_content)

            if not file_content:
                return ("ERROR: Uploaded file is empty or contains no valid text", 0, 0, "Empty file")

            if read_mode == "all":
                return ("\n".join(file_content), 0, total_lines, f"All {total_lines} lines")

            elif read_mode == "specific_line":
                if 0 <= line_index < total_lines:
                    return (file_content[line_index], line_index, total_lines, f"Line {line_index + 1}/{total_lines}")
                else:
                    return (f"ERROR: Line {line_index + 1} out of range (1-{total_lines})", 0, total_lines, "Out of range")

            elif read_mode == "sequential":
                state = self._execution_state[file_id]

                if control_after_generate == "increment":
                    current_index = state["current_line"] % total_lines
                    state["current_line"] = (state["current_line"] + 1) % total_lines

                elif control_after_generate == "loop":
                    current_index = state["current_line"] % total_lines
                    state["current_line"] = (state["current_line"] + 1) % total_lines

                elif control_after_generate == "random":
                    import random
                    random.seed(seed + state["total_executions"])
                    current_index = random.randint(0, total_lines - 1)

                else:
                    current_index = line_index % total_lines

                state["total_executions"] += 1
                selected_prompt = file_content[current_index]

                status = f"Prompt {current_index + 1}/{total_lines}"
                if control_after_generate == "increment":
                    next_line = (current_index + 1) % total_lines
                    status += f" (Next: {next_line + 1})"

                return (selected_prompt, current_index, total_lines, status)

        except UnicodeDecodeError:
            return ("ERROR: Cannot read file. Please ensure it's a valid UTF-8 text file.", 0, 0, "Encoding error")
        except Exception as e:
            return (f"ERROR: {str(e)}", 0, 0, "Error")

NODE_CLASS_MAPPINGS = {
    "PromptBatchLoader": PromptBatchLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptBatchLoader": "Prompt Batch Loader",
}
