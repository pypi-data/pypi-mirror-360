import os
import json
import argparse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from google import genai
import tiktoken
import re

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
model = "gemini-2.0-flash"

class DocumentChunker:
    def __init__(self, max_tokens=3000, overlap=200):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def split_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into chunks with overlap"""
        if self.count_tokens(text) <= self.max_tokens:
            return [text]
        
        sentences = self.split_by_sentences(text)
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Add overlap from the end of current chunk
                    overlap_sentences = self.get_overlap_sentences(current_chunk)
                    current_chunk = overlap_sentences + " " + sentence
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    # Single sentence too long, add it anyway
                    chunks.append(sentence)
                    current_chunk = ""
                    current_tokens = 0
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_overlap_sentences(self, chunk: str) -> str:
        """Get last few sentences for overlap"""
        sentences = self.split_by_sentences(chunk)
        overlap_text = ""
        tokens = 0
        
        for sentence in reversed(sentences):
            sentence_tokens = self.count_tokens(sentence)
            if tokens + sentence_tokens > self.overlap:
                break
            overlap_text = sentence + " " + overlap_text
            tokens += sentence_tokens
        
        return overlap_text.strip()

class SmartQuestionGenerator:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model = model_name
        self.client = client
    
    def generate_comprehensive_questions(self, chunk: str) -> List[str]:
        """Generate as many relevant questions as possible from the content"""
        
        question_instruction = """Extract EVERY possible question that can be answered from this text. Your goal is to create a comprehensive question dataset that covers all information in the content.

            EXTRACTION STRATEGY:
            1. Read through the entire text systematically
            2. Generate questions for EVERY fact, concept, process, relationship, and detail mentioned
            3. Create questions at multiple levels: basic facts, deeper understanding, analysis, implications
            4. Don't limit yourself - extract as many unique questions as the content supports
            5. Continue until you've exhausted all questionable content from the text
            6. Each question should test a different piece of information or understanding

            QUESTION TYPES TO INCLUDE:
            - Factual questions (who, what, when, where)
            - Conceptual questions (why, how does this work)
            - Analytical questions (what are the implications, relationships)
            - Comparative questions (how does X compare to Y)
            - Process questions (how is this done, what are the steps)
            - Application questions (how would this be used)
            - Definitional questions (what is the meaning of X)
            - Causal questions (what causes X, what are the effects)"""
        
        prompt = f"""
        Based on the following text, {question_instruction}

        TEXT:
        {chunk}

        COMPREHENSIVE QUESTION GENERATION RULES:
        1. Generate AS MANY questions as possible that can be answered from this text
        2. Each question must be unique and test different information
        3. Focus on ONE specific concept/fact per question
        4. Use clear, direct language
        5. End each question with a question mark
        6. Avoid compound questions (no "and", "or" connecting multiple ideas)
        7. Make questions contextually specific to this content
        8. Include variety: what, why, how, when, where, who questions
        9. Extract questions until no more meaningful questions can be formed
        10. Prioritize question coverage over arbitrary limits

        Your mission is to create a comprehensive question dataset - generate as many as the content supports!

        FORMAT: Return as JSON array of question strings only.
        """
        
        try:
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            questions_text = response.text
            
            # Extract JSON array
            json_start = questions_text.find('[')
            json_end = questions_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                questions_json = questions_text[json_start:json_end]
                questions = json.loads(questions_json)
                print(f"Generated {len(questions)} questions from chunk")
                return questions
            else:
                print("No valid JSON array found in response")
                return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []

class AnswerGenerator:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model = model_name
        self.client = client
    
    def generate_answers(self, chunk: str, questions: List[str]) -> List[str]:
        """Generate answers for questions"""
        prompt = f"""
        Based on the following text, provide thorough answers to each question.
        
        TEXT:
        {chunk}
        
        QUESTIONS:
        {json.dumps(questions)}
        
        ANSWER REQUIREMENTS:
        1. Each answer must be exactly 4-5 sentences long
        2. Provide detailed explanations with context from the text
        3. Include supporting evidence or reasoning
        4. Make answers self-contained and complete
        5. Use clear, informative language
        6. Start each answer with "Answer: " followed by your explanation
        
        FORMAT: 
        - Separate each answer with "---" on its own line
        - Don't repeat the questions in your response
        - Keep answers focused and comprehensive
        """
        
        try:
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            answers_text = response.text.strip()
            answer_list = answers_text.split('---')
            processed_answers = []
            
            for answer in answer_list:
                cleaned_answer = answer.strip()
                if cleaned_answer.startswith("Answer:"):
                    cleaned_answer = cleaned_answer[7:].strip()
                if cleaned_answer:
                    processed_answers.append(cleaned_answer)
            
            return processed_answers
        except Exception as e:
            print(f"Error generating answers: {e}")
            return []

class FormatConverter:
    @staticmethod
    def to_alpaca(question: str, answer: str, source_doc: str = "") -> Dict:
        """Convert to Alpaca format"""
        return {
            "instruction": question,
            "input": "",
            "output": answer,
            "source_document": source_doc
        }
    
    @staticmethod
    def to_chatml(question: str, answer: str, source_doc: str = "") -> Dict:
        """Convert to ChatML format"""
        return {
            "messages": [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ],
            "source_document": source_doc
        }
    
    @staticmethod
    def to_conversation(question: str, answer: str, source_doc: str = "") -> Dict:
        """Convert to conversation format"""
        return {
            "conversations": [
                {"from": "human", "value": question},
                {"from": "gpt", "value": answer}
            ],
            "source_document": source_doc
        }

class DuplicateDetector:
    def __init__(self, similarity_threshold=0.85):
        self.similarity_threshold = similarity_threshold
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def find_duplicates(self, questions: List[str]) -> List[List[int]]:
        """Find semantic duplicates using embeddings"""
        if len(questions) < 2:
            return []
        
        print(f"Checking for semantic duplicates among {len(questions)} questions...")
        embeddings = self.sentence_model.encode(questions)
        similarity_matrix = cosine_similarity(embeddings)
        
        duplicate_groups = []
        processed = set()
        
        for i in range(len(questions)):
            if i in processed:
                continue
                
            similar_indices = [i]
            for j in range(i + 1, len(questions)):
                if j not in processed and similarity_matrix[i][j] >= self.similarity_threshold:
                    similar_indices.append(j)
            
            if len(similar_indices) > 1:
                duplicate_groups.append(similar_indices)
                processed.update(similar_indices)
        
        return duplicate_groups
    
    def remove_duplicates(self, qa_pairs: List[Dict]) -> List[Dict]:
        """Remove duplicate Q&A pairs"""
        if not qa_pairs:
            return qa_pairs
        
        # Extract questions based on format
        questions = []
        for qa in qa_pairs:
            if "instruction" in qa:
                questions.append(qa["instruction"])
            elif "messages" in qa:
                questions.append(qa["messages"][0]["content"])
            elif "conversations" in qa:
                questions.append(qa["conversations"][0]["value"])
            else:
                questions.append("")
        
        duplicate_groups = self.find_duplicates(questions)
        
        if not duplicate_groups:
            return qa_pairs
        
        indices_to_remove = set()
        for group in duplicate_groups:
            # Keep the first one, remove the rest
            indices_to_remove.update(group[1:])
        
        cleaned_pairs = [qa_pairs[i] for i in range(len(qa_pairs)) if i not in indices_to_remove]
        
        print(f"Removed {len(indices_to_remove)} duplicate questions")
        return cleaned_pairs

def process_document(file_path: str, output_file: str, args) -> bool:
    """Process a single document"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Initialize components
        chunker = DocumentChunker()
        question_gen = SmartQuestionGenerator()
        answer_gen = AnswerGenerator()
        format_converter = FormatConverter()
        
        # Chunk the document
        chunks = chunker.chunk_document(content)
        print(f"Split document into {len(chunks)} chunks")
        
        all_qa_pairs = []
        total_questions = 0
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            
            # Generate comprehensive questions
            questions = question_gen.generate_comprehensive_questions(chunk)
            total_questions += len(questions)
            
            # Generate answers
            answers = answer_gen.generate_answers(chunk, questions)
            
            # Create Q&A pairs
            for question, answer in zip(questions, answers):
                if question and answer:
                    # Validate answer length
                    sentence_count = len([s for s in answer.split(".") if s.strip()])
                    if 3 <= sentence_count <= 6:
                        # Convert to specified format
                        if args.format == "alpaca":
                            qa_pair = format_converter.to_alpaca(
                                question, answer, os.path.basename(file_path)
                            )
                        elif args.format == "chatml":
                            qa_pair = format_converter.to_chatml(
                                question, answer, os.path.basename(file_path)
                            )
                        elif args.format == "conversation":
                            qa_pair = format_converter.to_conversation(
                                question, answer, os.path.basename(file_path)
                            )
                        
                        all_qa_pairs.append(qa_pair)
        
        # Remove duplicates (enabled by default)
        detector = DuplicateDetector(args.similarity_threshold)
        initial_count = len(all_qa_pairs)
        all_qa_pairs = detector.remove_duplicates(all_qa_pairs)
        print(f"Kept {len(all_qa_pairs)} out of {initial_count} Q&A pairs after duplicate removal")
        
        # Save to file
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.extend(all_qa_pairs)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {len(all_qa_pairs)} Q&A pairs from {total_questions} total questions for {file_path}")
        return True
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Sysgen - High-quality synthetic datasets creating Tool")
    
    # Input/Output
    parser.add_argument("--input-folder", type=str, default="md", help="Folder containing markdown files")
    parser.add_argument("--output", type=str, default="output.json", help="Output JSON file")
    
    # Format options
    parser.add_argument("--format", type=str, choices=["alpaca", "chatml", "conversation"], 
                       default="alpaca", help="Output format")
    
    # Duplicate handling
    parser.add_argument("--similarity-threshold", type=float, default=0.85, help="Similarity threshold for duplicates")
    
    args = parser.parse_args()
    
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is required")
        return
    
    # Find markdown files
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder {args.input_folder} does not exist")
        return
    
    md_files = [f for f in os.listdir(args.input_folder) if f.endswith(('.md', '.txt'))]
    
    if not md_files:
        print(f"No markdown/text files found in {args.input_folder}")
        return
    
    print(f"Found {len(md_files)} files to process")
    print(f"Format: {args.format}")
    print(f"Chunk size: 3000 tokens (default)")
    print(f"Overlap: 200 tokens (default)")
    print("Duplicate removal: Enabled (default)")
    
    # Process files
    total_qa_pairs = 0
    for md_file in md_files:
        file_path = os.path.join(args.input_folder, md_file)
        print(f"\nProcessing {md_file}")
        
        success = process_document(file_path, args.output, args)
        
        if success:
            print(f"Completed {md_file}")
            # Count current total
            if os.path.exists(args.output):
                with open(args.output, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
                    total_qa_pairs = len(current_data)
        else:
            print(f"Failed to process {md_file}")
    
    print(f"\nProcessing complete!")
    print(f"Total Q&A pairs generated: {total_qa_pairs}")
    print(f"Output saved to {args.output}")

if __name__ == "__main__":
    main()