# VIVA VOCE QUESTIONS & ANSWERS: AI-BASED COLLEGE ENQUIRY CHATBOT

This document contains 30 comprehensive Viva Voce questions with simple, accurate, and student-friendly answers designed for project defense and external examiner evaluations.

---

### Q1. What is an AI Chatbot?
**Answer:** An AI chatbot is a software application designed to simulate human conversation through text or voice interactions, allowing users to ask questions in natural language and receive automated, relevant answers.

### Q2. What is Natural Language Processing (NLP)?
**Answer:** Natural Language Processing (NLP) is a branch of Artificial Intelligence that enables computers to understand, interpret, and manipulate human language in a useful and meaningful way.

### Q3. How does this College Enquiry Chatbot work without using an expensive LLM API?
**Answer:** The chatbot uses classical Machine Learning and NLP. It converts the college FAQ questions and the student's enquiry into mathematical vectors using **TF-IDF Vectorization** and compares them using **Cosine Similarity**. The FAQ with the highest similarity score above a predefined threshold is returned as the answer.

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
**Answer:** Hallucination occurs when generative AI models invent false or unverified facts. Our chatbot completely prevents hallucination because it does not generate freeform text; it strictly retrieves pre-verified records from the college dataset or safely executes fallback prompts.

### Q13. Why did you choose Streamlit for the user interface?
**Answer:** Streamlit is an open-source Python framework that allows developers to create clean, responsive, and interactive data applications purely in Python, without writing complex HTML/CSS or managing frontend-backend server pipelines.

### Q14. How does `st.session_state` work in Streamlit?
**Answer:** Streamlit reruns the Python script from top to bottom on each user interaction. `st.session_state` provides a persistent dictionary to store variables (like the conversation message list `messages`) across reruns for the user's session.

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
**Answer:** Extremely easy. An administrator simply opens `college_faq.csv` in Excel or VS Code, adds new rows with category, question, and answer, and saves the file. The chatbot automatically indexes the new data upon reload without code modification.

### Q23. What automated tests were implemented, and what tool was used?
**Answer:** We implemented 26 automated unit and integration tests using `pytest`, covering greeting detection, gratitude responses, category queries (Courses, Fees, Hostel, Library, Placements, etc.), fallback triggers, invalid inputs, and CSV file validation. All 26 tests pass with 100% success.

### Q24. How does your system protect user privacy?
**Answer:** The chatbot does not collect or store student names, phone numbers, or IP addresses. Its logging mechanism records only the timestamp, character length, match score, category, and outcome status for performance monitoring.

### Q25. What is token normalization / preprocessing in your chatbot?
**Answer:** It converts input text to lowercase and normalizes common academic variations and plurals (e.g., *"fees"* to *"fee"*, *"hostels"* to *"hostel"*, *"timings"* to *"timing"*). This ensures high recall without relying on heavy external dependencies.

### Q26. Can this chatbot run without an active internet connection?
**Answer:** Yes. Because all dependencies (Python, Scikit-learn, Pandas, Streamlit) run locally on the host machine and the data is stored in a local CSV file, the chatbot functions completely offline on `http://localhost:8501`.

### Q27. What are the key advantages of this architecture over an API-based system like ChatGPT?
**Answer:**
1. Zero cost (no monthly API fees or per-token charges).
2. Works offline and on low-spec hardware.
3. 100% deterministic (zero risk of fake answers).
4. Sub-second response latency.
5. Complete data privacy (no college data sent to third-party cloud servers).

### Q28. What are the limitations of this project?
**Answer:** It relies on lexical and n-gram keyword overlap. If a student uses an entirely obscure phrasing with zero keyword intersection with the FAQ, the bot will trigger the fallback response. It is also currently restricted to English text.

### Q29. How can this project be enhanced in the future?
**Answer:**
1. Multilingual translation for regional Indian languages.
2. Voice input/output for campus kiosk displays.
3. Integration with college ERP systems for personalized student attendance and grade enquiries.
4. Hybrid dense vector retrieval using lightweight local sentence-transformers.

### Q30. What was your personal role and key learning from this project?
**Answer:** Through this project, I gained end-to-end practical experience in:
- Formulating real-world NLP pipelines using TF-IDF and Cosine Similarity.
- Designing full-stack web UIs using Streamlit with custom CSS.
- Applying software engineering best practices: modular programming, CSV schema validation, and test-driven development with Pytest.
- Analyzing the trade-offs between deterministic retrieval and generative AI in sensitive institutional domains.

