# Inspiration
Many products use ingredients that normal people can't understand, like Acetyl Hexapeptide-1 or 4-Methylbenzylidene Camphor. We decided to create an app that would read in an image of the ingredients used in a product and flag those that might be harmful.

# What it does
The app allows you to either upload an image of the ingredients of a cosmetic product or take a picture. Using OCR software, it reads in the text. Because OCR is often inaccurate, we also 'spell-check' each ingredient, based on a database of possible ingredients. After analyzing the ingredients, it produces a pie chart showing the percentages of High, Medium, and Low Risk ingredients, as well as the ingredient list with each individual hazard rating (also separated by High, Medium, and Low Risk).

# How we built it
We used the Kivy library to create the app UI, and a Python OCR library called pytesseract to read ingredients from the picture. We compiled a database of possible ingredients and their hazard ratings. Then, we used nltk's edit distance metric to spell-correct the text that was generated from pytesseract, using the database of possible ingredients. Using matplotlib, we created a pie chart from the hazard ratings of each ingredient, categorizing them by High, Medium, and Low Risk. Then we created a color-coded version of the list of ingredients and their hazard ratings (1-10).

# Challenges we ran into
Inaccurate string generated from pictures, due to contrast, skewing, noise, blur, etc. For these reasons, we found that it was much easier to generate a quality ingredients list from screenshots rather than pictures from a camera. No existing API for cosmetic analysis apps.

# Accomplishments that we're proud of
We accomplished our overall goal of creating a user-friendly app for consumers to quickly understand which ingredients in cosmetic products might be harmful. If we were to expand our database of ingredients, we could easily expand the scope of our app to be used for food restrictions as well.

# What we learned
Producing a string from an image using OCR; creating charts in matplotlib; NLTK and the idea behind spell-checkers; extracting data from an HTML file; creating and reading a database in Python and SQLite

# What's next for IngredientsChecker
Going forward, we would improve the rating system to account for the composition percentages of chemicals. We would also like to improve image to text precision and acuity so that pictures taken under various environments (dark, low-contrast, reflective surfaces) can be recognized. Furthermore, we would like to expand our data base to other products involving chemicals such as food.

