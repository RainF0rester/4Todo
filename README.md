# TaskTracker - Starter code for the project

Welcome! This guide will help you understand how this Flask web application works.

[TOC]


## Project Structure

Let's look at what files are in this project:

```
tasktracker/
├── app.py                # Main Flask application file
├── requirements.txt       # List of Python packages needed
├── templates/             # Folder for HTML templates
│   └── index.html        # The HTML page that users see
└── README.md             # Project documentation
```

### What Each File Does:

1. **`app.py`** - This is the "brain" of your application. It contains the Python code that runs your website.

2. **`requirements.txt`** - Lists all the Python packages (libraries) your project needs. In this case, just Flask.

3. **`templates/index.html`** - This is the HTML file that gets displayed in the browser. It's like the "face" of your website.

4. **`README.md`** - Documentation about the project.

---

## Understanding the Code

Let's break down `app.py` line by line:

### Line 1: Comment
```python
# Minimal Flask app
```
This is just a comment explaining what the file does. Comments start with `#` and are ignored by Python.

### Line 2: Import Statement
```python
from flask import Flask, render_template
```
**What it does:** Imports the Flask tools we need.
- `Flask` - The main Flask class to create our app
- `render_template` - A function to display HTML files

**Think of it like:** Getting the tools out of a toolbox before you start working.

### Line 4: Create the Flask App
```python
app = Flask(__name__)
```
**What it does:** Creates a new Flask application instance.
- `app` - This is our Flask application (we can name it anything, but `app` is conventional)
- `__name__` - This is a special Python variable (note the double underscores on both sides!)

**What is `__name__`?**
- `__name__` is a built-in Python variable that contains the name of the current module
- When you run `app.py` directly, `__name__` equals `'__main__'`
- When Flask imports your file, `__name__` equals `'app'` (the module name)
- Flask uses this to figure out where your application's root directory is, so it can find the `templates` folder and other files relative to your app

**Why double underscores (`__`)?**
- In Python, double underscores indicate special/magic variables that have special meaning
- Other examples: `__main__`, `__file__`, `__init__`
- These are Python conventions, not Flask-specific

**Think of it like:** Giving Flask your address so it knows where to look for your files (templates, static files, etc.)

### Lines 6-8: Define a Route
```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Breaking it down:**
- `@app.route('/')` - This is a **decorator**. It tells Flask: "When someone visits the root URL (`/`), run the function below."
  - `/` means the homepage (like `http://localhost:5000/`)
- `def index():` - This is a Python function that handles the request
- `return render_template('index.html')` - This tells Flask to find `index.html` in the `templates` folder and send it to the browser

**Think of it like:** Setting up a doorbell. When someone presses the doorbell (`/`), the `index()` function answers the door and shows them the `index.html` page.

### Lines 10-11: Run the App
```python
if __name__ == '__main__':
    app.run(debug=True)
```

**Breaking it down:**
- `if __name__ == '__main__':` - This checks if the script is being run directly (not imported by another file)
- `app.run(debug=True)` - Starts the web server
  - `debug=True` means Flask will automatically reload when you make changes, and show helpful error messages

**Think of it like:** Starting the engine of your car. The app won't run until you execute this.

---

## How to Run the Project

### Step 1: Install Flask

Open your terminal and navigate to the project folder, then run:

**On macOS/Linux:**
```bash
pip3 install flask
```

**On Windows:**
```bash
pip install flask
```

**Or use the requirements file:**
```bash
pip3 install -r requirements.txt
```

**What this does:** Downloads and installs Flask so Python can use it.

### Step 2: Run the Application

In your terminal, make sure you're in the project directory, then run:

**On macOS/Linux:**
```bash
python3 app.py
```

**On Windows:**
```bash
python app.py
```

**What you'll see:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

This means your server is running!

### Step 3: Open in Browser

Open your web browser and go to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

**What you'll see:** The welcome page from `index.html`!

### Step 4: Stop the Server

To stop the server, go back to your terminal and press:
```
Ctrl + C
```
(On Mac, it's the same: `Ctrl + C`)

---

## How It All Works Together

Here's the flow of what happens when you visit the website:

```
1. You type http://localhost:5000 in your browser
   ↓
2. Browser sends a request to Flask server
   ↓
3. Flask sees the request is for '/' (homepage)
   ↓
4. Flask runs the index() function
   ↓
5. index() function tells Flask to render 'index.html'
   ↓
6. Flask finds index.html in the templates folder
   ↓
7. Flask sends the HTML back to your browser
   ↓
8. Browser displays the webpage!
```

**Visual Flow:**
```
Browser → Flask Server → Route Handler → Template → Browser
```

---

## Making Your First Changes

### Change 1: Modify the Welcome Message

1. Open `templates/index.html`
2. Find this line:
   ```html
   <h1>Welcome to TaskTracker!</h1>
   ```
3. Change it to:
   ```html
   <h1>Hello, World! This is My First COMP9820 Project!</h1>
   ```
4. Save the file
5. Refresh your browser (the page should update automatically if debug mode is on)

### Change 2: Add a New Route

1. Open `app.py`
2. Add this code after the `index()` function:
   ```python
   @app.route('/about')
   def about():
       return '<h1>About Page</h1><p>This is the about page!</p>'
   ```
3. Save the file
4. Visit `http://localhost:5000/about` in your browser

**What happened?** You created a new route! Now your website has two pages:
- `/` - Homepage
- `/about` - About page

### Change 3: Add More Content to HTML

1. Open `templates/index.html`
2. Add this before the closing `</div>` tag:
   ```html
   <h2>My First Change</h2>
   <p>I just added this paragraph!</p>
   ```
3. Save and refresh your browser

---

## Common Questions

### Q: Why do I need a `templates` folder?
**A:** Flask looks for HTML files in a folder called `templates` by default. This keeps your project organized. You could change this, but it's a Flask convention.

### Q: What does `debug=True` do?
**A:** 
- Automatically reloads the server when you change code
- Shows detailed error messages if something goes wrong
- **Important:** Turn this off (`debug=False`) when you deploy your app to production!

### Q: Can I use a different port?
**A:** Yes! Change line 11 to:
```python
app.run(debug=True, port=8080)
```
Then access your site at `http://localhost:8080`

### Q: What if I get an error "Template not found"?
**A:** Make sure:
- The `templates` folder exists
- The `templates` folder is in the same directory as `app.py`
- The HTML file is named exactly `index.html` (case-sensitive!)

### Q: How do I add CSS styling?
**A:** You can:
1. Add CSS in the `<style>` tag in your HTML (like we did)
2. Create a `static` folder and put CSS files there
3. Link to external CSS files

---

## Next Steps

Now that you understand the basics, try:

1. **Add more routes** - Create `/contact`, `/help`, etc.
2. **Create more HTML templates** - Make separate HTML files for different pages
3. **Add more styling** - Make your pages look better with CSS
4. **Learn about forms** - Add input fields and buttons


---

## Key Terms Glossary

- **Flask**: Python web framework for building websites
- **Route**: A URL path that triggers a function
- **Template**: HTML file that Flask renders
- **Decorator**: `@app.route()` - modifies a function
- **Server**: Program that handles web requests
- **Localhost**: Your own computer (127.0.0.1)
- **Port**: A number that identifies a specific service (5000 is Flask's default)

---

## Summary

You've learned:
- ✅ What Flask is and why we use it
- ✅ How routes work (`@app.route('/')`)
- ✅ How templates are rendered (`render_template()`)
- ✅ How to run a Flask application
- ✅ How to make simple changes

**Congratulations!** You now understand the basics of the project starter code! 🎉

Keep experimenting and building. The best way to learn is by doing!


# Miscellaneous

<details close>
<summary>Useful info about "What is Flask?"</summary>

<br/>

## What is Flask?

**Flask** is a Python framework that helps you create websites and web applications. Think of it as a toolkit that makes building websites easier.

**Simple analogy:** 
- If building a website is like building a house, Flask provides you with the tools and structure (like a blueprint) so you don't have to build everything from scratch.

### Flask and Web Servers - What's the Relationship?

**Flask includes a built-in development web server:**
- When you run `app.run()`, Flask starts its own simple web server
- This server listens for requests from browsers and sends back responses
- It's perfect for learning and development (like we're doing now)

**Think of it like this:**
- **Flask** = The application framework (the logic, routes, templates)
- **Web Server** = The program that handles the network communication (receives requests, sends responses)
- Flask's built-in server combines both, but they're different concepts

**In production (real websites):**
- Flask applications usually run on separate production web servers like Gunicorn, uWSGI, or Apache
- These production servers are more robust and secure than Flask's built-in server
- But for learning, Flask's built-in server is perfect!

**Key concepts:**
- **Web Server**: A program that listens for requests from web browsers and sends back responses
- **Route**: A URL path (like `/` or `/about`) that your website responds to
- **Template**: An HTML file that Flask uses to create web pages
