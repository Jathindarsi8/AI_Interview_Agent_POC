# main_interviewer.py

from input_parser import parse_job_post, parse_company_profile, parse_resume
from ai_question_generator import generate_interview_questions
import json # For saving the transcript later (optional for now, but good to import)
import datetime # To timestamp the transcript filename (optional)

def run_interview_session(): # Renamed function for clarity
    """
    Main function to parse inputs, generate questions, and conduct a text-based interview.
    """
    print("Starting AI Interview Agent - Session...")

    job_post_file = "inputs/job_post_sample.txt"
    company_profile_file = "inputs/company_profile_sample.txt"
    resume_file = "inputs/resume_sample.txt"

    print(f"\nParsing job post from: {job_post_file}")
    job_details = parse_job_post(job_post_file)
    if not job_details:
        print("Failed to parse job post. Exiting.")
        return

    print(f"\nParsing company profile from: {company_profile_file}")
    company_details = parse_company_profile(company_profile_file)
    if not company_details:
        print("Failed to parse company profile. Exiting.")
        return

    print(f"\nParsing resume from: {resume_file}")
    resume_details = parse_resume(resume_file)
    if not resume_details:
        print("Failed to parse resume. Exiting.")
        return

    print("\nAll input documents parsed successfully!")

    print("\nGenerating interview questions using AI...")
    num_questions_to_generate = 7 
    ai_questions = generate_interview_questions(
        job_details,
        company_details,
        resume_details,
        num_questions=num_questions_to_generate
    )

    if not ai_questions: # Check if ai_questions is None or empty
        print("\nFailed to generate interview questions or no questions were returned. Please check previous error messages.")
        print("\nInterview session cannot proceed without questions.")
        return # Exit if no questions

    print(f"\n--- AI Generated Interview Questions ({len(ai_questions)} questions received) ---")
    for i, question in enumerate(ai_questions):
        print(f"({i+1}) {question}") # Just show the questions first (optional)
    
    # --- NEW: Interactive Q&A Session ---
    print("\n--- Starting Interactive Interview Session ---")
    print("The AI Interviewer will ask you questions. Type your answer and press Enter.")
    print("Type 'quit' as an answer to end the interview early.")
    
    interview_transcript = [] # To store Q&A pairs

    for i, question_text in enumerate(ai_questions):
        print(f"\nAI Interviewer (Question {i+1}/{len(ai_questions)}):")
        print(f"{question_text}")
        
        candidate_answer = input("Your Answer: ")
        
        if candidate_answer.lower() == 'quit':
            print("Interview ended by user.")
            break
            
        interview_transcript.append({
            "question_number": i + 1,
            "question": question_text,
            "answer": candidate_answer
        })

    print("\n--- Interview Session Ended ---")

    # --- NEW: Display and Save Transcript ---
    if interview_transcript:
        print("\n--- Interview Transcript ---")
        for qa_pair in interview_transcript:
            print(f"\nQ{qa_pair['question_number']}: {qa_pair['question']}")
            print(f"A: {qa_pair['answer']}")
        
        # Optional: Save transcript to a JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_filename = f"interview_transcript_{timestamp}.json"
        try:
            with open(transcript_filename, 'w', encoding='utf-8') as f:
                json.dump(interview_transcript, f, indent=4, ensure_ascii=False)
            print(f"\nInterview transcript saved to: {transcript_filename}")
        except Exception as e:
            print(f"\nError saving transcript: {e}")
            
    elif not ai_questions: # This case should be caught earlier
        pass # No transcript to show if no questions were generated
    else:
        print("\nNo answers were recorded in the transcript (interview might have been quit immediately or had no questions).")


    print("\nAI Interview Agent session complete.")

if __name__ == '__main__':
    run_interview_session() # Changed to call the renamed function