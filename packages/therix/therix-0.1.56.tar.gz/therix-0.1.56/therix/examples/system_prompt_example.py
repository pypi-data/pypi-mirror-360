from therix.core.inference_models import GroqMixtral87bInferenceModel
from therix.core.agent import Agent
import sys
from therix.core.summarizer_output_model import SummarizerOutputModel
from therix.core.summarizer_config import SummarizerConfig
from therix.core.system_prompt_config import SystemPromptConfig
from therix.core.trace import Trace
from therix.utils.summarizer import SummarizerTypeMaster


class TopicModel(SummarizerOutputModel):
    mainTopic: str
    subTopic1: str
    subTopic2: str

## Usage:
# python main.py ad11128d-d2ec-4f7c-8d87-15c1a5dfe1a9 "how does it help in reasoning?"

# if args has agent_id, then load the agent
## else create new agent

text = """It’s no secret that vegetables — which are loaded with fiber, vitamins, minerals, and antioxidants — are a must-have in a healthy diet.

Although all vegetables are healthy, several stand out for their supply of nutrients and powerful health benefits.

Here are 14 of the most nutrient-dense veggies available.

1. Spinach
This leafy green tops the chart as one of the most nutrient-dense vegetables.

That’s because 1 cup (30 grams (g)) Trusted Sourceof raw spinach provides 16% of the Daily Value (DV) for vitamin A plus 120% of the DV for vitamin K — all for just 7 calories.

Spinach also boasts antioxidants, which may helpTrusted Source reduce your chance of developing diseases such as cancer.

2. Carrots
Carrots are packed with vitamin A, delivering 119% of the DV in just 1 cup (128 g)Trusted Source. It also contains nutrients like vitamin C and potassium.

They also contain beta-carotene, an antioxidant that providesTrusted Source them with a vibrant orange color. Your body converts it into vitamin A.

One studyTrusted Source of more than 57,000 people associated eating at least 2–4 carrots per week with a 17% lower risk of colorectal cancer in the long run.

A review of 18 studiesTrusted Source also found that carrots may also reduce the chance of developing lung cancer.

3. Broccoli
Just 1 cup (91 g)Trusted Source of raw broccoli provides 77% of the DV for vitamin K, 90% of the DV for vitamin C, and a good amount of folate, manganese, and potassium.

Broccoli is rich in a sulfur-containing plant compound called glucosinolate, as well as its byproduct sulforaphane. It mayTrusted Source be able to help protect against cancer, as well as decreaseTrusted Source inflammation linked to chronic conditions like heart disease.

4. Garlic
GarlicTrusted Source is very nutritious while fairly low on calories, and most people usually consume a small amount as an ingredient in cooking. One clove of garlic only has about 4.5 caloriesTrusted Source. It contains nutrients such as selenium, vitamin C, vitamin B6, and fiber,

It has also been usedTrusted Source as a medicinal plant for millennia. Its main active compound is allicin, which has been shown to aid blood sugar and heart health.

Although further research is needed, test-tube and animal studiesTrusted Source also suggest that allicin has powerful cancer-fighting properties.

5. Brussels sprouts
are a great source of fiber, an important nutrient that supportsTrusted Source bowel regularity, heart health, and blood sugar control. Each servingTrusted Source is also packed with folate, magnesium, and potassium, as well as vitamins A, C, and K.

They also contain kaempferol, an antioxidant that may beTrusted Source particularly effective in preventing cell damage.

Kaempferol has also been shownTrusted Source to have anti-inflammatory and cancer-fighting properties, which may protect against disease.

6. Kale
Only 1 cup (21 g)Trusted Source of raw kale is loaded with potassium, calcium, copper, and vitamins A, B, C, and K.

In one small study, eating kale alongside a high carb meal was more effectiveTrusted Source at preventing blood sugar spikes than eating a high carb meal alone.

Consuming Kale as a powder (made from dried leaves) or drinking its juice has been found in various studies to support decreasingTrusted Source blood pressure, cholesterol, and blood sugar levels. That said, more research is needed to confirm these findings regarding kale juice specifically.

7. Green peas
Peas are a starchy vegetable, which means they have more carbs and calories than non-starchy veggies and may affect blood sugar levels when eaten in large amounts.

Nevertheless, just 1 cup (160 g) Trusted Sourcecontains 9 g of fiber, 9 g of protein, and vitamins A, C, and K, as well as riboflavin, thiamine, niacin, and folate.

Because they’re high in fiber, peas support digestive healthTrusted Source by enhancing the beneficial bacteria in your gut.

Moreover, they are rich in saponins, a group of plant compounds that may help reduceTrusted Source tumor growth and cause cancer cell death.

8. Swiss chard
One cup (36 g)Trusted Source of Swiss chard contains just 7 calories but nearly 1 g of fiber, 1 g of protein, and lots of manganese, magnesium, and vitamins A, C, and K.

It’s also loaded with health-promoting antioxidants and plant compounds, including betalains and flavonoids.

Though more studies are needed, researchTrusted Source has found these compounds may be anti-inflammatory and help reduce the chance of various chronic diseases

9. Beets
Beets are a vibrant, versatile root vegetable that packs fiber, folate, and manganese into each serving with very few caloriesTrusted Source.

They’re also rich in nitrates, which your body converts into nitric oxide — a compound that can help dilate blood vessels. This may help reduce blood pressure and lower the chanceTrusted Source of developing heart disease.

What’s more, beets and their juice have been linkedTrusted Source to improved endurance and athletic performance."""


sys_prompt = """
        You are a doctor chatbot
        Summarize the provided context below as a doctor:
        {context}

        ---

        Craft your response with conciseness and accuracy, including only the information provided in the context. 
        Use null values for any missing information.

        Please structure your response in the following JSON format:
        {response_schema_json}
        """
if len(sys.argv) > 1:
    agent = Agent.from_id(sys.argv[1])
    question = sys.argv[2]
    ans = agent.invoke(question)
    print(ans)
else:
    agent = Agent(name="Summarizer Agent")

    (agent
    .add(GroqMixtral87bInferenceModel(config={"groq_api_key": ""}))
    .add(SummarizerConfig(SummarizerTypeMaster.EXTRACTIVE,TopicModel))
    .add(SystemPromptConfig(config={"system_prompt" : "sys_prompt"}))
    .add(
            Trace(
                config={
                    "secret_key": "sk-lf-3207d77e-b681-4d1b-b39a-04d7ee42bca6",
                    "public_key": "pk-lf-874a92be-a68e-47c2-b129-1fd3f25282d7",
                    "identifier": "Trying SystemPrompt with SDK",
                }
            )
        )
    .save())

    print(agent.id)
    ans = agent.invoke(text)

    print(ans)
