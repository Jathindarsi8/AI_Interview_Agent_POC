# analyze_transcript.py

import json
import glob # To find files matching a pattern (e.g., the latest transcript)
import os

def load_latest_transcript(directory="."):
    """
    Finds and loads the most recent interview transcript JSON file from the given directory.
    """
    try:
        # List all files matching the pattern
        transcript_files = glob.glob(os.path.join(directory, "interview_transcript_*.json"))
        if not transcript_files:
            print("No transcript files found in the directory.")
            return None
        
        # Find the most recent file based on modification time or name (name implies time here)
        latest_file = max(transcript_files, key=os.path.getmtime)
        print(f"Loading transcript from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        return transcript_data
    except FileNotFoundError:
        print(f"Error: Could not find the transcript file: {latest_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the transcript file: {latest_file}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading the transcript: {e}")
        return None

def analyze_transcript_data(transcript):
    """
    Performs basic analysis on the loaded transcript data.
    """
    if not transcript:
        print("No transcript data to analyze.")
        return None

    num_questions_answered = len(transcript)
    total_words_in_answers = 0
    short_answer_threshold = 5 # Define what we consider a "short" answer
    short_answers_found = 0
    
    print("\n--- Basic Transcript Analysis ---")

    for item in transcript:
        answer = item.get("answer", "")
        words_in_answer = len(answer.split()) # Simple word count by splitting by space
        total_words_in_answers += words_in_answer
        
        if words_in_answer < short_answer_threshold and words_in_answer > 0: # Non-empty short answers
            short_answers_found += 1
            print(f"  - Short answer found for Q{item.get('question_number')}: '{answer}' ({words_in_answer} words)")

    average_words_per_answer = 0
    if num_questions_answered > 0:
        average_words_per_answer = total_words_in_answers / num_questions_answered

    analysis_summary = {
        "questions_answered": num_questions_answered,
        "total_words_in_answers": total_words_in_answers,
        "average_words_per_answer": round(average_words_per_answer, 2),
        "short_answers_detected (less than {} words)".format(short_answer_threshold): short_answers_found
    }
    
    return analysis_summary

def display_analysis(summary):
    """
    Displays the analysis summary.
    """
    if not summary:
        return
        
    print("\n--- Analysis Summary ---")
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")


if __name__ == "__main__":
    print("Starting Transcript Analyzer...")
    
    # Load the latest transcript (assumes it's in the same directory as this script)
    transcript_data = load_latest_transcript() 
    
    if transcript_data:
        analysis_results = analyze_transcript_data(transcript_data)
        if analysis_results:
            display_analysis(analysis_results)
    else:
        print("Could not perform analysis as no transcript was loaded.")
        
    print("\nTranscript analysis complete.")