from typing import TypedDict, TypeAlias

ReportItem: TypeAlias = str | list[dict[str, ReportItem]]
Report: TypeAlias = dict[str, ReportItem]

class WttrReport(TypedDict):
	current_condition: list[Report]
	nearest_area: list[Report]
	request: ReportItem
	weather: list[Report]