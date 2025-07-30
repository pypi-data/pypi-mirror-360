from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Self
from .api import SeedAudience, CustomAudience
from .audiences import AudienceType
from .participant import Participant
class FilterOperator(str, Enum):
    """
    Enum representing the filter operations.

    Members:
        - CONTAINS_ANY: At least one of the values must be present.
        - CONTAINS_NONE: None of the values can be present.
        - CONTAINS_ALL: All of the values must be present.
        - EMPTY: The attribute must be empty.
        - NOT_EMPTY: The attribute must not be empty.
    """
    CONTAINS_ANY = "CONTAINS_ANY_OF"
    CONTAINS_NONE = "CONTAINS_NONE_OF"
    CONTAINS_ALL = "CONTAINS_ALL_OF"
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT_EMPTY"


class Filter:
    """
    Class representing a filter.
    """
    def __init__(
        self, *, attribute: str, values: List[str], operator: FilterOperator
    ) -> None:
        """
        Initialize a filter.

        **Parameters**:
        - `attribute`: The attribute to filter on
        - `values`: The values to filter on
        - `operator`: The operator to use for the filter
        """
        self.attribute = attribute
        self.values = values
        self.operator = operator

    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary.

        **Returns**:
        - The dictionary representation of the filter
        """
        return {
            "operator": self.operator.value,
            "attribute": self.attribute,
            "values": self.values,
        }


class MatchOperator(str, Enum):
    """
    Enum representing the match operations.

    Members:
        - MATCH_ALL: All filter criteria must be satisfied.
        - MATCH_ANY: Any filter criteria may be satisfied.
    """
    # All filter criteria must be satisfied.
    MATCH_ALL = "AND"
    # Any filter criteria may be satisfied.
    MATCH_ANY = "OR"


class AudienceFilters:
    """
    Class representing the filters for an audience.
    """
    def __init__(
        self,
        *,
        filters: List[Filter],
        operator: MatchOperator,
    ) -> None:
        """
        Initialize an AudienceFilters instance.

        **Parameters**:
        - `filters`: The list of filters to apply
        - `operator`: The operator to use for the filters
        """
        self.filters = filters
        self.operator = operator

    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the filters to a dictionary.

        **Returns**:
        - The dictionary representation of the filters
        """
        return {
            "booleanOp": self.operator.value,
            "filters": [f.as_dict() for f in self.filters],
        }


class CombineOperator(str, Enum):
    """
    Enum representing the operations for combining audiences.

    Members:
        - INTERSECT: Users in both audiences.
        - UNION: All users.
        - DIFF: Users in first audience only.
    """
    # Users in both audiences.
    INTERSECT = "INTERSECT"
    # All users.
    UNION = "UNION"
    # Users in first audience only.
    DIFF = "DIFF"


class AudienceCombinator:
    def __init__(
        self,
        *,
        operator: CombineOperator,
        source_audience: AudienceType,
        filters: Optional[AudienceFilters] = None,
    ) -> None:
        """
        Initialize an AudienceCombinator instance.

        **Parameters**:
        - `operator`: The operator used to combine audiences
        - `source_audience`: The source audience to combine
        - `filters`: Optional filters to apply to the source audience
        """
        self.operator = operator
        self.source_audience = source_audience
        self.filters = filters

    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the audience combinator to a dictionary.

        **Returns**:
        - The dictionary representation of the audience combinator
        """
        return {
            "operator": self.operator.value,
            "sourceRef": self.source_audience.model_dump(mode="json"),
            "filters": self.filters.as_dict() if self.filters else None,
        }


class RuleBasedAudienceDefinition:
    """
    Class representing the definition of a rule-based audience.
    """

    def __init__(
        self,
        *,
        name: str,
        source_audience: AudienceType,
        filters: Optional[AudienceFilters] = None,
        combinators: Optional[List[AudienceCombinator]] = None,
        shared_with: Optional[List[Participant]] = None,
    ) -> None:
        """
        Initialize a rule-based audience definition.

        **Parameters**:
        - `name`: Name of the rule-based audience
        - `source_audience`: The source audience to build from
        - `filters`: Optional filters to apply to the audience
        - `combinators`: Optional combinators for combining multiple audiences
        - `shared_with`: Optional list of participant groups to share with
        """
        self.name = name
        self.source_audience = source_audience
        self.filters = filters
        self.combinators = combinators
        self.kind = "RULE_BASED"
        self.shared_with = [participant.id for participant in shared_with]

class RuleBasedAudienceBuilder:
    """
    Builder for constructing rule-based audience definitions.
    """

    def __init__(
        self,
        *,
        name: str,
        source_audience: AudienceType,
    ) -> None:
        """
        Initialise the rule-based audience builder.

        **Parameters**:
        - `name`: Name of the rule-based audience.
        - `source_audience`: The source audience that the rule-based audience will be built from.
        """
        self.name = name
        self.source_audience = source_audience
        self.filters = None
        self.combinators = None
        self.shared_with = []

    def with_share_with_participants(self, participants: List[Participant]) -> Self:
        """
        Make the rule-based audience available to the given participants.

        **Parameters**:
        - `participants`: The participants to share the rule-based audience with

        **Returns**:
        - The updated rule-based audience builder
        """
        self.shared_with = participants
        return self

    def with_filters(self, filters: AudienceFilters) -> Self:
        """
        Set the filters to be applied to the source audience.

        **Parameters**:
        - `filters`: Filters to be applied to the source audience.

        **Returns**:
        - The updated rule-based audience builder
        """
        self.filters = filters
        return self

    def with_combinator(self, combinators: List[AudienceCombinator]) -> Self:
        """
        Set the combinators to be applied to the audiences.
        This defines how multiple audiences can be combined.

        **Parameters**:
        - `combinators`: The list of combinators used to combine audiences.

        **Returns**:
        - The updated rule-based audience builder
        """
        self.combinators = combinators
        return self

    def build(self) -> RuleBasedAudienceDefinition:
        """
        Build the rule-based audience definition.

        **Returns**:
        - The rule-based audience definition
        """
        return RuleBasedAudienceDefinition(
            name=self.name,
            source_audience=self.source_audience,
            filters=self.filters,
            combinators=self.combinators,
            shared_with=self.shared_with,
        )


class AudienceCombinatorBuilder:
    """
    Builder for constructing an `AudienceCombinator`.
    """

    def __init__(
        self,
        *,
        operator: CombineOperator,
        source_audience: Union[SeedAudience, CustomAudience],
    ) -> None:
        """
        Initialise the audience combinator builder.

        **Parameters**:
        - `operator`: The operator used to combine audiences.
        - `source_audience`: The source audience to combine with.
        """
        self.operator = operator
        self.source_audience = source_audience
        self.filters = None

    def with_filters(self, filters: AudienceFilters) -> Self:
        """
        Set the filters to be applied to the source audience.

        **Parameters**:
        - `filters`: Filters to be applied to the source audience.

        **Returns**:
        - The updated audience combinator builder
        """
        self.filters = filters
        return self

    def build(self) -> AudienceCombinator:
        """
        Build the audience combinator.

        **Returns**:
        - The audience combinator
        """
        return AudienceCombinator(
            operator=self.operator,
            source_audience=self.source_audience,
            filters=self.filters,
        )
