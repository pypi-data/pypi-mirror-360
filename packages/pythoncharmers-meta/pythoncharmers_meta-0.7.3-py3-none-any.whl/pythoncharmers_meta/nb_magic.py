"""
An IPython extension that (currently) registers a single "magic": %nb

This grabs a few cells from a notebook on the filesystem, defaulting to the
most recently modified notebook in the highest-numbered ~/Trainer_XYZ/ folder.

For help on the magic, run:

    %nb?

"""

import warnings
from pathlib import Path
from typing import Iterable, Optional

from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magics.code import extract_code_ranges
from IPython.core.error import UsageError
import nbformat


def extract_code_ranges_inclusive(ranges_str: str) -> Iterable[tuple[int, int]]:
    """Turn a string of ranges, inclusive of the endpoints, into 2-tuples of
    (start, stop) suitable for use with range(start, stop).

    Examples
    --------
    >>> list(extract_code_ranges_inclusive("5-10 2"))
    [(5, 11), (2, 3)]

    >>> list(
    ...     tz.concat((range(start, stop) for (start, stop) in extract_code_ranges_inclusive('3-4 6 3')))
    ... )

    [3, 4, 6, 3]
    """
    return ((start + 1, stop + 1) for (start, stop) in extract_code_ranges(ranges_str))


def get_cell_nums(ranges_str: str) -> Iterable[int]:
    """
    Yields cell numbers specified in the given ranges_str string, assuming the
    ranges are specified inclusive of the endpoint.

    Example:
    >>> list(get_cell_nums('5-6 2 12'))
    [5, 6, 2, 12]
    """
    for start, stop in extract_code_ranges_inclusive(ranges_str):
        yield from range(start, stop)


def get_cell_input(cell_number: int, nb):
    "Return input for the given cell in the given notebook"
    if not isinstance(cell_number, int):
        raise ValueError("pass an integer cell number")
    for cell in nb["cells"]:
        if "execution_count" in cell and cell["execution_count"] == cell_number:
            return cell["source"]


def paths_sorted_by_mtime(paths: Iterable[Path], ascending: bool = True) -> list[Path]:
    """
    Return a sorted list of the given Path objects sorted by
    modification time.
    """
    mtimes = {path: path.stat().st_mtime for path in paths}
    return sorted(paths, key=mtimes.get)


def latest_trainer_path() -> Path:
    """
    Look for the highest-numbered ~/Trainer_XYZ folder and return it as a
    Path object.
    """
    # If there's just a "Trainer" folder by itself, don't assume it's the
    # current one, because this was our convention with earlier courses.
    # Participants who previously did an old course would otherwise get an
    # old trainer transcript if they use %nb
    # naked_trainer_folder = Path('~/Trainer').expanduser()
    # if naked_trainer_folder.exists():
    #     return naked_trainer_folder

    # Sort alphanumerically and return the last one.
    trainer_paths = [p for p in Path("~").expanduser().glob("Trainer_*") if p.is_dir()]
    try:
        latest_trainer_path = sorted(trainer_paths, key=course_num_from_trainer_path)[
            -1
        ]
        return latest_trainer_path
    except Exception:
        cwd = Path.cwd()
        warnings.warn(
            f"No ~/Trainer_* folders found. Using current directory {cwd}",
            RuntimeWarning,
        )
        return cwd


def latest_notebook_file(folder_path: Path) -> Path:
    """
    Return the most recently modified .ipynb file in the given folder
    path.
    """
    notebook_files = list(folder_path.glob("*.ipynb"))
    try:
        path = paths_sorted_by_mtime(notebook_files)[-1]
    except Exception:
        raise OSError(f"Cannot find any .ipynb files in {folder_path}")
    return path


def course_num_from_trainer_path(trainer_path: Path) -> int:
    """
    Returns a course number like 612 as an integer
    from a Trainer path like `Path('/home/jovyan/Trainer_612')`

    If the string after the _ (e.g. "612") is not possible to convert to a
    number, returns 0.
    """
    try:
        return int(trainer_path.name.split("_")[1])
    except Exception:
        return 0


@magics_class
class NotebookMagic(Magics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notebook_path = latest_trainer_path()

        # If notebook_file_override is set, use this notebook file for
        # %nb. If notebook_file_override is None, use the latest notebook
        # in the notebook_path (given by %nbpath):
        self.notebook_file_override = None

    @line_magic
    def nbpath(self, arg_s: str) -> Optional[str]:
        """
        Usage:
            %nbpath
            Show the folder path being queried for %nb

            %nbpath ~/Trainer_614
            Set ~/Trainer_614 as the folder to query for %nb

            %nbpath --reset
            Reset the folder being queried for %nb to the highest-numbered ~/Trainer_XYZ folder.
        """
        if arg_s == "":
            return str(self.notebook_path)
        elif "--reset" in arg_s:
            self.notebook_path = latest_trainer_path()
        else:
            new_notebook_path = Path(arg_s).expanduser().resolve()
            if new_notebook_path.exists():
                self.notebook_path = new_notebook_path
            else:
                raise UsageError(f"path {new_notebook_path} does not exist")

    @line_magic
    def nbfile(self, arg_s: str) -> Optional[str]:
        """
        Usage:
            %nbfile
            Show the file in %nbpath being queried for %nb

            %nbfile "Training day 1.ipynb"
            Set the notebook file in %nbpath to be queried for %nb

            %nbfile --reset
            Reset the notebook file to the most recently modified
            .ipynb file in the directory given by %nbpath.
        """
        if arg_s == "":
            if self.notebook_file_override is not None:
                print(f"The default notebook is set to {self.notebook_file_override}")
                return self.notebook_file_override
            else:
                my_notebook_file = latest_notebook_file(self.notebook_path)
                print(
                    f"No default notebook is set. Using the most recently modified file in %nbpath. This is currently {my_notebook_file}"
                )
                return str(my_notebook_file)
        elif "--reset" in arg_s:
            self.notebook_file_override = None
            print(
                "The default notebook has been unset. The most recently modified .ipynb file will be used in the directory given by %nbpath."
            )
            return None
        else:
            # Strip off any quotes at the start or end of the filename
            # and expand ~ to the user's home folder.
            # Then resolve any symlinks to get an absolute path.
            filepath = Path(arg_s.strip('"').strip("'")).expanduser().resolve()
            if not filepath.exists():
                raise Exception(f"notebook {filepath} does not exist")
            else:
                # Interpret it as a path or filename relative to %nbpath
                filepath = self.notebook_path / filepath
            self.notebook_file_override = filepath
            print(f"Set default notebook file to {self.notebook_file_override}")

    @line_magic
    def nb(self, arg_s):
        """Load code into the current frontend.
        Usage:

          %nb n1-n2 n3-n4 n5 ...

        or:

          %nb -f ipynb_filename n1-n2 n3-n4 n5 ...

          where `ipynb_filename` is a filename of a Jupyter notebook

        Ranges:

          Ranges are space-separated and inclusive of the endpoint.

          Example: 123 126 131-133

          This gives the contents of these code cells: 123, 126, 131, 132, 133.

        Optional arguments:

          -f ipynb_filename: the filename of a Jupyter notebook (optionally
              omitting the .ipynb extension). Default is the most recently
              modified .ipynb file in the highest-numbered ~/Trainer_XYZ/
              folder.

          -v [notebook_version]: default is 4
        """
        opts, args = self.parse_options(arg_s, "v:f:", mode="list")
        # for i, arg in enumerate(args):
        #     print(f'args[{i}] is {args[i]}')

        if "f" in opts:
            fname = opts["f"]
            if not fname.endswith(".ipynb"):
                fname += ".ipynb"
            path = Path(fname)
            if not path.exists():
                raise UsageError(f"File {path.absolute()} does not exist")
        else:
            # If there's a default set, use it:
            if self.notebook_file_override is not None:
                my_notebook_file = self.notebook_file_override
            else:
                try:
                    my_notebook_file = latest_notebook_file(self.notebook_path)
                except Exception:
                    raise UsageError(
                        "No default notebook set (%nbfile); no notebook filename specified (-f option); and cannot infer it."
                    )

        if "v" in opts:
            try:
                version = int(opts["v"])
            except ValueError:
                warnings.warn(
                    "Cannot interpret version number as an integer. Defaulting to version 4."
                )
                version = 4
        else:
            version = 4

        codefrom = " ".join(args)

        # Load notebook into a dict
        nb = nbformat.read(my_notebook_file, as_version=version)

        # Get cell numbers
        cellnums = list(get_cell_nums(codefrom))

        # Get cell contents
        contents = [get_cell_input(cellnum, nb) for cellnum in cellnums]

        # Remove Nones
        contents = [c for c in contents if c is not None]

        # print(*contents, sep='\n\n')
        contents = "\n\n".join(contents)
        contents = "# %nb {}\n".format(arg_s) + contents

        self.shell.set_next_input(contents, replace=True)


# In order to actually use these magics, you must register them with a
# running IPython. See load_ipython_extension() in __init__.py.

