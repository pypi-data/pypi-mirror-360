"""
School of Rock: Student Performance Rating
Rate student performances from 1-10 just like Dewey would!
"""

import os

import pandas as pd

from school_of_prompt import optimize


def main():
    # Student performance data from Battle of the Bands
    student_performances = [
        {
            "student": "Zack",
            "instrument": "guitar",
            "performance": "Played a perfect solo, hit every note, crowd went wild",
            "dewey_rating": 10,
        },
        {
            "student": "Katie",
            "instrument": "drums",
            "performance": "Solid drumming but missed a few beats during the bridge",
            "dewey_rating": 7,
        },
        {
            "student": "Summer",
            "instrument": "keyboards",
            "performance": "Beautiful melody, very technical, but lacked stage presence",
            "dewey_rating": 8,
        },
        {
            "student": "Lawrence",
            "instrument": "keyboards",
            "performance": "Nervous and made several mistakes, needs more practice",
            "dewey_rating": 4,
        },
        {
            "student": "Freddy",
            "instrument": "drums",
            "performance": "Energetic and passionate, perfect rhythm throughout",
            "dewey_rating": 9,
        },
        {
            "student": "Tomika",
            "instrument": "vocals",
            "performance": "Powerful voice that gave everyone chills, amazing range",
            "dewey_rating": 10,
        },
    ]

    df = pd.DataFrame(student_performances)
    df.to_csv("student_performances.csv", index=False)

    results = optimize(
        data="student_performances.csv",
        task="rate performance from 1-10",
        prompts=[
            "Rate this {instrument} performance from 1-10: {performance}",
            "As a rock teacher, how would you score this? {student} on {instrument}: {performance}",
            "Performance rating (1-10): {performance}",
            "School of Rock grade for {student}: {performance}",
        ],
        model="gpt-3.5-turbo",
        metrics=["mae", "accuracy"],
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True,
    )

    print("\\n" + "🥁" * 50)
    print("DEWEY'S STUDENT PERFORMANCE RATINGS")
    print("🥁" * 50)
    print(f"Best prompt for rating performances: {results['best_prompt']}")
    print(
        f"Rating accuracy (MAE): {results['prompts'][list(results['prompts'].keys())[0]]['scores']['mae']:.2f}"
    )

    # Show some predictions vs Dewey's actual ratings
    best_details = results["details"][0]
    print("\\n🎸 Predictions vs Dewey's Ratings:")
    for i, (pred, actual) in enumerate(
        zip(best_details["predictions"], best_details["actuals"])
    ):
        student = student_performances[i]["student"]
        print(f"  {student}: AI rated {pred}/10, Dewey rated {actual}/10")

    print("\\nRock on! Now we can rate performances like a true rock teacher! 🤘")

    os.remove("student_performances.csv")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("🎸 Set your OPENAI_API_KEY to start rating performances!")
        print("export OPENAI_API_KEY='sk-your-key-here'")
    else:
        main()
