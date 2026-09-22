import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from config.config import get_logger

logger = get_logger(__name__)


class ParquetAnalytics:
    """Analytics data access over the latest Gold Parquet batch per dataset."""

    DATASETS = ("students", "attendance", "academics", "events", "transportation", "facilities")

    def __init__(self, gold_root: str | None = None):
        self.gold_root = Path(gold_root or os.getenv("SMART_CAMPUS_GOLD_ROOT", "data/lake/gold"))
        if not self.gold_root.exists() or not any(self.gold_root.rglob("*.parquet")):
            raise FileNotFoundError(f"Gold Parquet root not found: {self.gold_root}")
        self._cache: dict[str, pd.DataFrame] = {}

    def close(self) -> None:
        self._cache.clear()

    def _load(self, dataset: str) -> pd.DataFrame:
        if dataset in self._cache:
            return self._cache[dataset].copy()
        path = self.gold_root / f"dataset={dataset}"
        if not path.exists():
            raise FileNotFoundError(f"Gold Parquet dataset not found: {path}")
        frame = pd.read_parquet(path)
        if frame.empty:
            self._cache[dataset] = frame
            return frame.copy()
        if "processing_timestamp" in frame.columns:
            timestamps = pd.to_datetime(frame["processing_timestamp"], errors="coerce")
            latest = timestamps.max()
            if pd.notna(latest):
                frame = frame.loc[timestamps == latest].copy()
        self._cache[dataset] = frame
        return frame.copy()

    @staticmethod
    def _records(frame: pd.DataFrame) -> List[Dict[str, Any]]:
        cleaned = frame.astype(object).where(pd.notna(frame), None)
        return cleaned.to_dict(orient="records")

    @staticmethod
    def _rounded(value: Any, digits: int = 2) -> Any:
        return round(float(value), digits) if pd.notna(value) else 0

    def get_total_students(self) -> int:
        return len(self._load("students"))

    def get_students_by_department(self) -> List[Dict]:
        frame = self._load("students")
        frame = frame[frame["department"] != "Unknown"]
        return self._records(frame.groupby("department", as_index=False).size().rename(columns={"size": "count"}).sort_values("count", ascending=False))

    def get_student_details(self, limit: int = 10) -> List[Dict]:
        columns = ["student_id", "name", "email", "age", "gender", "department", "status"]
        return self._records(self._load("students").loc[:, [c for c in columns if c in self._load("students").columns]].head(limit))

    def get_student_records(self, department: str | None = None, year: int | None = None, limit: int = 100) -> List[Dict]:
        students = self._load("students").copy()
        academics = self._load("academics").groupby("student_id", as_index=False).agg(avg_gpa=("gpa", "mean"))
        students = students.merge(academics, on="student_id", how="left")
        students["year"] = students["age"].map(lambda age: "Year 1" if 18 <= age <= 19 else "Year 2" if 20 <= age <= 21 else "Year 3" if 22 <= age <= 23 else "Year 4")
        if department:
            students = students[students["department"] == department]
        if year:
            students = students[students["year"] == f"Year {year}"]
        return self._records(students.sort_values("student_id").head(limit))

    def get_students_by_year(self) -> List[Dict]:
        frame = self._load("students").copy()
        frame["year"] = frame["age"].map(lambda age: "Freshman" if 18 <= age <= 19 else "Sophomore" if 20 <= age <= 21 else "Junior" if 22 <= age <= 23 else "Senior")
        return self._records(frame.groupby("year", as_index=False).size().rename(columns={"size": "count"}).sort_values("year"))

    def get_students_count_by_age_group(self) -> List[Dict]:
        frame = self._load("students")
        return self._records(frame[frame["age_group"] != "Unknown"].groupby("age_group", as_index=False).size().rename(columns={"size": "count"}).sort_values("age_group"))

    def get_students_by_gender(self) -> List[Dict]:
        frame = self._load("students")
        frame = frame[frame["gender"].notna() & (frame["gender"] != "Unknown")]
        return self._records(frame.groupby("gender", as_index=False).size().rename(columns={"size": "count"}).sort_values("count", ascending=False))

    def get_student_status_distribution(self) -> List[Dict]:
        frame = self._load("students")
        return self._records(frame.groupby("status", as_index=False).size().rename(columns={"size": "count"}).sort_values("count", ascending=False))

    def get_attendance_statistics(self) -> Dict:
        frame = self._load("attendance")
        return {"total_students": int(frame["student_id"].nunique()), "avg_attendance": self._rounded(frame["attendance_percentage"].mean()), "min_attendance": frame["attendance_percentage"].min(), "max_attendance": frame["attendance_percentage"].max()}

    def get_attendance_by_status(self) -> List[Dict]:
        frame = self._load("attendance")
        result = frame.groupby("status", as_index=False).agg(count=("status", "size"), avg_attendance=("attendance_percentage", "mean"))
        result["avg_attendance"] = result["avg_attendance"].round(2)
        return self._records(result.sort_values("count", ascending=False))

    def _attendance_by_student(self) -> pd.DataFrame:
        students = self._load("students")[["student_id", "name", "email", "department"]]
        attendance = self._load("attendance")
        result = attendance.groupby("student_id", as_index=False).agg(avg_attendance=("attendance_percentage", "mean"), sessions_tracked=("date", "nunique"))
        return result.merge(students, on="student_id", how="inner")

    def get_low_attendance_students(self, threshold: float = 75.0) -> List[Dict]:
        result = self._attendance_by_student()
        return self._records(result[result["avg_attendance"] < threshold].sort_values("avg_attendance"))

    def get_attendance_by_department(self) -> List[Dict]:
        students = self._load("students")[["student_id", "department"]]
        attendance = self._load("attendance").merge(students, on="student_id", how="left")
        result = attendance[attendance["department"] != "Unknown"].groupby("department", as_index=False).agg(students=("student_id", "nunique"), avg_attendance=("attendance_percentage", "mean"), total_sessions=("date", "nunique"))
        result["avg_attendance"] = result["avg_attendance"].round(2)
        return self._records(result.sort_values("avg_attendance", ascending=False))

    def get_department_low_attendance(self, department: str, limit: int = 100) -> List[Dict]:
        result = self._attendance_by_student()
        return self._records(result[result["department"] == department].sort_values("avg_attendance").head(limit))

    def get_attendance_trends(self, limit: int = 30) -> List[Dict]:
        frame = self._load("attendance")
        result = frame.groupby("date", as_index=False).agg(students_present=("student_id", "nunique"), avg_attendance=("attendance_percentage", "mean"), present_count=("status", lambda values: (values.str.lower() == "present").sum()), absent_count=("status", lambda values: (values.str.lower() == "absent").sum()))
        result["avg_attendance"] = result["avg_attendance"].round(2)
        return self._records(result.sort_values("date", ascending=False).head(limit))

    def get_chronic_absentees(self, threshold: float = 50.0) -> List[Dict]:
        result = self._attendance_by_student()
        return self._records(result[result["avg_attendance"] < threshold].sort_values("avg_attendance"))

    def get_academic_statistics(self) -> Dict:
        frame = self._load("academics")
        return {"total_students": int(frame["student_id"].nunique()), "avg_gpa": self._rounded(frame["gpa"].mean()), "min_gpa": frame["gpa"].min(), "max_gpa": frame["gpa"].max()}

    def get_grade_distribution(self) -> List[Dict]:
        frame = self._load("academics").dropna(subset=["grade"])
        return self._records(frame.groupby("grade", as_index=False).size().rename(columns={"size": "count"}).sort_values("grade"))

    def _academic_by_student(self) -> pd.DataFrame:
        academics = self._load("academics")
        students = self._load("students")[["student_id", "name", "email", "department"]]
        result = academics.groupby("student_id", as_index=False).agg(avg_gpa=("gpa", "mean"), courses=("course_id", "count"), failing_grades=("grade", lambda values: values.isin(["D", "F"]).sum()))
        return result.merge(students, on="student_id", how="inner")

    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        return self._records(self._academic_by_student().sort_values("avg_gpa", ascending=False).head(limit))

    def get_department_top_performers(self, department: str, limit: int = 100) -> List[Dict]:
        result = self._academic_by_student()
        return self._records(result[result["department"] == department].sort_values("avg_gpa", ascending=False).head(limit))

    def get_struggling_students(self, gpa_threshold: float = 2.0) -> List[Dict]:
        return self._records(self._academic_by_student().query("avg_gpa < @gpa_threshold").sort_values("avg_gpa"))

    def get_academics_by_department(self) -> List[Dict]:
        students = self._load("students")[["student_id", "department"]]
        frame = self._load("academics").merge(students, on="student_id", how="left")
        result = frame[frame["department"] != "Unknown"].groupby("department", as_index=False).agg(students=("student_id", "nunique"), avg_gpa=("gpa", "mean"), min_gpa=("gpa", "min"), max_gpa=("gpa", "max"), total_courses=("course_id", "count"))
        for column in ["avg_gpa", "min_gpa", "max_gpa"]:
            result[column] = result[column].round(2)
        return self._records(result.sort_values("avg_gpa", ascending=False))

    def get_grade_statistics(self) -> Dict:
        frame = self._load("academics").dropna(subset=["gpa"])
        return {"total_grades": len(frame), "avg_gpa": self._rounded(frame["gpa"].mean()), "min_gpa": frame["gpa"].min(), "max_gpa": frame["gpa"].max(), "excellent_count": int((frame["gpa"] >= 3.5).sum()), "good_count": int(((frame["gpa"] >= 3) & (frame["gpa"] < 3.5)).sum()), "average_count": int(((frame["gpa"] >= 2) & (frame["gpa"] < 3)).sum()), "below_average_count": int((frame["gpa"] < 2).sum())}

    def get_top_courses(self, limit: int = 10) -> List[Dict]:
        frame = self._load("academics")
        result = frame.groupby(["course_id", "course_name"], as_index=False).agg(enrollment=("student_id", "nunique"), avg_gpa=("gpa", "mean"), excellent_students=("grade", lambda x: x.isin(["A", "A+"]).sum()))
        result["avg_gpa"] = result["avg_gpa"].round(2)
        return self._records(result.sort_values("enrollment", ascending=False).head(limit))

    def get_event_statistics(self) -> Dict:
        frame = self._load("events")
        return {"total_events": len(frame), "total_capacity": frame["capacity"].sum(), "avg_capacity": round(frame["capacity"].mean(), 0) if len(frame) else 0}

    def get_recent_events(self, limit: int = 5, status: str | None = None, location: str | None = None) -> List[Dict]:
        frame = self._load("events").copy()
        if location:
            frame = frame[frame["location"] == location]
        if status:
            today = pd.Timestamp.now().normalize()
            dates = pd.to_datetime(frame["date"], errors="coerce")
            if status == "upcoming":
                frame = frame[dates > today]
            elif status == "ongoing":
                frame = frame[dates == today]
            elif status == "completed":
                frame = frame[dates < today]
            else:
                return []
        return self._records(frame.sort_values("date", ascending=False).head(limit))

    def get_events_by_location(self) -> List[Dict]:
        frame = self._load("events")
        frame = frame[frame["location"] != "Unknown"]
        return self._records(frame.groupby("location", as_index=False).agg(count=("event_id", "size"), total_capacity=("capacity", "sum")).sort_values("count", ascending=False))

    def get_events_by_location_detailed(self) -> List[Dict]:
        frame = self._load("events")
        frame = frame[frame["location"] != "Unknown"]
        result = frame.groupby("location", as_index=False).agg(event_count=("event_id", "size"), total_capacity=("capacity", "sum"), avg_capacity=("capacity", "mean"), earliest_date=("date", "min"), latest_date=("date", "max"))
        result["avg_capacity"] = result["avg_capacity"].round(0)
        return self._records(result.sort_values("event_count", ascending=False))

    def get_events_by_type(self) -> List[Dict]:
        return [{"total_events": self.get_event_statistics().get("total_events", 0), "total_capacity": self.get_event_statistics().get("total_capacity", 0)}]

    def get_transportation_status(self) -> List[Dict]:
        frame = self._load("transportation")
        return self._records(frame.groupby("status", as_index=False).agg(count=("vehicle_id", "size"), avg_capacity=("capacity", "mean")).assign(avg_capacity=lambda x: x["avg_capacity"].round(0)).sort_values("count", ascending=False))

    def get_vehicle_by_type(self) -> List[Dict]:
        frame = self._load("transportation")
        return self._records(frame[frame["vehicle_type"] != "Unknown"].groupby("vehicle_type", as_index=False).agg(count=("vehicle_id", "size"), total_capacity=("capacity", "sum")).sort_values("count", ascending=False))

    def get_vehicle_utilization(self) -> List[Dict]:
        frame = self._load("transportation")
        result = frame.groupby("vehicle_type", as_index=False).agg(total_vehicles=("vehicle_id", "size"), total_capacity=("capacity", "sum"), avg_capacity=("capacity", "mean"), active_vehicles=("status", lambda x: (x.str.lower() == "active").sum()), maintenance_vehicles=("status", lambda x: (x.str.lower() == "maintenance").sum()))
        result["avg_capacity"] = result["avg_capacity"].round(0)
        return self._records(result.sort_values("total_vehicles", ascending=False))

    def get_vehicle_health(self) -> Dict:
        frame = self._load("transportation")
        active = int((frame["status"].str.lower() == "active").sum())
        maintenance = int((frame["status"].str.lower() == "maintenance").sum())
        inactive = int((frame["status"].str.lower() == "inactive").sum())
        return {"total_vehicles": len(frame), "total_capacity": frame["capacity"].sum(), "active_count": active, "maintenance_count": maintenance, "inactive_count": inactive, "health_percentage": round(100 * active / len(frame), 2) if len(frame) else 0}

    def get_facilities_status(self) -> List[Dict]:
        frame = self._load("facilities")
        return self._records(frame.groupby("status", as_index=False).agg(count=("facility_id", "size"), avg_capacity=("capacity", "mean")).assign(avg_capacity=lambda x: x["avg_capacity"].round(0)).sort_values("count", ascending=False))

    def get_facilities_by_type(self) -> List[Dict]:
        frame = self._load("facilities")
        result = frame[frame["type"] != "Unknown"].groupby("type", as_index=False).agg(count=("facility_id", "size"), total_capacity=("capacity", "sum"), locations=("location", lambda x: ",".join(sorted(set(x)))))
        return self._records(result.sort_values("count", ascending=False))

    def get_facilities_overview(self) -> List[Dict]:
        frame = self._load("facilities")
        result = frame[frame["type"] != "Unknown"].groupby("type", as_index=False).agg(total_facilities=("facility_id", "size"), total_capacity=("capacity", "sum"), avg_capacity=("capacity", "mean"), operational=("status", lambda x: (x.str.lower() == "operational").sum()), maintenance=("status", lambda x: (x.str.lower() == "under maintenance").sum()), unique_locations=("location", "nunique"))
        result["avg_capacity"] = result["avg_capacity"].round(0)
        return self._records(result.sort_values("total_facilities", ascending=False))

    def get_facilities_maintenance_status(self) -> Dict:
        frame = self._load("facilities")
        operational = int((frame["status"].str.lower() == "operational").sum())
        maintenance = int((frame["status"].str.lower() == "under maintenance").sum())
        return {"total_facilities": len(frame), "total_capacity": frame["capacity"].sum(), "operational_count": operational, "maintenance_count": maintenance, "operational_percentage": round(100 * operational / len(frame), 2) if len(frame) else 0}

    def get_facilities_by_location(self) -> List[Dict]:
        frame = self._load("facilities")
        result = frame[frame["location"] != "Unknown"].groupby("location", as_index=False).agg(facility_count=("facility_id", "size"), total_capacity=("capacity", "sum"), types=("type", lambda x: ",".join(sorted(set(x)))), operational=("status", lambda x: (x.str.lower() == "operational").sum()))
        return self._records(result.sort_values("facility_count", ascending=False))

    def get_data_quality_metrics(self) -> Dict:
        students = self._load("students")
        attendance = self._load("attendance")
        academics = self._load("academics")
        return {"students": {"total_records": len(students), "null_emails": int((students["email"] == "Unknown").sum()), "null_names": int((students["name"] == "Unknown").sum())}, "attendance": {"total_records": len(attendance), "invalid_percentages": int(((attendance["attendance_percentage"] < 0) | (attendance["attendance_percentage"] > 100)).sum())}, "academics": {"total_records": len(academics), "invalid_gpa": int(((academics["gpa"] < 0) | (academics["gpa"] > 4)).sum())}}

    def get_comprehensive_quality_metrics(self) -> Dict:
        result = {}
        key_columns = {"students": ["student_id"], "attendance": ["student_id", "date"], "academics": ["student_id", "course_id"], "events": ["event_id"], "transportation": ["vehicle_id"], "facilities": ["facility_id"]}
        for dataset in self.DATASETS:
            frame = self._load(dataset)
            invalid = 0
            null_count = int(frame.isna().sum().sum())
            if dataset == "attendance":
                invalid = int(((frame["attendance_percentage"] < 0) | (frame["attendance_percentage"] > 100)).sum())
            elif dataset == "academics":
                invalid = int(((frame["gpa"] < 0) | (frame["gpa"] > 4)).sum())
            keys = [column for column in key_columns[dataset] if column in frame.columns]
            duplicate_count = int(frame.duplicated(subset=keys).sum()) if keys else int(frame.duplicated().sum())
            issues = null_count + invalid
            result[dataset] = {"total_records": len(frame), "input_records": len(frame), "valid_records": len(frame) - invalid, "rejected_records": None, "missing_values": null_count, "null_count": null_count, "duplicates": duplicate_count, "invalid_count": invalid, "validation_results": "Gold contains validated records; rejected records are not stored in Gold", "quality_score": round(max(0, 100 - issues / len(frame) * 100), 2) if len(frame) else 0}
        return result