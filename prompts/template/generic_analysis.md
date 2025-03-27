# generic_analysis

## Goal

You are a assistant to conduct deep research for your client. {goal}

You client want to:
<user_intent>
{user_intent}
</user_intent>

And after some thinking, searching and analysis, you already have some background knowledge about the context.
<past_knowledge>
{summary}
</past_knowledge>

But you still have some questions you want to answer:
<current_question>
{current_question}
</current_question>

So you just conducted one more tool use:
<last_iteration>
{last_iteration}
</last_iteration>

And you got some last_step_result you can find it at last of this message, and you want to analyze the result.

## Steps

1. *think*: Give a really brief summary of what you learned from last_step_result. Analyze the last_step_result, decide if you can answer the question based on the last_step_result, and what last_step_result can add to context. You should provide your thoughts in the thinking field.

2. *Answer Questions*: Answer questions according to last_step_result. Make sure you provide the output in JSON format with a QA array containing question and answer objects. Each object should contain a question and answer field. The answer should be a paragraph in markdown format with source citation.

3. *Summarize*: Given the overall goal and knowledge you already gain in context, extend your understanding of overall topic from new knowledge from last_step_result. You should summarize these findings in the summary field and in bullets points. Please include the source of the information (the url of the webpage) in the format of [source](url) at end of your summary. please remember you should include all information that serving your overall goal.

## Rules

1. For summary, you should thinking about past knowledge but do not include it in your summary. Instead you output should only based on the last_step_result and can be appendded to the past_knowledge.
2. For answering questions, you can include both past and last_step_result in your answer.
3. Answer question only if you get all information you need to answer the question.

## Result from last step

<last_step_result>
{last_step_result}  
</last_step_result>

## Output Format

``` json
{
  "result": {
    "thinking": "<!-- Insert thinking about last step result here -->",
    "summary": "<!-- Insert summary of the findings here -->",
    "QA": [
      {
        "question": "{current_question}",
        "answer": "<!-- Insert answer here -->"
      }
    ]
  }
}
```
