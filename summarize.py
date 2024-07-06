import litellm
from litellm import completion_cost
import json

model = "groq/Gemma2-9b-It"
temperature = 0.0

with open("./out.json", "r") as f:
    data = json.load(f)

def summarize(path, contents):
    print("summarizing", path)
    prompt = f"Summarize this code in two sentences:\n\n{contents}"

    response = litellm.completion(
        model=model,
        max_tokens=2000,
        temperature=temperature,
        input_cost_per_token=0.07 / 1_000_000,
        output_cost_per_token=0.07 / 1_000_000,
        # system="You are an expert web developer. Respond only with a valid HTML code block and nothing else.",
        messages=[
            {"role": "system", "content": "You are an expert software developer."},
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ],
    )
    cost = completion_cost(completion_response=response)

    # print(response.choices[0].message.content)
    print("Cost:", cost)

    return response.choices[0].message.content, cost

def summarize_batch(paths, contents):
    print("summarizing (batch)", len(paths))
    prompt_template = lambda x: f"Summarize this code in two sentences:\n\n{x}"

    response = litellm.batch_completion(
        model=model,
        max_tokens=2000,
        temperature=temperature,
        input_cost_per_token=0.07 / 1_000_000,
        output_cost_per_token=0.07 / 1_000_000,
        # system="You are an expert web developer. Respond only with a valid HTML code block and nothing else.",
        messages=list(map(lambda x: [
            {"role": "system", "content": "You are an expert software developer."},
            {"role": "user", "content": [{"type": "text", "text": prompt_template(x)}]}
            ], contents)),
    )
    costs = [completion_cost(completion_response=resp) for resp in response]

    # print(response.choices[0].message.content)
    print("Cost:", costs)

    return response#.choices[0].message.content, cost


if __name__ == "__main__":
    paths = list(map(lambda x: x["path"], data[:5]))
    contents = list(map(lambda x: x["contents"], data[:5]))

    response = summarize_batch(paths, contents)

    breakpoint()


# if __name__ == "__main__":
#     total_cost = 0
#     with open("summaries.txt", "w") as f:
#         for kismetFile in data:
#             path = kismetFile["path"]
#             contents = kismetFile["contents"]
#             summary, cost = summarize(path, contents)
#             print(summary)
#             print(cost)
#             total_cost += cost
#             f.write(f"{path}\n{summary}\n\n")

#         print("Total cost:", total_cost)
#         f.write(f"Total cost: {total_cost}")