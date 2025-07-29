from .core import AssetTool
from .util import in_folder, relative_path

from pathlib import Path
from typing import List, Dict

import re
import os
import sys
import zlib
import shutil

import fnmatch

class CommonAssetTool(AssetTool):
    def __init__(self):
        super().__init__()

    def build_cmd(self, input_file: Path) -> str:
        return f"@$(PYTHON) -m AssetForge.tool {self.tool_name()} {str(os.path.relpath(input_file, self.build_folder))} {str(os.path.relpath(self.input_folder, self.build_folder))} {str(self.output_folder.relative_to(self.build_folder))} >> log.txt 2>&1"


class LinkingTool(CommonAssetTool):
    """
    Simply takes every file in an input folder and makes an output file that just links the input file.
    
    The output file will be placed in the output folder preserving the relative path from the input folder.
    For example, if the input file is `imgs/penguin.png` (with `imgs/penguin.png` relative to the input folder),
    the output file will be created as `<output_folder>/imgs/penguin.png`.
    """
    def __init__(self, pattern=r".*"):
        super().__init__() 
        self.pattern = pattern
    
    def tool_name(self):
        return "LinkingTool"
    
    def check_match(self, file_path: Path) -> bool:
        return in_folder(file_path, self.input_folder) and bool(re.match(self.pattern, str(file_path), re.IGNORECASE))

    def define_dependencies(self, file_path: Path) -> List[Path]:
        return [] # No additional dependencies for linking.

    def define_outputs(self, file_path: Path) -> List[Path]:
        return [self.output_folder / file_path.resolve().relative_to(self.input_folder)] # Return the same relative path so that the output file in the output folder will have the same structure.
    
    @staticmethod
    def build(file_path: Path, input_folder: Path, output_folder: Path) -> None:
        """
        Creates a symbolic link in the output folder that points to the input file.
        
        Assumes that the current working directory is the input folder.
        """
        input_file = file_path
        output_file = output_folder / file_path.resolve().relative_to(input_folder)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.exists():
            os.remove(output_file)

        try:
            output_file.symlink_to(input_file.resolve())
            print(f"Created symlink: {output_file} -> {input_file.resolve()}")
        except Exception as e:
            print(f"Error creating symlink for {input_file} at {output_file}: {e}")

class CopyingTool(CommonAssetTool):
    """
    todo
    """
    def __init__(self, pattern=r".*"):
        super().__init__() 
        self.pattern = pattern
    
    def tool_name(self):
        return "CopyingTool"
    
    def check_match(self, file_path: Path) -> bool:
        return in_folder(file_path, self.input_folder) and bool(re.match(self.pattern, str(file_path), re.IGNORECASE))

    def define_dependencies(self, file_path: Path) -> List[Path]:
        return [] # No additional dependencies for linking.

    def define_outputs(self, file_path: Path) -> List[Path]:
        return [self.output_folder / file_path.resolve().relative_to(self.input_folder)] # Return the same relative path so that the output file in the output folder will have the same structure.

    @staticmethod
    def build(file_path: Path, input_folder: Path, output_folder: Path) -> None:
        """
        Creates a symbolic link in the output folder that points to the input file.
        
        Assumes that the current working directory is the input folder.
        """
        input_file = file_path
        output_file = output_folder / file_path.resolve().relative_to(input_folder)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(input_file, output_file)

class CompressionTool(CommonAssetTool):
    """
    todo
    """
    def tool_name(self):
        return "CompressionTool"
    
    def check_match(self, file_path: Path) -> bool:
        return file_path.suffixes.count(".bin") == 1 and file_path.suffixes[-1] == ".bin"

    def define_dependencies(self, file_path: Path) -> List[Path]:
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        # Return the same relative path so that the output file in the output folder will have the same structure.
        return [self.output_folder / relative_path(file_path, [self.input_folder, self.output_folder]).with_name(file_path.name + ".z")]
    
    @staticmethod
    def build(file_path: Path, input_folder: Path, output_folder: Path) -> None:
        input_path = file_path
        output_path = output_folder / relative_path(file_path, [input_folder, output_folder]).with_name(file_path.name + ".z")

        with open(input_path, "rb") as fin:
            data = fin.read()
        
        compressed_data = zlib.compress(data)
    
        # Write the compressed data to a file
        with open(output_path, "wb") as fout:
            fout.write(compressed_data)

# class IgnoreItToolDecorator(AssetTool):
#     def __init__(self, tool : AssetTool, ignore_it_name : str):
#         self.tool = tool
#         self.ignore_it_name = ignore_it_name
    
#     def tool_name(self):
#         return self.tool.tool_name()
    
#     def matches_ignore_pattern(self, file: Path, pattern: str, base: Path) -> bool:
#         """
#         Check if a file matches an ignore pattern.
#         This simplified version does the following:
#           - It computes the relative path of the file to the base directory (where the ignore file is located).
#           - If the pattern starts with '/', we treat it as relative to that base.
#           - Otherwise, the pattern is matched against the entire relative path or just the file name.
#         """
#         try:
#             rel_path = file.relative_to(base)
#         except ValueError:
#             # file is not under the base directory, so it doesn't match this ignore rule.
#             return False

#         # Normalize to posix path (using forward slashes) for consistent matching
#         rel_str = rel_path.as_posix()

#         if pattern.startswith('/'):
#             # Remove the leading slash and match only against the relative path from the base directory.
#             pattern = pattern[1:]
#             return fnmatch.fnmatch(rel_str, pattern)
#         else:
#             # For simplicity, check if the pattern matches the full relative path
#             # or the file name itself.
#             return fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(file.name, pattern)
    
#     def start(self, input_folder: Path, output_folder: Path):
#         super().start(input_folder, output_folder)

#         # go through all of the files in input folder and find all files with the file name .<self.name> ie if name="gitignore" look for files .gitignore
#         self.whitelist = set()

#         for file in input_folder.rglob("*"):
#             if file.is_file() and file.name != f".{self.ignore_it_name}":
#                 self.whitelist.add(file)
        
#         for dotfile in input_folder.rglob("*"):
#             if dotfile.is_file() and dotfile.name == f".{self.ignore_it_name}":
#                 base_dir = dotfile.parent
#                 with dotfile.open("r") as f:
#                     for line in f:
#                         line = line.strip()
#                         if not line or line.startswith("#"):
#                             continue
                        
#                         blacklist = set()

#                         for wfile in self.whitelist:
#                             if self.matches_ignore_pattern(wfile, line, base_dir):
#                                 blacklist.add(wfile)
                        
#                         for bfile in blacklist:
#                             self.whitelist.remove(bfile)

#         self.tool.start(input_folder, output_folder)

#     def check_match(self, file_path: Path) -> bool:
#         if (in_folder(file_path, self.input_folder)):
#             if file_path in self.whitelist:
#                 return self.tool.check_match(file_path)
#             else:
#                 return False
#         else:
#             return self.tool.check_match(file_path)

#     def define_dependencies(self, file_path: Path) -> List[Path]:
#         return self.tool.define_dependencies(file_path)

#     def define_outputs(self, file_path: Path) -> List[Path]:
#         return self.tool.define_outputs(file_path)
    
#     @staticmethod
#     def build(file_path: Path, input_folder: Path, output_folder: Path) -> None:
#         return self.tool.build(file_path, input_folder, output_folder)
    
def main_func(tools: List[AssetTool]):
    tools = {tool.tool_name() : tool for tool in tools}

    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <tool_name> <input_file> <input_folder> <output_folder>")
        print("Available tools:")
        for tool in tools.values():
            print(f" - {tool.tool_name()}")
        sys.exit(1)

    tool_name = sys.argv[1]
    input_file = Path(sys.argv[2]).resolve()
    input_folder = Path(sys.argv[3]).resolve()
    output_folder = Path(sys.argv[4]).resolve()

    tool = tools[tool_name]
    tool.build(input_file, input_folder, output_folder)
