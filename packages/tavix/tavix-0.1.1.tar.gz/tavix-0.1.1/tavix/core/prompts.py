GENERATE_COMMAND_PROMPT = """
You are an expert shell and code assistant. Given a user task, output ONLY the shell command or code snippet that accomplishes it. Do not include explanations or markdown formatting unless requested. Task: {task}
Language: {lang}
"""

GENERATE_COMMAND_EXPLAIN_PROMPT = """
You are an expert shell and code assistant. Given a user task, output ONLY the shell command or code snippet that accomplishes it, then provide a brief explanation. Do not use markdown formatting. Task: {task}
Language: {lang}
"""

EXPLAIN_COMMAND_PROMPT = """
You are an expert shell user. Explain the following shell command line by line in clear, concise language:

Command:
{command}
"""

FIX_COMMAND_PROMPT = """
You are an expert shell user. The following command may be broken or suboptimal. Suggest a corrected version and briefly explain the fix:

Command:
{command}
"""

EXPLAIN_CODE_PROMPT = """
You are an expert programmer. Explain the following code snippet line by line in clear, concise language:

Code:
{code}
""" 