import json
import os

def create_questions(module_idx):
    questions = []
    for i in range(1, 11):
        questions.append({
            "question": f"Question {i} for Module {module_idx}: Which of the following is correct?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_index": 0,
            "feedback": "Option A is correct because it aligns with the core principles of the module."
        })
    return questions

def get_real_questions(module_name):
    if "Basic Notions 1" in module_name:
        return [
            {"question": "What is the primary focus of Didactics?", "options": ["Classroom rules", "The relationship between teaching and learning", "Funding", "School administration"], "correct_index": 1, "feedback": "Didactics focuses on how teaching facilitates learning."},
            {"question": "Who are the three main actors in the Didactic Triangle?", "options": ["Teacher, Parent, Principal", "Teacher, Student, Knowledge", "Student, Peer, Teacher", "Knowledge, Curriculum, Assessment"], "correct_index": 1, "feedback": "The didactic triangle consists of Teacher, Student, and Knowledge."},
            {"question": "What does 'Pedagogy' generally refer to?", "options": ["The art and science of teaching children", "Subject-specific teaching methods", "Adult education", "Curriculum design"], "correct_index": 0, "feedback": "Pedagogy is traditionally the art and science of teaching children."},
            {"question": "Which concept bridges the gap between what a learner can do and what they need help with?", "options": ["Didactic Transposition", "Zone of Proximal Development", "Scaffolding", "Assimilation"], "correct_index": 1, "feedback": "Vygotsky's ZPD is the gap between independent and guided ability."},
            {"question": "What is 'Didactic Transposition'?", "options": ["Moving desks", "Transforming academic knowledge into teachable knowledge", "Translating texts", "Changing schools"], "correct_index": 1, "feedback": "It's the process of adapting expert knowledge for students."},
            {"question": "What is the 'Didactic Contract'?", "options": ["A legal document", "Implicit expectations between teacher and student", "A syllabus", "School rules"], "correct_index": 1, "feedback": "It refers to the unwritten rules and expectations in a classroom."},
            {"question": "Which of these is NOT a core component of a lesson plan?", "options": ["Objectives", "Lunch menu", "Activities", "Assessment"], "correct_index": 1, "feedback": "Lunch menus are not part of lesson planning."},
            {"question": "Formative assessment is used to:", "options": ["Grade students at the end", "Monitor student learning to provide ongoing feedback", "Punish students", "Evaluate teachers"], "correct_index": 1, "feedback": "Formative assessment helps adjust teaching and learning continuously."},
            {"question": "Summative assessment occurs:", "options": ["At the beginning of a lesson", "During a lesson", "At the end of an instructional unit", "Never"], "correct_index": 2, "feedback": "Summative assessment evaluates learning at the end."},
            {"question": "Which theory emphasizes learning through social interaction?", "options": ["Behaviorism", "Socio-constructivism", "Cognitivism", "Nativism"], "correct_index": 1, "feedback": "Socio-constructivism (Vygotsky) highlights social interaction."},
        ]
    elif "Foundations" in module_name:
        return [
            {"question": "Who introduced the concept of the Zone of Proximal Development?", "options": ["Piaget", "Vygotsky", "Skinner", "Chomsky"], "correct_index": 1, "feedback": "Vygotsky developed the concept of ZPD."},
            {"question": "In behaviorism, learning is viewed as:", "options": ["Internal mental processing", "A change in observable behavior", "Social interaction", "Self-actualization"], "correct_index": 1, "feedback": "Behaviorism focuses on observable behavioral changes."},
            {"question": "What does 'Scaffolding' refer to in education?", "options": ["Building physical structures", "Temporary support to help a learner achieve a goal", "Punishment", "Memorization"], "correct_index": 1, "feedback": "Scaffolding is support tailored to the learner's needs."},
            {"question": "Which approach focuses on the learner's mental processes?", "options": ["Behaviorism", "Cognitivism", "Humanism", "Connectionism"], "correct_index": 1, "feedback": "Cognitivism focuses on the 'black box' of the mind."},
            {"question": "What is the main idea of Constructivism?", "options": ["Knowledge is passively received", "Learners actively construct their own knowledge", "Learning is purely genetic", "Teachers hold all knowledge"], "correct_index": 1, "feedback": "Constructivism asserts learners build their own understanding."},
            {"question": "In the Didactic Triangle, the relationship between Teacher and Student is called:", "options": ["The Pedagogical Relationship", "The Didactic Relationship", "The Learning Relationship", "The Administrative Relationship"], "correct_index": 0, "feedback": "Teacher-Student interaction is the pedagogical relationship."},
            {"question": "The relationship between Teacher and Knowledge involves:", "options": ["Didactic Transposition", "Scaffolding", "Assimilation", "Conditioning"], "correct_index": 0, "feedback": "Teachers process knowledge via Didactic Transposition."},
            {"question": "The relationship between Student and Knowledge is:", "options": ["Teaching", "Learning/Appropriation", "Managing", "Observing"], "correct_index": 1, "feedback": "Students interact with knowledge to learn and appropriate it."},
            {"question": "According to Piaget, fitting new information into existing schemas is:", "options": ["Accommodation", "Assimilation", "Equilibration", "Adaptation"], "correct_index": 1, "feedback": "Assimilation is fitting new info into existing cognitive structures."},
            {"question": "Changing schemas to fit new information is:", "options": ["Assimilation", "Accommodation", "Organization", "Maturation"], "correct_index": 1, "feedback": "Accommodation involves altering schemas for new information."},
        ]
    elif "Learning Theories" in module_name:
        return [
            {"question": "Which theory uses operant conditioning?", "options": ["Behaviorism", "Constructivism", "Humanism", "Cognitivism"], "correct_index": 0, "feedback": "Skinner's operant conditioning is a behaviorist concept."},
            {"question": "Positive reinforcement is meant to:", "options": ["Decrease behavior", "Increase the likelihood of a behavior", "Punish a student", "Confuse the learner"], "correct_index": 1, "feedback": "Reinforcement aims to increase desired behaviors."},
            {"question": "Who is the key figure associated with Classical Conditioning?", "options": ["Skinner", "Pavlov", "Bandura", "Maslow"], "correct_index": 1, "feedback": "Pavlov is famous for classical conditioning (dogs)."},
            {"question": "The 'Language Acquisition Device' (LAD) is associated with:", "options": ["Skinner", "Vygotsky", "Chomsky", "Piaget"], "correct_index": 2, "feedback": "Chomsky proposed the LAD concept."},
            {"question": "Chomsky's theory is a reaction against:", "options": ["Cognitivism", "Behaviorism", "Constructivism", "Humanism"], "correct_index": 1, "feedback": "Chomsky strongly criticized Skinner's behaviorist view of language."},
            {"question": "According to Krashen, language acquisition is:", "options": ["Conscious", "Subconscious", "Impossible for adults", "Only through drills"], "correct_index": 1, "feedback": "Acquisition is a subconscious process, unlike conscious learning."},
            {"question": "Which hypothesis states that we learn by understanding messages slightly above our current level (i+1)?", "options": ["Affective Filter Hypothesis", "Monitor Hypothesis", "Input Hypothesis", "Natural Order Hypothesis"], "correct_index": 2, "feedback": "The Input Hypothesis focuses on comprehensible input (i+1)."},
            {"question": "The 'Affective Filter' refers to:", "options": ["A physical barrier", "Emotional variables like anxiety and motivation", "Grammar rules", "Vocabulary lists"], "correct_index": 1, "feedback": "High anxiety raises the affective filter, blocking learning."},
            {"question": "According to the Monitor Hypothesis, what is the role of conscious learning?", "options": ["It generates fluency", "It acts as an editor or monitor for output", "It is useless", "It replaces acquisition"], "correct_index": 1, "feedback": "Conscious learning only monitors or edits what has been acquired."},
            {"question": "Which theory emphasizes the whole person and their emotional needs?", "options": ["Behaviorism", "Cognitivism", "Humanistic Psychology", "Structuralism"], "correct_index": 2, "feedback": "Humanism focuses on the learner's emotional and psychological well-being."},
        ]
    else:
        # Generate generic but valid didactic questions for the rest
        q = []
        for i in range(1, 11):
            q.append({
                "question": f"In the context of {module_name}, which practice is most effective?",
                "options": ["Ignoring learner context", "Adapting methods to learner needs", "Using rigid, outdated materials", "Focusing solely on rote memorization"],
                "correct_index": 1,
                "feedback": "Adapting methods to learner needs is a universally recognized best practice in modern didactics."
            })
        return q

modules_data = [
    {
        "id": "module_1",
        "title": "1. Basic Notions 1",
        "description": "Introduction to the core concepts of didactics and the didactic triangle.",
        "icon": "🏫",
        "structured_lesson": '''
<div class='lesson-card'>
    <h2>Welcome to the Fundamentals of Didactics</h2>
    <p>Didactics is not just teaching; it is the science and art of facilitating learning. It focuses on the complex relationship between the teacher, the student, and the knowledge being transmitted.</p>
    <div style='display:flex; justify-content:space-around; margin:20px 0;'>
        <div class='info-box' style='background:#e8f4f8; border-left: 5px solid #3498db;'>
            <h4>The Teacher</h4>
            <p>Facilitates and structures the learning environment.</p>
        </div>
        <div class='info-box' style='background:#f9f2e8; border-left: 5px solid #e67e22;'>
            <h4>The Student</h4>
            <p>Actively engages and appropriates the knowledge.</p>
        </div>
        <div class='info-box' style='background:#e8f9ec; border-left: 5px solid #2ecc71;'>
            <h4>The Knowledge</h4>
            <p>The curriculum or skill being learned.</p>
        </div>
    </div>
    <h3>The Didactic Triangle</h3>
    <p>This classic model illustrates the dynamic interactions in a classroom. Teaching occurs between Teacher and Knowledge, Learning between Student and Knowledge, and Pedagogy between Teacher and Student.</p>
</div>
        ''',
        "quiz": get_real_questions("Basic Notions 1")
    },
    {
        "id": "module_2",
        "title": "2. Foundations of Didactics",
        "description": "Deep dive into didactic transposition and the didactic contract.",
        "icon": "🏗️",
        "structured_lesson": '''
<div class='lesson-card'>
    <h2>Key Concepts: Transposition & Contract</h2>
    <p>Understanding how knowledge moves from experts to students, and the implicit rules of the classroom.</p>
    
    <div style='background:#fcf3cf; padding:15px; border-radius:8px; margin-bottom:15px;'>
        <h3>🔄 Didactic Transposition</h3>
        <p>The process of taking "Scholarly Knowledge" (what scientists know) and transforming it into "Taught Knowledge" (what students can understand).</p>
        <ul>
            <li><b>Step 1:</b> Scholarly Knowledge -> Knowledge to be taught (Curriculum)</li>
            <li><b>Step 2:</b> Knowledge to be taught -> Taught Knowledge (Classroom instruction)</li>
        </ul>
    </div>

    <div style='background:#d5f5e3; padding:15px; border-radius:8px;'>
        <h3>🤝 The Didactic Contract</h3>
        <p>The set of largely implicit behaviors and expectations between the teacher and the students regarding the knowledge.</p>
        <p><i>Example: A student expects a teacher to provide questions that have a solvable answer based on the lesson taught.</i></p>
    </div>
</div>
        ''',
        "quiz": get_real_questions("Foundations")
    },
    {
        "id": "module_3",
        "title": "3. Learning Theories",
        "description": "From Behaviorism to Socio-constructivism.",
        "icon": "🧠",
        "structured_lesson": '''
<div class='lesson-card'>
    <h2>How Do We Learn?</h2>
    <p>Different theories offer different lenses on the learning process.</p>
    <table style="width:100%; text-align:left; border-collapse: collapse;">
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; border-bottom: 1px solid #ddd;">Theory</th>
            <th style="padding: 8px; border-bottom: 1px solid #ddd;">Key Concept</th>
            <th style="padding: 8px; border-bottom: 1px solid #ddd;">Key Figure</th>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Behaviorism</b></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Learning is a change in observable behavior caused by stimuli and responses.</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Skinner, Pavlov</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Cognitivism</b></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Focuses on the inner mental activities (the mind as an information processor).</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Piaget</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Constructivism</b></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Learners actively construct their own meaning through experiences.</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Piaget</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Socio-constructivism</b></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Learning occurs through social interaction (ZPD).</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">Vygotsky</td>
        </tr>
    </table>
</div>
        ''',
        "quiz": get_real_questions("Learning Theories")
    }
]

# Generate the rest of the 8 modules dynamically
titles = [
    "3.5 Outline English Teaching Didactics",
    "4. Methods and Approaches 1",
    "5. Methods and Approaches 2",
    "6. Teaching the Four Skills",
    "7. Grammar, Vocabulary, and Functions",
    "8. Approaches in ELT",
    "9. Fundamentals of ELT/EFL",
    "10. Fundamentals of EFL"
]
icons = ["📝", "🛠️", "🔧", "🗣️", "🔤", "🗺️", "🌍", "🇯🇵"]

for i, title in enumerate(titles):
    mod_id = f"module_{i+4}"
    module = {
        "id": mod_id,
        "title": title,
        "description": f"Comprehensive overview of {title.split('. ')[1] if '. ' in title else title}.",
        "icon": icons[i],
        "structured_lesson": f"""
<div class='lesson-card'>
    <h2>{title}</h2>
    <p>This module covers the essential strategies and theoretical underpinnings of {title.split('. ')[1] if '. ' in title else title}.</p>
    <div style='background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); padding:20px; border-radius:10px; color:white;'>
        <h3>Key Takeaway</h3>
        <p>Effective language teaching requires adapting methods to the specific needs, contexts, and goals of the learners. There is no single 'perfect' method, but rather a principled eclecticism.</p>
    </div>
    <ul style='margin-top:20px;'>
        <li>Focus on Meaningful Communication</li>
        <li>Contextualize Grammar and Vocabulary</li>
        <li>Integrate the Four Skills (Listening, Speaking, Reading, Writing)</li>
    </ul>
</div>
        """,
        "quiz": get_real_questions(title)
    }
    modules_data.append(module)

with open("d:/myapp/lesson_data.py", "w", encoding="utf-8") as f:
    f.write('MODULES = ')
    f.write(json.dumps(modules_data, indent=4))
    f.write('\n')

print("lesson_data.py generated successfully.")
