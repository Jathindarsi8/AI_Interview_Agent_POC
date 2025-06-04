# ai_question_generator.py

import google.generativeai as genai
import os # For potentially using environment variables later

# --- STEP 1: API KEY CONFIGURATION ---
# This is the standard placeholder string. DO NOT CHANGE THIS LINE.
API_KEY_PLACEHOLDER = "YOUR_GEMINI_API_KEY_GOES_HERE" 

# YOUR ACTUAL API KEY IS PLACED DIRECTLY HERE:
# Replace the example key below with your actual key if it's different.
actual_api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # <<< Your specific API Key

try:
    # This check sees if 'actual_api_key' is different from the placeholder
    if actual_api_key == API_KEY_PLACEHOLDER or not actual_api_key: 
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("WARNING: API Key is either the placeholder or empty.")
        print(f"Please ensure the 'actual_api_key' variable in the script is set to your real API key.")
        print(f"It is currently set to: '{actual_api_key}'")
        print("The script will likely fail or use a non-functional key if not updated correctly.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        # Attempt to configure anyway, it will likely fail if key is bad/placeholder
        genai.configure(api_key=actual_api_key) 
    else:
        # This block SHOULD execute if your key is correctly entered above
        genai.configure(api_key=actual_api_key)
        print("Gemini API key configured successfully with your provided key.")

except Exception as e:
    print(f"Error during initial Gemini API configuration: {e}")
    print("This might be due to an issue with the API key format or other setup problems.")
    # Set a flag or raise an error to prevent further execution if critical
    # For now, subsequent calls will likely fail if this part errors out.


def generate_interview_questions(job_details, company_details, resume_details, num_questions=5):
    """
    Generates interview questions using the Gemini API based on parsed data.
    """
    # This check is important! It ensures the calling code provides the necessary data.
    if not job_details or not company_details or not resume_details:
        print("Error: Missing input data for question generation. One or more detail objects are None or empty.")
        return None # Return None to indicate failure

    prompt_parts = [
        "You are an expert AI interviewer. Your task is to generate insightful interview questions.",
        "Based on the following job description, company profile, and candidate resume, please generate",
        f"{num_questions} personalized interview questions. The questions should aim to assess the candidate's suitability",
        "for the role, their alignment with company values, and delve deeper into their listed experiences and skills.",
        "Format each question on a new line, starting with '- '. Do not include any other introductory or concluding text, only the questions.",
        "\n--- JOB DESCRIPTION ---",
        f"Job Title: {job_details.get('title', 'N/A')}",
        f"Description: {job_details.get('description', 'N/A')}",
        "Responsibilities:",
        *[f"  - {resp}" for resp in job_details.get('responsibilities', [])],
        "Requirements:",
        *[f"  - {req}" for req in job_details.get('requirements', [])],
        
        "\n--- COMPANY PROFILE ---",
        f"Company Name: {company_details.get('company_name', 'N/A')}",
        f"Mission: {company_details.get('mission', 'N/A')}",
        f"Vision: {company_details.get('vision', 'N/A')}",
        "Core Values:",
        *[f"  - {val}" for val in company_details.get('core_values', [])],

        "\n--- CANDIDATE RESUME ---",
        f"Candidate Name: {resume_details.get('name', 'N/A')}",
        f"Candidate Summary: {resume_details.get('summary', 'N/A')}",
        "Candidate Experience:",
        *[f"  - {exp.get('title_company_date', 'N/A')}: {', '.join(exp.get('description', []))}" for exp in resume_details.get('experience', [])],
        "Candidate Education:",
        *[f"  - {edu}" for edu in resume_details.get('education', [])],
        "Candidate Skills:",
        *[f"  - {skill}" for skill in resume_details.get('skills', [])],
        
        "\n--- INTERVIEW QUESTIONS ---" 
    ]
    prompt = "\n".join(prompt_parts)
    
    try:
        # The API key is configured globally. If 'genai.configure' failed earlier,
        # this call will likely raise an exception caught below.
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        
        if not response.parts: 
            block_reason_message = "Unknown reason or no specific block message."
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                block_reason_message = response.prompt_feedback.block_reason_message
            elif hasattr(response, 'candidates') and response.candidates and response.candidates[0].finish_reason != 'STOP':
                 block_reason_message = f"Generation stopped. Reason: {response.candidates[0].finish_reason.name}"

            print(f"Warning: Prompt was blocked or an empty response was received. Reason: {block_reason_message}")
            return [f"Error: Prompt blocked by safety filter or empty response - {block_reason_message}"]
        
        generated_text = response.text 
        questions = [q[2:].strip() for q in generated_text.splitlines() if q.strip().startswith("- ")]
        
        if not questions and generated_text: 
            questions = [q.strip() for q in generated_text.splitlines() if q.strip() and len(q.strip()) > 5] 
        
        if not questions: 
            print(f"Warning: Could not parse specific questions from LLM response. Ensure the model is following prompt format.")
            print(f"LLM Raw Response (first 300 chars): {generated_text[:300]}...")
            return ["Error: No usable questions from LLM."] if not generated_text else [generated_text]

        return questions
        
    except Exception as e:
        print(f"An error occurred during the Gemini API call: {e}")
        return None 


if __name__ == '__main__':
    print("Testing AI Question Generator with real API call (using dummy input data)...")

    # Dummy data for testing - THIS MUST BE COMPLETE
    dummy_job_details = {
        "title": "Senior Python Developer",
        "description": "Looking for an experienced Python developer to lead innovative projects and mentor junior team members in a fast-paced agile environment.",
        "responsibilities": ["Lead development of new features", "Mentor junior developers", "Design scalable software architecture", "Write and review high-quality code"],
        "requirements": ["5+ years Python experience", "Strong understanding of Django/Flask", "Experience with cloud platforms (AWS/GCP)", "Excellent problem-solving skills", "Proven leadership abilities"]
    }
    dummy_company_details = {
        "company_name": "FutureTech Solutions",
        "mission": "To empower businesses with next-generation AI and cloud technologies.",
        "vision": "To be the leading global partner for digital transformation and intelligent automation.",
        "core_values": ["Innovation", "Customer Obsession", "Integrity", "Collaboration", "Continuous Learning"]
    }
    dummy_resume_details = {
        "name": "Alex Wren",
        "summary": "A highly skilled and results-oriented Senior Python Developer with 8 years of experience in designing, developing, and deploying robust applications. Proven ability to lead projects and deliver high-quality software solutions.",
        "experience": [
            {"title_company_date": "Lead Python Developer - Innovatech Ltd (2020 - Present)", "description": ["Led a team of 5 developers on a flagship AI product.", "Architected and implemented a new microservices backend.", "Reduced API latency by 30%"]},
            {"title_company_date": "Software Engineer - Data Systems Co. (2017 - 2020)", "description": ["Developed data processing pipelines using Python and Spark.", "Contributed to multiple successful product releases."]}
        ],
        "education": ["MSc in Advanced Computer Science - Tech University (2017)", "BSc Computer Engineering - State College (2015)"],
        "skills": ["Python", "Django", "Flask", "FastAPI", "AWS", "Docker", "Kubernetes", "Microservices", "Agile", "CI/CD", "Leadership", "Problem Solving"]
    }

    # Check if 'actual_api_key' (defined at the very top) is not the placeholder
    api_key_is_set_correctly = False
    if 'actual_api_key' in globals() and actual_api_key and actual_api_key != API_KEY_PLACEHOLDER:
        api_key_is_set_correctly = True
    
    if api_key_is_set_correctly:
        # The initial print statement "Gemini API key configured successfully..." should confirm the key was passed to genai.configure()
        # Now we directly call the function with the dummy data.
        generated_questions = generate_interview_questions(
            dummy_job_details,
            dummy_company_details,
            dummy_resume_details,
            num_questions=7 
        )

        if generated_questions:
            print("\n--- AI Generated Interview Questions ---")
            for i, q in enumerate(generated_questions):
                print(f"{i+1}. {q}")
        else:
            # This 'else' could be triggered if generate_interview_questions returns None (due to missing input data or API error)
            print("\nNo questions were generated by the function, or an error occurred during the API call.")
            print("Check for earlier error messages from 'generate_interview_questions' or the API call itself.")
    else:
        print("\nSkipped actual question generation because the 'actual_api_key' variable at the top of the script")
        print("is still the placeholder or empty. Please set your real API key there.")
