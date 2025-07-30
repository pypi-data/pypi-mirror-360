"""
School of Rock: Content Safety for Young Rockers
Classify music content as appropriate for kids or not - keeping it school-safe!
"""

import os

import pandas as pd

from school_of_prompt import CustomMetric, optimize


class RockSafetyPrecision(CustomMetric):
    """Custom metric that prioritizes catching inappropriate content for kids."""

    @property
    def name(self):
        return "rock_safety_precision"

    def calculate(self, predictions, actuals):
        # Convert to binary: inappropriate=1, appropriate=0
        pred_inappropriate = [
            1 if "inappropriate" in str(p).lower() else 0 for p in predictions
        ]
        actual_inappropriate = [
            1 if "inappropriate" in str(a).lower() else 0 for a in actuals
        ]

        # Calculate precision for "inappropriate" class
        tp = sum(p and a for p, a in zip(pred_inappropriate, actual_inappropriate))
        fp = sum(p and not a for p, a in zip(pred_inappropriate, actual_inappropriate))

        return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def main():
    # Music content that needs safety evaluation for the school
    music_content = [
        {
            "lyrics": "We're gonna rock this school and show everyone how awesome music is!",
            "safety": "appropriate",
        },
        {
            "lyrics": "Drinking whiskey and raising hell all night long, breaking all the rules",
            "safety": "inappropriate",
        },
        {
            "lyrics": "Learning guitar chords and playing with my friends in the band",
            "safety": "appropriate",
        },
        {
            "lyrics": "Violence and destruction, burning down the establishment with rage",
            "safety": "inappropriate",
        },
        {
            "lyrics": "Music class is fun when we all play together as a team",
            "safety": "appropriate",
        },
        {
            "lyrics": "Getting wasted at the bar, smoking cigarettes behind the school",
            "safety": "inappropriate",
        },
        {
            "lyrics": "Practice makes perfect, let's work on this song for the talent show",
            "safety": "appropriate",
        },
    ]

    df = pd.DataFrame(music_content)
    df.to_csv("music_content.csv", index=False)

    results = optimize(
        data="music_content.csv",
        task="classify content safety for school",
        prompts=[
            "Is this appropriate for a school music program? {lyrics}",
            "School-safe content check: {lyrics}",
            "Can kids hear this in music class? {lyrics}",
            "Principal's content approval: {lyrics}",
        ],
        model={
            "name": "gpt-4",
            "temperature": 0.0,  # More consistent for safety decisions
            "max_tokens": 10,
        },
        metrics=[
            "accuracy",
            "precision",
            RockSafetyPrecision(),  # Our custom safety metric
        ],
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True,
    )

    print("\\n" + "🛡️" * 50)
    print("SCHOOL OF ROCK CONTENT SAFETY RESULTS")
    print("🛡️" * 50)
    print(f"Best prompt for safety checking: {results['best_prompt']}")
    print(f"Safety detection accuracy: {results['best_score']:.3f}")

    # Show all metrics for best prompt
    best_prompt_key = list(results["prompts"].keys())[0]
    scores = results["prompts"][best_prompt_key]["scores"]
    print("\\n🎸 Safety Metrics:")
    for metric, score in scores.items():
        print(f"  {metric}: {score:.3f}")

    print("\\nNow we can keep our rock school content kid-friendly! 🤘👶")

    os.remove("music_content.csv")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("🎸 Set your OPENAI_API_KEY to check content safety!")
        print("export OPENAI_API_KEY='sk-your-key-here'")
    else:
        main()
