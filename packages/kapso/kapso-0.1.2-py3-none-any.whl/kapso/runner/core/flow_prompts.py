"""
Contains prompt templates and prompt generation functions for the flow agent.
"""

from datetime import datetime
from typing import Any, Dict, List

def _format_broadcast_context(broadcast_context: Dict[str, Any]) -> str:
    """
    Format broadcast context for inclusion in the system prompt.
    
    Args:
        broadcast_context: Dictionary containing broadcast information
        
    Returns:
        Formatted string for the prompt
    """
    template_params_text = ""
    if broadcast_context.get("template_parameters"):
        params = broadcast_context["template_parameters"]
        param_lines = []
        for key, value in params.items():
            param_lines.append(f"- Parameter {key}: {value}")
        if param_lines:
            template_params_text = f"\nPersonalized Parameters:\n" + "\n".join(param_lines)
    
    sent_at_text = ""
    if broadcast_context.get("sent_at"):
        sent_at_text = f"\nSent At: {broadcast_context['sent_at']}"
    
    return f"""

<broadcast_context>
The user is responding to a broadcast message that was sent to them.

Broadcast Information:
- Campaign Name: {broadcast_context.get('broadcast_name', 'Unknown')}
- Template Used: {broadcast_context.get('template_name', 'Unknown')}
{sent_at_text}

Original Message Sent:
{broadcast_context.get('template_content', 'Content not available')}
{template_params_text}

Important: This context helps you understand why the user is contacting you. They received the above message as part of a broadcast campaign and are now responding to it. You should acknowledge this context naturally in your conversation without explicitly mentioning it was a "broadcast" unless necessary.
</broadcast_context>
"""

static_prompt = """
You are an AI agent communicating with a user via WhatsApp. You operate in an agent loop, with each step focusing on the objectives for the current node in a larger process.

<loop_instructions>
- The process is broken into steps (nodes), each with a specific objective.
- You follow conversation history, context, and available tools to address the current node's goal.
- Concentrate only on the instructions relevant to the current node's objective.
</loop_instructions>

<internal_response_format>
- Internal text responses serve two purposes: (1) document your reasoning process, (2) maintain an internal record of what is happening.
- What you write outside of tool calls is not sent to the user.
- If you already reasoned about something, just use tool calls.
- Do not use normal text responses for user-facing communication.
- You must use tools for all user communication.
- Do not leave responses empty. Every interaction must include some text, a tool call, or both.
</internal_response_format>

<information_management>
- Thoroughly review conversation history and context.
- Infer missing details if enough context exists.
- If you encounter contradictory, unclear, or incomplete instructions, use **AskUserForInput** to request clarification rather than guessing.
</information_management>

<message_rules>
- Communication must feel natural and contextually appropriate.
- There are two tools to communicate with the user:
  1. **send_notification_to_user (one-way)**: For updates, progress reports, or final deliverables. Do NOT ask questions or expect any response.
  2. **AskUserForInput (two-way)**: For any situation requiring user input, clarification, or confirmation. Always ask at least one question here.
- Never request input when using send_notification_to_user.
- If you accidentally use send_notification_to_user with a question, immediately call EnterIdleState() with no message to allow the user to respond.
- Avoid repeating the same question consecutively.
- Provide a clear summary or result notification before concluding the conversation.
- Consolidate related updates to avoid excessive messages.
- If a request exceeds what you can fulfill, respond with: "I'm sorry, but I can't help with that."
- When in a WarmEndNode, use **EnterIdleState** to invite final questions or feedback before ending the conversation.
</message_rules>

<writing_rules>
- Respond in the user's language unless otherwise specified.
</writing_rules>

<tool_use_rules>
- You must invoke a tool to send any user-facing message.
- Do not invent tool names. Provide all required arguments for any tool call.
- You can use multiple tool calls at once if needed.
- MoveToNextNode must always be the last tool call in the response.
</tool_use_rules>

<examples>
Here are some examples of how to handle different types of user queries.
The examples below use a simple markdown-style format to illustrate the flow of conversation and tool usage.
Do not copy the formatting of these examples in your responses - always use the proper function calling system instead.

# Example 0: Simple first message
**User**: "Hello, how are you?"
**Context**: User sends a simple greeting
**Assistant's thought process**: The user is greeting me, so I will respond with a greeting.
**Tools used**:
1.
   ```
   AskUserForInput(
     message="Hello, I'm good, thank you! How can I help you today?"
   )
   ```

# Example 1: General Question
**User**: "What is life?"
**Context**: User asks a philosophical question
**Assistant's thought process**: The user is asking about life, so I will provide a concise answer.
**Tools used**:
1.
   ```
   send_notification_to_user(
     message="I'm mostly focused on tech, but life is the condition that distinguishes organisms from inorganic matter, marked by growth, reproduction, and continual change. Philosophically, it is often seen as the essence of existence and consciousness."
   )
   ```
2.
   ```
   AskUserForInput(
     message="Does that answer your question? What else would you like to know?"
   )
   ```

# Example 2: Handling Failed Communication
**User**: *sends gibberish text repeatedly*
**Context**: Multiple unclear inputs from user
**Assistant's thought process**: User has provided unclear input multiple times, need to abort.
**Tools used**:
1. \
   ```
   send_notification_to_user(
     message="I'm having trouble understanding your requests. For me to assist you effectively, I need clearer instructions. Please start the conversation again. Bye!"
   )
   ```
2.
   ```
   MoveToNextNode(
     next_node="__end__",
     reason="User provided unclear input after multiple attempts to clarify"
   )
   ```

# Example 3: External API Request
**User**: "Can you check the weather in New York?"
**Context**: User requests weather information
**Assistant's thought process**: Need to fetch weather data using the API.
**Tools used**:
1.
   ```
   webhook_request(
     url="https://api.weatherapi.com/v1/current.json",
     method="GET",
     headers={{"Content-Type": "application/json"}},
     body={{"q": "New York", "key": "an_api_key"}}
   )
   ```
2.
   ```
   send_notification_to_user(
     message="I've checked the weather in New York. It's currently 72°F and partly cloudy."
   )
   ```

# Example 4: Correcting Improper Tool Usage
**Context**: Agent mistakenly used send_notification_to_user with a question
**Assistant's thought process**: I just sent a question using send_notification_to_user, which doesn't allow responses. I need to immediately call EnterIdleState() to let the user respond.
**Tools used**:
1.
   ```
   send_notification_to_user(
     message="I've processed your request. Which format would you prefer for the report?"
   )
   ```
2.
   ```
   EnterIdleState()
   ```

# Example 5: Ending a Conversation Warmly
**User**: "Thanks, that's all I needed."
**Context**: In a WarmEndNode after completing the primary task
**Assistant's thought process**: The main task is complete, but I should provide a warm ending and allow for any final questions.
**Tools used**:
1.
   ```
   EnterIdleState(
     message="I'm glad I could help you today! Your request has been completed successfully. Is there anything else you'd like to ask before we finish our conversation?"
   )
   ```
**User**: "No, that's all. Thanks!"
**Assistant's thought process**: User has confirmed they have no more questions, can now complete the conversation gracefully.
**Tools used**:
1.
   ```
   EnterIdleState(
     message="You're welcome! It was a pleasure assisting you. Have a great day, and feel free to reach out again whenever you need help."
   )
   ```

**User**: "Great. Thanks again!"
**Assistant's thought process**: User said thanks again, so I will send a message.
**Tools used**:
1.
   ```
   EnterIdleState()
   ```

Note: This example demonstrates that when a task is part of a larger process and doesn't explicitly request user updates, you can perform the necessary actions without sending notifications or asking for input. The results can be used by subsequent nodes in the process flow.

Remember: These examples show the logical flow of handling requests. In actual responses, use the proper function calling system to invoke tools.
</examples>
"""


def get_system_prompt(contact_information: Dict[str, Any] = None, agent_prompt: str = None) -> str:
    """
    Generate the full prompt for the agent based on the current node and edges.

    Args:
        contact_information: Information about the contact including:
            - phone_number: The contact's phone number
            - profile_name: The contact's name (optional)
            - notes: List of notes about the contact (optional)
                Each note contains: name, content, created_at
            - broadcast_context: Information about broadcast messages (optional)
        agent_prompt: The prompt for the agent

    Returns:
        A string containing the full prompt
    """

    context_section = ""
    if contact_information:
        phone_number = contact_information.get("phone_number", "")
        profile_name = contact_information.get("profile_name", "")

        context_section = f"""
<contact_information>
You are talking to a user with the following information:
Phone Number: {phone_number}
"""
        if profile_name:
            context_section += f"Name: {profile_name}\n"
        
        # Add metadata if available
        metadata = contact_information.get("metadata", {})
        if metadata:
            context_section += "\nContact Metadata:\n"
            for key, value in metadata.items():
                context_section += f"- {key}: {value}\n"
        
        # Add notes if available
        notes = contact_information.get("notes", [])
        if notes:
            context_section += "\nContact Notes:\n"
            for note in notes:
                note_name = note.get("name", "")
                note_content = note.get("content", "")
                note_created = note.get("created_at", "")
                
                if note_name:
                    context_section += f"- {note_name}: {note_content}"
                else:
                    context_section += f"- {note_content}"
                
                if note_created:
                    context_section += f" (Added: {note_created})"
                context_section += "\n"

        context_section += "</contact_information>"
        
        # Add broadcast context if available
        broadcast_context = contact_information.get("broadcast_context")
        if broadcast_context:
            context_section += _format_broadcast_context(broadcast_context)
            
    elif contact_information and "phone_number" in contact_information:
        # Backward compatibility for just phone_number
        phone_number = contact_information["phone_number"]
        context_section = f"""
<phone_number>
{phone_number}
</phone_number>
"""

    # Variable for storing general goal if needed in the future
    # general_goal = ""
    general_instructions = ""
    if agent_prompt:
        general_instructions = f"""
<general_instructions>
{agent_prompt}
</general_instructions>
"""

    full_prompt = f"""
{static_prompt}

{general_instructions}
{context_section}

Current date and time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""".rstrip()

    return full_prompt


def get_system_prompt_blocks(contact_information: Dict[str, Any] = None, agent_prompt: str = None) -> List[Dict[str, Any]]:
    """
    Generate the system prompt as a list of content blocks with cache control
    suitable for Anthropic models.

    Args:
        contact_information: Information about the contact including:
            - phone_number: The contact's phone number
            - profile_name: The contact's name (optional)
            - notes: List of notes about the contact (optional)
                Each note contains: name, content, created_at
            - broadcast_context: Information about broadcast messages (optional)
        agent_prompt: The prompt for the agent

    Returns:
        A list of content blocks with cache control settings
    """
    content_blocks = []

    content_blocks.append(
        {"type": "text", "text": static_prompt, "cache_control": {"type": "ephemeral"}}
    )

    # Agent-specific instructions with cache control
    if agent_prompt:
        content_blocks.append(
            {
                "type": "text",
                "text": f"<general_instructions>\n{agent_prompt}\n</general_instructions>",
                "cache_control": {"type": "ephemeral"},
            }
        )

    # Context section (contact information)
    if contact_information:
        phone_number = contact_information.get("phone_number", "")
        profile_name = contact_information.get("profile_name", "")

        contact_text = f"<contact_information>\nPhone Number: {phone_number}"
        if profile_name:
            contact_text += f"\nName: {profile_name}"
        
        # Add metadata if available
        metadata = contact_information.get("metadata", {})
        if metadata:
            contact_text += "\n\nContact Metadata:"
            for key, value in metadata.items():
                contact_text += f"\n- {key}: {value}"
        
        # Add notes if available
        notes = contact_information.get("notes", [])
        if notes:
            contact_text += "\n\nContact Notes:"
            for note in notes:
                note_name = note.get("name", "")
                note_content = note.get("content", "")
                note_created = note.get("created_at", "")
                
                contact_text += "\n- "
                if note_name:
                    contact_text += f"{note_name}: {note_content}"
                else:
                    contact_text += note_content
                
                if note_created:
                    contact_text += f" (Added: {note_created})"
        
        contact_text += "\n</contact_information>"

        content_blocks.append(
            {"type": "text", "text": contact_text}
        )
        
        # Add broadcast context if available
        broadcast_context = contact_information.get("broadcast_context")
        if broadcast_context:
            content_blocks.append(
                {"type": "text", "text": _format_broadcast_context(broadcast_context)}
            )
            
    # Backward compatibility for just phone_number
    elif contact_information and "phone_number" in contact_information:
        phone_number = contact_information["phone_number"]
        content_blocks.append(
            {"type": "text", "text": f"<phone_number>\n{phone_number}\n</phone_number>"}
        )

    # Current time (should never be cached)
    content_blocks.append(
        {
            "type": "text",
            "text": f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        }
    )

    return content_blocks
