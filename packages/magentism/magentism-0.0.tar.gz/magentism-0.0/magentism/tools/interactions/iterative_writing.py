import os
from langchain_core.messages import SystemMessage, HumanMessage, ChatMessage
from models.bots import Bot
from .get_user_input import get_user_input


def iterative_document_writer(document_path: str, document_type: str = None, max_iterations: int = None):
    """
    Collaboratively write or improve a document through iterative Q&A sessions.
    
    This function uses an AI assistant to identify gaps in a document and ask targeted
    questions to gather missing information. It then integrates the answers to create
    a more complete document. The process repeats until the user stops providing answers.
    
    Args:
        document_path (str): Path to the document file. If the file doesn't exist,
                           a new document will be created. If it exists, the content
                           will be iteratively improved.
        document_type (str, optional): Description of what type of document this is
                                     (e.g., "functional specification", "project plan",
                                     "research paper"). If not provided, will be inferred
                                     from the filename by removing underscores and extension.
        max_iterations (int, optional): Maximum number of questions the assistant will ask the user
    
    Returns:
        None: The function prints the updated document content after each iteration
              and continues until the user provides an empty response.
    
    Example:
        >>> iterative_document_writer("/tmp/project_spec.md", "project specification")
        >>> iterative_document_writer("/tmp/meeting_notes.txt")  # type inferred as "meeting notes"
    """
    if not document_type:
        document_type = os.path.basename(document_path).split(".")[0].replace("_", " ")
    
    bot = Bot("mistral")
    
    # Load existing document content if file exists
    current_content = None
    if os.path.isfile(document_path):
        with open(document_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
    
    # Load previous conversation if available
    

    # Main iterative improvement loop
    i = 0
    while max_iterations is None or i < max_iterations:
        i += 1
        # Generate a targeted question based on current state
        if current_content:
            # Ask about existing document gaps
            question_response = bot.invoke([
                SystemMessage(content=f"""You are reviewing a {document_type} document to identify the most critical missing information.

Your task:
1. Analyze the document to find the single most important gap or missing element
2. The document's final comment (<!-- -->) is a transcript of the conversation that led to the writing of the document; use it make your question integrate into the conversation flow; user responses (👤) can be seen as instructions
3. DO NOT ask a question if:
   - The same or similar question has already been asked
   - The topic is already addressed in the document content (even if marked as "to be done later", "à voir plus tard", "will be addressed", etc.)
   - The document explicitly mentions the topic will be covered separately or later
4. Look for genuinely missing information that has NOT been discussed or acknowledged
5. Ask ONE specific, actionable question that would help fill a real gap
6. Use the same language as the document
7. Output only the question - no explanations or preamble

Focus on gaps that would significantly improve the document's completeness and usefulness, but avoid topics that are already planned or deferred."""),
                HumanMessage(content=current_content),
            ])
        else:
            # Initial question for new document
            question_response = bot.invoke([
                SystemMessage(content=f"""You are helping a user start writing a {document_type}.

Your task:
1. Ask ONE strategic question whose answer will provide a strong foundation for the document
2. Focus on the most essential information needed to begin
3. Use the same language as the user
4. Output only the question - no explanations or preamble"""),
                HumanMessage(content=document_type),
            ])
        
        question = question_response.content.strip()
        
        # Get user's answer
        user_answer = get_user_input(question)
        if not user_answer or not user_answer.strip():
            break
        
        # Integrate the new information into the document
        comments = ""
        if current_content:
            if "<!--" in current_content:
                current_content, comments = current_content.split("<!--", 1)
                current_content = current_content.strip()
                comments = comments.split("-->")[0].strip()
            # Update existing document
            integration_response = bot.invoke([
                SystemMessage(content=f"""You must integrate new information into an existing {document_type}.

Context:
- Question asked: {question}
- User's answer: {user_answer}

Your task:
1. Always integrate the user's answer into the existing document
2. Maintain the original language and style of the document
3. Ensure logical flow and coherence
4. The document must be well-structured (split long sections with titles) and coherent
5. Do not infer: what you write must directly derive from the user's input
6. Output ONLY the complete updated document - no commentary

The user will provide the current document next."""),
                HumanMessage(content=current_content),
            ])
        else:
            # Create new document
            integration_response = bot.invoke([
                SystemMessage(content=f"""Create a {document_type} that incorporates the user's response.

Context:
- Question asked: {question}
- User's answer: {user_answer}

Your task:
1. Draft a well-structured {document_type} that incorporates this information
2. Use the same language as the user's answer
3. Create a professional, coherent document structure
4. Do not infer: what you write must directly derive from the user's input
5. Output ONLY the document content - no commentary

The user will send a trigger message next."""),
                HumanMessage(content="?")
            ])
        
        current_content = f"{integration_response.content.strip()}\n\n\n\n<!--\n\n{comments}\n\n🤖\n{question}\n\n👤\n{user_answer}\n\n-->\n"
        open(document_path, "w").write(current_content)
        print()


if __name__ == "__main__":
    # iterative_document_writer("/tmp/functional_specifications.md", "cahier des charges fonctionnel (pas technique); commençons par décrire le projet")
    import sys
    iterative_document_writer(sys.argv[1], sys.argv[2])
