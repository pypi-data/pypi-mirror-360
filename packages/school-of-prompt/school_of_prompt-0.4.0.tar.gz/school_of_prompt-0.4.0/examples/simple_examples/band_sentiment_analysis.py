"""
School of Rock: Band Review Sentiment Analysis
Analyze fan reviews of the School of Rock band performances!
"""

import os

from school_of_prompt import optimize


def main():
    # School of Rock band performance reviews
    band_reviews = [
        {
            "review": "Dewey's guitar solo was absolutely mind-blowing! Best show ever!",
            "sentiment": "positive",
        },
        {
            "review": "Katie's drumming was off-beat and the whole performance sucked.",
            "sentiment": "negative",
        },
        {
            "review": "Zack's bass lines were solid, pretty good overall show.",
            "sentiment": "neutral",
        },
        {
            "review": "Summer's keyboard skills blew me away! Incredible talent!",
            "sentiment": "positive",
        },
        {
            "review": "The band seemed unprepared and it was a total disaster.",
            "sentiment": "negative",
        },
        {
            "review": "Lawrence on keyboards was decent, nothing spectacular though.",
            "sentiment": "neutral",
        },
        {
            "review": "This band rocks! They're going to be famous someday!",
            "sentiment": "positive",
        },
        {
            "review": "Boring performance, I've seen middle schoolers play better.",
            "sentiment": "negative",
        },
    ]

    # Save sample data to CSV for demo
    import pandas as pd

    df = pd.DataFrame(band_reviews)
    df.to_csv("band_reviews.csv", index=False)

    # Optimize prompts for analyzing band review sentiment
    results = optimize(
        data="band_reviews.csv",
        task="classify sentiment",
        prompts=[
            "How does this fan feel about the School of Rock band? {review}",
            "Is this review positive, negative, or neutral? {review}",
            "What's the sentiment of this band review: {review}",
            "Fan reaction analysis: {review}",
        ],
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True,
    )

    print("\\n" + "🎸" * 50)
    print("SCHOOL OF ROCK BAND REVIEW ANALYSIS")
    print("🎸" * 50)
    print(f"Best prompt for analyzing fan reviews: {results['best_prompt']}")
    print(f"Sentiment analysis accuracy: {results['best_score']:.3f}")
    print("\\nNow we know how to analyze what fans think of our rock shows! 🤘")

    # Clean up demo file
    os.remove("band_reviews.csv")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("🎸 Set your OPENAI_API_KEY to rock this analysis!")
        print("export OPENAI_API_KEY='sk-your-key-here'")
    else:
        main()
