from flask import Flask, render_template, request
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from PyPDF2 import PdfReader

app = Flask(__name__)

def extract_text(file):
    # Extract text from the file
    if file.filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.filename.endswith('.txt'):
        return extract_text_from_txt(file)
    else:
        return None

def extract_text_from_pdf(file):
    try:
        # Extract text from PDF
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        # Handle the exception
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_txt(file):
    # Extract text from plain text file
    return file.read().decode("utf-8")

def summarize_document(text):
    # Tokenizing the text
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Creating frequency table to keep the score of each word
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    # Calculating sentence scores
    sentences = sent_tokenize(text)
    sentence_scores = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentence_scores:
                    sentence_scores[sentence] += freq
                else:
                    sentence_scores[sentence] = freq

    # Sorting sentences by score
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)

    # Generating bullet points for the top sentences
    summary = ''
    num_lines = 0
    for sentence in sorted_sentences:
        if num_lines >= 20:  # Ensuring at least 20 lines in the summary
            break
        if sentence_scores[sentence] > 1:  # Adjust this threshold as needed
            summary += f"{sentence}<br><br>"
            num_lines += 1
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded"
        
        file = request.files['file']
        
        if file.filename == '':
            return "No file selected"
        
        text = extract_text(file)
        if text is None:
            return "Unsupported file format. Please upload a PDF or text file."
        
        summary = summarize_document(text)
        return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
