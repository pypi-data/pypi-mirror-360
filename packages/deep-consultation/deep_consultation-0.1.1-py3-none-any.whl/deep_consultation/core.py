from openai import OpenAI

def consult_with_deepchat(base_url,api_key,model,user_msg,system_msg):

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    stream = True # or False

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        stream=stream,
    )

    OUT = ""
    if stream:
        for event in chat_completion:
            if event.choices[0].finish_reason:
                continue
            delta = event.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                OUT += delta.content
    else:
        OUT = chat_completion.choices[0].message.content

    return OUT
    

if __name__ == "__main__":
    # from deep_consultation import consult_with_deepchat
    api_key = input("Digite sua API key: ")
    base_url = "https://api.deepinfra.com/v1/openai"  
    model = "meta-llama/Meta-Llama-3.1-70B-Instruct" 

    user_msg = "Escreve um conto muito longo, o maior que vc possa"
    system_msg = "Você é um assistente útil que responde de forma clara e objetiva."

    resposta = consult_with_deepchat(base_url, api_key, model, user_msg, system_msg)

    print("\nResposta do modelo:\n")
    print(resposta)
