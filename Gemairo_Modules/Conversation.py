import os
import tempfile

class Conversation:
    def __init__(self, id, isServer, replicateClient):
        self.defineVariables(id, isServer)
        self.createMemory()
        self.replicateClient = replicateClient

    def defineVariables(self, id, isServer):
        self.conversationID = id
        self.isActive = not isServer
        self.isServer = isServer
        self.conversationHistory = ""

        current_file = __file__
        current_directory = os.path.dirname(current_file)
        self.file_path = os.path.join(current_directory, '..', 'Conversation_Data', id + '.txt')

    def createMemory(self):
        try:
            with open(self.file_path, 'r') as f:
                self.memory = f.read()
        except FileNotFoundError:
            print("new conversation id, creating file...")
            self.memory = ""

    def summarize_conversation(self, text):
        # Ensure the output folder exists
        output_folder = tempfile.gettempdir()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the prompt template with placeholders for variables
        prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            summerize this conversation, only save the important information to memory,
            if the user (not gemairo) asked not to save the conversation, do not include this in the summery, also do this if nothing interesting happened.
        <|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{text}<|eot_id|><|start_header_id|>assistant<|end_header_id>\n\n"""

        # Format the prompt template with the given name and text
        formatted_prompt = prompt_template.format(text=text.lower())
        input_data = {
            "top_p": 0.9,
            "prompt": formatted_prompt,
            "min_tokens": 0,
            "temperature": 0.6,
            "presence_penalty": 1.15
        }   

        try:
            full_response = ""
            for event in self.replicateClient.stream("meta/llama-4-maverick-instruct", input=input_data):
                if hasattr(event, 'data'):
                    full_response += event.data  # Accumulate the event data

            # Clean up the response to ensure it doesn't end with {}
            full_response = full_response.strip()
            if full_response.endswith('{}'):
                full_response = full_response[:-2].strip()  # Remove the last two characters

            return full_response
        except Exception as e:
            print(f"Error fetching response: {e}")
            return "Sorry, something went wrong with the response."
    
    def saveMessageToHistory(self, message, reply):
        newMessageData = ""
        newMessageData += ("\n")
        newMessageData += (f"\nUsername:   {message.author.name} ({message.author.display_name})")
        try:
            newMessageData += (f"\n{message.author.display_name}:    {message.content}")
        except Exception as e:
                print(f"Error writing Message: {e}")

        if reply != 'null':
            newMessageData += (f"\nGemairo:   {reply}")

        self.conversationHistory += (newMessageData)
        
        import os

        with open(self.file_path, 'a+') as file:  
            file.seek(0)
            lines = file.readlines()
            if len(lines) > 100:
                full_str = "".join(lines)
                summary = self.summarize_conversation(full_str)
            else:
                summary = None
            file.write(f"{newMessageData}")

        self.memory += newMessageData

        if summary:
            with open(self.file_path, 'w') as file:
                file.write(summary)