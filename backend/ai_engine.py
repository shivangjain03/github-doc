import openai
import os


def generate_documentation(code_text: str) -> str:
    prompt = f"""
    You are an expert software engineer and technical writer.

Your job is to read the following codebase and generate a professional-level documentation in **Markdown format**.

Include:

1. 🎯 **Overall project purpose** and what problem it solves
2. 🧩 **Module-level summaries** (what each file/class/function is for)
3. 🧠 **Code logic and workflows** (explain decisions and flow)
4. 📊 **Workflow diagrams** (as Mermaid syntax)
5. 🗂️ **Architecture diagram** (if possible, use file-level structure)
6. 🧬 **Service/API dependency diagrams**
7. 🛠️ **Database ER diagrams** (if schema or ORM found)
8. 💡 **Best practices & improvement suggestions**

Generate clean, **linked sections** (with `##` and `###` headings) and include Mermaid diagrams where applicable.

The codebase is:

    {code_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1500
    )

    return response['choices'][0]['message']['content']
