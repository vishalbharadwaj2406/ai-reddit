import os
import glob

# Get app name from environment variable (default to 'App')
APP_NAME = os.getenv("APP_NAME", "App")

# List of markdown files to process (recursive)
md_files = glob.glob("**/*.md", recursive=True)

for md_file in md_files:
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    # Replace [APP_NAME] with the environment variable value
    new_content = content.replace("[APP_NAME]", APP_NAME)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(new_content)

print(f"All markdown files updated with APP_NAME='{APP_NAME}'")
