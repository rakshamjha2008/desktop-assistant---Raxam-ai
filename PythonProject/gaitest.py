from google import genai
from config import apikey

# Gemini model
MODEL = "gemini-3-flash-preview"

# Connect to Gemini
client = genai.Client(api_key=apikey)


def test_raxam_ai():
    try:
        print("=" * 40)
        print("       RAXAM AI CONNECTION TEST")
        print("=" * 40)

        response = client.models.generate_content(
            model=MODEL,
            contents=(
                "Introduce yourself as RAXAM AI, "
                "the personal AI assistant of Raksham. "
                "Keep your introduction friendly and short."
            ),
        )

        print("\nRAXAM AI:")
        print(response.text)
        print("\nConnection successful!")

    except Exception as error:
        print("\nConnection failed.")
        print("Error:", error)


if __name__ == "__main__":
    test_raxam_ai()


