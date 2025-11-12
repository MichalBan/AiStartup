# AiStartup
Playing with billion dollars startup tools - python, web scraping and openai API

# Steps
The script executes following steps:
 1. send cv document in pdf to AI assistant (GPT-5)
 2. scrape html of website with job offers
 3. extract links to offers from the html
 4. scrape the html of website with a random job description
 5. extract the job description from the html
 6. ask the AI assitant to create new cv based on the sent one, modifying it to suit the job description better
 7. save the AI response as pdf
 
# extracting links to job offers
At first I attempted to extract links using AI (get_links_ai() method), but the scrapped html was so large it didn't fit in the models context. The solution to this problem was to extract them manually, using text.find(). The problem of this approach is that it only works for the one website.

# extracting job description
Once again the html of the website was too large to be processed by AI. Extracting the description manually was difficult because every offer had a different layout and used different html classes. The solution was to extract text from every element that is a header of some form of paragraph. This is not guaranteed to work, but so far it hasn't failed a single time.

# creating a new cv with AI

## defining output
At first I tried to make the AI assistant output pdf document. This works on the web client, but is apparently impossible with API. The solution was to make the AI output text in some format that can later be converted to pdf.

## creating cv attempt 1 - plain text
Without further instructions the AI outputs text that can later be copy-pasted to chosen cv template. This can work if we provide cv template in some text form and use string manipulation to produce the final document in some format that can be rendered to pdf. For now I decided to take a different approach.

## creating cv attempt 2 - markdown
I tried to ask the AI to produce the cv document as markdown. This can later be saved as pdf with MarkdownPdf library. While the AI did output valid markdown the results were unsatisfactory - the document looked very bad eastetically. Prompt engineering failed to achieve desired quality.

## creating cv attempt 3 - image generation
The next idea was to use AI to generate the cv as an image of document with given text. This resulted in documents that looked extremely high quality at a glance, but the text had many errors like missing or misshaped letters.

## creating cv attempt 4 - html
The approach that yielded the best results was to ask the AI assistant to generate the cv as html. This resulted in document that had the desired content while being formatted like a cv.
