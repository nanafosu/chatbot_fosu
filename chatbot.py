import tkinter as tk
from tkinter import scrolledtext, PhotoImage
from datetime import datetime

import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import psycopg2
import bcrypt
# Import the Text widget
from tkinter import simpledialog, Toplevel, Text, Scrollbar

# Load the Tkinter root window
root = tk.Tk()
root.title("Azubi Africa Chatbot")

# Configure colors
root.configure(bg='sky blue')

# Add Azubi Africa logo
azubi_logo = PhotoImage(file='images/azubi_logo.png')
logo_label = tk.Label(root, image=azubi_logo, bg='sky blue')
logo_label.pack()

# Create chat history area
chat_history_text = scrolledtext.ScrolledText(root, state='disabled', bg='lightgray', wrap='word', width=40, height=10)
chat_history_text.pack(padx=10, pady=10, fill='both', expand=True)

# Create user input field
user_input_field = tk.Entry(root, bg='white')
user_input_field.pack(padx=10, pady=5, fill='x', expand=True)

# Create send button
send_button = tk.Button(root, text='Send', command=lambda: process_user_input(), bg='lightgreen')
send_button.pack(pady=5)

# Add login button
login_button = tk.Button(root, text='Login as Admin', command=lambda: login_as_admin(), bg='lightblue')
login_button.pack(pady=5)

# Database connection configuration
with psycopg2.connect(
    host="localhost",
    port="5432",
    database="azubi_chatbot",
    user="postgres",
    password="itvaigv1986"
) as db_connection:

    # Variable to track login status
    admin_logged_in = False

    # Create a function to handle user input
    def process_user_input(event=None):
        user_input = user_input_field.get()

        if not user_input:
            return  # Do nothing if the user input is empty

        chat_history_text.configure(state='normal')
        chat_history_text.insert('end', 'You: ' + user_input + '\n')

        # Check if the user wants to end the conversation
        if user_input.lower() == 'exit':
            root.destroy()  # Close the Tkinter window
            return

        # Chatbot logic
        ints = predict_class(user_input)
        if ints:
            res = get_response(ints, intents)
            chat_history_text.insert('end', 'Bot: ' + res + '\n')
            # Store the conversation in the database
            store_conversation(user_input, res)
        else:
            chat_history_text.insert('end', "Bot: I'm sorry, I don't understand that.\n")

        chat_history_text.see('end')  # Scroll to the end
        chat_history_text.configure(state='disabled')

        user_input_field.delete(0, 'end')  # Clear the user input field

    # Bind the Enter key to the user input field
    user_input_field.bind('<Return>', process_user_input)

    # Create a function for administrator login
    def login_as_admin():
        global admin_logged_in

        if not admin_logged_in:
            username = simpledialog.askstring("Admin Login", "Enter Admin Username:")
            if username:
                try:
                    with db_connection.cursor() as cursor:
                        # Retrieve the hashed password for the given username
                        sql = "SELECT hashed_password FROM admin_users WHERE username = %s"
                        cursor.execute(sql, (username,))
                        result = cursor.fetchone()

                        if result:
                            hashed_password = result[0].encode('utf-8')

                            # Prompt user for password using password entry widget
                            password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
                            if password and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                                chat_history_text.configure(state='normal')
                                chat_history_text.insert('end', 'You are now logged in as Admin.\n')
                                chat_history_text.configure(state='disabled')
                                admin_logged_in = True

                                # Open a new window to display conversations
                                admin_window = Toplevel(root)
                                admin_window.title("Admin Console")

                                # Retrieve conversations from the database
                                conversations = retrieve_conversations()

                                # Display conversations in the new window
                                display_conversations(admin_window, conversations)
                            else:
                                chat_history_text.configure(state='normal')
                                chat_history_text.insert('end', 'Invalid credentials for Admin login.\n')
                                chat_history_text.configure(state='disabled')
                        else:
                            chat_history_text.configure(state='normal')
                            chat_history_text.insert('end', 'Invalid credentials for Admin login.\n')
                            chat_history_text.configure(state='disabled')

                except Exception as e:
                    print(f"Error during admin login authentication: {e}")
            else:
                chat_history_text.configure(state='normal')
                chat_history_text.insert('end', 'Admin login cancelled.\n')
                chat_history_text.configure(state='disabled')

        elif admin_logged_in:
            chat_history_text.configure(state='normal')
            chat_history_text.insert('end', 'Admin is already logged in.\n')
            chat_history_text.configure(state='disabled')

    # ...

    # Function to retrieve conversations from the database
    def retrieve_conversations():
        try:
            with db_connection.cursor() as cursor:
                # Retrieve all conversations from the database
                sql = "SELECT user_input, bot_response, timestamp FROM azubi_chat_history"
                cursor.execute(sql)
                conversations = cursor.fetchall()
            return conversations
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []

    # Function to display conversations in the admin window
    def display_conversations(admin_window, conversations):
        text_widget = Text(admin_window, wrap='word', height=20, width=80)
        text_widget.pack(expand=True, fill='both')

        scrollbar = Scrollbar(admin_window, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)

        if not conversations:
            text_widget.insert('end', "No conversations available.")
        else:
            for conv in conversations:
                conversation_text = f"{conv[2]} - User: {conv[0]}\nBot: {conv[1]}\n\n"
                text_widget.insert('end', conversation_text)

        # Disable text editing to make it read-only
        text_widget.config(state='disabled')


    # Bind the Enter key to the user input field
    user_input_field.bind('<Return>', lambda event=None: process_user_input())

    # Load the chatbot model and data
    lemmatizer = WordNetLemmatizer()
    with open('intents.json', 'r') as file:
        intents = json.load(file)

    words = pickle.load(open('words.pk', 'rb'))
    classes = pickle.load(open('classes.pk', 'rb'))
    model = load_model('chatbot_model.h5')

    # Define chatbot functions
    def clean_up_sentence(sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words

    def bag_of_words(sentence):
        sentence_words = clean_up_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(sentence):
        bow = bag_of_words(sentence)
        res = model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25

        # Get the index of the highest probability
        max_prob_index = np.argmax(res)

        # Check if the probability is above the threshold
        if res[max_prob_index] > ERROR_THRESHOLD:
            return_list = [{'intent': classes[max_prob_index], 'probability': str(res[max_prob_index])}]
            return return_list
        else:
            return []

    def get_response(intents_list, intents_json):
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']

        # Set a default value for result
        result = "I'm sorry, I don't understand that."

        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['response'])
                break

        return result

    def store_conversation(user_input, bot_response):
        try:
            with db_connection.cursor() as cursor:
                # Insert conversation into the database
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO azubi_chat_history (user_input, bot_response, timestamp) VALUES (%s, %s, %s)"
                cursor.execute(sql, (user_input, bot_response, current_time))
            db_connection.commit()
        except Exception as e:
            print(f"Error storing conversation in the database: {e}")

    # Run the Tkinter main loop
    root.mainloop()
