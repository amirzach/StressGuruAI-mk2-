import random
import nltk
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize NLTK
nltk.download("punkt")
stemmer = nltk.PorterStemmer()

# Load data from a JSON file instead of data.py
DATA_FILE = 'chat_data.json'

# Load existing data or create a new structure if file doesn't exist
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = {"greetings": ["Hello!", "Hi!", "Hey!"], 
                "goodbyes": ["Goodbye!", "See you!", "Take care!"],
                "keywords": [], 
                "responses": []}
    return data

chat_data = load_data()

# Tokenize and stem user input
def preprocess(sentence):
    tokens = nltk.word_tokenize(sentence.lower())
    return ' '.join([stemmer.stem(token) for token in tokens])

# Train the chatbot using TF-IDF vectorization
def train_vectorizer(keywords):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(keywords)  # Fit on existing keywords
    return vectorizer, X

# Get the best response using TF-IDF similarity
def get_response(user_input, vectorizer, X):
    user_input_processed = preprocess(user_input)
    input_vector = vectorizer.transform([user_input_processed])
    
    # Compute cosine similarity with known keywords
    similarities = cosine_similarity(input_vector, X).flatten()
    best_match = similarities.argmax()

    if similarities[best_match] > 0.5:  # Only respond if similarity is good enough
        return chat_data["responses"][best_match]
    return "I'm not sure how to respond to that. Would you like to add a new keyword? (yes/no)"

# Save updated chat data to JSON file
def save_data():
    with open(DATA_FILE, 'w') as file:
        json.dump(chat_data, file, indent=4)
    print("Data has been saved to chat_data.json")

# Add new keyword and response to the chatbot’s data
def add_keyword_response(user_input):
    new_keyword = input("Enter the new keyword: ")
    new_response = input(f"How should I respond to '{new_keyword}'? ")
    
    chat_data["keywords"].append(new_keyword)
    chat_data["responses"].append(new_response)
    print(f"New keyword '{new_keyword}' added with response: '{new_response}'")
    
    save_data()  # Save the updated data
    
    # Check if the new keyword matches the last input and respond immediately
    if new_keyword in preprocess(user_input):
        return new_response
    return "The new keyword has been added, but I still don't understand your previous input."

# Chat loop
def chat():
    print("Chatbot:", random.choice(chat_data["greetings"]))
    print("Chatbot: I'm your friendly chatbot. Type 'exit' to end the conversation.")
    
    vectorizer, X = train_vectorizer(chat_data["keywords"])  # Train the vectorizer

    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "exit":
            print("Chatbot:", random.choice(chat_data["goodbyes"]))
            break
        
        response = get_response(user_input, vectorizer, X)
        print("Chatbot:", response)
        
        # Check if user wants to add a new keyword
        if response.startswith("I'm not sure how to respond to that"):
            add_keyword = input("Would you like to add a new keyword? (yes/no): ")
            if add_keyword.lower() == 'yes':
                immediate_response = add_keyword_response(user_input)
                print("Chatbot:", immediate_response)
            elif add_keyword.lower() == 'no':
                print("Chatbot: Okay, feel free to ask me something else!")

if __name__ == "__main__":
    chat()
