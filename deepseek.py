import os,json
import time,subprocess
from openai import OpenAI

keyy = str(input('Api key: '))

def Json_cleaning(Your_json):
    a = Your_json.replace("\n"," ")
    b = json.loads(a)
    c = str(b["To customer"]).replace("\n"," ")
    return c

def extract_server_command(Your_json):
    try:
        a = Your_json.replace("\n"," ")
        b = json.loads(a)
        if "To server" in b:
            return str(b["To server"]).strip()
        return ""
    except:
        return ""

def execute_server_command(command):
    if not command:
        return
    
    if command.startswith("+add") or command.startswith("+Remove") or command.startswith("+finish"):
        order_file = os.path.join("Server", "AI_order_command.txt")
        
        if not os.path.exists("Server"):
            os.makedirs("Server")
            
        with open(order_file, 'w') as f:
            f.write(f'{command}')
        
        print(f"Server command received: {command}")

class OpenAICLI:
    def __init__(self):
        self.client = OpenAI(api_key=keyy, base_url="https://api.deepseek.com")
        if not self.client.api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable")

        # Customizable settings
        self.system_prompt = """
# Kmitl icecream shop Drive-Through AI Operator

You are a friendly, efficient Thai-speaking drive-through operator at Kmitl icecream shop. Your goal is to create a positive customer experience while accurately taking orders and naturally upselling when appropriate.

## Core Instructions
- **Primary Language**: Respond primarily in Thai language
- **Secondary Language**: Use English only when necessary
- **Personality**: Friendly, patient, attentive, and efficient
- **Goal**: Take accurate orders while creating a positive experience

## Menu Items and Options

### Drink
```
"Milk_tea": { #ชานม
    "Classical_milk_tea": 30.00, #ชานมคลาสสิก
    "Pandan_milk_tea": 35.00, #ชานมใบเตย
    "Brown_sugar_milk_tea": 40.00, #ชานมบราวชูก้า
    "Mango_milk_tea": 50.00, #ชานมมะม่วง
    "Starwberry_creamy_tea": 45.00 #ชานมสตรอว์เบอร์รี
}
"Fruit_tea": { # ชาผลไม่้
    "Kiwi_jasmin": 35.00,  #ชากีวี่
    "Lemonade_tea": 25.00, #ชามะนาว
    "Lemon_black_tea": 30.00, #ชามะนาวดำ
    "Mango_tea": 25.00 #ชามะม่วง
},
```

Size = {
"R": "Regular size",
"L": "Large size (+$5)",
"EL": "Extra Large size (+$10)",
}

Ice = {
    "R": "Regular Ice", #น้ำแช็งปกติ
    "L": "Light Ice", #น้ำแช็งน้อย
    "E": "Extra Ice", #เพิ่มน้ำแข็ง
}

Sugar = {
    "50": "50%", #หวาน 50 / หวานน้อย
    "70": "70%", #หวาน 70
    "100": "100%", #หวานปกติ
}



## Order Command System

- **+add <ENG_item_name> <Size> <Ice> <Sugar>** - Add items to cart
  - Example: `+add Mango_milk_tea L L 70`

  - #IMPORTANT: If customer doesn't specify size,ice or sugar just use '-',No need to ask any futher
  - Example: `+add Pandan_milk_tea - - -`
  
  - Use / to separate multiple items
  - Example: `+add Starwberry_creamy_tea R L - / +add Mango_milk_tea EL E 50`
  - Example: `+add Kiwi_jasmin R L 70 / +add Kiwi_jasmin R L 70 / +add Kiwi_jasmin R L 70`

- **+Remove <item_id>** - Remove items from cart
  - Example: `+Remove 1`
  - Use / to separate multiple items

- **-Human_operator** - Transfer to a human operator

- **+finish** - Complete and finalize the order

## Response Format
All responses must follow this JSON format:
```
{
  "To customer": "Your friendly message to the customer in Thai",
  "To server": "Command to process in the system"
}
```

## Core Service Guidelines

1. **Customer Interaction Flow**:
   - Greet warmly with time-appropriate greeting (สวัสดีครับ)
   - Suggest complementary items naturally
   - Thank the customer

2. **Special Situations**:
   - Use speaking tone not wrinting tone ,everything you say is going to say out loud
   - For unavailable items, suggest alternatives
   - For complex orders, break down confirmation into manageable parts
   - If technical issues arise, apologize and use the -Human_operator command

3. **Thai Language Courtesy**:
   - Use polite particles (ค่ะ) appropriately
   - Maintain friendly but respectful tone
   - The price is in THB(baht)



"""
        self.user_prompt = "Customer: "
        self.ai_prompt = "Assistant: "
        self.temperature = 0.4
        self.model = "deepseek-chat"

        # Initialize conversation history
        self.conversation_history = []
        if self.system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt
            })

    def chat(self):
        print("OpenAI CLI - Type 'exit' to end the conversation")
        
        while True:
                user_input = input(f"\n{self.user_prompt}")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Time the API response
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=self.temperature,
                )

                elapsed_time = time.time() - start_time
                
                ai_response = response.choices[0].message.content
                print(f"\n{self.ai_prompt} ({elapsed_time:.2f}s): {ai_response}")
                y = Json_cleaning(ai_response)
                
                server_command = extract_server_command(ai_response)
                execute_server_command(server_command)
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                

if __name__ == "__main__":
    try:
        subprocess.Popen(['start', 'python', 'Cashier.py'], shell=True)
        subprocess.Popen(['start', 'python', 'ui_test.py'])
        
        cli = OpenAICLI()
        cli.chat()
    except ValueError as e:
        print(e)