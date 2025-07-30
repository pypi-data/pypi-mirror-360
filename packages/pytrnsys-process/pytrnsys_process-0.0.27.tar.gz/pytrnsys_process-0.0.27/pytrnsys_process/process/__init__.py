from pytrnsys_process.process.data_structures import (
    Simulation,
    SimulationsData,
)
from pytrnsys_process.process.file_type_detector import (
    get_file_type_using_file_content,
    get_file_type_using_file_name,
    has_pattern,
)

from pytrnsys_process.process.process_batch import (
    process_single_simulation,
    process_whole_result_set,
    process_whole_result_set_parallel,
    do_comparison,
)

__all__ = [
    "Simulation",
    "SimulationsData",
    "get_file_type_using_file_content",
    "get_file_type_using_file_name",
    "has_pattern",
    "process_single_simulation",
    "process_whole_result_set",
    "process_whole_result_set_parallel",
    "do_comparison",
]
