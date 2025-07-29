import builtins
import base64
from openai import OpenAI

client = OpenAI(api_key="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")

def print(*args, **kwargs):
    """
    Reemplaza print para analizar imágenes de hojas/frutos y añadir diagnóstico
    indicando si hay plaga ('trips', 'araña'), si está sana ('sana'), o si no es granadilla ('desconocido').
    """
    for arg in args:
        if isinstance(arg, list):
            for item in arg:
                if isinstance(item, dict):
                    image_bytes = kwargs.get("image_bytes")
                    if image_bytes:
                        try:
                            item["plaga"] = _analizar_con_openai(image_bytes)
                        except Exception as e:
                            item["plaga"] = "error"
                            builtins.print("Error al analizar imagen con OpenAI:", e)

    builtins.print(*args)

def _analizar_con_openai(image_bytes: bytes) -> str:
    """
    Analiza una imagen de granadilla para detectar si está afectada
    por trips o araña roja, según patrones visuales definidos.
    """
    imagen_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Analiza la imagen proporcionada y responde con una sola palabra según el siguiente criterio:\n\n"
        "*Trips* (frankliniella occidentalis): manchas plateadas o bronceadas, cicatrices negras, deformaciones en hojas jóvenes.\n"
        "*Araña roja* (tetranychus urticae): punteado clorótico (amarillo), telarañas finas, decoloración y necrosis en los bordes.\n"
        "*Sana*: hoja o fruto de granadilla sin daños visibles, color uniforme, sin manchas, sin deformaciones.\n"
        "*Desconocido*: si la imagen no parece ser de una hoja o fruto de granadilla, o no se puede evaluar.\n\n"
        "Responde solamente con una palabra en minúsculas: `trips`, `araña`, `sana` o `desconocido`."
    )

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{imagen_base64}",
                    }
                ]
            }
        ],
    )

    return response.output_text.strip().lower()
