# Hospital Management System with AI Doctor Consultation
# This system provides patient and doctor record management along with AI-powered medical consultation

# Import necessary libraries for system operations, file handling, and AI integration
import os                                    # For operating system interface (clearing screen, file operations)
import sys                                   # For system-specific parameters and functions
import csv                                   # For CSV file operations (future use)
from abc import ABC, abstractmethod         # For creating abstract base classes
from typing import List, Dict               # For type hints to improve code readability
import google.generativeai as genai        # Google's Generative AI library for AI doctor functionality
import re                                   # For regular expression pattern matching

# Color class for terminal output formatting
class Colors:
    """
    ANSI color codes for colored terminal output
    These codes work on most Unix-based systems 
    and Windows with proper terminal support
    """
    RESET = "\033[0m"      # Reset to default color
    RED = "\033[31m"       # Red text
    GREEN = "\033[32m"     # Green text
    YELLOW = "\033[33m"    # Yellow text
    BLUE = "\033[34m"      # Blue text
    MAGENTA = "\033[35m"   # Magenta text
    CYAN = "\033[36m"      # Cyan text
    WHITE = "\033[37m"     # White text

# Configure Gemini AI with API key for medical consultation features
# NOTE: In production, this should be stored as an environment variable for security
genai.configure(api_key="AIzaSyDcPBrBXgmEb37CyszcVt_GW7KXHT8VdZo")

# Medicine database with costs in Pakistani Rupees
MEDICINE_DATABASE = {
    # Common Pain Relief Medicines
    "paracetamol": {"cost": 15, "type": "tablet", "unit": "per tablet"},
    "acetaminophen": {"cost": 15, "type": "tablet", "unit": "per tablet"},
    "ibuprofen": {"cost": 25, "type": "tablet", "unit": "per tablet"},
    "aspirin": {"cost": 12, "type": "tablet", "unit": "per tablet"},
    "diclofenac": {"cost": 30, "type": "tablet", "unit": "per tablet"},
    "naproxen": {"cost": 40, "type": "tablet", "unit": "per tablet"},
    
    # Antibiotics
    "amoxicillin": {"cost": 45, "type": "capsule", "unit": "per capsule"},
    "azithromycin": {"cost": 80, "type": "tablet", "unit": "per tablet"},
    "ciprofloxacin": {"cost": 55, "type": "tablet", "unit": "per tablet"},
    "doxycycline": {"cost": 35, "type": "capsule", "unit": "per capsule"},
    "cephalexin": {"cost": 40, "type": "capsule", "unit": "per capsule"},
    
    # Cold and Flu Medicines
    "cetirizine": {"cost": 20, "type": "tablet", "unit": "per tablet"},
    "loratadine": {"cost": 18, "type": "tablet", "unit": "per tablet"},
    "pseudoephedrine": {"cost": 25, "type": "tablet", "unit": "per tablet"},
    "dextromethorphan": {"cost": 30, "type": "syrup", "unit": "per 5ml"},
    "guaifenesin": {"cost": 35, "type": "syrup", "unit": "per 5ml"},
    
    # Gastrointestinal Medicines
    "omeprazole": {"cost": 60, "type": "capsule", "unit": "per capsule"},
    "ranitidine": {"cost": 25, "type": "tablet", "unit": "per tablet"},
    "loperamide": {"cost": 22, "type": "tablet", "unit": "per tablet"},
    "simethicone": {"cost": 18, "type": "tablet", "unit": "per tablet"},
    "domperidone": {"cost": 30, "type": "tablet", "unit": "per tablet"},
    
    # Vitamins and Supplements
    "vitamin d": {"cost": 50, "type": "tablet", "unit": "per tablet"},
    "vitamin c": {"cost": 15, "type": "tablet", "unit": "per tablet"},
    "calcium": {"cost": 35, "type": "tablet", "unit": "per tablet"},
    "iron": {"cost": 40, "type": "tablet", "unit": "per tablet"},
    "multivitamin": {"cost": 55, "type": "tablet", "unit": "per tablet"},
    
    # Topical Applications
    "betamethasone": {"cost": 120, "type": "cream", "unit": "per tube"},
    "hydrocortisone": {"cost": 80, "type": "cream", "unit": "per tube"},
    "clotrimazole": {"cost": 90, "type": "cream", "unit": "per tube"},
    "mupirocin": {"cost": 150, "type": "ointment", "unit": "per tube"},
    
    # Emergency/Common Medicines
    "salbutamol": {"cost": 180, "type": "inhaler", "unit": "per inhaler"},
    "prednisolone": {"cost": 65, "type": "tablet", "unit": "per tablet"},
    "metformin": {"cost": 20, "type": "tablet", "unit": "per tablet"},
    "amlodipine": {"cost": 45, "type": "tablet", "unit": "per tablet"},
    "atenolol": {"cost": 30, "type": "tablet", "unit": "per tablet"}
}

class HMS:
    """
    Hospital Management System main class
    Contains static methods for displaying system logo and exit message
    """
    
    @staticmethod
    def logo():
        """
        Display the hospital management system logo
        Uses colored output for better visual appeal
        """
        print("\n\t\t\t  ", end="")                                      # Print spacing before logo
        print(Colors.BLUE + "=" * 34 + Colors.RESET)                     # Blue border line
        print(f"\t\t\t  |-- HOSPITAL MANAGEMENT SYSTEM --|")             # System title
        print("\t\t\t  " + Colors.BLUE + "=" * 34 + Colors.RESET)        # Blue border line

    @staticmethod
    def end():
        """
        Display exit message with developer credits
        Shows thank you message and team member information
        """
        print("\n" * 4)                                                   # Add vertical spacing
        print(f"\t\tTHANK YOU FOR TESTING OUR {Colors.BLUE}HOSPITAL MANAGEMENT SYSTEM{Colors.RESET}")
        print(f"\n\t\t{Colors.MAGENTA}CODE DESIGNERS:{Colors.RESET}")     # Team credits header
        # Display team member names and IDs with different colors
        print(f"\t\t             Hafsa Fatima    : {Colors.GREEN}F2022266713{Colors.RESET}")
        print(f"\t\t             Urooj Asghar    : {Colors.YELLOW}F2022266035{Colors.RESET}")
        print("\n" * 7)                                                   # Add vertical spacing

class Person(ABC):
    """
    Abstract base class for Person
    Defines common attributes for both Patient and Doctor classes
    Uses ABC (Abstract Base Class) to enforce implementation of info() method in child classes
    """
    
    def __init__(self):
        """
        Initialize common person attributes
        All attributes are initialized with default values
        """
        self.fname = ""        # First name
        self.lname = ""        # Last name
        self.gender = ""       # Gender
        self.blood = ""        # Blood group
        self.age = 0          # Age (integer)
        self.mobile = 0       # Mobile number (integer)

    @abstractmethod
    def info(self):
        """
        Abstract method that must be implemented by child classes
        Forces Patient and Doctor classes to have their own info() implementation
        """
        pass

class Patient(Person):
    """
    Patient class inheriting from Person
    Handles all patient-related operations including CRUD operations
    """
    
    def __init__(self):
        """
        Initialize Patient object
        Calls parent constructor and adds patient-specific attributes
        """
        super().__init__()     # Call parent class constructor
        self.problem = ""      # Patient's medical problem (not currently used)
        self.count = 0        # Counter for patients (not currently used)

    def info(self):
        """
        Collect patient information from user input
        Includes input validation for numeric fields
        Returns: bool - True if information collected successfully, False otherwise
        """     
        # Collect basic information (string inputs)
        self.fname = input("Enter First Name: ")
        self.lname = input("Enter Last Name: ")
        self.gender = input("Enter Gender: ")
        
        # Collect numeric information with error handling
        try:
            self.age = int(input("Enter Age: "))                    # Convert to integer
            self.mobile = int(input("Enter Mobile Number: "))       # Convert to integer
        except ValueError:
            # Handle case where user enters non-numeric values
            print(f"{Colors.RED}Invalid input. Please enter numbers for age and mobile.{Colors.RESET}")
            return False
        
        self.blood = input("Enter Blood Group: ")
        return True                                                  # Return success

    def add_patient(self):
        """
        Add a new patient to the system
        Clears screen, shows interface, collects info, and saves to file
        """
        # Clear screen (works on both Windows and Unix systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        HMS.logo()                                                   # Display system logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.GREEN}PATIENT{Colors.RESET}/{Colors.RED}INSERT PATIENT{Colors.RESET}\n")
        
        # Collect patient information
        if self.info():
            try:
                # Append patient data to file in CSV format
                with open("PATIENT.txt", "a") as file:
                    # Write comma-separated values with newline
                    file.write(f"{self.fname},{self.lname},{self.gender},{self.age},{self.mobile},{self.blood}\n")
                print(f"{Colors.GREEN}Patient record inserted successfully.{Colors.RESET}")
            except Exception as e:
                # Handle file operation errors
                print(f"{Colors.RED}Error opening the file: {e}{Colors.RESET}")
        
        input("Press Enter to go back...")                           # Wait for user input before returning

    def display_patients(self):
        """
        Display all patient records from the file
        Reads file line by line and formats output
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.GREEN}PATIENT{Colors.RESET}/{Colors.RED}DISPLAY PATIENT{Colors.RESET}\n")
        
        try:
            with open("PATIENT.txt", "r") as file:                   # Open file in read mode
                count = 0                                            # Initialize record counter
                
                # Read file line by line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Ensure we have complete patient data (6 fields)
                        if len(data) >= 6:
                            count += 1                              # Increment counter
                            
                            # Display formatted patient information
                            print(f"{Colors.RED}Record {Colors.RESET}{count}:")
                            print(f"Name           : {data[0]} {data[1]}")    # First + Last name
                            print(f"Gender         : {data[2]}")
                            print(f"Age            : {data[3]}")
                            print(f"Mobile Number  : {data[4]}")
                            print(f"Blood Group    : {data[5]}")
                            print("----------------------------------")       # Separator line
                
                # Display message if no records found
                if count == 0:
                    print(f"{Colors.RED}No records found.{Colors.RESET}")
                    
        except FileNotFoundError:
            # Handle case where file doesn't exist
            print(f"{Colors.RED}No records found.{Colors.RESET}")
        
        input("Press Enter to go back...")                           # Wait for user input

    def search_patient(self):
        """
        Search for a specific patient by mobile number
        Mobile number is used as unique identifier
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.YELLOW}PATIENT{Colors.RESET}/{Colors.RED}SEARCH PATIENT{Colors.RESET}\n")
        
        try:
            # Get mobile number to search for
            mobile_no = int(input("Enter Mobile No. of the patient to search: "))
            found = False                                            # Flag to track if patient found
            
            with open("PATIENT.txt", "r") as file:                   # Open file in read mode
                # Search through each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if record is complete and mobile number matches
                        if len(data) >= 6 and int(data[4]) == mobile_no:
                            found = True                             # Mark as found
                            
                            # Display patient information
                            print(f"Name           : {data[0]} {data[1]}")
                            print(f"Gender         : {data[2]}")
                            print(f"Age            : {data[3]}")
                            print(f"Mobile Number  : {data[4]}")
                            print(f"Blood Group    : {data[5]}")
                            print("----------------------------------")
            
            # Display message if patient not found
            if not found:
                print(f"{Colors.RED}Patient record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            # Handle invalid input or missing file
            print(f"{Colors.RED}Invalid input or no records found.{Colors.RESET}")
        
        input("Press Enter to go back...")                           # Wait for user input

    def modify_patient(self):
        """
        Modify existing patient record
        Searches by mobile number and allows updating all fields
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.YELLOW}PATIENT{Colors.RESET}/{Colors.RED}MODIFY PATIENT{Colors.RESET}\n")
        
        try:
            # Get mobile number of patient to modify
            mobile_no = int(input("Enter Mobile No. of the patient to modify: "))
            found = False                                            # Flag to track if patient found
            lines = []                                              # List to store all file lines
            
            with open("PATIENT.txt", "r") as file:                   # Open file in read mode
                # Process each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if this is the record to modify
                        if len(data) >= 6 and int(data[4]) == mobile_no:
                            found = True                             # Mark as found
                            
                            # Show existing data
                            print("\nExisting Data:")
                            print(f"Name           : {data[0]} {data[1]}")
                            print(f"Gender         : {data[2]}")
                            print(f"Age            : {data[3]}")
                            print(f"Mobile Number  : {data[4]}")
                            print(f"Blood Group    : {data[5]}")
                            print("Enter new data:\n")
                            
                            # Get new information
                            if self.info():
                                # Create new record with updated information
                                lines.append(f"{self.fname},{self.lname},{self.gender},{self.age},{self.mobile},{self.blood}\n")
                                print(f"{Colors.GREEN}Record modified successfully.{Colors.RESET}")
                        else:
                            # Keep existing records unchanged
                            lines.append(line)
            
            # Write updated data back to file if patient was found
            if found:
                with open("PATIENT.txt", "w") as file:               # Open in write mode (overwrites file)
                    file.writelines(lines)                          # Write all lines
            else:
                print(f"{Colors.RED}Patient record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            # Handle invalid input or file errors
            print(f"{Colors.RED}Invalid input or error accessing file.{Colors.RESET}")
        
        input("Press Enter to go back...")                           # Wait for user input

    def discharge_patient(self):
        """
        Remove patient record from the system (discharge)
        Searches by mobile number and removes the record
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.YELLOW}PATIENT{Colors.RESET}/{Colors.RED}DISCHARGE PATIENT{Colors.RESET}\n")
        
        try:
            # Get mobile number of patient to discharge
            mobile_no = int(input("Enter Mobile No. of the patient to discharge: "))
            found = False                                            # Flag to track if patient found
            lines = []                                              # List to store remaining records
            
            with open("PATIENT.txt", "r") as file:                   # Open file in read mode
                # Process each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if this is the record to remove
                        if len(data) >= 6 and int(data[4]) == mobile_no:
                            found = True                             # Mark as found (but don't add to lines)
                        else:
                            # Keep all other records
                            lines.append(line)
            
            # Write remaining records back to file if patient was found
            if found:
                with open("PATIENT.txt", "w") as file:               # Open in write mode
                    file.writelines(lines)                          # Write remaining lines
                print(f"{Colors.GREEN}Patient discharged successfully.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Patient record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            # Handle invalid input or file errors
            print(f"{Colors.RED}Invalid input or error accessing file.{Colors.RESET}")
        
        input("Press Enter to go back...")                           # Wait for user input

    def menu(self):
        """
        Display patient management menu
        Provides options for all patient-related operations
        """
        while True:                                                  # Loop until user chooses to go back
            os.system('cls' if os.name == 'nt' else 'clear')        # Clear screen
            HMS.logo()                                               # Display logo
            
            # Display navigation and menu options
            print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.GREEN}PATIENT{Colors.RESET}\n")
            print(f"{Colors.GREEN}[1]{Colors.RESET} INSERT PATIENT")          # Add new patient
            print(f"{Colors.GREEN}[2]{Colors.RESET} DISPLAY PATIENT")         # Show all patients
            print(f"{Colors.GREEN}[3]{Colors.RESET} MODIFY PATIENT")          # Update patient info
            print(f"{Colors.GREEN}[4]{Colors.RESET} SEARCH PATIENT")          # Find specific patient
            print(f"{Colors.GREEN}[5]{Colors.RESET} DISCHARGE PATIENT")       # Remove patient
            print(f"{Colors.GREEN}[6]{Colors.RESET} BACK")                    # Return to main menu
            
            # Get user choice
            choice = input(f"\n\nPlease Select {Colors.YELLOW}(1-6):{Colors.RESET} ")
            
            # Execute corresponding function based on choice
            if choice == '1':
                self.add_patient()           # Call add patient function
            elif choice == '2':
                self.display_patients()      # Call display patients function
            elif choice == '3':
                self.modify_patient()        # Call modify patient function
            elif choice == '4':
                self.search_patient()        # Call search patient function
            elif choice == '5':
                self.discharge_patient()     # Call discharge patient function
            elif choice == '6':
                break                        # Exit loop and return to main menu

class Doctor(Person):
    """
    Doctor class inheriting from Person
    Handles doctor record management and AI consultation functionality
    """
    
    def __init__(self):
        """
        Initialize Doctor object
        Adds doctor-specific attributes to inherited Person attributes
        """
        super().__init__()                   # Call parent class constructor
        self.id = 0                         # Doctor ID (unique identifier)
        self.salary = 0                     # Doctor's salary
        self.from_time = ""                 # Start time of duty
        self.to_time = ""                   # End time of duty
        self.specialization = ""            # Medical specialization
        self.experience = ""                # Years of experience
        self.ai_model = None               # AI model instance for consultation
        self.conversation_history = []      # Store conversation for context
        self.prescribed_medicines = []      # Store prescribed medicines for billing
        self.question_count = 0            # Track number of questions asked by AI doctor

    def list_available_models(self):
        """
        Debug function to list available AI models
        Helps troubleshoot AI initialization issues
        Returns: list of available model names
        """
        try:
            models = genai.list_models()                             # Get available models from API
            print(f"{Colors.YELLOW}Available models:{Colors.RESET}")
            
            # Display each available model
            for model in models:
                print(f"- {model.name}")
            
            return [model.name for model in models]                  # Return list of model names
        except Exception as e:
            # Handle API errors
            print(f"{Colors.RED}Error listing models: {e}{Colors.RESET}")
            return []

    def initialize_ai_doctor(self):
        """
        Initialize the AI model for medical consultation with enhanced medicine prescription
        Tries multiple model names and tests connectivity
        Returns: bool - True if initialization successful, False otherwise
        """
        try:
            # List of model names to try (in order of preference)
            model_names = [
                'gemini-1.5-flash',           # Fast, lightweight model
                'gemini-1.5-pro',             # More capable model
                'models/gemini-1.5-flash',    # Alternative naming convention
                'models/gemini-1.5-pro',      # Alternative naming convention
                'gemini-2.0-flash'            # Newer version (if available)
            ]
            
            model_initialized = False        # Flag to track successful initialization
            
            # Try each model name
            for model_name in model_names:
                try:
                    print(f"{Colors.YELLOW}Trying model: {model_name}...{Colors.RESET}")
                    self.ai_model = genai.GenerativeModel(model_name)    # Create model instance
                    
                    # Test the model with a simple request
                    test_response = self.ai_model.generate_content("Hello, are you working?")
                    if test_response and test_response.text:
                        print(f"{Colors.GREEN}Successfully initialized with model: {model_name}{Colors.RESET}")
                        model_initialized = True
                        break                                        # Exit loop on success
                except Exception as model_error:
                    # Log error and try next model
                    print(f"{Colors.RED}Failed with {model_name}: {str(model_error)}{Colors.RESET}")
                    continue
            
            # If all preferred models failed, try first available model
            if not model_initialized:
                print(f"{Colors.RED}All model attempts failed. Listing available models...{Colors.RESET}")
                available_models = self.list_available_models()
                
                if available_models:
                    try:
                        first_model = available_models[0]           # Get first available model
                        print(f"{Colors.YELLOW}Trying first available model: {first_model}...{Colors.RESET}")
                        self.ai_model = genai.GenerativeModel(first_model)
                        
                        # Test the model
                        test_response = self.ai_model.generate_content("Hello")
                        if test_response and test_response.text:
                            model_initialized = True
                            print(f"{Colors.GREEN}Successfully initialized with: {first_model}{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}Failed with available model: {e}{Colors.RESET}")
                
                # Return False if no model could be initialized
                if not model_initialized:
                    return False
            
            # Enhanced system prompt for prescription-based billing
            system_prompt = f"""
            You are a professional medical doctor providing consultation. Follow these guidelines:
            
            1. Ask maximum 3-5 questions before providing diagnosis and treatment
            2. Be warm, empathetic, and conversational - like a real doctor
            3. After collecting sufficient information, provide a complete prescription
            4. ALWAYS prescribe medicines from this available list: {', '.join(MEDICINE_DATABASE.keys())}
            5. For each medicine, specify: name, dosage (mg), frequency (times per day), duration (days)
            6. Format prescriptions as: "Medicine: [name] [dosage]mg, [frequency] times daily for [duration] days"
            7. Prescribe 2-4 medicines minimum for a complete treatment
            8. Keep responses natural and human-like
            9. Show genuine concern for the patient's wellbeing
            10. NEVER mention costs during consultation - only prescribe medicines
            
            Example prescription format:
            "Based on your symptoms, I'm prescribing:
            Medicine: Paracetamol 500mg, 3 times daily for 5 days
            Medicine: Amoxicillin 250mg, 2 times daily for 7 days"
            """
            
            # Initialize conversation history with system prompt and reset counters
            self.conversation_history = [system_prompt]
            self.question_count = 0  # Track number of questions asked
            self.prescribed_medicines = []  # Reset prescribed medicines list
            
            return True                                              # Return success
            
        except Exception as e:
            # Handle any unexpected errors
            print(f"{Colors.RED}Error initializing AI Doctor: {e}{Colors.RESET}")
            return False

    def extract_medicines_from_response(self, response_text):
        """
        Extract prescribed medicines from AI response for billing calculation
        Uses regex patterns to find medicine prescriptions
        
        Args:
            response_text (str): AI doctor's response containing prescriptions
        
        Returns:
            list: List of prescribed medicines with details
        """
        prescribed = []
        
        # Pattern to match medicine prescriptions
        # Matches: "Medicine: [name] [dosage]mg, [frequency] times daily for [duration] days"
        patterns = [
            r"Medicine:\s*([a-zA-Z\s]+)\s*(\d+)mg,?\s*(\d+)\s*times?\s*daily\s*for\s*(\d+)\s*days?",
            r"Take\s*([a-zA-Z\s]+)\s*(\d+)mg\s*(\d+)\s*times?\s*daily\s*for\s*(\d+)\s*days?",
            r"([a-zA-Z\s]+)\s*(\d+)mg\s*-\s*(\d+)\s*times?\s*daily\s*for\s*(\d+)\s*days?",
            r"Prescribe\s*([a-zA-Z\s]+)\s*(\d+)mg,?\s*(\d+)\s*times?\s*daily\s*for\s*(\d+)\s*days?"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                medicine_name = match.group(1).strip().lower()
                dosage = int(match.group(2))
                frequency = int(match.group(3))
                duration = int(match.group(4))
                
                # Check if medicine exists in database
                if medicine_name in MEDICINE_DATABASE:
                    total_tablets = frequency * duration
                    prescribed.append({
                        'name': medicine_name,
                        'dosage': dosage,
                        'frequency': frequency,
                        'duration': duration,
                        'total_quantity': total_tablets,
                        'unit_cost': MEDICINE_DATABASE[medicine_name]['cost'],
                        'total_cost': total_tablets * MEDICINE_DATABASE[medicine_name]['cost']
                    })
        
        return prescribed

    def get_ai_response(self, patient_input, is_final_summary=False):
        """
        Get AI response for patient input with improved prescription handling
        Manages conversation context and generates appropriate medical responses
        
        Args:
            patient_input (str): Patient's message or symptoms
            is_final_summary (bool): Whether to generate final diagnosis
        
        Returns:
            str: AI doctor's response
        """
        try:
            # Ensure AI model is initialized
            if not self.ai_model:
                if not self.initialize_ai_doctor():
                    return "I'm sorry, I'm currently unavailable. Please try again later."
            
            # Initialize question counter if not exists
            if not hasattr(self, 'question_count'):
                self.question_count = 0
            
            # Build conversation context starting with system prompt
            conversation_context = f"{self.conversation_history[0]}\n\n"
            
            # Add recent conversation history (limit to last 10 exchanges to manage memory)
            recent_history = self.conversation_history[1:]           # Skip system prompt
            if len(recent_history) > 20:                            # Keep last 10 exchanges (20 entries: patient + doctor)
                recent_history = recent_history[-20:]
            
            # Add conversation history to context
            for entry in recent_history:
                conversation_context += f"{entry}\n"
            
            # Add current patient input with appropriate prompt based on question count
            if is_final_summary:
                # Special prompt for final diagnosis with prescription
                conversation_context += f"Patient: {patient_input}\n\n"
                conversation_context += f"Now provide a comprehensive final diagnosis with specific medicine prescriptions from the available list: {', '.join(list(MEDICINE_DATABASE.keys())[:10])}... Use the format 'Medicine: [name] [dosage]mg, [frequency] times daily for [duration] days'\n\nDoctor:"
            else:
                # Check if it's time to provide diagnosis (after 3-5 questions)
                if self.question_count >= 3:
                    conversation_context += f"Patient: {patient_input}\n\n"
                    conversation_context += f"You have asked {self.question_count} questions. Now provide a complete diagnosis with specific medicine prescriptions using this format: 'Medicine: [name] [dosage]mg, [frequency] times daily for [duration] days'. Choose medicines from: {', '.join(list(MEDICINE_DATABASE.keys())[:10])}...\n\nDoctor:"
                else:
                    # Regular conversation prompt with question guidance
                    conversation_context += f"Patient: {patient_input}\n\n"
                    conversation_context += f"This is question {self.question_count + 1}. Ask one focused medical question to better understand the patient's condition. Be empathetic and human-like.\n\nDoctor:"
            
            # Generate AI response
            response = self.ai_model.generate_content(conversation_context)
            
            if response and response.text:
                ai_response = response.text.strip()                 # Remove whitespace
                
                # Clean up response format
                if ai_response.startswith("Doctor:"):
                    ai_response = ai_response[7:].strip()           # Remove "Doctor:" prefix if present
                
                # Extract medicines from response if it contains prescriptions
                medicines = self.extract_medicines_from_response(ai_response)
                if medicines:
                    self.prescribed_medicines.extend(medicines)
                
                # Add conversation to history for context
                self.conversation_history.append(f"Patient: {patient_input}")
                self.conversation_history.append(f"Doctor: {ai_response}")
                
                # Increment question count for regular questions (not final summary)
                if not is_final_summary and self.question_count < 5:
                    # Check if the response contains a question mark (indicating a question was asked)
                    if "?" in ai_response:
                        self.question_count += 1
                
                # Manage memory - keep system prompt + last 30 entries
                if len(self.conversation_history) > 31:
                    self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-30:]
                
                return ai_response
            else:
                # Handle case where AI doesn't generate response
                return "I'm sorry, I couldn't process your request. Could you please tell me more about how you're feeling?"
            
        except Exception as e:
            # Handle API errors gracefully
            return f"I apologize for the technical difficulty. Please describe your symptoms again, and I'll do my best to help you."

    def calculate_consultation_bill(self):
        """
        Calculate total bill based on prescribed medicines and fixed charges
        NO REGISTRATION FEE - Only consultation fee and medicines
        Returns: tuple (medicine_cost, total_cost, bill_details)
        """
        # Fixed hospital charges - ONLY consultation fee (NO registration fee)
        consultation_fee = 2000
        
        # Calculate medicine costs
        medicine_cost = 0
        medicine_details = []
        
        if self.prescribed_medicines:
            for medicine in self.prescribed_medicines:
                medicine_details.append({
                    'name': medicine['name'].title(),
                    'quantity': medicine['total_quantity'],
                    'unit_cost': medicine['unit_cost'],
                    'total_cost': medicine['total_cost']
                })
                medicine_cost += medicine['total_cost']
        else:
            # If no medicines were prescribed, add a basic consultation charge
            medicine_details.append({
                'name': 'Basic Health Consultation',
                'quantity': 1,
                'unit_cost': 500,
                'total_cost': 500
            })
            medicine_cost = 500
        
        # Calculate total - ONLY consultation and medicines (NO registration fee)
        total_cost = consultation_fee + medicine_cost
        
        bill_details = {
            'consultation_fee': consultation_fee,
            'medicine_cost': medicine_cost,
            'medicine_details': medicine_details,
            'total_cost': total_cost
        }
        
        return medicine_cost, total_cost, bill_details

    def show_final_bill(self):
        """
        Display consultation bill with dynamic medicine costs
        Shows itemized charges including prescribed medicines
        NO REGISTRATION FEE INCLUDED
        """
        # Wait for user to be ready to view bill
        print(f"\n{Colors.YELLOW}Press Enter to view consultation bill...{Colors.RESET}")
        input()
        
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Calculate bill based on prescribed medicines
        medicine_cost, total_cost, bill_details = self.calculate_consultation_bill()
        
        # Display formatted bill
        print(f"\n\n\t\t\t\t    {Colors.YELLOW}CONSULTATION BILL{Colors.RESET}")
        print("\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        
        # Hospital charges - ONLY consultation fee
        print("\t* HOSPITAL CHARGES:                                                            *")
        print(f"\t* AI Doctor Consultation Fee                : Rs. {bill_details['consultation_fee']}                          *")
        print("\t*                                                                              *")
        
        # Medicine charges
        print("\t* PRESCRIBED MEDICINES:                                                        *")
        for medicine in bill_details['medicine_details']:
            name_display = medicine['name'][:25] + "..." if len(medicine['name']) > 25 else medicine['name']
            print(f"\t* {name_display:<30} x {medicine['quantity']:<3} @ Rs.{medicine['unit_cost']:<4} = Rs.{medicine['total_cost']:<6} *")
        
        print("\t*                                                                              *")
        print(f"\t* Total Medicine Cost                       : Rs. {Colors.CYAN}{medicine_cost}{Colors.RESET}                           *")
        print(f"\t* Total Consultation Fee                    : Rs. {Colors.YELLOW}{bill_details['consultation_fee']}{Colors.RESET}                          *")
        print("\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        
        # Total
        print(f"\t* TOTAL AMOUNT                              : Rs. {Colors.GREEN}{total_cost}{Colors.RESET}                         *")
        print("\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        
        # Thank you message
        print(f"\n\t\t{Colors.GREEN}Thank you for using our AI Doctor consultation service!{Colors.RESET}")
        print(f"\t\t{Colors.CYAN}Your health is our priority. Get well soon!{Colors.RESET}")
        
        # Medicine pickup information
        if bill_details['medicine_details'] and bill_details['medicine_details'][0]['name'] != 'Basic Health Consultation':
            print(f"\n\t\t{Colors.MAGENTA}Please collect your prescribed medicines from the pharmacy.{Colors.RESET}")
        
        # Wait for user input before returning
        input(f"\n\t\t\tPress {Colors.RED}ENTER{Colors.RESET} to return to main menu")

    def info(self):
        """
        Collect doctor information from user input
        Includes validation for numeric fields
        Returns: bool - True if successful, False if validation fails
        """
        print(f"{Colors.RESET}Doctor Details")
        
        # Collect basic information
        self.fname = input("Enter First Name: ")
        self.lname = input("Enter Last Name: ")
        self.gender = input("Enter Gender: ")
        
        # Collect numeric information with validation
        try:
            self.age = int(input("Enter Age: "))
            self.salary = int(input("Enter salary: "))
        except ValueError:
            print(f"{Colors.RED}Invalid input for age or salary.{Colors.RESET}")
            return False
        
        # Collect duty time information
        print(f"{Colors.MAGENTA}Enter Duty time{Colors.RESET}")
        self.from_time = input("From: ")
        self.to_time = input("To: ")
        
        # Collect doctor ID with validation
        try:
            self.id = int(input("Enter ID: "))
        except ValueError:
            print(f"{Colors.RED}Invalid ID input.{Colors.RESET}")
            return False
        
        # Collect specialization and experience
        self.specialization = input("Enter Specialization: ")
        self.experience = input("Doctor Experience (years): ")
        return True

    def add_doctor(self):
        """
        Add new doctor to the system
        Similar to add_patient but with doctor-specific fields
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.YELLOW}DOCTOR{Colors.RESET}/{Colors.CYAN}INSERT DOCTOR{Colors.RESET}\n")
        print(f"{Colors.YELLOW}DOCTOR", end="")
        
        # Collect doctor information
        if self.info():
            try:
                # Save doctor data to file in CSV format
                with open("DOCTOR.txt", "a") as file:
                    # Write all doctor fields separated by commas
                    file.write(f"{self.fname},{self.lname},{self.gender},{self.age},{self.salary},{self.from_time},{self.to_time},{self.id},{self.specialization},{self.experience}\n")
                print(f"{Colors.GREEN}Doctor record inserted successfully.{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error opening the file: {e}{Colors.RESET}")
        
        input("Press Enter to go back...")

    def display_doctors(self):
        """
        Display all doctor records
        Shows formatted information for all doctors in the system
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.RED}MAIN{Colors.RESET}/{Colors.YELLOW}DOCTOR{Colors.RESET}/{Colors.CYAN}DISPLAY DOCTOR{Colors.RESET}\n")
        
        try:
            with open("DOCTOR.txt", "r") as file:                    # Open doctor file
                count = 0                                            # Initialize counter
                
                # Process each line in the file
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Ensure complete doctor record (10 fields)
                        if len(data) >= 10:
                            count += 1
                            
                            # Display formatted doctor information
                            print(f"{Colors.GREEN}Record {Colors.RESET}{count}:")
                            print(f"Name              : Dr. {data[0]} {data[1]}")    # Add "Dr." prefix
                            print(f"Gender            : {data[2]}")
                            print(f"Age               : {data[3]}")
                            print(f"Salary            : {data[4]}")
                            print(f"Timing (from-to)  : {data[5]} - {data[6]}")     # Combined timing
                            print(f"Doctor ID         : {data[7]}")
                            print(f"Specialization    : {data[8]}")
                            print(f"Experience        : {data[9]} years")
                            print("----------------------------------")
                
                # Display message if no records found
                if count == 0:
                    print(f"{Colors.RED}No records found.{Colors.RESET}")
        except FileNotFoundError:
            print(f"{Colors.RED}No records found.{Colors.RESET}")
        
        input("Press Enter to go back...")

    def search_doctor(self):
        """
        Search for doctor by ID
        Doctor ID is used as unique identifier
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.RED}MAIN{Colors.RESET}/{Colors.YELLOW}DOCTOR{Colors.RESET}/{Colors.CYAN}SEARCH DOCTOR{Colors.RESET}\n")
        
        try:
            # Get doctor ID to search for
            doctor_id = int(input("Enter ID of the doctor to search: "))
            found = False                                            # Flag for tracking if found
            
            with open("DOCTOR.txt", "r") as file:                    # Open doctor file
                # Search through each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if record is complete and ID matches
                        if len(data) >= 10 and int(data[7]) == doctor_id:    # data[7] is doctor ID
                            found = True
                            
                            # Display doctor information
                            print(f"Name              : Dr. {data[0]} {data[1]}")
                            print(f"Gender            : {data[2]}")
                            print(f"Age               : {data[3]}")
                            print(f"Salary            : {data[4]}")
                            print(f"Timing (from-to)  : {data[5]} - {data[6]}")
                            print(f"Doctor ID         : {data[7]}")
                            print(f"Specialization    : {data[8]}")
                            print(f"Experience        : {data[9]} years")
                            print("----------------------------------")
            
            # Display message if doctor not found
            if not found:
                print(f"{Colors.RED}Doctor record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            print(f"{Colors.RED}Invalid input or no records found.{Colors.RESET}")
        
        input("Press Enter to go back...")

    def modify_doctor(self):
        """
        Modify existing doctor record
        Similar to modify_patient but uses doctor ID as identifier
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.RED}MAIN{Colors.RESET}/{Colors.YELLOW}DOCTOR{Colors.RESET}/{Colors.CYAN}MODIFY DOCTOR{Colors.RESET}\n")
        
        try:
            # Get doctor ID to modify
            doctor_id = int(input("Enter ID of the doctor to modify: "))
            found = False                                            # Flag for tracking if found
            lines = []                                              # Store all file lines
            
            with open("DOCTOR.txt", "r") as file:                    # Open doctor file
                # Process each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if this is the record to modify
                        if len(data) >= 10 and int(data[7]) == doctor_id:
                            found = True
                            
                            # Show existing data
                            print("\nExisting Data:")
                            print(f"Name              : Dr. {data[0]} {data[1]}")
                            print(f"Gender            : {data[2]}")
                            print(f"Age               : {data[3]}")
                            print(f"Salary            : {data[4]}")
                            print(f"Timing (from-to)  : {data[5]} - {data[6]}")
                            print(f"Doctor ID         : {data[7]}")
                            print(f"Specialization    : {data[8]}")
                            print(f"Experience        : {data[9]} years")
                            print("\nEnter new data:\n")
                            
                            # Get new information
                            if self.info():
                                # Create new record with updated information
                                lines.append(f"{self.fname},{self.lname},{self.gender},{self.age},{self.salary},{self.from_time},{self.to_time},{self.id},{self.specialization},{self.experience}\n")
                                print(f"{Colors.GREEN}Record modified successfully.{Colors.RESET}")
                        else:
                            # Keep existing records unchanged
                            lines.append(line)
            
            # Write updated data back to file if doctor was found
            if found:
                with open("DOCTOR.txt", "w") as file:                # Overwrite file
                    file.writelines(lines)
            else:
                print(f"{Colors.RED}Doctor record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            print(f"{Colors.RED}Invalid input or error accessing file.{Colors.RESET}")
        
        input("Press Enter to go back...")

    def delete_doctor(self):
        """
        Delete doctor record from system
        Removes doctor by ID
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display navigation breadcrumb
        print(f"\t\t\t\t {Colors.MAGENTA}MAIN{Colors.RESET}/{Colors.YELLOW}DOCTOR{Colors.RESET}/{Colors.CYAN}DELETE DOCTOR{Colors.RESET}\n")
        
        try:
            # Get doctor ID to delete
            doctor_id = int(input("Enter ID of the doctor to delete: "))
            found = False                                            # Flag for tracking if found
            lines = []                                              # Store remaining records
            
            with open("DOCTOR.txt", "r") as file:                    # Open doctor file
                # Process each line
                for line in file:
                    if line.strip():                                 # Skip empty lines
                        data = line.strip().split(',')              # Split CSV data
                        
                        # Check if this is the record to delete
                        if len(data) >= 10 and int(data[7]) == doctor_id:
                            found = True                             # Mark as found (but don't add to lines)
                        else:
                            # Keep all other records
                            lines.append(line)
            
            # Write remaining records back to file if doctor was found
            if found:
                with open("DOCTOR.txt", "w") as file:                # Overwrite file
                    file.writelines(lines)
                print(f"{Colors.GREEN}Doctor record deleted successfully.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Doctor record not found.{Colors.RESET}")
                
        except (ValueError, FileNotFoundError):
            print(f"{Colors.RED}Invalid input or error accessing file.{Colors.RESET}")
        
        input("Press Enter to go back...")

    def consultation(self):
        """
        Main AI consultation function with prescription-based billing
        Handles the interactive conversation between patient and AI doctor
        """
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        HMS.logo()                                                   # Display logo
        
        # Display consultation header
        print(f"\t\t\t {Colors.CYAN}AI DOCTOR {Colors.RESET}AND {Colors.YELLOW}PATIENT {Colors.GREEN}CONSULTATION{Colors.RESET}\n")
        
        # Initialize AI Doctor and reset prescription list
        print(f"{Colors.YELLOW}Initializing AI Doctor...{Colors.RESET}")
        self.prescribed_medicines = []  # Reset for new consultation
        
        if not self.initialize_ai_doctor():
            # Handle initialization failure
            print(f"{Colors.RED}Failed to initialize AI Doctor. Please check your internet connection and API key.{Colors.RESET}")
            input("Press Enter to go back...")
            return
        
        # Display successful initialization and instructions
        print(f"{Colors.GREEN}AI Doctor is ready for consultation!{Colors.RESET}\n")
        print(f"{Colors.MAGENTA}How to use:{Colors.RESET}")
        print(f"• Describe your symptoms naturally")                 # Natural language input
        print(f"• Answer the doctor's questions honestly")           # Interactive conversation
        print(f"• The doctor will diagnose and prescribe after a few questions")  # Updated instruction
        print(f"• Type '{Colors.RED}exit{Colors.RESET}' to quit consultation\n")  # Command to quit
        
        # Generate initial greeting from AI
        greeting = self.get_ai_response("Hello doctor, I would like to start a medical consultation. Please greet me warmly and ask about my main health concern.")
        print(f"{Colors.CYAN}Doctor: {greeting}{Colors.RESET}\n")
        
        # Main consultation loop
        while True:
            try:
                # Get patient input
                patient_response = input(f"{Colors.YELLOW}You: {Colors.RESET}").strip()
                
                # Check for exit commands (quit without diagnosis)
                if patient_response.lower() in ['exit', 'quit', 'q', 'bye', 'stop']:
                    print(f"{Colors.YELLOW}Consultation ended. Take care and feel better soon!{Colors.RESET}")
                    input("Press Enter to go back...")
                    return                                           # Exit without showing bill
                
                # Handle empty input
                if not patient_response:
                    print(f"{Colors.RED}Please tell me about your symptoms or how you're feeling.{Colors.RESET}")
                    continue
                
                # Get AI doctor response for regular conversation
                print(f"{Colors.YELLOW}Doctor is analyzing...{Colors.RESET}")      # Show processing message
                doctor_response = self.get_ai_response(patient_response)
                print(f"{Colors.CYAN}Doctor: {doctor_response}{Colors.RESET}\n")
                
                # Check if diagnosis was provided (contains medicine/prescription keywords)
                diagnosis_keywords = ['medicine:', 'medication', 'tablet', 'capsule', 'syrup', 'prescription', 'dosage', 'mg', 'times daily', 'treatment plan']
                if any(keyword in doctor_response.lower() for keyword in diagnosis_keywords):
                    # Ask if patient wants to see the bill
                    print(f"{Colors.GREEN}Consultation completed! Your treatment plan has been provided.{Colors.RESET}")
                    bill_choice = input(f"Would you like to see the consultation bill? (y/n): ").strip().lower()
                    if bill_choice in ['y', 'yes']:
                        self.show_final_bill()
                    else:
                        print(f"{Colors.GREEN}Thank you for choosing our AI Doctor service. Get well soon!{Colors.RESET}")
                        input("Press Enter to go back...")
                    return
                
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print(f"\n{Colors.RED}Consultation interrupted.{Colors.RESET}")
                break
            except Exception as e:
                # Handle unexpected errors
                print(f"{Colors.RED}An error occurred: {e}{Colors.RESET}")
                print(f"{Colors.YELLOW}Please try describing your symptoms again.{Colors.RESET}")
                continue
        
        # If loop ends without completion, still offer bill
        bill_choice = input(f"Would you like to see the consultation bill? (y/n): ").strip().lower()
        if bill_choice in ['y', 'yes']:
            self.show_final_bill()

    def menu(self):
        """
        Display doctor management menu
        Provides options for all doctor-related operations
        """
        while True:                                                  # Loop until user chooses to go back
            os.system('cls' if os.name == 'nt' else 'clear')        # Clear screen
            HMS.logo()                                               # Display logo
            
            # Display navigation and menu options
            print(f"\t\t\t\t {Colors.RED}MAIN{Colors.RESET}/{Colors.BLUE}DOCTOR{Colors.RESET}\n")
            print(f"{Colors.CYAN}[1]{Colors.RESET} INSERT DOCTOR")           # Add new doctor
            print(f"{Colors.CYAN}[2]{Colors.RESET} DISPLAY DOCTOR")          # Show all doctors
            print(f"{Colors.CYAN}[3]{Colors.RESET} MODIFY DOCTOR")           # Update doctor info
            print(f"{Colors.CYAN}[4]{Colors.RESET} SEARCH DOCTOR")           # Find specific doctor
            print(f"{Colors.CYAN}[5]{Colors.RESET} DELETE DOCTOR")           # Remove doctor
            print(f"{Colors.CYAN}[6]{Colors.RESET} BACK")                    # Return to main menu
            
            # Get user choice
            choice = input(f"\n\nPlease Select {Colors.YELLOW}(1-6):{Colors.RESET} ")
            
            # Execute corresponding function based on choice
            if choice == '1':
                self.add_doctor()            # Call add doctor function
            elif choice == '2':
                self.display_doctors()       # Call display doctors function
            elif choice == '3':
                self.modify_doctor()         # Call modify doctor function
            elif choice == '4':
                self.search_doctor()         # Call search doctor function
            elif choice == '5':
                self.delete_doctor()         # Call delete doctor function
            elif choice == '6':
                break                        # Exit loop and return to main menu

def main():
    """
    Main function - entry point of the application
    Creates instances and handles the main menu loop with AI doctor initialization
    """
    # Create instances of main classes
    doctor = Doctor()                        # Doctor instance for doctor operations and AI consultation
    patient = Patient()                      # Patient instance for patient operations
    hms = HMS()                             # HMS instance for logo and exit functions

    # Initialize AI Doctor at startup for better performance
    print(f"{Colors.YELLOW}Welcome to Hospital Management System!{Colors.RESET}")
    print(f"{Colors.CYAN}Initializing AI Doctor for consultation services...{Colors.RESET}")
    
    # Pre-initialize AI to avoid delays during consultation
    try:
        if doctor.initialize_ai_doctor():
            print(f"{Colors.GREEN}AI Doctor initialized successfully!{Colors.RESET}")
        else:
            print(f"{Colors.RED}AI Doctor initialization failed. Consultation may not work properly.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}AI initialization error: {e}{Colors.RESET}")
    
    input(f"{Colors.YELLOW}Press Enter to continue to main menu...{Colors.RESET}")

    # Main application loop
    while True:                                                      # Loop until user chooses to exit
        os.system('cls' if os.name == 'nt' else 'clear')            # Clear screen
        hms.logo()                                                   # Display system logo
        
        # Display main menu options
        print(f"\t\t\t\t    {Colors.RED}   MAIN{Colors.RESET}\n")
        print(f"{Colors.BLUE}[1]{Colors.RESET} DOCTOR DETAILS")               # Doctor management
        print(f"{Colors.BLUE}[2]{Colors.RESET} PATIENT DETAILS")              # Patient management
        print(f"{Colors.BLUE}[3]{Colors.RESET} AI DOCTOR CONSULTATION")       # AI consultation feature
        print(f"{Colors.BLUE}[4]{Colors.RESET} SYSTEM EXIT")                  # Exit application
        
        # Get user choice
        choice = input(f"\n\nPlease Select {Colors.YELLOW}(1-4):{Colors.RESET} ")
        
        # Execute corresponding function based on choice
        if choice == '1':
            doctor.menu()                    # Go to doctor management menu
        elif choice == '2':
            patient.menu()                   # Go to patient management menu
        elif choice == '3':
            doctor.consultation()            # Start AI consultation
        elif choice == '4':
            # Exit application gracefully
            os.system('cls' if os.name == 'nt' else 'clear')        # Clear screen
            hms.end()                                                # Show exit message
            break                                                    # Exit main loop
        else:
            # Handle invalid input
            print(f"{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")
            input("Press Enter to continue...")                      # Wait before showing menu again

# Python entry point - ensures main() only runs when script is executed directly
if __name__ == "__main__":
    main()                                   # Start the application
