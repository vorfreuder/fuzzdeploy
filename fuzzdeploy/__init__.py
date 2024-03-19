import os

from .BugFoundByTimeAnalysis import BugFoundByTimeAnalysis
from .Builder import Builder
from .CasrTriageAnalysis import CasrTriageAnalysis
from .CoverageAnalysis import CoverageAnalysis
from .Deployer import Deployer
from .EdgeAnalysis import EdgeAnalysis
from .EdgeOverTimeAnalysis import EdgeOverTimeAnalysis
from .ExcelManager import ExcelManager
from .JointAnalysis import JointAnalysis
from .Maker import Maker
from .StateAnalysis import StateAnalysis
from .utility import console

console.print(
    "[bold]fuzzdeploy developed by [yellow]vorfreuder[/yellow]@https://github.com/vorfreuder[/bold]"
)
invalid_folders = []
directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
for item in ["fuzzers", "targets"]:
    for folder in os.listdir(os.path.join(directory, item)):
        if not folder.islower():
            invalid_folders.append((item, folder))
if invalid_folders:
    console.print(f"[red]Invalid folder name found:")
    for item, folder in invalid_folders:
        console.print(f"[red]   {item}/{folder}")
    console.print(
        f"[red]Please follow the naming convention for docker images, e.g. lowercase."
    )
