import requests
import random
import time
import pandas as pd
from datetime import datetime

# Category mapping
categories = {
    "1": ("General Knowledge", 9),
    "2": ("Books", 10),
    "3": ("Film", 11),
    "4": ("Music", 12),
    "5": ("Science", 17),
    "6": ("Computers", 18),
    "7": ("Maths", 19),
    "8": ("Sports", 21),
    "9": ("Geography", 22),
    "10": ("History", 23),
    "11": ("Politics", 24)
}

# Track category-wise performance
score_record = {cat[0]: "Not Attempted" for cat in categories.values()}

# Get questions from API
def get_questions(cat_id):
    url = f"https://opentdb.com/api.php?amount=10&category={cat_id}&type=multiple"
    response = requests.get(url)
    return response.json().get('results', [])

# Quiz session logic
def quiz_session(category_name, cat_id, username):
    questions = get_questions(cat_id)
    score = 0
    total = 0
    incorrect_summary = []

    print(f"\n🧠 Starting quiz in category: {category_name}")

    for q in questions:
        print(f"\nQuestion {total + 1}: {q['question']}")
        options = q['incorrect_answers'] + [q['correct_answer']]
        random.shuffle(options)

        for i, option in enumerate(options):
            print(f"{i+1}. {option}")

        start_time = time.time()
        try:
            ans = int(input("Your answer (1-4): "))
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)

            if options[ans - 1] == q['correct_answer']:
                score += 1
                print(f"✅ Correct! ⏱️ Time: {time_taken} sec")
            else:
                print(f"❌ Wrong! Correct: {q['correct_answer']} ⏱️ Time: {time_taken} sec")
                incorrect_summary.append({
                    "Question": q['question'],
                    "Your Answer": options[ans - 1],
                    "Correct Answer": q['correct_answer']
                })
        except:
            print("❌ Invalid input.")
            continue

        total += 1
        cont = input("Continue to next question? (y/n): ").lower()
        if cont != 'y':
            break

    print(f"\n📊 {username}'s Score in {category_name}: {score}/{total}")
    score_record[category_name] = f"{score}/{total}"

    # Incorrect answer review
    if incorrect_summary:
        print("\n❌ Review of Incorrect Answers:")
        for idx, item in enumerate(incorrect_summary, 1):
            print(f"\n{idx}. {item['Question']}")
            print(f"   ❌ Your Answer: {item['Your Answer']}")
            print(f"   ✅ Correct Answer: {item['Correct Answer']}")

    save_score(username, category_name, score, total)

# Save score to CSV
def save_score(username, category, score, total):
    filename = "quiz_scores.csv"
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Category", "Score", "Total", "Date"])

    new_entry = {
        "Name": username,
        "Category": category,
        "Score": score,
        "Total": total,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(filename, index=False)
    print("💾 Score saved to quiz_scores.csv")

# Show final report
def show_final_report(username):
    print("\n📈 Final Quiz Summary:")
    print(f"👤 Name: {username}")
    print("📊 Your category-wise Scores:")
    for cat, score in score_record.items():
        print(f" your total score is:- {cat}: {score}")
    print("\n🏁 Thank you for playing!")

# Start the game
def start_quiz():
    print("🎮 Welcome to the StaxTech Quiz Game!")
    username = input("Enter your name: ")

    while True:
        print("\n📚 Available Categories:")
        for key, (name, _) in categories.items():
            print(f"{key}. {name}")

        choice = input("\nChoose a category by number (e.g., 5 for Science): ")
        if choice in categories:
            cat_name, cat_id = categories[choice]
            quiz_session(cat_name, cat_id, username)
        else:
            print("❌ Invalid category number. Please try again.")
            continue

        again = input("\nDo you want to take another quiz? (y/n): ").lower()
        if again != 'y':
            show_final_report(username)
            break

start_quiz()