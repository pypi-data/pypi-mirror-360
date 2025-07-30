from typing import Any, Dict, List
from typing_extensions import Self
import json


class LalAudienceStatistics:
    """
    Class representing the statistics of a given lookalike audience.
    """

    def __init__(
        self,
        auc: float,
        fpr: List[float],
        tpr: List[float],
    ) -> None:
        """
        Initialize an instance of LalAudienceStatistics.

        **Parameters**:
        - `auc`: The area under the ROC curve
        - `fpr`: The list of false positive rates (in order of decreasing discrimination threshold)
        - `tpr`: The list of true positive rates (in order of decreasing discrimination threshold)
        """
        self.auc = auc
        self.fpr = fpr
        self.tpr = tpr

    def model_dump(self) -> Dict[str, Any]:
        """
        Convert the instance to a dictionary following pydantic model_dump convention.

        **Returns**:
        - Dictionary representation of the statistics
        """
        return {
            "quality": {
                "roc_curve": {"auc": self.auc, "fpr": self.fpr, "tpr": self.tpr}
            }
        }

    def model_dump_json(self, indent: int = None) -> str:
        """
        Convert the instance to a JSON string following pydantic model_dump_json convention.

        **Parameters**:
        - `indent`: Number of spaces for indentation in the JSON output

        **Returns**:
        - JSON string representation of the statistics
        """
        return json.dumps(self.model_dump(), indent=indent)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Self:
        """
        Create an instance from a dictionary.

        **Parameters**:
        - `d`: Dictionary containing the statistics data

        **Returns**:
        - New LalAudienceStatistics instance
        """
        roc_curve = d["quality"]["roc_curve"]
        return cls(
            auc=roc_curve["auc"],
            fpr=roc_curve["fpr"],
            tpr=roc_curve["tpr"],
        )
