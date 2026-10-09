
import csv
from pathlib import Path
from datetime import datetime

# Define input and output file paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "students.csv"
OUTPUT_DIR = BASE_DIR / "output"

SUBJECTS = ["python", "sql", "html"]
PASS_MARKS = 35


def process_students():
    # Check whether the input file exists
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE.name} was not found.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    processed_students = []
    invalid_rows = 0

    # Open and read the CSV file
    try:
        with INPUT_FILE.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {"name", *SUBJECTS}
            if not reader.fieldnames or not required_columns.issubset(
                reader.fieldnames
            ):
                print("Error: CSV headers are missing or incorrect.")
                return

            for row in reader:
                try:
                    name = (row.get("name") or "").strip()
                    if not name:
                        raise ValueError("Missing student name")

                    marks = {}
                    for subject in SUBJECTS:
                        mark = float(row[subject])
                        if not 0 <= mark <= 100:
                            raise ValueError("Marks must be 0 to 100")
                        marks[subject] = mark

                    total = sum(marks.values())
                    average = total / len(SUBJECTS)
                    result = (
                        "Pass"
                        if all(m >= PASS_MARKS for m in marks.values())
                        else "Fail"
                    )

                    processed_students.append({
                        "name": name,
                        **marks,
                        "total": round(total, 2),
                        "average": round(average, 2),
                        "result": result,
                    })

                except (ValueError, TypeError, KeyError):
                    invalid_rows += 1
                    print(f"Skipping invalid row: {row}")

    except (OSError, csv.Error) as error:
        print(f"Could not read the input file: {error}")
        return

    # Generate the processed CSV file
    output_csv = OUTPUT_DIR / "processed_students.csv"
    fieldnames = ["name", *SUBJECTS, "total", "average", "result"]

    try:
        with output_csv.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_students)

        total_students = len(processed_students)
        passed = sum(
            student["result"] == "Pass"
            for student in processed_students
        )
        failed = total_students - passed
        class_average = (
            sum(s["average"] for s in processed_students)
            / total_students
            if total_students else 0
        )

        # Generate the summary report
        report_file = OUTPUT_DIR / "summary_report.txt"
        with report_file.open("w", encoding="utf-8") as file:
            file.write("STUDENT PERFORMANCE REPORT\n")
            file.write("=" * 30 + "\n")
            file.write(
                f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            )
            file.write(f"Students processed: {total_students}\n")
            file.write(f"Passed: {passed}\n")
            file.write(f"Failed: {failed}\n")
            file.write(f"Invalid rows skipped: {invalid_rows}\n")
            file.write(f"Class average: {class_average:.2f}\n")

            if processed_students:
                top_student = max(
                    processed_students,
                    key=lambda student: student["average"]
                )
                file.write(
                    f"Highest average: {top_student['name']} "
                    f"({top_student['average']:.2f})\n"
                )

        print("Automation completed successfully!")
        print(f"Processed data: {output_csv}")
        print(f"Summary report: {report_file}")

    except OSError as error:
        print(f"Could not write output files: {error}")


if __name__ == "__main__":
    process_students()