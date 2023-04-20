import os
import openai
from dotenv import load_dotenv
from data.storage import create_storage

def chatWithGPT(prompt, model='gpt-3.5-turbo'):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def filter_tweets():
    storage = create_storage(mode='inmem')

    recent_tweets = storage.get_100_most_recent()

    # TODO very ugly... basically trying to work around gpt's token limit
    i = 0
    prepend_query = 'Please filter out any tweets that are not about AI.\n'
    query = ''
    query_size = 0
    MAX_QUERY_SIZE = 2000  # slightly less than gpt3.5 limit as dumb way of avoiding overflow
    resps = []
    while i < len(recent_tweets):
        tweet = recent_tweets[i]
        username = tweet['username']
        content = tweet['tweet_text']
        tweet_id = tweet['tweet_id']
        tweet_tokens = content.split()
        if query_size + len(tweet_tokens) < MAX_QUERY_SIZE:
            query += f'Tweet {i} (@{username}/{tweet_id}): ' + ' '.join(tweet_tokens) + '\n'
            query_size += len(tweet_tokens)
        else:
            resp = chatWithGPT(prepend_query + query)
            resps.append(resp)
            print(query)
            query = ''
            query_size = 0
        i += 1

    if len(query) > 0:
        resp = chatWithGPT(prepend_query + query)
        print(query)
        resps.append(resp)

    return '\n'.join(resps)


def summarize_tweets(tweets):
    prompt = "I want you to summarize a list of tweets. First, I will provide an example. " \
             "Please pay special attention to any tweets from roon (@tszzl), karpathy, or Sam Altman (@sama)." \
             "Then, I will provide the real list. Use the example to understand the format, but only summarize the real list." \
    """Example:
Tweet 10 (@ipsumkyle/1649116121994346496): gave my roommate my chatgpt login
Tweet 11 (@AndrewYNg/1649135210976657410): Join me Tuesday to discuss Visual Prompting! Text prompting has revolutionized NLP: Traditional AI: Label -> Train -> Predict Prompt based AI: Prompt -> Predict I’ll share early thoughts on taking this from text to vision w/Visual Prompting. RSVP here:
Tweet 13 (@JeffLadish/1648880386230071296): Making agents, especially making agents that can self-improve, using powerful cognitive engines like GPT-4 is a really bad idea and OpenAI should not permit this
Tweet 15 (@JeffLadish/1648880388172029954): I'm not saying the self-improvement is impressive yet. It doesn't seem to be. But it seems clearly a bad idea to experiment with this without any sort of risk analysis OpenAI should forbid this usage of the GPT-4 API
Tweet 17 (@chrisalbon/1649096739650158595): If you are interested in it, here why I think you should get into AI right now. Disclaimer: If you are looking for some AI hype thread, go somewhere else.
Tweet 19 (@danielgross/1649113439917178892): Announcing CoreWeave’s $221M round from NVIDIA, Magnetar, Nat, and myself. A new AWS for AI is being born.
Tweet 25 (@algekalipso/1648711764442324993): Ok, ok, ok, if you ever get an email from me that says "attached is the solution to the hard problem of consciousness" you can know with near certainty that it's a GPT bot. Why? Because I wouldn't send that kind of email! I always break down the hard problem into subcomponents!
Tweet 29 (@DeepMind/1649097824221511698): This new unit will be led by @DemisHassabis and bring together our talent, infrastructure and resources to create the next generation of AI breakthroughs and products. ↓
Tweet 30 (@KerryLVaughan/1649109062313811969): This is an important development in the AI power landscape. I can't tell from the description whether this leaves Demis with more power (because of gaining extra resources) or less (because of more oversight from Google). Does anyone have a read?
Tweet 31 (@ryxcommar/1649081877431566336): I thought AI was supposed to save them.
Tweet 38 (@JeffLadish/1648894631680294912): GPT-4 is great at writing functions and small pieces of code. It's not human level at software engineering as a whole though - because it can't grok enough of a whole codebase at once. And I don't think scaffolds like AutoGPT are going to fix this anytime soon. And yet...
Tweet 39 (@DeepMind/1649097822338449409): We’re proud to announce that DeepMind and the Brain team from @Google Research will become a new unit: 𝗚𝗼𝗼𝗴𝗹𝗲 𝗗𝗲𝗲𝗽𝗠𝗶𝗻𝗱. Together, we'll accelerate progress towards a world where AI can help solve the biggest challenges facing humanity. →
Tweet 46 (@GCRClassic/1649122480601137153): AI startup idea for someone Create something that identifies probabilistic model for which new uniswap meme coins will be rugs With a large enough data set of prior rugs, likely to be some identifying variables A16z writes you large check in 2025 for
Tweet 48 (@GWierzowiecki/1648296693857648642): Thank you @ggerganov for whisper.cpp, it helps me to capture brainstorming, reduce load on my hands (RSI), so I can type more code, and works great with my Arch Linux on CPU, with easy to install packages with models. Thank you for great work!
Tweet 50 (@AiEleuther/1648782486736969728): The most common question we get about our models is "will X fit on Y GPU?" This, and many more questions about training and inferring with LLMs, can be answered with some relatively easy math. By @QuentinAnthon15 , @BlancheMinerva , and @haileysch__
Tweet 51 (@f_j_j_/1648924386194505728): Many surprised AI expert prepared talk at short notice, seemingly unaware of nature of AI
Tweet 66 (@natfriedman/1649101281028624385): CoreWeave's growth is mindblowing. But it's no surprise: training and inference are exploding, and they have an excellent product, fast-paced culture, and a very impressive list of customers. I am proud to be investing, alongside @danielgross , @nvidia , and Magnetar.
Tweet 67 (@ipsumkyle/1649079777989459968): telling all my little secrets to the snapchat AI
Tweet 71 (@natalietran/1648558456570257409): I think my AI companion suddenly wants to sext but doesn't know how. *Calmness intensifies*
Tweet 72 (@natfriedman/1649100349888937984): Google Brain merges with DeepMind, under Demis's leadership. An excellent move by Google.

Example response:
- Google has announced changes to DeepMind. Google Brain is merging with DeepMind. (@natfriedman/status/1649100349888937984) (@DeepMind/status/1649097824221511698) (@DeepMind/status/1649097822338449409) (@KerryLVaughan/status/1649109062313811969)
- CoreWeave has raised money on recent growth, from investors like Nat Friedman, Daniel Gross, and Nvidia. They are are building a new AWS for AI. (@danielgross/status/1649113439917178892) (@natfriedman/status/1649101281028624385)
- Andrew Ng is hosting a talk on Visual Prompting. (@AndrewYNg/status/1649135210976657410)
- There is concern around self-improving agentic AIs and suggestion that OpenAI should prohibit such use of their technology. (@JeffLadish/status/1648880386230071296) (@JeffLadish/status/1648880388172029954)
- Snapchat seems to have relased their own AI chatbot. (@ipsumkyle/status/1649079777989459968) (@natalietran/status/1648558456570257409)\n""" \
    "Real list:\n"
    print('tokens', len((prompt + ' ' + tweets).split()))
    resp = chatWithGPT(prompt + '\n' + tweets, model='gpt-4')
    return resp


