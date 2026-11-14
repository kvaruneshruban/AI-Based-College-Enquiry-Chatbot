# VIVA VOCE QUESTIONS & ANSWERS: AI-BASED COLLEGE ENQUIRY CHATBOT

This document contains 40 comprehensive Viva Voce questions with simple, accurate, and student-friendly answers designed for project defense and external examiner evaluations.

---

### Q1. What is an AI Chatbot?
**Answer:** An AI chatbot is a software application designed to simulate human conversation through text or voice interactions, allowing users to ask questions in natural language and receive automated, relevant answers.

### Q2. What is Natural Language Processing (NLP)?
**Answer:** Natural Language Processing (NLP) is a branch of Artificial Intelligence that enables computers to understand, interpret, and manipulate human language in a useful and meaningful way.

### Q3. How does this College Enquiry Chatbot work without relying strictly on an expensive cloud LLM API?
**Answer:** The chatbot uses a robust offline-first architecture. It converts the college FAQ questions and the student's enquiry into mathematical vectors using **TF-IDF Vectorization** and compares them using **Cosine Similarity**. The FAQ with the highest similarity score above a predefined threshold is returned as the answer.

### Q4. What is TF-IDF?
**Answer:** TF-IDF stands for **Term Frequency - Inverse Document Frequency**. It is a statistical numerical statistic that reflects how important a word is to a document in a collection or corpus.

### Q5. What is Term Frequency (TF)?
**Answer:** Term Frequency measures how frequently a term occurs in a document.
$$\text{TF}(t, d) = \frac{\text{Number of times term } t \text{ appears in document } d}{\text{Total number of terms in document } d}$$

### Q6. What is Inverse Document Frequency (IDF)?
**Answer:** Inverse Document Frequency measures how important or unique a word is across all documents. Common words like "is", "the", and "of" get low IDF scores, while informative domain words like "hostel", "tuition", and "admission" get high scores.
$$\text{IDF}(t) = \ln\left(\frac{1 + \text{Total Documents}}{1 + \text{Documents containing term } t}\right) + 1$$

### Q7. What is Cosine Similarity?
**Answer:** Cosine Similarity is a mathematical metric used to measure the similarity between two non-zero vectors in a multi-dimensional inner product space. It measures the cosine of the angle between the two vectors:
$$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$
Its value ranges from $0$ (completely unrelated) to $1$ (exact match).

### Q8. Why did you use Cosine Similarity instead of Euclidean Distance?
**Answer:** Euclidean distance is sensitive to document length (a longer sentence has larger coordinates and greater Euclidean distance). Cosine similarity measures the orientation (angle) rather than the magnitude, making it invariant to sentence length differences.

### Q9. What are Stop Words, and why are they removed?
**Answer:** Stop words are common words in a language (such as *a, an, the, in, on, is*) that appear frequently but carry minimal domain-specific meaning. Removing them reduces vector dimensionality and prevents common words from skewing similarity calculations.

### Q10. What is an N-gram, and what range is used in your project?
**Answer:** An N-gram is a contiguous sequence of $n$ items from a given sample of text. Our project uses `ngram_range=(1, 2)`, which captures both single words (unigrams like *"fee"*) and two-word phrases (bigrams like *"hostel fee"* or *"computer science"*).

### Q11. What is the purpose of the Similarity Threshold?
**Answer:** The similarity threshold (set to $0.25$ by default) acts as a safety boundary. If the best cosine similarity score between the user's question and any FAQ entry is below $0.25$, the system triggers a fallback message instead of returning a wrong answer.

### Q12. What is "AI Hallucination", and how does this project prevent it?
**Answer:** Hallucination occurs when generative AI models invent false or unverified facts. Our chatbot completely prevents hallucination because all core answers are strictly grounded in verified records from the college dataset (`college_faq.csv`) and structured fee definitions (`fee_manager.py`).

### Q13. Why did you choose Streamlit for the user interface?
**Answer:** Streamlit is an open-source Python framework that allows developers to create clean, responsive, and interactive data applications purely in Python, without writing complex frontend-backend pipelines.

### Q14. How does `st.session_state` work in Streamlit?
**Answer:** Streamlit reruns the Python script from top to bottom on each user interaction. `st.session_state` provides a persistent dictionary to store variables (like the conversation message list `messages`, active filter, and authentication status) across reruns for the user's session.

### Q15. Why did you use Pandas in this project?
**Answer:** Pandas is used to load tabular dataset files (`college_faq.csv`), validate required columns (`category`, `question`, `answer`), remove blank records, and perform fast category filtering.

### Q16. What is the role of Scikit-learn in this project?
**Answer:** Scikit-learn provides the optimized machine learning algorithms: `TfidfVectorizer` for feature extraction and `cosine_similarity` for vector distance computation.

### Q17. How does the chatbot handle greetings and thank-you messages?
**Answer:** The chatbot includes regular expression pattern matching for conversational pleasantries (e.g., *"Hello"*, *"Good morning"*, *"Thank you"*, *"Bye"*). It intercepts these intents before vector matching and delivers instantaneous canned responses.

### Q18. How are empty or whitespace-only inputs handled?
**Answer:** The system checks if `not user_query or not user_query.strip()`. If true, it returns an informative prompt asking the student to enter a valid question, with a confidence score of $0.0$.

### Q19. How does category filtering improve search accuracy?
**Answer:** When a user selects a specific department (e.g., *"Hostel"*), non-matching categories in the similarity vector are masked with a value of $-1.0$. This guarantees that only FAQs within the chosen topic are evaluated.

### Q20. What is the purpose of the fallback message?
**Answer:** When an enquiry falls outside the FAQ dataset or when the similarity score is below the threshold, the fallback message politely informs the user that verified data was not found and provides the college's official admissions phone number and email address.

### Q21. Why are all answers marked with `[DEMO DATA]`?
**Answer:** Academic integrity requires that sample data is not misrepresented as official college data. Marking answers as `[DEMO DATA]` makes it clear that the project is in demonstration mode and ready for real institutional data insertion.

### Q22. How easy is it to update the college knowledge base?
**Answer:** Extremely easy. An administrator can either edit `college_faq.csv` directly in Excel/VS Code or use the live FAQ Manager inside the authenticated Admin Desk to add, edit, or delete FAQs in real time.

### Q23. What automated tests were implemented, and what tool was used?
**Answer:** We implemented 35 automated tests using `pytest` across two test suites (`test_chatbot.py` with 26 tests and `test_features.py` with 9 tests). All 35 tests pass with a 100% success rate.

### Q24. How does your system protect user privacy?
**Answer:** The public chat session does not harvest unsolicited user data. Activity logs record only timestamps, character lengths, match scores, and categories for quality monitoring. Only when a student explicitly fills out the lead form is contact info safely logged to `leads.csv`.

### Q25. What is token normalization / preprocessing in your chatbot?
**Answer:** It converts input text to lowercase and normalizes common academic variations and plurals (e.g., *"fees"* to *"fee"*, *"hostels"* to *"hostel"*, *"timings"* to *"timing"*). This ensures high recall without relying on heavy external dependencies.

### Q26. Can this chatbot run without an active internet connection?
**Answer:** Yes. Because all primary dependencies (Python, Scikit-learn, Pandas, Streamlit) run locally on the host machine and knowledge bases reside in local CSV files, the chatbot operates 100% offline on `http://localhost:8501`.

### Q27. What are the key advantages of this architecture over an ungrounded API-based system?
**Answer:**
1. Zero operational cost (no mandatory per-token charges).
2. Works offline and on low-spec hardware.
3. 100% deterministic (eliminates fictitious answers).
4. Sub-second response latency.
5. Institutional privacy (sensitive college data is not uploaded to third-party cloud servers).

### Q28. What are the limitations of this project?
**Answer:** It relies on lexical and n-gram keyword overlap with fuzzy distance. Unusually convoluted multi-clause questions may require breaking down into separate conversational turns. The system is also currently optimized for the English language.

### Q29. How can this project be enhanced in the future?
**Answer:**
1. Multilingual translation for regional Indian languages (Hindi, Tamil, Telugu).
2. Physical campus kiosk packaging with push-to-talk hardware.
3. Integration with college ERP systems for personalized student attendance and grade enquiries.
4. Dense vector embeddings using local sentence-transformers (e.g., `all-MiniLM-L6-v2`).

### Q30. What was your personal role and key learning from this project?
**Answer:** I gained end-to-end practical experience in:
- Formulating real-world NLP retrieval pipelines using TF-IDF and Cosine Similarity.
- Developing full-stack web UIs using Streamlit with custom CSS.
- Implementing multi-turn dialogue memory and hybrid fallback agents.
- Applying software engineering best practices: modular architecture, automated testing with Pytest, and administrative analytics.

### Q31. What is the Hybrid AI Architecture in this chatbot?
**Answer:** The Hybrid AI Architecture integrates Google Gemini 2.5 Flash for conversational dialogue with an offline-first Local Conversational Agent. If an API key is available, Gemini phrases the response warmly; otherwise, the Local Agent provides fluent, structured responses. In both cases, the answer is strictly grounded in verified institutional data.

### Q32. How does Multi-Turn Conversational Memory work?
**Answer:** `ai_agent.py` maintains a session history buffer that stores recent user queries, bot responses, and active academic entities (e.g., "Computer Science Engineering"). When a follow-up query is received, the agent consults this buffer to resolve contextual pronouns and intent.

### Q33. How does the chatbot resolve follow-up questions like "What is the fee for that?"
**Answer:** When the chatbot detects contextual pronouns such as *"that"*, *"it"*, or *"the first one"*, the multi-turn context tracker extracts the active topic from the preceding turn (e.g., "CSE") and merges it with the current query (becoming "What is the fee for CSE?"), ensuring accurate retrieval.

### Q34. How is the dedicated Fee Manager (`fee_manager.py`) designed and what is the two-tier display?
**Answer:** `fee_manager.py` contains structured data for departments (CSE, ECE, EEE, Mech, Civil, IT, AI&DS), auxiliary fees (hostel, lab, transport), and scholarships. The two-tier display shows the specific requested fee breakdown first, followed by a complete institutional fee summary table.

### Q35. How does the fuzzy typo tolerance handle student spelling mistakes?
**Answer:** The chatbot incorporates a fuzzy matching algorithm based on normalized character edit distances. Common misspellings like *"admision"*, *"hostal"*, *"scolorship"*, and *"librari"* are matched to their canonical vocabulary tokens before vectorization.

### Q36. How does the Student Admission Lead Capture system work?
**Answer:** Prospective students can submit their contact details, desired course, and 10+2 marks via an interactive modal form. The system generates a formatted tracking ID (`VRCE-26-XXXXX`), confirms receipt with the user, and records the lead in `leads.csv`.

### Q37. How does the Staff & Administrative Desk function, and how is it secured?
**Answer:** The Admin Desk is accessible via the sidebar and secured by a confidential PIN (`admin123`). Once authenticated, staff can view live enquiry metrics, export admission leads, review user feedback, track unanswered queries, and perform live FAQ CRUD operations.

### Q38. How does the system track knowledge gaps (Unanswered Queries Tracker)?
**Answer:** Whenever a student's question scores below the confidence threshold, it triggers the fallback response and automatically logs the query, timestamp, and similarity score into `unanswered_queries.csv`. Administrators can review these gaps to continuously expand the FAQ dataset.

### Q39. How are voice inputs (STT) and voice outputs (TTS) implemented?
**Answer:** Voice input is handled through browser Speech-to-Text, allowing students to speak their queries. For voice output, each bot response includes a "Read Aloud 🔊" option powered by HTML5 Web Speech API synthesis, vocalizing the answer clearly.

### Q40. What does the extended Pytest test suite (`tests/test_features.py`) verify?
**Answer:** `test_features.py` verifies the extended functionality: Gemini hybrid fallback execution, multi-turn follow-up resolution, fuzzy typo correction, lead capture generation and CSV integrity, feedback logging, unanswered query recording, departmental fee calculations, and live FAQ CRUD updates.
