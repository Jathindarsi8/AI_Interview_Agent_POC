# input_parser.py (v6 for Experience, Projects, Certifications)
import re
import json # Added for pretty printing the final dict in debug

# --- Keep these functions as they were (assuming they worked for you) ---
def parse_job_post(filepath):
    job_details = {"title": None, "description": None, "responsibilities": [], "requirements": []}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            current_section = None
            description_buffer = []
            for line in f:
                line = line.strip()
                if not line: continue
                if line.lower().startswith("job title:"):
                    job_details["title"] = line.split(":", 1)[1].strip()
                    current_section = None
                elif line.lower().startswith("description:"):
                    description_buffer.append(line.split(":", 1)[1].strip())
                    current_section = "description"
                elif line.lower().startswith("responsibilities:"): 
                    current_section = "responsibilities"
                    if description_buffer: job_details["description"] = " ".join(description_buffer); description_buffer = []
                elif line.lower().startswith("requirements:"): 
                    current_section = "requirements"
                    if description_buffer: job_details["description"] = " ".join(description_buffer); description_buffer = []
                elif current_section == "description":
                    description_buffer.append(line)
                elif line.startswith("- ") and current_section == "responsibilities":
                     job_details["responsibilities"].append(line[2:].strip())
                elif line.startswith("- ") and current_section == "requirements":
                     job_details["requirements"].append(line[2:].strip())
            if description_buffer: job_details["description"] = " ".join(description_buffer) # Final flush for description
    except FileNotFoundError: print(f"DEBUG (parse_job_post): File not found at {filepath}"); return None
    except Exception as e: print(f"DEBUG (parse_job_post): Error: {e}"); return None
    return job_details

def parse_company_profile(filepath):
    company_details = {"company_name": None, "mission": None, "vision": None, "core_values": []}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            current_section = None
            mission_buffer = []
            vision_buffer = []
            for line in f:
                line = line.strip()
                if not line: continue
                if line.lower().startswith("company name:"): 
                    company_details["company_name"] = line.split(":", 1)[1].strip()
                    current_section = None
                elif line.lower().startswith("mission:"):
                    mission_buffer.append(line.split(":", 1)[1].strip())
                    current_section = "mission"
                elif line.lower().startswith("vision:"):
                    vision_buffer.append(line.split(":", 1)[1].strip())
                    current_section = "vision"
                    if mission_buffer: company_details["mission"] = " ".join(mission_buffer); mission_buffer = []
                elif line.lower().startswith("core values:"): 
                    current_section = "core_values"
                    if mission_buffer: company_details["mission"] = " ".join(mission_buffer); mission_buffer = []
                    if vision_buffer: company_details["vision"] = " ".join(vision_buffer); vision_buffer = []
                elif current_section == "mission":
                    mission_buffer.append(line)
                elif current_section == "vision":
                    vision_buffer.append(line)
                elif line.startswith("- ") and current_section == "core_values": 
                    company_details["core_values"].append(line[2:].strip())
            if mission_buffer: company_details["mission"] = " ".join(mission_buffer)
            if vision_buffer: company_details["vision"] = " ".join(vision_buffer)
    except FileNotFoundError: print(f"DEBUG (parse_company_profile): File not found at {filepath}"); return None
    except Exception as e: print(f"DEBUG (parse_company_profile): Error: {e}"); return None
    return company_details
# --- End of previously working functions ---


# --- UPDATED parse_resume (v6) ---
def parse_resume(filepath):
    print("\nDEBUG: ---- ENTERING parse_resume (v6) ----")
    print(f"DEBUG: Attempting to parse resume from: {filepath}")

    resume_details = {
        "name": None, "email": None, "phone": None, "linkedin": None,
        "summary": "", "skills": [], "experience": [], "education": [],
        "projects": [], "certifications": []
    }
    
    lines = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line_raw.rstrip('\n\r') for line_raw in f.readlines()]
        print(f"DEBUG: Successfully read {len(lines)} lines from resume file.")
    except FileNotFoundError:
        print(f"DEBUG ERROR: Resume file NOT FOUND at {filepath}")
        return resume_details 
    except Exception as e:
        print(f"DEBUG ERROR: An error occurred while reading the resume file: {e}")
        return resume_details 

    if not lines:
        print("DEBUG ERROR: Resume file is empty after reading.")
        return resume_details 

    # Contact Info Parsing
    if len(lines) > 0:
        line_content = lines[0].strip()
        if line_content.lower().startswith("name:"): resume_details["name"] = line_content[len("name:"):].strip()
        else: resume_details["name"] = line_content
        print(f"DEBUG: Parsed Name: '{resume_details['name']}'")

    if len(lines) > 1:
        line_content = lines[1].strip()
        if line_content.lower().startswith("email:"): resume_details["email"] = line_content[len("email:"):].strip()
        else:
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a_zA-Z0-9.-]+\.[a-zA-Z]{2,}", line_content)
            if email_match: resume_details["email"] = email_match.group(0)
        print(f"DEBUG: Parsed Email: '{resume_details['email']}'")
    
    if len(lines) > 2:
        line_content = lines[2].strip()
        if line_content.lower().startswith("phone:"): resume_details["phone"] = line_content[len("phone:"):].strip()
        print(f"DEBUG: Parsed Phone: '{resume_details['phone']}'")

    if len(lines) > 3:
        line_content = lines[3].strip()
        if line_content.lower().startswith("linkedin:"): resume_details["linkedin"] = line_content[len("linkedin:"):].strip()
        print(f"DEBUG: Parsed LinkedIn: '{resume_details['linkedin']}'")
    
    print("\nDEBUG: ---- STARTING SECTION SCAN & PARSE (v6) ----")
    current_section = None
    current_item_details = None # For multi-line items like experience or projects
    
    start_scan_index = 0 
    for idx in range(min(len(lines), 5)): 
        if lines[idx].strip() == "":
            start_scan_index = idx + 1
            break
    if start_scan_index == 0 and len(lines) > 4 : start_scan_index = 4
    elif start_scan_index == 0 : start_scan_index = 0

    print(f"DEBUG: Will start scanning for section headers from file line index {start_scan_index}")

    i = start_scan_index
    while i < len(lines):
        line_stripped = lines[i].strip()
        line_stripped_lower = line_stripped.lower()
        
        # print(f"DEBUG SCAN (line {i+1}): '{line_stripped}' | Current Section: {current_section}")

        # Section Header Detection 
        # Using exact match for the stripped lowercase line
        new_section_detected = False
        if line_stripped_lower == "summary:":
            current_section = "summary"
            if current_item_details: current_item_details = None # Finalize previous complex item
            print(f"DEBUG ******** FOUND SECTION: Summary **********")
            new_section_detected = True
        elif line_stripped_lower == "skills:":
            current_section = "skills"
            if current_item_details: current_item_details = None 
            print(f"DEBUG ******** FOUND SECTION: Skills **********")
            new_section_detected = True
        elif line_stripped_lower == "experience:": 
            current_section = "experience"
            current_item_details = None # Reset for a new experience item
            print(f"DEBUG ******** FOUND SECTION: Experience **********")
            new_section_detected = True
        elif line_stripped_lower == "education:":
            current_section = "education"
            if current_item_details: current_item_details = None 
            print(f"DEBUG ******** FOUND SECTION: Education **********")
            new_section_detected = True
        elif line_stripped_lower == "highlighted project works:":
            current_section = "projects"
            current_item_details = None # Reset for a new project item
            print(f"DEBUG ******** FOUND SECTION: Highlighted Project Works **********")
            new_section_detected = True
        elif line_stripped_lower == "certifications:":
            current_section = "certifications"
            if current_item_details: current_item_details = None 
            print(f"DEBUG ******** FOUND SECTION: Certifications **********")
            new_section_detected = True

        if new_section_detected:
            i += 1 
            continue 

        # Content Parsing
        if current_section == "summary":
            if line_stripped: resume_details["summary"] += line_stripped + " "
        
        elif current_section == "skills":
            if line_stripped.startswith("- ") or line_stripped.startswith("• "): 
                skill = line_stripped[2:].strip()
                resume_details["skills"].append(skill)
            elif line_stripped: # If skill is not starting with '-' but is on a new line
                 resume_details["skills"].append(line_stripped)

        elif current_section == "education":
            if line_stripped: resume_details["education"].append(line_stripped)
        
        elif current_section == "experience":
            if line_stripped:
                if not line_stripped.startswith("• ") and not line_stripped.startswith("- "):
                    # This line is likely a new job title/company/date
                    current_item_details = {"title_company_date": line_stripped, "description_points": []}
                    resume_details["experience"].append(current_item_details)
                    print(f"DEBUG [Experience Start]: New item '{line_stripped}'")
                elif (line_stripped.startswith("• ") or line_stripped.startswith("- ")) and current_item_details:
                    # This is a description point for the current job
                    description_point = line_stripped[2:].strip()
                    current_item_details["description_points"].append(description_point)
                    print(f"DEBUG [Experience Detail]: Added '{description_point}' to '{current_item_details['title_company_date']}'")
            elif not line_stripped and current_item_details: # Blank line might signify end of current item
                current_item_details = None # Reset

        elif current_section == "projects":
            if line_stripped:
                if not line_stripped.startswith("• ") and not line_stripped.startswith("- "):
                    # New project title or detail line
                    if not current_item_details or ":" not in line_stripped or any(kw in line_stripped.lower() for kw in ["stack:", "role:", "domain:", "impact:", "overview:"]):
                         # Assume new project title if no current item or not a typical detail line
                        current_item_details = {"title": line_stripped, "details": [], "contributions": []}
                        resume_details["projects"].append(current_item_details)
                        print(f"DEBUG [Project Start]: New item '{line_stripped}'")
                    elif current_item_details: # It's a detail line for current project
                         current_item_details["details"].append(line_stripped)
                         print(f"DEBUG [Project Detail]: Added detail '{line_stripped}'")
                elif (line_stripped.startswith("• ") or line_stripped.startswith("- ")) and current_item_details:
                    contribution = line_stripped[2:].strip()
                    current_item_details["contributions"].append(contribution)
                    print(f"DEBUG [Project Contribution]: Added '{contribution}'")
            elif not line_stripped and current_item_details:
                current_item_details = None

        elif current_section == "certifications":
            if line_stripped:
                resume_details["certifications"].append(line_stripped.replace("• ", "").strip())
        
        i += 1 

    resume_details["summary"] = resume_details["summary"].strip()
            
    print("DEBUG: ---- LEAVING parse_resume (v6) ----")
    return resume_details


# --- Test Block (from previous version, should work) ---
if __name__ == "__main__":
    print("--- Starting input_parser.py test for RESUME ONLY (Simplified Debug Version) ---")
    
    sample_resume_path = "inputs/resume_sample.txt" 

    print(f"\n--- Attempting to parse resume: {sample_resume_path} ---")
    parsed_resume_data = parse_resume(sample_resume_path)
    
    print("\n--- RAW Parsed Resume Data Dictionary (from Simplified Debug Version) ---")
    if parsed_resume_data:
        print(json.dumps(parsed_resume_data, indent=4)) # Pretty print
    else:
        print("Resume parsing returned None.")
    
    print("-" * 30)
    print("--- End of input_parser.py test ---")

