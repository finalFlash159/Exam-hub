import os
from dotenv import load_dotenv

def main() -> None:
    # Load env
    load_dotenv('.env')
    print('HAS_KEY=', bool(os.getenv('OPENAI_API_KEY')))

    try:
        from openai import OpenAI
    except Exception as e:
        print('SDK_IMPORT_ERROR:', e)
        return

    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        messages = [{"role": "user", "content": "Reply with OK"}]
        resp = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=messages,
            temperature=0.0,
            max_tokens=10,
        )
        print('Choices:', len(resp.choices))
        if resp.choices:
            print('Message:', resp.choices[0].message.content.strip())
    except Exception as e:
        import traceback
        print('CALL_ERROR:', type(e).__name__, str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()


