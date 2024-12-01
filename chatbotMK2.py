import json
import os
import random

# Load chatbot data from JSON
def load_chatbot_data():
    with open('chatbot_data.json', 'r') as file:
        data = json.load(file)
    return data['greetings'], data['greeting_reactions'], data['small_talk'], data['exit_prompts']

# Load DASS-21 questions and categories from JSON
def load_dass_data():
    with open('dass_data.json', 'r') as file:
        data = json.load(file)
    return data['questions'], data['categories']

# Helper function to select a small talk response based on weights
def weighted_random_choice(options):
    total_weight = sum(option['weight'] for option in options)
    rand_val = random.uniform(0, total_weight)
    cumulative_weight = 0

    for option in options:
        cumulative_weight += option['weight']
        if rand_val <= cumulative_weight:
            return option['text']

# Handle user response to greeting
def handle_greeting_response(greeting_reactions):
    response = input("User: ").strip().lower()

    if any(word in response for word in ["good", "great", "fantastic", "awesome"]):
        print("Chatbot:", random.choice(greeting_reactions["good"]))
    elif any(word in response for word in ["okay", "fine", "alright", "not bad"]):
        print("Chatbot:", random.choice(greeting_reactions["okay"]))
    elif any(word in response for word in ["bad", "sad", "terrible", "awful"]):
        print("Chatbot:", random.choice(greeting_reactions["bad"]))
    else:
        print("Chatbot: I'm here for you, whatever you're feeling.")

    # Ask if the user is ready to proceed with the evaluation
    while True:
        proceed = input("Chatbot: Can I ask you some questions to better understand how you're feeling? (yes/no)\nUser: ").strip().lower()
        if proceed in ["yes", "y"]:
            return True
        elif proceed in ["no", "n"]:
            print("Chatbot: That's okay. We can just chat if you prefer.")
            return False
        else:
            print("Chatbot: Please answer with 'yes' or 'no'.")

# Keyword-based response to score mapping
def extract_score_from_response(response):
    keywords = {
        0: ["no", "never", "not at all"],
        1: ["a little", "sometimes", "rarely"],
        2: ["maybe", "occasionally", "quite a bit"],
        3: ["yes", "often", "frequently", "a lot"]
    }

    response = response.lower()  # Make the response case-insensitive
    for score, words in keywords.items():
        if any(word in response for word in words):
            return score  # Return the corresponding score if a keyword is found
    return None  # Return None if no keyword matches

# Collect user responses for DASS-21 questions with small talk
def ask_questions(questions, categories, small_talk, exit_prompts):
    responses = []
    question_pairs = list(zip(questions, categories))
    random.shuffle(question_pairs)  # Shuffle questions for randomness

    for i, (question, category) in enumerate(question_pairs):
        while True:
            print("Chatbot:", weighted_random_choice(small_talk))  # Print a small talk response
            response = input(f"Chatbot: {question} (Feel free to respond naturally or type 'exit' to stop)\nUser: ").strip()

            if response.lower() == 'exit':
                print("Chatbot:", random.choice(exit_prompts))  # Offer polite exit prompt
                if input("Chatbot: (yes/no)\nUser: ").strip().lower() == 'no':
                    return responses  # Return collected responses so far

            score = extract_score_from_response(response)
            if score is not None:
                responses.append((score, category))  # Store response with category
                break
            else:
                print("Chatbot: I couldn't quite catch that. Could you rephrase or respond differently?")

    return responses

# Calculate scores for each category
def calculate_scores(responses):
    stress_score = sum(response for response, cat in responses if cat == "S")
    anxiety_score = sum(response for response, cat in responses if cat == "A")
    depression_score = sum(response for response, cat in responses if cat == "D")

    # Multiply by 2 as per DASS-21 scoring rules
    return {
        "Stress": stress_score * 2,
        "Anxiety": anxiety_score * 2,
        "Depression": depression_score * 2
    }

# Provide feedback based on scores
def provide_feedback(scores):
    severity_labels = {
        "Stress": [(0, 14, "Normal"), (15, 18, "Mild"), (19, 25, "Moderate"), 
                   (26, 33, "Severe"), (34, float('inf'), "Extremely Severe")],
        "Anxiety": [(0, 7, "Normal"), (8, 9, "Mild"), (10, 14, "Moderate"), 
                    (15, 19, "Severe"), (20, float('inf'), "Extremely Severe")],
        "Depression": [(0, 9, "Normal"), (10, 13, "Mild"), (14, 20, "Moderate"), 
                       (21, 27, "Severe"), (28, float('inf'), "Extremely Severe")]
    }

    print("\nChatbot: Here's what I've noticed so far:")
    for category, score in scores.items():
        for min_score, max_score, label in severity_labels[category]:
            if min_score <= score <= max_score:
                print(f"{category}: {score} - {label}")
                break

    print("\nChatbot: It's okay to feel how you're feeling. If you need to talk more, I'm here.")
    print("Chatbot: If things get tough, please consider reaching out to someone you trust or a professional.")

# Main chat function
def chat():
    greetings, greeting_reactions, small_talk, exit_prompts = load_chatbot_data()
    print("Chatbot:", random.choice(greetings))  

    if handle_greeting_response(greeting_reactions):
        questions, categories = load_dass_data()
        responses = ask_questions(questions, categories, small_talk, exit_prompts)

        if responses:
            scores = calculate_scores(responses)
            provide_feedback(scores)
        else:
            print("Chatbot: No responses collected. That's okay. If you need to talk, I'm always here.")
    else:
        print("Chatbot: Thanks for chatting! Take care, and feel free to reach out anytime.")

if __name__ == "__main__":
    chat()
