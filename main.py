import tkinter as tk

# Function to process user input and generate responses
def process_user_input():
    user_input = user_input_field.get()
    if user_input.lower() == "hello":
        response = "Hi there! 😄"

    elif user_input == "about" :
        response = "Azubi Africa is a community of dedicated and committed individuals who have bought into the vision of training competent Cloud Engineers, Front End Engineers and Data Analytics Engineers"
    
    elif user_input == "program duration" :
        response = "All the programs have a duration of 9 months to completion"

    elif user_input == "tips" :
        response = "Stay put. If you fail to plan. You are planning to fail"

    elif user_input == "contacts" :
        response = "To contact us dial +233 123 4566 0302, email us at info@azubiafrica.org or visit our website at www.azubiafrica.org"

    elif user_input == "instructors" :
        response = "Upon joining the program, you will be trained by professionals who have experience in the field of your choice"

    elif user_input == "career opportunities" :
        response = "You pursue either Front End Web Development, Cloud Engineering or Data Analytics"

    elif user_input == "payment options" :
        response = "Finance your education through a monthly payment of €600 or income share agreement"

    elif user_input == "help" :
        response = "Kindly avoid typo errors. For more information about Azubi call +233 123 4566 0302 or visit our website at www.azubiafrica.org"

    else:
        response = "Opps! Check for errors. Type help for more information"
    
    chat_history_text.config(state='normal')  # Enable editing
    chat_history_text.insert('end', f'You: {user_input}\nChatbot: {response}\n\n')
    chat_history_text.config(state='disabled')  # Disable editing

    user_input_field.delete(0, 'end')  # Clear the input field

# Create the main window
root = tk.Tk()
root.title("Chatbot")

# Configure colors
root.configure(bg='sky blue')
chat_history_text = tk.Text(root, state='disabled', bg='lightgray', wrap='word')
user_input_field = tk.Entry(root, bg='white')
send_button = tk.Button(root, text='Send', command=process_user_input, bg='lightgreen')

# Create a layout
chat_history_text.pack(padx=10, pady=10, fill='both', expand=True)
user_input_field.pack(padx=10, pady=5, fill='x', expand=True)
send_button.pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
